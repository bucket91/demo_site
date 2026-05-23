#!/usr/bin/env python3
import os, sys, re, html as html_mod

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = "/tmp/docx_venv/bin/python3"

def convert_docx(path):
    if not os.path.exists(VENV_PYTHON):
        return None, "python-docx not installed. Run: python3 -m venv /tmp/docx_venv && /tmp/docx_venv/bin/pip install python-docx"
    import subprocess
    r = subprocess.run([VENV_PYTHON, "-c", """
import sys, json
try:
    from docx import Document
    doc = Document(sys.argv[1])
    out = []
    for p in doc.paragraphs:
        style = p.style.name.lower() if p.style else ''
        text = p.text.strip()
        if not text:
            continue
        text_esc = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if 'heading 1' in style:
            out.append('<h1>' + text_esc + '</h1>')
        elif 'heading 2' in style:
            out.append('<h2>' + text_esc + '</h2>')
        elif 'heading 3' in style:
            out.append('<h3>' + text_esc + '</h3>')
        elif 'list' in style:
            out.append('<li>' + text_esc + '</li>')
        else:
            out.append('<p>' + text_esc + '</p>')
    print(json.dumps({'ok': True, 'html': '<div class=\\"doc-content\\">\\n' + '\\n'.join(out) + '\\n</div>', 'title': os.path.splitext(os.path.basename(sys.argv[1]))[0]}))
except Exception as e:
    print(json.dumps({'ok': False, 'error': str(e)}))
""", path], capture_output=True, text=True)
    try:
        import json as j
        result = j.loads(r.stdout.strip())
        return result, None
    except Exception as e:
        return None, f"Parse error: {e}\n{r.stderr}"

def main_gui():
    from PyQt5 import QtWidgets, QtCore, QtGui
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("""
        QMainWindow, QDialog { background: #1e1e1e; }
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

    w = QtWidgets.QWidget()
    w.setWindowTitle("Word to HTML Converter")
    w.setMinimumSize(700, 500)
    layout = QtWidgets.QVBoxLayout(w)
    layout.setContentsMargins(12, 12, 12, 12)

    # file selection
    file_row = QtWidgets.QHBoxLayout()
    path_input = QtWidgets.QLineEdit()
    path_input.setPlaceholderText("Select a .docx file...")
    file_row.addWidget(path_input, 1)
    browse_btn = QtWidgets.QPushButton("Browse")
    file_row.addWidget(browse_btn)
    layout.addLayout(file_row)

    # preview
    preview = QtWidgets.QTextEdit()
    preview.setReadOnly(True)
    preview.setPlaceholderText("HTML preview will appear here...")
    layout.addWidget(preview, 1)

    # status
    status = QtWidgets.QLabel("")
    status.setProperty("class", "dim")
    layout.addWidget(status)

    # save options
    save_row = QtWidgets.QHBoxLayout()
    save_standalone = QtWidgets.QPushButton("Save as HTML")
    save_standalone.setEnabled(False)
    save_row.addWidget(save_standalone)

    save_to_site = QtWidgets.QPushButton("Add to Site + Generate")
    save_to_site.setEnabled(False)
    save_row.addWidget(save_to_site)

    layout.addLayout(save_row)

    current_html = [""]
    current_title = [""]
    current_path = [""]

    def browse():
        p, _ = QtWidgets.QFileDialog.getOpenFileName(w, "Select .docx", "", "Word Documents (*.docx)")
        if p:
            path_input.setText(p)
            convert()

    def convert():
        p = path_input.text().strip()
        if not p or not p.endswith('.docx'):
            return
        current_path[0] = p
        status.setText("Converting...")
        QtWidgets.QApplication.processEvents()
        result, err = convert_docx(p)
        if err:
            status.setText(f"Error: {err}")
            preview.setPlainText(err)
            return
        if not result.get('ok'):
            status.setText(f"Error: {result.get('error', 'unknown')}")
            preview.setPlainText(result.get('error', ''))
            return
        html = result['html']
        title = result['title']
        current_html[0] = html
        current_title[0] = title
        preview.setHtml(html)
        status.setText(f"Converted: {title} ({len(html)} chars)")
        save_standalone.setEnabled(True)
        save_to_site.setEnabled(True)

    browse_btn.clicked.connect(browse)
    path_input.returnPressed.connect(convert)

    def save_as():
        p, _ = QtWidgets.QFileDialog.getSaveFileName(w, "Save HTML", current_title[0] + ".html", "HTML Files (*.html)")
        if p:
            full = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_mod.escape(current_title[0])}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1>{html_mod.escape(current_title[0])}</h1>
  </header>
  <main>
{current_html[0]}
  </main>
</body>
</html>"""
            with open(p, 'w') as f:
                f.write(full)
            status.setText(f"Saved: {p}")

    def add_to_site():
        dlg = QtWidgets.QDialog(w)
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
        title_input = QtWidgets.QLineEdit(current_title[0])
        dl.addWidget(title_input)

        name_label = QtWidgets.QLabel("Sidebar name:")
        name_label.setProperty("class", "dim")
        dl.addWidget(name_label)
        name_input = QtWidgets.QLineEdit(current_title[0])
        dl.addWidget(name_input)

        btns = QtWidgets.QHBoxLayout()
        ok = QtWidgets.QPushButton("Add & Generate")
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(dlg.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        dl.addLayout(btns)

        def do_add():
            cat = cat_input.text().strip()
            title = title_input.text().strip()
            name = name_input.text().strip()
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
    <h1>{html_mod.escape(title)}</h1>
    <nav><a href="{rel}/index.html">Home</a></nav>
    <button class="theme-toggle" onclick="toggleTheme()">&#x2600;&#xFE0F;</button>
  </header>
  <div class="layout">
    <aside class="sidebar" id="sidebar">
    </aside>
    <main>
{current_html[0]}
    </main>
  </div>
</body>
</html>"""
            with open(fpath, 'w') as f:
                f.write(full)
            # add to reference.txt
            ref_file = os.path.join(SITE_DIR, "template reference.txt")
            if os.path.exists(ref_file):
                with open(ref_file) as f:
                    ref = f.read()
                # find the category section and add entry
                cat_header = '\t' + cat.capitalize()
                entry = f'\n\t\t{{Name:"{name}"\n\t\t File: "/{cat}/{fname}"}}'
                if cat_header in ref:
                    ref = ref.replace(cat_header, cat_header + entry)
                else:
                    ref += f'\n\t{cat.capitalize()}{entry}\n'
                with open(ref_file, 'w') as f:
                    f.write(ref)
            dlg.accept()
            status.setText(f"Added: {fpath}. Running generate...")
            QtWidgets.QApplication.processEvents()
            import subprocess
            r = subprocess.run([sys.executable, os.path.join(SITE_DIR, 'generate.py')],
                             cwd=SITE_DIR, capture_output=True, text=True)
            status.setText(r.stdout.strip() if r.returncode == 0 else r.stderr.strip())

        ok.clicked.connect(do_add)
        dlg.exec_()

    save_standalone.clicked.connect(save_as)
    save_to_site.clicked.connect(add_to_site)

    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main_gui()
