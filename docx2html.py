#!/usr/bin/env python3
import os, sys, re, html as html_mod, zipfile, base64
from html.parser import HTMLParser
from PyQt5 import QtWidgets, QtCore

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))


class _HtmlCleaner(HTMLParser):
    REMOVE_KEEP_CONTENT = {'html', 'head', 'body'}
    REMOVE_WITH_CONTENT = {'style', 'script', 'title'}
    VOID_REMOVE = {'meta', 'link', 'base'}
    UNWRAP = {'span'}
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
            if 'index.html' not in z.namelist():
                return None, "No index.html found in zip (is this a Google Docs export?)"

            html_bytes = z.read('index.html')
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

            html_body = '<div class="doc-content">\n' + clean_html.strip() + '\n</div>'
            return {'ok': True, 'html': html_body, 'title': title}, None
    except zipfile.BadZipFile:
        return None, "Corrupted zip file"
    except Exception as e:
        return None, str(e)


class ImportWidget(QtWidgets.QWidget):
    navigate_to_management = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QLabel { color: #e0e0e0; }
            QLabel.dim { color: #999; }
            QTextEdit, QLineEdit {
                background: #2a2a2a; color: #e0e0e0; border: 1px solid #333;
                border-radius: 6px; padding: 6px;
            }
            QPushButton {
                background: #555; color: #fff; border: none;
                border-radius: 6px; padding: 8px 16px;
            }
            QPushButton:hover { background: #666; }
            QPushButton:disabled { background: #333; color: #666; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        file_row = QtWidgets.QHBoxLayout()
        self.path_input = QtWidgets.QLineEdit()
        self.path_input.setPlaceholderText("Select a Google Docs zip export...")
        file_row.addWidget(self.path_input, 1)
        browse_btn = QtWidgets.QPushButton("Browse")
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        self.preview = QtWidgets.QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("HTML preview will appear here...")
        layout.addWidget(self.preview, 1)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setProperty("class", "dim")
        layout.addWidget(self.status_label)

        save_row = QtWidgets.QHBoxLayout()
        self.save_standalone = QtWidgets.QPushButton("Save as HTML")
        self.save_standalone.setEnabled(False)
        save_row.addWidget(self.save_standalone)

        self.save_to_site = QtWidgets.QPushButton("Add to Site + Generate")
        self.save_to_site.setEnabled(False)
        save_row.addWidget(self.save_to_site)

        layout.addLayout(save_row)

        self.current_html = ""
        self.current_title = ""
        self.current_path = ""

        browse_btn.clicked.connect(self.browse)
        self.path_input.returnPressed.connect(self.convert)
        self.save_standalone.clicked.connect(self.save_as)
        self.save_to_site.clicked.connect(self.add_to_site)

    def browse(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select zip export", "", "Google Docs Export (*.zip)")
        if p:
            self.path_input.setText(p)
            self.convert()

    def convert(self):
        p = self.path_input.text().strip()
        if not p or not p.lower().endswith('.zip'):
            return
        self.current_path = p
        self.status_label.setText("Extracting & cleaning...")
        QtWidgets.QApplication.processEvents()
        result, err = convert_zip(p)
        if err:
            self.status_label.setText(f"Error: {err}")
            self.preview.setPlainText(err)
            return
        if not result.get('ok'):
            self.status_label.setText(f"Error: {result.get('error', 'unknown')}")
            self.preview.setPlainText(result.get('error', ''))
            return
        html = result['html']
        title = result['title']
        self.current_html = html
        self.current_title = title
        self.preview.setHtml(html)
        self.status_label.setText(f"Imported: {title} ({len(html)} chars)")
        self.save_standalone.setEnabled(True)
        self.save_to_site.setEnabled(True)

    def save_as(self):
        p, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save HTML", self.current_title + ".html", "HTML Files (*.html)")
        if p:
            full = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_mod.escape(self.current_title)}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1>{html_mod.escape(self.current_title)}</h1>
  </header>
  <main>
{self.current_html}
  </main>
</body>
</html>"""
            with open(p, 'w', encoding="utf-8") as f:
                f.write(full)
            self.status_label.setText(f"Saved: {p}")

    def add_to_site(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Add to Site")
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
            dlg.accept()
            self.navigate_to_management.emit(fpath)

        ok.clicked.connect(do_add)
        dlg.exec_()


def main_gui():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    w.setWindowTitle("Import Google Docs Export")
    w.setMinimumSize(700, 500)
    layout = QtWidgets.QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(ImportWidget())
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main_gui()
