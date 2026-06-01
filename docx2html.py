#!/usr/bin/env python3
import os, sys, re, html as html_mod, zipfile, base64, email, email.policy, email.parser
from html.parser import HTMLParser
from PyQt6 import QtWidgets, QtCore

_APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(_APP_DIR, "site")

import sidebar_util
from generate import clear_sidebar_cache


class _HtmlCleaner(HTMLParser):
    REMOVE_KEEP_CONTENT = {'html', 'head', 'body'}
    REMOVE_WITH_CONTENT = {'style', 'script', 'title'}
    VOID_REMOVE = {'meta', 'link', 'base'}
    UNWRAP = set()
    VOID_KEEP = {'br', 'hr', 'img', 'input', 'area', 'col', 'embed', 'source', 'track', 'wbr'}

    def __init__(self, images):
        super().__init__()
        self.images = images
        self.out = []
        self.skip_depth = 0

    def _esc_attr(self, s):
        return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in self.REMOVE_WITH_CONTENT:
            self.skip_depth += 1
            return
        if tag in self.REMOVE_KEEP_CONTENT | self.VOID_REMOVE | self.UNWRAP:
            return

        clean = []
        for name, val in attrs:
            name = name.lower()
            if name == 'class':
                continue
            if name == 'style' and val:
                val = re.sub(
                    r'\b(color|background|background-color)\s*:\s*[^;]+;?\s*',
                    '', val, flags=re.I
                ).strip()
                if not val:
                    continue
            clean.append((name, val))

        attrs_str = ''
        if clean:
            attrs_str = ' ' + ' '.join(f'{n}="{self._esc_attr(v)}"' for n, v in clean)

        if tag == 'img':
            src = dict(attrs).get('src', '')
            if src in self.images:
                clean = [(n, v) for n, v in clean if n != 'src']
                attrs_str = ''
                if clean:
                    attrs_str = ' ' + ' '.join(f'{n}="{self._esc_attr(v)}"' for n, v in clean)
                self.out.append(f'<img{attrs_str} src="{self.images[src]}">')
                return

        if tag in self.VOID_KEEP:
            self.out.append(f'<{tag}{attrs_str}>')
        else:
            self.out.append(f'<{tag}{attrs_str}>')

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self.REMOVE_WITH_CONTENT:
            if self.skip_depth > 0:
                self.skip_depth -= 1
            return
        if tag in self.REMOVE_KEEP_CONTENT | self.UNWRAP | self.VOID_REMOVE:
            return
        if tag in self.VOID_KEEP:
            return
        self.out.append(f'</{tag}>')

    def handle_data(self, data):
        if self.skip_depth == 0:
            self.out.append(data)

    def handle_entityref(self, name):
        if self.skip_depth == 0:
            self.out.append(f'&{name};')

    def handle_charref(self, name):
        if self.skip_depth == 0:
            self.out.append(f'&#{name};')


MIME_MAP = {
    '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.gif': 'image/gif', '.svg': 'image/svg+xml', '.webp': 'image/webp',
    '.bmp': 'image/bmp',
}


def convert_zip(path):
    if not zipfile.is_zipfile(path):
        return None, "Not a valid zip file"
    try:
        with zipfile.ZipFile(path, 'r') as z:
            html_candidates = [n for n in z.namelist() if n.endswith('.html')]
            if 'index.html' in z.namelist():
                chosen = 'index.html'
            elif len(html_candidates) == 1:
                chosen = html_candidates[0]
            elif len(html_candidates) == 0:
                return None, "No HTML file found in zip"
            else:
                return None, f"Multiple HTML files found ({len(html_candidates)}). Expected a single file."

            html_bytes = z.read(chosen)
            try:
                html_content = html_bytes.decode('utf-8')
            except UnicodeDecodeError:
                html_content = html_bytes.decode('latin-1')

            image_names = {
                n for n in z.namelist()
                if n.startswith('images/') and not n.endswith('/')
            }
            images = {}
            for img_name in image_names:
                data = z.read(img_name)
                ext = os.path.splitext(img_name)[1].lower()
                mime = MIME_MAP.get(ext, 'application/octet-stream')
                images[img_name] = f'data:{mime};base64,{base64.b64encode(data).decode()}'

            cleaner = _HtmlCleaner(images)
            cleaner.feed(html_content)
            clean_html = ''.join(cleaner.out)

            title_m = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL | re.IGNORECASE)
            title = title_m.group(1).strip() if title_m else os.path.splitext(os.path.basename(path))[0]

            html_body = '<div class="ck-content">\n' + clean_html.strip() + '\n</div>'
            return {'ok': True, 'html': html_body, 'title': title}, None
    except zipfile.BadZipFile:
        return None, "Corrupted zip file"
    except Exception as e:
        return None, str(e)


def convert_mht(path):
    try:
        with open(path, 'rb') as f:
            msg = email.parser.BytesParser(policy=email.policy.default).parse(f)

        images = {}
        html_content = None

        for part in msg.walk():
            ct = part.get_content_type()
            if ct == 'text/html' and html_content is None:
                charset = part.get_content_charset() or 'utf-8'
                payload = part.get_payload(decode=True)
                if payload:
                    html_content = payload.decode(charset, errors='replace')
            elif part.get_content_maintype() == 'image':
                data = part.get_payload(decode=True)
                if not data:
                    continue
                cl = part.get('Content-Location', '') or ''
                filename = os.path.basename(cl)
                if not filename:
                    cid = part.get('Content-ID', '')
                    if cid:
                        filename = cid.strip('<>')
                if not filename:
                    continue
                ext = os.path.splitext(filename)[1].lower()
                mime = MIME_MAP.get(ext, 'application/octet-stream')
                images[filename] = f'data:{mime};base64,{base64.b64encode(data).decode()}'

        if not html_content:
            return None, "No HTML content found in MHT file"

        html_content = re.sub(r'src="file:///[^"]*?([^"/]+)"', r'src="\1"', html_content)

        title_m = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL | re.IGNORECASE)
        title = title_m.group(1).strip() if title_m else os.path.splitext(os.path.basename(path))[0]

        cleaner = _HtmlCleaner(images)
        cleaner.feed(html_content)
        clean_html = ''.join(cleaner.out)
        html_body = '<div class="ck-content">\n' + clean_html.strip() + '\n</div>'

        return {'ok': True, 'html': html_body, 'title': title}, None
    except Exception as e:
        return None, str(e)


def convert_html(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except UnicodeDecodeError:
        try:
            with open(path, 'r', encoding='latin-1') as f:
                html_content = f.read()
        except Exception as e:
            return None, str(e)
    except Exception as e:
        return None, str(e)

    # Extract title from HTML
    title_m = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL | re.IGNORECASE)
    title = title_m.group(1).strip() if title_m else os.path.splitext(os.path.basename(path))[0]

    # Clean the HTML content
    cleaner = _HtmlCleaner({})
    cleaner.feed(html_content)
    clean_html = ''.join(cleaner.out)
    html_body = '<div class="ck-content">\n' + clean_html.strip() + '\n</div>'

    return {'ok': True, 'html': html_body, 'title': title}, None


def convert_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.mht', '.mhtml'):
        return convert_mht(path)
    elif ext == '.zip':
        return convert_zip(path)
    elif ext == '.html':
        return convert_html(path)
    else:
        return None, "Unsupported file type. Use .html, .zip, .mht, or .mhtml."


class ImportWidget(QtWidgets.QWidget):
    navigate_to_management = QtCore.pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QLabel { color: #c9d1d9; }
            QLabel.dim { color: #6e7681; }
            QTextEdit, QLineEdit {
                background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; padding: 6px;
            }
            QPushButton {
                background: #21262d; color: #c9d1d9; border: none;
                border-radius: 6px; padding: 8px 16px;
            }
            QPushButton:hover { background: #30363d; }
            QPushButton:disabled { background: #30363d; color: #484f58; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        file_row = QtWidgets.QHBoxLayout()
        self.path_input = QtWidgets.QLineEdit()
        self.path_input.setPlaceholderText("Select a .html, .zip (Google Docs) or .mht file (Word)...")
        file_row.addWidget(self.path_input, 1)
        browse_btn = QtWidgets.QPushButton("Browse")
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setProperty("class", "dim")
        layout.addWidget(self.status_label)

        btn_row = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Save")
        self.save_btn.setEnabled(False)
        btn_row.addWidget(self.save_btn)
        self.fullscreen_btn = QtWidgets.QPushButton("Preview")
        self.fullscreen_btn.setEnabled(False)
        self.fullscreen_btn.clicked.connect(self._show_fullscreen)
        btn_row.addWidget(self.fullscreen_btn)
        layout.addLayout(btn_row)

        self.current_html = ""
        self.current_title = ""
        self.current_path = ""

        browse_btn.clicked.connect(self.browse)
        self.path_input.returnPressed.connect(self.convert)
        self.save_btn.clicked.connect(self.save_to_site)

    def browse(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select file to import", "",
            "Supported files (*.html *.zip *.mht *.mhtml);;HTML files (*.html);;Google Docs Export (*.zip);;MHT files (*.mht *.mhtml)")
        if p:
            self.path_input.setText(p)
            self.convert()

    def convert(self):
        p = self.path_input.text().strip()
        if not p:
            return
        ext = os.path.splitext(p)[1].lower()
        if ext not in ('.html', '.zip', '.mht', '.mhtml'):
            self.status_label.setText("Unsupported file type. Use .html, .zip, .mht, or .mhtml.")
            return
        self.current_html = ""
        self.save_btn.setEnabled(False)
        self.fullscreen_btn.setEnabled(False)
        self.current_path = p
        self.status_label.setText("Extracting & cleaning...")
        QtWidgets.QApplication.processEvents()
        result, err = convert_file(p)
        if err:
            self.status_label.setText(f"Error: {err}")
            return
        if not result.get('ok'):
            self.status_label.setText(f"Error: {result.get('error', 'unknown')}")
            return
        html = result['html']
        title = result['title']
        self.current_html = html
        self.current_title = title
        self.status_label.setText(f"Imported: {title} ({len(html)} chars)")
        self.save_btn.setEnabled(True)
        self.fullscreen_btn.setEnabled(True)

    def _show_fullscreen(self):
        if not self.current_html:
            return
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Preview – Full Screen")
        dlg.setStyleSheet("QDialog { background: #0d1117; }")
        dl = QtWidgets.QVBoxLayout(dlg)
        dl.setContentsMargins(0, 0, 0, 0)
        viewer = QtWidgets.QTextEdit()
        viewer.setReadOnly(True)
        viewer.setHtml(self.current_html or "")
        viewer.setStyleSheet("""
            QTextEdit { background: #fff; color: #000; border: none; }
        """)
        dl.addWidget(viewer)
        bar = QtWidgets.QWidget()
        bar.setStyleSheet("background: #161b22; padding: 6px 12px;")
        bl = QtWidgets.QHBoxLayout(bar)
        bl.setContentsMargins(0, 0, 0, 0)
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton { background: #21262d; color: #c9d1d9; border: none;
                          border-radius: 4px; padding: 6px 16px; }
            QPushButton:hover { background: #30363d; }
        """)
        close_btn.clicked.connect(dlg.accept)
        bl.addStretch()
        bl.addWidget(close_btn)
        dl.addWidget(bar)
        dlg.resize(1000, 750)
        dlg.exec()

    def save_to_site(self):
        sidebar_util.SITE_DIR = SITE_DIR
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Save to Site")
        dlg.setMinimumWidth(400)
        dl = QtWidgets.QVBoxLayout(dlg)

        cat_label = QtWidgets.QLabel("Category (folder):")
        cat_label.setProperty("class", "dim")
        dl.addWidget(cat_label)
        cat_input = QtWidgets.QLineEdit("blog")
        dl.addWidget(cat_input)

        title_label = QtWidgets.QLabel("Page title:")
        title_label.setProperty("class", "dim")
        dl.addWidget(title_label)
        title_input = QtWidgets.QLineEdit(self.current_title)
        dl.addWidget(title_input)

        btns = QtWidgets.QHBoxLayout()
        ok = QtWidgets.QPushButton("Save & Go to Management")
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(dlg.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        dl.addLayout(btns)

        def do_add():
            cat = cat_input.text().strip()
            title = title_input.text().strip()
            if not cat or not title:
                return
            target_dir = os.path.join(SITE_DIR, cat)
            os.makedirs(target_dir, exist_ok=True)
            slug = title.lower().replace(' ', '-').replace('--', '-')
            slug = re.sub(r'[^a-z0-9-]', '', slug)
            fname = slug + '.html'
            fpath = os.path.join(target_dir, fname)
            rel = os.path.relpath(SITE_DIR, target_dir).replace('\\', '/')
            full = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_mod.escape(title)}</title>
  <link rel="stylesheet" href="{rel}/style.css">
</head>
<body>
  <header>
    <button class="sidebar-toggle" onclick="toggleSidebar()">&#9776;</button>
    <h1><a href="{rel}/index.html">{html_mod.escape(title)}</a></h1>
    <button class="theme-toggle" onclick="toggleTheme()">&#x2600;&#xFE0F;</button>
  </header>
  <div class="layout">
    <aside class="sidebar" id="sidebar">
    </aside>
    <main>
{self.current_html}
    </main>
  </div>
</body>
</html>"""
            with open(fpath, 'w', encoding="utf-8") as f:
                f.write(full)

            rel_path = '/' + os.path.relpath(fpath, SITE_DIR).replace('\\', '/')
            sidebar_data = sidebar_util.load_sidebar()
            found = False
            for c in sidebar_data:
                if c["category"] == cat:
                    c["entries"].append({"name": title, "file": rel_path})
                    found = True
                    break
            if not found:
                sidebar_data.append({"category": cat, "entries": [{"name": title, "file": rel_path}]})
            sidebar_util.save_sidebar(sidebar_data)
            clear_sidebar_cache()

            dlg.accept()
            self.navigate_to_management.emit(fpath, cat)

        ok.clicked.connect(do_add)
        dlg.exec()


def main_gui():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    w.setWindowTitle("Import Google Docs Export")
    w.setMinimumSize(700, 500)
    layout = QtWidgets.QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(ImportWidget())
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main_gui()
