#!/usr/bin/env python3
import re, os, glob, json, sys
from git_util import git_run as _git_run, get_git_path as _get_git_path, _make_push_url

_APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(_APP_DIR, "site")
SETTINGS_DIR = os.path.join(_APP_DIR, "settings")
TEMPLATE_FILE = os.path.join(SITE_DIR, "template.html")
CONFIG_FILE = os.path.join(SETTINGS_DIR, "config.json")
ROOT_CONFIG_FILE = os.path.join(_APP_DIR, "site_tools.config")

import sidebar_util
sidebar_util.SITE_DIR = SITE_DIR

_SKIP_DIRS = {'.git', '__pycache__', 'node_modules', 'build', 'build_venv', 'dist', '.github', 'fonts', 'bundled-git', 'mingit', 'ckeditor'}
_SKIP_FILES = {'template.html', '404.html'}

_CONFIG_CACHE = None

def load_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    default = {
        "owner_name": "",
        "owner_bio": "",
        "owner_title": "",
        "owner_contacts": [],
        "site_title": "Placeholder",
        "gui_font_size": 14,
        "site_padding": 20,
    }
    token_keys = ["supabase_url", "supabase_anon_key", "git_remote_url",
                   "git_user_name", "git_user_email", "github_token"]
    for k in token_keys:
        default[k] = ""
    cfg = dict(default)
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as f:
            cfg.update({k: v for k, v in json.load(f).items() if k in default})
    if os.path.exists(ROOT_CONFIG_FILE):
        with open(ROOT_CONFIG_FILE, encoding="utf-8") as f:
            cfg.update({k: v for k, v in json.load(f).items() if k in token_keys})
    _CONFIG_CACHE = cfg
    return cfg

def clear_config_cache():
    global _CONFIG_CACHE
    _CONFIG_CACHE = None

CONFIG = load_config()
_SIDEBAR_CACHE = None

def get_sidebar_cached():
    global _SIDEBAR_CACHE
    if _SIDEBAR_CACHE is None:
        _SIDEBAR_CACHE = sidebar_util.load_sidebar()
    return _SIDEBAR_CACHE

def clear_sidebar_cache():
    global _SIDEBAR_CACHE
    _SIDEBAR_CACHE = None

def save_config(cfg):
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    token_keys = {"supabase_url", "supabase_anon_key", "git_remote_url",
                   "git_user_name", "git_user_email", "github_token"}
    tokens = {k: cfg[k] for k in token_keys if k in cfg}
    settings = {k: v for k, v in cfg.items() if k not in token_keys}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
    if tokens:
        with open(ROOT_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(tokens, f, indent=2)
    clear_config_cache()

def scan_categories():
    sidebar_data = get_sidebar_cached()
    categories = []
    for cat in sidebar_data:
        entries = []
        for entry in cat["entries"]:
            full_path = os.path.join(SITE_DIR, entry["file"].lstrip('/'))
            if os.path.exists(full_path):
                entries.append((entry["name"], entry["file"]))
        if entries:
            categories.append((cat["category"], entries))
    return categories

def rel_path(from_file, to_absolute):
    from_dir = os.path.dirname(os.path.abspath(from_file))
    to_full = os.path.join(SITE_DIR, to_absolute.lstrip('/'))
    return os.path.relpath(to_full, from_dir).replace('\\', '/')

def generate_sidebar(categories, current_file):
    owner_name = CONFIG.get("owner_name", "")
    owner_bio = CONFIG.get("owner_bio", "")
    owner_avatar = "avatar.png" if os.path.exists(os.path.join(SITE_DIR, "avatar.png")) else ""
    owner_title = CONFIG.get("owner_title", "")
    html = ''
    if owner_name:
        html += '      <div class="sidebar-owner">\n'
        if owner_avatar:
            src = rel_path(current_file, '/' + owner_avatar)
            html += f'        <img src="{src}" alt="{owner_name}" class="owner-avatar">\n'
        html += f'        <div class="owner-name">{owner_name}</div>\n'
        if owner_title:
            html += f'        <div class="owner-title">{owner_title}</div>\n'
        if owner_bio:
            html += f'        <div class="owner-bio">{owner_bio}</div>\n'
        html += '      </div>\n'
    html += '      <div class="sidebar-top">\n'
    html += '        <h2>Menu</h2>\n'
    html += '        <button class="close-btn" onclick="toggleSidebar()">&times;</button>\n'
    html += '      </div>\n'
    for cat_name, entries in categories:
        html += '      <div class="category">\n'
        html += f'        <div class="category-header" onclick="toggleCategory(this)">\n'
        html += f'          {cat_name} <span class="arrow">&#9654;</span>\n'
        html += '        </div>\n'
        html += '        <ul class="sub-links">\n'
        for name, file_path in entries:
            href = rel_path(current_file, file_path)
            html += f'          <li><a href="{href}">{name}</a></li>\n'
        html += '        </ul>\n'
        html += '      </div>\n'
    return html



def extract_main(html):
    if '<main' not in html:
        return html.strip()
    m = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
    if m:
        return m.group(1).strip()
    pos = html.find('<main')
    end = html.find('</main>', pos)
    if end != -1:
        return html[pos + html[pos:].find('>') + 1:end].strip()
    return html.strip()

def extract_title(html):
    if '<title' not in html:
        return "Page"
    m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    if m:
        return m.group(1).strip()
    pos = html.find('<title>')
    end = html.find('</title>', pos)
    if end != -1:
        return html[pos + 7:end].strip()
    return "Page"

def make_comments_block(filepath):
    url = CONFIG.get("supabase_url", "")
    key = CONFIG.get("supabase_anon_key", "")
    if not url or not key:
        return '', ''
    rel = '/' + os.path.relpath(filepath, SITE_DIR).replace('\\', '/')
    for cat in get_sidebar_cached():
        for entry in cat["entries"]:
            if entry["file"] == rel and entry.get("comments") is False:
                return '', ''
    page = rel.replace('/index.html', '/').replace('.html', '')
    block = '''  <div id="comments-section" data-page="''' + page + '''">
    <h3>Comments</h3>
    <div id="comments-list"></div>
    <form id="comment-form">
      <input id="comment-name" type="text" placeholder="Your name" required>
      <textarea id="comment-body" placeholder="Write a comment..." required></textarea>
      <button type="submit">Post Comment</button>
    </form>
  </div>
  <script>
const SUPABASE_URL = ''' + repr(url) + ''';
const SUPABASE_ANON_KEY = ''' + repr(key) + ''';
(function() {
  var section = document.getElementById('comments-section');
  var page = section ? section.getAttribute('data-page') : '/';
  async function loadComments() {
    try {
      var res = await fetch(
        SUPABASE_URL + '/rest/v1/comments?page=eq.' + encodeURIComponent(page) + '&order=created_at.desc',
        { headers: { apikey: SUPABASE_ANON_KEY } }
      );
      if (!res.ok) return;
      var comments = await res.json();
      var list = document.getElementById('comments-list');
      if (!list) return;
      if (comments.length === 0) {
        list.innerHTML = '<p class="no-comments">No comments yet.</p>';
        return;
      }
      list.innerHTML = comments.map(function(c) {
        return '<div class="comment">' +
          '<div class="comment-header">' +
            '<strong>' + esc(c.name) + '</strong>' +
            '<span class="comment-date">' + new Date(c.created_at).toLocaleDateString() + '</span>' +
          '</div>' +
          '<p>' + esc(c.body) + '</p>' +
        '</div>';
      }).join('');
    } catch (e) {}
  }
  async function submitComment(e) {
    e.preventDefault();
    var nameInput = document.getElementById('comment-name');
    var bodyInput = document.getElementById('comment-body');
    var name = nameInput.value.trim();
    var body = bodyInput.value.trim();
    if (!name || !body) return;
    var btn = e.target.querySelector('button');
    btn.disabled = true;
    try {
      await fetch(SUPABASE_URL + '/rest/v1/comments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          apikey: SUPABASE_ANON_KEY,
          Prefer: 'return=representation'
        },
        body: JSON.stringify({ page: page, name: name, body: body })
      });
    } catch (e) {}
    nameInput.value = '';
    bodyInput.value = '';
    btn.disabled = false;
    loadComments();
  }
  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }
  document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('comment-form');
    if (form) {
      form.addEventListener('submit', submitComment);
      loadComments();
    }
  });
})();
  </script>'''
    return block, ''

CONTACT_PATTERNS = [
    ('whatsapp',  lambda u: 'https://wa.me/' + u.lstrip('+').replace('-','').replace(' ','')),
    ('telegram',  lambda u: 'https://t.me/' + u.lstrip('@')),
    ('youtube',   lambda u: 'https://youtube.com/@' + u.lstrip('@')),
    ('instagram', lambda u: 'https://instagram.com/' + u.lstrip('@')),
    ('twitter',   lambda u: 'https://x.com/' + u.lstrip('@')),
    ('x',         lambda u: 'https://x.com/' + u.lstrip('@')),
    ('facebook',  lambda u: 'https://facebook.com/' + u.lstrip('@')),
    ('github',    lambda u: 'https://github.com/' + u.lstrip('@')),
    ('linkedin',  lambda u: 'https://linkedin.com/in/' + u.lstrip('@')),
    ('phone',     lambda u: 'tel:' + u.lstrip('+').replace('-','').replace(' ','')),
]

def normalize_contact_url(label, url):
    if url.startswith(('http://', 'https://', 'mailto:', 'tel:')):
        return url
    if '@' in url and '.' in url.split('@')[-1]:
        return 'mailto:' + url
    label_lower = label.lower()
    for keyword, builder in CONTACT_PATTERNS:
        if keyword in label_lower:
            return builder(url)
    if '@' in url:
        return 'mailto:' + url
    return url

def make_homepage_content(categories, current_file):
    owner_name = CONFIG.get("owner_name", "")
    owner_bio = CONFIG.get("owner_bio", "")
    owner_avatar = "avatar.png" if os.path.exists(os.path.join(SITE_DIR, "avatar.png")) else ""
    owner_title = CONFIG.get("owner_title", "")
    owner_contacts = CONFIG.get("owner_contacts", [])
    html = '''<div class="home-hero">
  <h1>Welcome</h1>
  <p class="home-tagline">Explore the site</p>
</div>
<div class="home-sections">
'''
    if owner_name:
        html += '  <div class="home-card owner-card">\n'
        if owner_avatar:
            src = rel_path(current_file, '/' + owner_avatar)
            html += f'    <img src="{src}" alt="{owner_name}" class="owner-card-avatar">\n'
        html += f'    <div class="owner-card-name">{owner_name}</div>\n'
        if owner_title:
            html += f'    <div class="owner-card-title">{owner_title}</div>\n'
        if owner_bio:
            html += f'    <div class="owner-card-bio">{owner_bio}</div>\n'
        if owner_contacts:
            html += '    <div class="owner-card-contacts">\n'
            for c in owner_contacts:
                url = normalize_contact_url(c.get("label", ""), c.get("url", ""))
                html += f'      <a href="{url}" class="owner-card-link">{c["label"]}</a>\n'
            html += '    </div>\n'
        html += '  </div>\n'
    for cat_name, entries in categories:
        html += f'''  <div class="home-card">
    <h2>{cat_name}</h2>
    <ul>
'''
        for name, file_path in entries:
            href = rel_path(current_file, file_path)
            html += f'      <li><a href="{href}">{name}</a></li>\n'
        html += '''    </ul>
  </div>
'''
    html += '</div>'
    return html

def build_page(filepath, categories):
    with open(filepath, encoding="utf-8") as f:
        src = f.read()

    if not os.path.exists(TEMPLATE_FILE):
        return False

    title = extract_title(src)
    is_home = os.path.basename(filepath) == 'index.html'
    content = make_homepage_content(categories, filepath) if is_home else extract_main(src)
    sidebar = generate_sidebar(categories, filepath)
    comments_block, _ = make_comments_block(filepath)
    style_rel = os.path.relpath(os.path.join(SITE_DIR, 'style.css'), os.path.dirname(os.path.abspath(filepath)))
    style_rel = style_rel.replace('\\', '/')
    adv_css = os.path.join(SITE_DIR, 'advanced.css')
    if os.path.exists(adv_css):
        adv_rel = os.path.relpath(adv_css, os.path.dirname(os.path.abspath(filepath)))
        adv_rel = adv_rel.replace('\\', '/')
    else:
        adv_rel = ''
    content_css = os.path.join(SITE_DIR, 'content.css')
    if os.path.exists(content_css):
        content_rel = os.path.relpath(content_css, os.path.dirname(os.path.abspath(filepath)))
        content_rel = content_rel.replace('\\', '/')
    else:
        content_rel = ''
    toggle = '        <button class="theme-toggle" onclick="toggleTheme()">\u2600\ufe0f</button>'

    # Video background
    adv_json_path = os.path.join(SETTINGS_DIR, "advanced_theme.json")
    video_html = ""
    if os.path.exists(adv_json_path):
        try:
            with open(adv_json_path, encoding="utf-8") as _f:
                adv_data = json.load(_f)
            bg = adv_data.get("backgrounds", {})
            if bg.get("enabled") and bg.get("type") == "video":
                vid_path = bg.get("bg_video", "")
                if vid_path:
                    vid_abs = os.path.join(SITE_DIR, vid_path)
                    if os.path.exists(vid_abs):
                        vid_rel = os.path.relpath(vid_abs, os.path.dirname(os.path.abspath(filepath)))
                        vid_rel = vid_rel.replace("\\", "/")
                        video_html = (
                            '<div id="bg-video-container">'
                            '<video autoplay muted loop playsinline id="bg-video">'
                            f'<source src="{vid_rel}" type="video/webm">'
                            '</video>'
                            '</div>'
                        )
        except Exception:
            video_html = ""

    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        tmpl = f.read()

    site_title = CONFIG.get("site_title", "Placeholder")
    home_rel = os.path.relpath(SITE_DIR, os.path.dirname(os.path.abspath(filepath)))
    home_path = os.path.join(home_rel, 'index.html').replace('\\', '/')
    result = tmpl.replace('{{HOME_PATH}}', home_path)
    result = result.replace('{{SITE_TITLE}}', site_title)
    result = result.replace('{{TITLE}}', title)
    result = result.replace('{{STYLE_PATH}}', style_rel)
    result = result.replace('{{CONTENT_STYLE_PATH}}', content_rel)
    result = result.replace('{{ADVANCED_STYLE_PATH}}', adv_rel)
    result = result.replace('{{THEME_TOGGLE}}', toggle)
    result = result.replace('{{VIDEO_BG}}', video_html)
    result = result.replace('{{SIDEBAR}}', sidebar)
    result = result.replace('{{CONTENT}}', content)
    result = result.replace('{{COMMENTS}}', comments_block)
    padding = CONFIG.get("site_padding", 20)
    result = result.replace('{{SITE_PADDING}}', str(padding))

    with open(filepath, 'w', encoding="utf-8") as f:
        f.write(result)
    return True



def generate_404(categories, log_func=print):
    path = os.path.join(SITE_DIR, "404.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Not Found</title>
</head>
<body>
  <main>
    <div class="home-hero">
      <h1>404</h1>
      <p class="home-tagline">Page not found</p>
      <p style="margin-top:1rem"><a href="index.html">Go home</a></p>
    </div>
  </main>
</body>
</html>""")
    if build_page(path, categories):
        log_func("  Generated: 404.html")
    return True


def generate_all(log_func=print):
    clear_sidebar_cache()
    clear_config_cache()
    CONFIG.update(load_config())
    try:
        categories = scan_categories()
        log_func(f"Found {len(categories)} section{'s' if len(categories)!=1 else ''} from folders")

        html_files = glob.glob(os.path.join(SITE_DIR, "**/*.html"), recursive=True)
        updated = 0
        for fp in sorted(html_files):
            rel = os.path.relpath(fp, SITE_DIR)
            if any(part in _SKIP_DIRS for part in rel.split(os.sep)):
                continue
            if os.path.basename(fp) in _SKIP_FILES:
                continue
            if build_page(fp, categories):
                rel = os.path.relpath(fp, SITE_DIR)
                log_func(f"  Wrapped: {rel}")
                updated += 1

        index_path = os.path.join(SITE_DIR, "index.html")
        if not os.path.exists(index_path):
            with open(index_path, "w", encoding="utf-8") as f:
                f.write("<!DOCTYPE html><html><head><title>Home</title></head><body><main></main></body></html>")
            log_func("  Created: index.html")
            if build_page(index_path, categories):
                log_func("  Wrapped: index.html")
                updated += 1

        generate_404(categories, log_func)
        updated += 1

        log_func(f"\nDone. {updated} files wrapped.")
        return True
    finally:
        clear_sidebar_cache()

def git_commit_push(log_func=print):
    msg = "update site via generator"
    url = CONFIG.get("git_remote_url", "")
    token = CONFIG.get("github_token", "")
    push_url = _make_push_url(url, token)
    name = CONFIG.get("git_user_name", "")
    email = CONFIG.get("git_user_email", "")
    orig_remote = None
    try:
        if name:
            _git_run(["config", "user.name", name], cwd=SITE_DIR, capture_output=True)
        if email:
            _git_run(["config", "user.email", email], cwd=SITE_DIR, capture_output=True)
        if url:
            r = _git_run(["remote", "get-url", "origin"], cwd=SITE_DIR, capture_output=True, text=True)
            if r.returncode == 0:
                orig_remote = r.stdout.strip()
            if orig_remote != push_url:
                _git_run(["remote", "remove", "origin"], cwd=SITE_DIR, capture_output=True)
                _git_run(["remote", "add", "origin", push_url], cwd=SITE_DIR, capture_output=True)
        _git_run(["add", "-A"], cwd=SITE_DIR, check=True, capture_output=True)
        r = _git_run(["commit", "-m", msg], cwd=SITE_DIR, capture_output=True, text=True)
        if r.returncode == 0:
            log_func(r.stdout.strip())
        else:
            log_func(r.stderr.strip())
        if url:
            _git_run(["pull", "--rebase", "origin", "HEAD"], cwd=SITE_DIR, capture_output=True, text=True)
            r2 = _git_run(["push", "-u", "origin", "HEAD"], cwd=SITE_DIR, capture_output=True, text=True)
            log_func(r2.stdout.strip() or r2.stderr.strip())
    except Exception as e:
        log_func(f"Git error: {e}")
    finally:
        if orig_remote and orig_remote != push_url:
            _git_run(["remote", "remove", "origin"], cwd=SITE_DIR, capture_output=True)
            _git_run(["remote", "add", "origin", orig_remote], cwd=SITE_DIR, capture_output=True)
def run_generate_captured():
    """Run local generate only (no git). Returns last line of output."""
    import io
    buf = io.StringIO()
    def log(msg):
        print(msg)
        buf.write(msg + '\n')
    clear_config_cache()
    CONFIG.update(load_config())
    generate_all(log)
    output = buf.getvalue().strip()
    return output.split('\n')[-1] if output else "Done"

def main():
    generate_all()

if __name__ == "__main__":
    main()
