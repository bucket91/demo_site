#!/usr/bin/env python3
import re, os, glob, json

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(SITE_DIR, "template.html")
REF_FILE = os.path.join(SITE_DIR, "template reference.txt")
CONFIG_FILE = os.path.join(SITE_DIR, "config.json")

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
        "owner_name": "",
        "owner_bio": "",
        "owner_avatar": "",
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return {**default, **json.load(f)}
    return default

CONFIG = load_config()

def parse_ref(filepath):
    categories = []
    with open(filepath) as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        indent = len(line) - len(line.lstrip('\t'))
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if indent == 1:
            cat_name = stripped
            entries = []
            i += 1
            while i < len(lines):
                l = lines[i]
                ind = len(l) - len(l.lstrip('\t'))
                s = l.strip()
                if not s:
                    i += 1
                    continue
                if ind < 2:
                    break
                if s.startswith('{Name:'):
                    name = s.split('"')[1]
                    i += 1
                    fl = lines[i].strip()
                    file_path = fl.split('"')[1]
                    entries.append((name, file_path))
                i += 1
            categories.append((cat_name, entries))
        else:
            i += 1

    return categories

def rel_path(from_file, to_absolute):
    from_dir = os.path.dirname(os.path.abspath(from_file))
    to_full = os.path.join(SITE_DIR, to_absolute.lstrip('/'))
    return os.path.relpath(to_full, from_dir)

def generate_sidebar(categories, current_file):
    owner_name = CONFIG.get("owner_name", "")
    owner_bio = CONFIG.get("owner_bio", "")
    owner_avatar = CONFIG.get("owner_avatar", "")
    html = ''
    if owner_name:
        html += '      <div class="sidebar-owner">\n'
        if owner_avatar:
            html += f'        <img src="{owner_avatar}" alt="{owner_name}" class="owner-avatar">\n'
        html += f'        <div class="owner-name">{owner_name}</div>\n'
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

def write_comments_js():
    url = CONFIG.get("supabase_url", "")
    key = CONFIG.get("supabase_anon_key", "")
    js = '''const SUPABASE_URL = $URL;
const SUPABASE_ANON_KEY = $KEY;

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
'''.replace('$URL', repr(url)).replace('$KEY', repr(key))
    with open(os.path.join(SITE_DIR, 'comments.js'), 'w') as f:
        f.write(js)

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
    js_rel = os.path.relpath(os.path.join(SITE_DIR, 'comments.js'), os.path.dirname(os.path.abspath(filepath)))
    block = '''  <div id="comments-section" data-page="''' + page + '''">
    <h3>Comments</h3>
    <div id="comments-list"></div>
    <form id="comment-form">
      <input id="comment-name" type="text" placeholder="Your name" required>
      <textarea id="comment-body" placeholder="Write a comment..." required></textarea>
      <button type="submit">Post Comment</button>
    </form>
  </div>
  <script src="''' + js_rel + '''"></script>'''
    return block, js_rel

def make_nav(filepath):
    rel = os.path.relpath(SITE_DIR, os.path.dirname(os.path.abspath(filepath)))
    home = os.path.join(rel, 'index.html').replace('\\', '/')
    return f'<a href="{home}">Home</a>'

def build_page(filepath, categories):
    with open(filepath) as f:
        src = f.read()

    if not os.path.exists(TEMPLATE_FILE):
        return False

    title = extract_title(src)
    content = extract_main(src)
    sidebar = generate_sidebar(categories, filepath)
    nav = make_nav(filepath)
    comments_block, comments_js_path = make_comments_block(filepath)
    style_rel = os.path.relpath(os.path.join(SITE_DIR, 'style.css'), os.path.dirname(os.path.abspath(filepath)))
    style_rel = style_rel.replace('\\', '/')
    toggle = '        <button class="theme-toggle" onclick="toggleTheme()">\u2600\ufe0f</button>'

    with open(TEMPLATE_FILE) as f:
        tmpl = f.read()

    result = tmpl.replace('{{TITLE}}', title)
    result = result.replace('{{STYLE_PATH}}', style_rel)
    result = result.replace('{{NAV}}', nav)
    result = result.replace('{{THEME_TOGGLE}}', toggle)
    result = result.replace('{{SIDEBAR}}', sidebar)
    result = result.replace('{{CONTENT}}', content)
    result = result.replace('{{COMMENTS}}', comments_block)
    result = result.replace('{{COMMENTS_JS_PATH}}', comments_js_path)

    with open(filepath, 'w') as f:
        f.write(result)
    return True

def generate_all(log_func=print):
    if not os.path.exists(REF_FILE):
        log_func(f"Reference file not found: {REF_FILE}")
        return False

    CONFIG.update(load_config())
    write_comments_js()

    categories = parse_ref(REF_FILE)
    log_func(f"Parsed {len(categories)} categories from reference.txt")

    html_files = glob.glob(os.path.join(SITE_DIR, "**/*.html"), recursive=True)
    updated = 0
    skip = {os.path.basename(TEMPLATE_FILE)}
    for fp in sorted(html_files):
        if os.path.basename(fp) in skip:
            continue
        if build_page(fp, categories):
            rel = os.path.relpath(fp, SITE_DIR)
            log_func(f"  Wrapped: {rel}")
            updated += 1

    log_func(f"\nDone. {updated} files wrapped.")
    return True

def git_commit_push(log_func=print):
    msg = CONFIG.get("git_commit_message", "update site via generator")
    auto = CONFIG.get("git_auto_push", True)
    url = CONFIG.get("git_remote_url", "")
    name = CONFIG.get("git_user_name", "")
    email = CONFIG.get("git_user_email", "")
    try:
        import subprocess
        if name:
            subprocess.run(["git", "config", "user.name", name], cwd=SITE_DIR, capture_output=True)
        if email:
            subprocess.run(["git", "config", "user.email", email], cwd=SITE_DIR, capture_output=True)
        if url:
            r = subprocess.run(["git", "remote", "get-url", "origin"], cwd=SITE_DIR, capture_output=True, text=True)
            if r.returncode != 0 or r.stdout.strip() != url:
                subprocess.run(["git", "remote", "remove", "origin"], cwd=SITE_DIR, capture_output=True)
                subprocess.run(["git", "remote", "add", "origin", url], cwd=SITE_DIR, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=SITE_DIR, check=True, capture_output=True)
        r = subprocess.run(["git", "commit", "-m", msg], cwd=SITE_DIR, capture_output=True, text=True)
        if r.returncode == 0:
            log_func(r.stdout.strip())
        else:
            log_func(r.stderr.strip())
        if auto and url:
            r2 = subprocess.run(["git", "push", "-u", "origin", "HEAD"], cwd=SITE_DIR, capture_output=True, text=True)
            log_func(r2.stdout.strip() or r2.stderr.strip())
    except Exception as e:
        log_func(f"Git error: {e}")

def main():
    generate_all()
    git_commit_push()

if __name__ == "__main__":
    main()
