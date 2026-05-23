#!/usr/bin/env python3
import os, sys, re, html as html_mod
from PyQt5 import QtWidgets, QtCore, QtGui

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

def convert_docx(path):
    try:
        from docx import Document
    except ImportError:
        return None, "python-docx not available — rebuild with 'pip install python-docx' first"
    try:
        from lxml import etree
        doc = Document(path)
        nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
                 'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
                 'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                 'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture'}

        def esc(t):
            return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') if t else ''

        def run_to_html(run_elem):
            parts = []
            has_drawing = run_elem.find('.//w:drawing', nsmap) is not None
            if has_drawing:
                img = run_to_img(run_elem)
                if img:
                    parts.append(img)
            texts = run_elem.findall('.//w:t', nsmap)
            text = ''.join(t.text or '' for t in texts)
            if text:
                inner = esc(text)
                if run_elem.find('.//w:b', nsmap) is not None:
                    inner = f'<strong>{inner}</strong>'
                if run_elem.find('.//w:i', nsmap) is not None:
                    inner = f'<em>{inner}</em>'
                if run_elem.find('.//w:u', nsmap) is not None:
                    inner = f'<u>{inner}</u>'
                parts.append(inner)
            return ''.join(parts)

        def run_to_img(run_elem):
            blip = run_elem.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
            if blip is not None:
                embed = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if embed and embed in self_images:
                    rel = self_images[embed]
                    img_data = rel.target_part.blob
                    ext = os.path.splitext(rel.target_ref)[1] or '.png'
                    b64 = base64.b64encode(img_data).decode()
                    return f'<img src="data:image/{ext.lstrip(".")};base64,{b64}" style="max-width:100%">'
            return ''

        def para_to_html(para_elem):
            pPr = para_elem.find('w:pPr', nsmap)
            style_name = ''
            numPr = None
            if pPr is not None:
                style_el = pPr.find('w:pStyle', nsmap)
                if style_el is not None:
                    style_name = (style_el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') or '').lower()
                numPr = pPr.find('w:numPr', nsmap)

            inner = ''.join(run_to_html(r) for r in para_elem.findall('w:r', nsmap))
            inner = inner.strip()
            if not inner:
                return ''

            is_list = numPr is not None or 'list' in style_name
            if 'heading 1' in style_name:
                return f'<h1>{inner}</h1>'
            elif 'heading 2' in style_name:
                return f'<h2>{inner}</h2>'
            elif 'heading 3' in style_name:
                return f'<h3>{inner}</h3>'
            elif 'heading 4' in style_name:
                return f'<h4>{inner}</h4>'
            elif 'heading 5' in style_name:
                return f'<h5>{inner}</h5>'
            elif 'heading 6' in style_name:
                return f'<h6>{inner}</h6>'
            elif is_list:
                return f'<li>{inner}</li>'
            elif 'code' in style_name:
                return f'<pre><code>{inner}</code></pre>'
            elif 'quote' in style_name or 'block text' in style_name:
                return f'<blockquote>{inner}</blockquote>'
            else:
                return f'<p>{inner}</p>'

        def table_to_html(table_elem):
            rows = table_elem.findall('.//w:tr', nsmap)
            if not rows:
                return ''
            html = '<table>\n'
            for row in rows:
                html += '  <tr>\n'
                cells = row.findall('w:tc', nsmap)
                for cell in cells:
                    cell_html = ''
                    for p in cell.findall('w:p', nsmap):
                        cell_html += para_to_html(p)
                    html += f'    <td>{cell_html}</td>\n'
                html += '  </tr>\n'
            html += '</table>'
            return html

        def extract_images():
            images = {}
            for rel_id, rel in doc.part.rels.items():
                if "image" in rel.reltype:
                    images[rel_id] = rel
            return images

        self_images = extract_images()
        import base64

        body = doc.element.body
        out = []
        for child in body:
            tag = etree.QName(child).localname
            if tag == 'p':
                h = para_to_html(child)
                if h:
                    out.append(h)
            elif tag == 'tbl':
                h = table_to_html(child)
                if h:
                    out.append(h)
            elif tag == 'sectPr':
                continue
            elif tag == 'bookmarkStart':
                continue

        html_body = '<div class="doc-content">\n' + '\n'.join(out) + '\n</div>'
        title = os.path.splitext(os.path.basename(path))[0]
        return {'ok': True, 'html': html_body, 'title': title}, None
    except Exception as e:
        return None, str(e)

class DocxToHtmlWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QLabel { color: #e0e0e0; }
            QLabel.dim { color: #999; font-size: 11px; }
            QTextEdit, QLineEdit {
                background: #2a2a2a; color: #e0e0e0; border: 1px solid #333;
                border-radius: 6px; padding: 6px; font-size: 13px;
            }
            QPushButton {
                background: #555; color: #fff; border: none;
                border-radius: 6px; padding: 8px 16px; font-size: 13px;
            }
            QPushButton:hover { background: #666; }
            QPushButton:disabled { background: #333; color: #666; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # file selection
        file_row = QtWidgets.QHBoxLayout()
        self.path_input = QtWidgets.QLineEdit()
        self.path_input.setPlaceholderText("Select a .docx file...")
        file_row.addWidget(self.path_input, 1)
        browse_btn = QtWidgets.QPushButton("Browse")
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        # preview
        self.preview = QtWidgets.QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("HTML preview will appear here...")
        layout.addWidget(self.preview, 1)

        # status
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setProperty("class", "dim")
        layout.addWidget(self.status_label)

        # save options
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

    navigate_to_management = QtCore.pyqtSignal(str)

    def browse(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select .docx", "", "Word Documents (*.docx)")
        if p:
            self.path_input.setText(p)
            self.convert()

    def convert(self):
        p = self.path_input.text().strip()
        if not p or not p.endswith('.docx'):
            return
        self.current_path = p
        self.status_label.setText("Converting...")
        QtWidgets.QApplication.processEvents()
        result, err = convert_docx(p)
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
        self.status_label.setText(f"Converted: {title} ({len(html)} chars)")
        self.save_standalone.setEnabled(True)
        self.save_to_site.setEnabled(True)

    def save_as(self):
        p, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save HTML", self.current_title + ".html", "HTML Files (*.html)")
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
            with open(p, 'w') as f:
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
            with open(fpath, 'w') as f:
                f.write(full)
            dlg.accept()
            self.navigate_to_management.emit(fpath)

        ok.clicked.connect(do_add)
        dlg.exec_()

def main_gui():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    w.setWindowTitle("Word to HTML Converter")
    w.setMinimumSize(700, 500)
    layout = QtWidgets.QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(DocxToHtmlWidget())
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main_gui()
