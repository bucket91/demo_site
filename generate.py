#!/usr/bin/env python3
import re, os, glob

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_FILE = os.path.join(SITE_DIR, "template reference.txt")

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
                    # next line should be File:
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
    html = '      <div class="sidebar-top">\n'
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

COMMENTS_ENABLED = True

COMMENTS_BLOCK = '''  <div id="comments-section" data-page="{page}">
    <h3>Comments</h3>
    <div id="comments-list"></div>
    <form id="comment-form">
      <input id="comment-name" type="text" placeholder="Your name" required>
      <textarea id="comment-body" placeholder="Write a comment..." required></textarea>
      <button type="submit">Post Comment</button>
    </form>
  </div>
'''

def cleanup_old(content):
    content = re.sub(r'<div id="giscus-comments".*?</div>\s*', '', content, flags=re.DOTALL)
    content = re.sub(r'<script src="https://giscus\.app.*?</script>\s*', '', content, flags=re.DOTALL)
    while 'id="comments-section"' in content:
        content = re.sub(r'<div id="comments-section".*?</div>\s*', '', content, count=1, flags=re.DOTALL)
    content = re.sub(r'\s*<script src=".*?comments\.js"></script>\s*', '', content)
    return content

def ensure_comments(content, filepath):
    if not COMMENTS_ENABLED:
        return content
    if 'id="comments-section"' in content:
        return content
    rel = os.path.relpath(os.path.join(SITE_DIR, 'comments.js'), os.path.dirname(os.path.abspath(filepath)))
    page = '/' + os.path.relpath(filepath, SITE_DIR).replace('\\', '/')
    page = page.replace('/index.html', '/').replace('.html', '')
    block = COMMENTS_BLOCK.replace('{page}', page)
    html = block + '  <script src="' + rel + '"></script>\n'
    content = content.replace('</main>', '</main>\n' + html)
    return content

THEME_TOGGLE = '        <button class="theme-toggle" onclick="toggleTheme()">\u2600\ufe0f</button>\n'

THEME_SCRIPT = r'''
  <script>
    function toggleTheme() {
      document.body.classList.toggle('dark-mode');
      var b = document.body.classList.contains('dark-mode');
      localStorage.setItem('theme', b ? 'dark' : 'light');
      document.querySelector('.theme-toggle').textContent = b ? '\u{1F319}' : '\u2600\uFE0F';
    }
    (function() {
      var btn = document.querySelector('.theme-toggle');
      if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        if (btn) btn.textContent = '\u{1F319}';
      }
    })();
  </script>
'''

def ensure_toggle(content):
    if 'theme-toggle' in content:
        return content
    content = content.replace('</header>', THEME_TOGGLE + '\n  </header>')
    return content

def ensure_script(content):
    if 'function toggleTheme()' in content and 'function toggleSidebar()' in content:
        return content
    script = '''
  <script>
    function toggleSidebar() {
      document.getElementById('sidebar').classList.toggle('open');
    }
    function toggleCategory(header) {
      header.classList.toggle('active');
      header.querySelector('.arrow').classList.toggle('open');
      header.nextElementSibling.classList.toggle('open');
    }
  </script>'''
    content = content.replace('</body>', THEME_SCRIPT + script + '\n</body>')
    return content

def update_html(filepath, sidebar_html):
    with open(filepath) as f:
        content = f.read()

    content = cleanup_old(content)

    pattern = r'(<aside class="sidebar" id="sidebar">\s*).*?(\s*</aside>)'
    content = re.sub(pattern, lambda m: m.group(1) + '\n' + sidebar_html + m.group(2), content, count=1, flags=re.DOTALL)

    content = ensure_toggle(content)
    content = ensure_comments(content, filepath)
    content = ensure_script(content)
    with open(filepath, 'w') as f:
        f.write(content)
    return True

def main():
    if not os.path.exists(REF_FILE):
        print(f"Reference file not found: {REF_FILE}")
        return

    categories = parse_ref(REF_FILE)
    print(f"Parsed {len(categories)} categories from reference.txt")

    html_files = glob.glob(os.path.join(SITE_DIR, "**/*.html"), recursive=True)
    updated = 0
    for fp in sorted(html_files):
        sidebar_html = generate_sidebar(categories, fp)
        if update_html(fp, sidebar_html):
            rel = os.path.relpath(fp, SITE_DIR)
            print(f"  Updated: {rel}")
            updated += 1

    print(f"\nDone. {updated} files updated.")

if __name__ == "__main__":
    main()
