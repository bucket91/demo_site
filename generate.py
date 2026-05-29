#!/usr/bin/env python3
import re, os, glob, json, sys
from git_util import git_run as _git_run, get_git_path as _get_git_path

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(SITE_DIR, "template.html")
REF_FILE = os.path.join(SITE_DIR, "template reference.txt")
CONFIG_FILE = os.path.join(SITE_DIR, "config.json")
LOCAL_CONFIG_FILE = os.path.join(SITE_DIR, "config.local.json")

def load_config():
    default = {
        "supabase_url": "",
        "supabase_anon_key": "",
        "comments_enabled": True,
        "git_remote_url": "",
        "git_user_name": "",
        "git_user_email": "",
        "git_commit_message": "update site via generator",
        "git_auto_push": True,
        "github_token": "",
        "owner_name": "",
        "owner_bio": "",
        "owner_avatar": "",
        "owner_title": "",
        "owner_contacts": [],
        "site_title": "Placeholder",
        "custom_font_url": "",
        "custom_font_family": "",
        "gui_font_size": 14,
    }
    cfg = default
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as f:
            cfg = {**default, **json.load(f)}
    if os.path.exists(LOCAL_CONFIG_FILE):
        with open(LOCAL_CONFIG_FILE, encoding="utf-8") as f:
            cfg.update(json.load(f))
    return cfg

CONFIG = load_config()

def parse_ref_names():
    ref = {}
    if not os.path.exists(REF_FILE):
        return ref
    with open(REF_FILE, encoding="utf-8") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith('{Name:'):
            name = stripped.split('"')[1]
            i += 1
            fl = lines[i].strip()
            file_path = fl.split('"')[1]
            ref[file_path] = name
        i += 1
    return ref

def scan_categories():
    ref_names = parse_ref_names()
    categories = []
    skip = {'.git', '__pycache__', 'node_modules', 'build', 'build_venv', 'dist', '.github', 'fonts', 'bundled-git', 'mingit'}
    for item in sorted(os.listdir(SITE_DIR)):
        dirpath = os.path.join(SITE_DIR, item)
        if not os.path.isdir(dirpath) or item in skip:
            continue
        html_files = sorted(glob.glob(os.path.join(dirpath, "*.html")))
        if not html_files:
            continue
        cat_name = item.capitalize()
        entries = []
        for fp in html_files:
            rel_fp = '/' + os.path.relpath(fp, SITE_DIR).replace('\\', '/')
            name = ref_names.get(rel_fp)
            if not name:
                name = os.path.splitext(os.path.basename(fp))[0]
                name = name.replace('-', ' ').replace('_', ' ').title()
            entries.append((name, rel_fp))
        categories.append((cat_name, entries))
    return categories

def rel_path(from_file, to_absolute):
    from_dir = os.path.dirname(os.path.abspath(from_file))
    to_full = os.path.join(SITE_DIR, to_absolute.lstrip('/'))
    return os.path.relpath(to_full, from_dir)

def generate_sidebar(categories, current_file):
    owner_name = CONFIG.get("owner_name", "")
    owner_bio = CONFIG.get("owner_bio", "")
    owner_avatar = CONFIG.get("owner_avatar", "")
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
    m = re.search(r'<main>(.*?)</main>', html, re.DOTALL)
    if m:
        return m.group(1).strip()
    return html.strip()

def extract_title(html):
    m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    if m:
        return m.group(1).strip()
    return "Page"

def make_comments_block(filepath):
    if not CONFIG.get("comments_enabled", True):
        return '', ''
    page = '/' + os.path.relpath(filepath, SITE_DIR).replace('\\', '/')
    page = page.replace('/index.html', '/').replace('.html', '')
    url = CONFIG.get("supabase_url", "")
    key = CONFIG.get("supabase_anon_key", "")
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
    await fetch(SUPABASE_URL + '/rest/v1/comments', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: SUPABASE_ANON_KEY,
        Prefer: 'return=representation'
      },
      body: JSON.stringify({ page: page, name: name, body: body })
    });
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

def make_nav(filepath):
    rel = os.path.relpath(SITE_DIR, os.path.dirname(os.path.abspath(filepath)))
    home = os.path.join(rel, 'index.html').replace('\\', '/')
    return f'<a href="{home}">Home</a>'

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
    owner_avatar = CONFIG.get("owner_avatar", "")
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
    nav = make_nav(filepath)
    comments_block, _ = make_comments_block(filepath)
    style_rel = os.path.relpath(os.path.join(SITE_DIR, 'style.css'), os.path.dirname(os.path.abspath(filepath)))
    style_rel = style_rel.replace('\\', '/')
    toggle = '        <button class="theme-toggle" onclick="toggleTheme()">\u2600\ufe0f</button>'

    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        tmpl = f.read()

    site_title = CONFIG.get("site_title", "Placeholder")
    home_rel = os.path.relpath(SITE_DIR, os.path.dirname(os.path.abspath(filepath)))
    home_path = os.path.join(home_rel, 'index.html').replace('\\', '/')
    result = tmpl.replace('{{HOME_PATH}}', home_path)
    result = result.replace('{{SITE_TITLE}}', site_title)
    result = result.replace('{{TITLE}}', title)
    result = result.replace('{{STYLE_PATH}}', style_rel)
    font_url = CONFIG.get("custom_font_url", "") or ""
    font_link = f'  <link href="{font_url}" rel="stylesheet">' if font_url else ""
    result = result.replace('{{FONT_LINK}}', font_link)
    result = result.replace('{{NAV}}', nav)
    result = result.replace('{{THEME_TOGGLE}}', toggle)
    result = result.replace('{{SIDEBAR}}', sidebar)
    result = result.replace('{{CONTENT}}', content)
    result = result.replace('{{COMMENTS}}', comments_block)

    with open(filepath, 'w', encoding="utf-8") as f:
        f.write(result)
    return True

def clean_ref_file(log_func=print):
    if not os.path.exists(REF_FILE):
        return
    with open(REF_FILE, encoding="utf-8") as f:
        lines = f.readlines()
    out = []
    i = 0
    header = ''
    entries_buffer = []
    removed = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped and not stripped.startswith('{Name:') and not stripped.startswith('File:'):
            if header and entries_buffer:
                out.append(header)
                for name_line, file_line in entries_buffer:
                    out.append(name_line)
                    out.append(file_line)
                out.append('\n')
            elif header:
                pass
            header = lines[i]
            entries_buffer = []
        elif stripped.startswith('{Name:'):
            name_line = lines[i]
            i += 1
            file_line = lines[i] if i < len(lines) else ''
            file_path = ''
            if file_line.strip().startswith('File:'):
                try:
                    file_path = file_line.strip().split('"')[1]
                except IndexError:
                    pass
            full_path = os.path.join(SITE_DIR, file_path.lstrip('/')) if file_path else ''
            if full_path and os.path.exists(full_path):
                entries_buffer.append((name_line, file_line))
            else:
                removed += 1
        i += 1
    if header and entries_buffer:
        out.append(header)
        for name_line, file_line in entries_buffer:
            out.append(name_line)
            out.append(file_line)
        out.append('\n')
    with open(REF_FILE, 'w', encoding="utf-8") as f:
        f.write(''.join(out).rstrip('\n') + '\n')
    if removed:
        log_func(f"  Cleaned {removed} stale reference(s)")

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
    CONFIG.update(load_config())
    clean_ref_file(log_func)

    categories = scan_categories()
    log_func(f"Found {len(categories)} section{'s' if len(categories)!=1 else ''} from folders")

    html_files = glob.glob(os.path.join(SITE_DIR, "**/*.html"), recursive=True)
    updated = 0
    skip_dirs = {'.git', '__pycache__', 'node_modules', 'build', 'build_venv', 'dist', '.github', 'fonts', 'bundled-git', 'mingit'}
    skip_base = {os.path.basename(TEMPLATE_FILE), "404.html"}
    for fp in sorted(html_files):
        rel = os.path.relpath(fp, SITE_DIR)
        if any(part in skip_dirs for part in rel.split(os.sep)):
            continue
        if os.path.basename(fp) in skip_base:
            continue
        if build_page(fp, categories):
            rel = os.path.relpath(fp, SITE_DIR)
            log_func(f"  Wrapped: {rel}")
            updated += 1

    generate_404(categories, log_func)
    updated += 1

    log_func(f"\nDone. {updated} files wrapped.")
    return True

def _make_push_url(url, token):
    if token and url.startswith('https://'):
        return url.replace('https://', f'https://{token}@', 1)
    return url


def git_commit_push(log_func=print):
    msg = CONFIG.get("git_commit_message", "update site via generator")
    auto = CONFIG.get("git_auto_push", True)
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
        if auto and url:
            r2 = _git_run(["push", "-u", "origin", "HEAD"], cwd=SITE_DIR, capture_output=True, text=True)
            log_func(r2.stdout.strip() or r2.stderr.strip())
    except Exception as e:
        log_func(f"Git error: {e}")
    finally:
        if orig_remote and orig_remote != push_url:
            _git_run(["remote", "remove", "origin"], cwd=SITE_DIR, capture_output=True)
            _git_run(["remote", "add", "origin", orig_remote], cwd=SITE_DIR, capture_output=True)
def run_generate_captured():
    """Run generate and return the last line of output."""
    import io
    buf = io.StringIO()
    def log(msg):
        print(msg)
        buf.write(msg + '\n')
    CONFIG.update(load_config())
    generate_all(log)
    git_commit_push(log)
    output = buf.getvalue().strip()
    return output.split('\n')[-1] if output else "Done"

def main():
    generate_all()
    git_commit_push()

if __name__ == "__main__":
    main()
