#!/usr/bin/env python3
import re, os, glob

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_FILE = os.path.join(SITE_DIR, "template reference.txt")

# ── Giscus config ──────────────────────────────────────────────
# Replace with your actual repo + category info from giscus.app
GISCUS = {
    "enabled":    True,
    "repo":       "YOUR_OWNER/YOUR_REPO",     # e.g. "mhd/mysite"
    "repo_id":    "YOUR_REPO_ID",             # get from giscus.app
    "category":   "General",                  # your Discussion category
    "category_id":"YOUR_CATEGORY_ID",         # get from giscus.app
    "mapping":    "pathname",
    "theme":      "preferred_color_scheme",
}

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

def ensure_script(content):
    if 'toggleCategory' in content:
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
    content = content.replace('</body>', script + '\n</body>')
    return content

def ensure_giscus(content):
    if not GISCUS["enabled"] or 'giscus' in content:
        return content
    html = '\n  <div id="giscus-comments" style="max-width:800px;margin:2rem auto;padding:0 1rem">\n'
    html += f'    <script src="https://giscus.app/client.js"\n'
    html += f'            data-repo="{GISCUS["repo"]}"\n'
    html += f'            data-repo-id="{GISCUS["repo_id"]}"\n'
    html += f'            data-category="{GISCUS["category"]}"\n'
    html += f'            data-category-id="{GISCUS["category_id"]}"\n'
    html += f'            data-mapping="{GISCUS["mapping"]}"\n'
    html += f'            data-strict="0"\n'
    html += f'            data-reactions-enabled="1"\n'
    html += f'            data-emit-metadata="0"\n'
    html += f'            data-input-position="bottom"\n'
    html += f'            data-theme="{GISCUS["theme"]}"\n'
    html += f'            data-lang="en"\n'
    html += f'            crossorigin="anonymous"\n'
    html += f'            async>\n'
    html += f'    </script>\n'
    html += '  </div>\n'
    content = content.replace('</main>', '</main>\n' + html)
    return content

def update_html(filepath, sidebar_html):
    with open(filepath) as f:
        content = f.read()

    pattern = r'(<aside class="sidebar" id="sidebar">\s*).*?(\s*</aside>)'
    new_content = re.sub(pattern, lambda m: m.group(1) + '\n' + sidebar_html + m.group(2), content, count=1, flags=re.DOTALL)

    if new_content == content:
        return False
    new_content = ensure_script(new_content)
    new_content = ensure_giscus(new_content)
    with open(filepath, 'w') as f:
        f.write(new_content)
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
