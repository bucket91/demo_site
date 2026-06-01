import os, sys, json, shutil, re
from PyQt6 import QtWidgets, QtCore, QtWebEngineWidgets, QtWebEngineCore

_APP_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(_APP_DIR, "site")


def _ensure_ckeditor():
    target = os.path.join(_APP_DIR, "ckeditor")
    required = {"editor.html", "ckeditor5.umd.js", "ckeditor5.css"}
    need_copy = False
    if not os.path.isdir(target):
        need_copy = True
    else:
        present = set(os.listdir(target))
        if not required.issubset(present):
            try:
                shutil.rmtree(target)
            except OSError:
                pass
            need_copy = True
    if need_copy:
        if getattr(sys, 'frozen', False):
            src = os.path.join(sys._MEIPASS, "ckeditor")
        else:
            src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ckeditor")
        if os.path.isdir(src):
            shutil.copytree(src, target)
    editor_html = os.path.join(target, "editor.html")
    umd_js = os.path.join(target, "ckeditor5.umd.js")
    if os.path.exists(editor_html) and os.path.exists(umd_js):
        with open(editor_html, encoding="utf-8") as f:
            html = f.read()
        with open(umd_js, encoding="utf-8") as f:
            js = f.read()
        changed = False
        ext_pattern = '<script src="ckeditor5.umd.js"></script>'
        if ext_pattern in html:
            html = html.replace(ext_pattern, '<script>' + js + '</script>')
            changed = True
        merge_marker = '</script>\n\n<script>'
        if merge_marker in html:
            idx = html.find(merge_marker)
            html = html[:idx] + '\n\n' + html[idx + len(merge_marker):]
            changed = True
        source_map = '//# sourceMappingURL=ckeditor5.umd.js.map'
        if source_map in html:
            html = html.replace(source_map, '')
            changed = True
        if changed:
            with open(editor_html, 'w', encoding="utf-8") as f:
                f.write(html)


class _EditorPage(QtWebEngineCore.QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def javaScriptConsoleMessage(self, level, msg, line, source):
        label = {0: "info", 1: "warning", 2: "error"}.get(level, str(level))
        if level >= 2:
            print(f"[CKEditor JS {label}] {msg} (at {source}:{line})")


class CkeditorTab(QtWidgets.QWidget):
    file_loaded = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        _ensure_ckeditor()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setPage(_EditorPage(self.view))
        s = self.view.settings()
        s.setAttribute(QtWebEngineCore.QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        s.setAttribute(QtWebEngineCore.QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        s.setAttribute(QtWebEngineCore.QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        editor_path = os.path.join(_APP_DIR, "ckeditor", "editor.html")
        self.view.setUrl(QtCore.QUrl.fromLocalFile(editor_path))
        layout.addWidget(self.view, 1)

        bar = QtWidgets.QWidget()
        bar.setStyleSheet("background: #161b22; border-top: 1px solid #30363d;")
        bl = QtWidgets.QHBoxLayout(bar)
        bl.setContentsMargins(12, 8, 12, 8)

        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("color: #6e7681; font-size: 12px;")
        bl.addWidget(self.status_label, 1)

        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.clicked.connect(self._clear)
        bl.addWidget(clear_btn)

        export_btn = QtWidgets.QPushButton("Export HTML")
        export_btn.setProperty("class", "primary")
        export_btn.setStyleSheet("background: #58a6ff; color: #fff; border: none; border-radius: 6px; padding: 8px 20px;")
        export_btn.clicked.connect(self._export)
        bl.addWidget(export_btn)

        layout.addWidget(bar)

        self._ready = False
        self.view.loadFinished.connect(lambda ok: self._on_loaded(ok))

    def _on_loaded(self, ok):
        if not ok:
            self.status_label.setText("Failed to load editor")
            return
        self.view.page().runJavaScript(
            "typeof ckeditor5 !== 'undefined'",
            lambda loaded: self._on_ckeditor_check(loaded)
        )

    def _on_ckeditor_check(self, loaded):
        if not loaded:
            self.status_label.setText("CKEditor failed to load")
            return
        self._ready = True
        self.status_label.setText("Ready")

    def load_file(self, file_path):
        try:
            with open(file_path, encoding="utf-8") as f:
                html = f.read()
        except Exception as e:
            self.status_label.setText(f"Error reading file: {e}")
            return
        content = html
        m = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL | re.IGNORECASE)
        if m:
            content = m.group(1).strip()
        js_content = json.dumps(content)
        self.view.page().runJavaScript(f"setEditorContent({js_content})")
        self.status_label.setText(f"Loaded: {os.path.basename(file_path)}")
        self.file_loaded.emit(os.path.basename(file_path))

    def _clear(self):
        if self._ready:
            self.view.page().runJavaScript("setEditorContent('')")
            self.status_label.setText("Cleared")

    def _export(self):
        if not self._ready:
            self.status_label.setText("Editor not ready yet")
            return
        self.view.page().runJavaScript("getEditorContentClean()", self._on_export_result)

    def _on_export_result(self, html):
        html = html.strip()
        if not html:
            self.status_label.setText("Nothing to export")
            return
        cb = QtWidgets.QApplication.clipboard()
        cb.setText(html)
        self.status_label.setText(f"Exported {len(html)} chars to clipboard")
