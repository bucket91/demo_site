#!/usr/bin/env python3
import os, sys, json
from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))


class WysiwygEditor(QtWidgets.QDialog):
    def __init__(self, html_content="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Page Editor")
        self.setMinimumSize(800, 550)
        self.resize(1000, 700)
        self.setStyleSheet("""
            QDialog { background: #0d1117; }
            QPushButton {
                background: #21262d; color: #c9d1d9; border: none;
                border-radius: 6px; padding: 8px 20px;
            }
            QPushButton:hover { background: #30363d; }
            QPushButton.primary { background: #58a6ff; }
            QPushButton.primary:hover { background: #79c0ff; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.view = QtWebEngineWidgets.QWebEngineView()
        editor_path = os.path.join(SITE_DIR, "ckeditor", "editor.html")
        self.view.setUrl(QtCore.QUrl.fromLocalFile(editor_path))
        layout.addWidget(self.view, 1)

        bar = QtWidgets.QWidget()
        bar.setStyleSheet("background: #161b22; border-top: 1px solid #30363d;")
        bl = QtWidgets.QHBoxLayout(bar)
        bl.setContentsMargins(12, 8, 12, 8)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("color: #6e7681; font-size: 12px;")
        bl.addWidget(self.status_label, 1)

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        bl.addWidget(cancel_btn)

        self.save_btn = QtWidgets.QPushButton("Save & Close")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.clicked.connect(self._on_save)
        bl.addWidget(self.save_btn)

        layout.addWidget(bar)

        self._result_html = ""
        self._ready = False

        self.view.loadFinished.connect(lambda ok: self._on_loaded(ok, html_content))

    def _on_loaded(self, ok, initial_html):
        if not ok:
            self.status_label.setText("Failed to load editor")
            return
        self._ready = True
        if initial_html:
            escaped = json.dumps(initial_html)
            self.view.page().runJavaScript(f"setEditorContent({escaped})")

    def _on_save(self):
        if not self._ready:
            self.status_label.setText("Editor not ready yet")
            return
        self.save_btn.setEnabled(False)
        self.save_btn.setText("Saving...")
        self.view.page().runJavaScript("getEditorContent()", self._on_content_received)

    def _on_content_received(self, html):
        html = html.strip()
        if not html:
            self.status_label.setText("Content is empty — write something first")
            self.save_btn.setEnabled(True)
            self.save_btn.setText("Save & Close")
            return
        html = self._extract_base64(html)
        self._result_html = html
        self.accept()

    def _extract_base64(self, html):
        import re, base64 as b64, hashlib, os
        SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(SITE_DIR, "images")
        os.makedirs(img_dir, exist_ok=True)
        pattern = r'src="data:(image/[^";]+|video/[^";]+);base64,([^"]+)"'
        count = 0

        def _replace(m):
            nonlocal count
            mime = m.group(1)
            data_b64 = m.group(2)
            raw = b64.b64decode(data_b64)
            h = hashlib.md5(raw).hexdigest()[:12]
            if mime.startswith("video/"):
                ext = "webm"
            else:
                ext = "webp"
            fname = f"embed_{h}.{ext}"
            fpath = os.path.join(img_dir, fname)
            if not os.path.exists(fpath):
                try:
                    with open(fpath, "wb") as f:
                        f.write(raw)
                except Exception:
                    return m.group(0)
            count += 1
            return f'src="images/{fname}"'

        result = re.sub(pattern, _replace, html)
        if count:
            self.status_label.setText(f"Extracted {count} embedded file(s) to images/")
        return result

    def result_html(self):
        return self._result_html
