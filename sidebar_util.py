import os, json

SITE_DIR = None
SIDEBAR_FILE = "sidebar.json"

def _sidebar_path():
    return os.path.join(SITE_DIR, SIDEBAR_FILE)

def load_sidebar():
    path = _sidebar_path()
    if not os.path.exists(path):
        return []
    skip = {'.git', '__pycache__', 'node_modules', 'build', 'build_venv', 'dist', '.github', 'fonts', 'bundled-git', 'mingit', 'ckeditor'}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [c for c in data if c.get("category") not in skip]

def save_sidebar(data):
    path = _sidebar_path()
    skip = {'.git', '__pycache__', 'node_modules', 'build', 'build_venv', 'dist', '.github', 'fonts', 'bundled-git', 'mingit', 'ckeditor'}
    data = [c for c in data if c.get("category") not in skip]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def auto_discover():
    existing = set()
    for cat in load_sidebar():
        for entry in cat["entries"]:
            existing.add(entry["file"])

    skip = {'.git', '__pycache__', 'node_modules', 'build', 'build_venv', 'dist', '.github', 'fonts', 'bundled-git', 'mingit', 'ckeditor'}
    discovered = []
    for item in sorted(os.listdir(SITE_DIR)):
        d = os.path.join(SITE_DIR, item)
        if not os.path.isdir(d) or item in skip:
            continue
        for fname in sorted(os.listdir(d)):
            if not fname.endswith('.html'):
                continue
            rel = '/' + os.path.relpath(os.path.join(d, fname), SITE_DIR).replace('\\', '/')
            if rel not in existing:
                name = os.path.splitext(fname)[0].replace('-', ' ').replace('_', ' ').title()
                discovered.append({"category": item, "file": rel, "name": name})
    return discovered

def init_from_filesystem():
    skip = {'.git', '__pycache__', 'node_modules', 'build', 'build_venv', 'dist', '.github', 'fonts', 'bundled-git', 'mingit', 'ckeditor'}
    data = []
    for item in sorted(os.listdir(SITE_DIR)):
        d = os.path.join(SITE_DIR, item)
        if not os.path.isdir(d) or item in skip:
            continue
        html_files = sorted([f for f in os.listdir(d) if f.endswith('.html')])
        if not html_files:
            continue
        entries = []
        for fname in html_files:
            rel = '/' + os.path.relpath(os.path.join(d, fname), SITE_DIR).replace('\\', '/')
            name = os.path.splitext(fname)[0].replace('-', ' ').replace('_', ' ').title()
            entries.append({"name": name, "file": rel})
        data.append({"category": item, "entries": entries})
    if data:
        save_sidebar(data)
    return data
