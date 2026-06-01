import os, sys, json, shutil, re
from PyQt6 import QtWidgets, QtCore, QtWebEngineWidgets, QtWebEngineCore

_APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
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


class _EditorPage(QtWebEngineCore.QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)

    def javaScriptConsoleMessage(self, level, msg, line, source):
        label = {0: "info", 1: "warning", 2: "error"}.get(level, str(level))
        if level >= 2:
            print(f"[CKEditor JS {label}] {msg} (at {source}:{line})")


class CkeditorTab(QtWidgets.QWidget):
    file_loaded = QtCore.pyqtSignal(str)

    _profile = None

    @classmethod
    def _get_profile(cls):
        if cls._profile is None:
            cache_dir = os.path.join(_APP_DIR, "cache", "ckeditor")
            os.makedirs(cache_dir, exist_ok=True)
            cls._profile = QtWebEngineCore.QWebEngineProfile("ckeditor", None)
            cls._profile.setCachePath(cache_dir)
            cls._profile.setHttpCacheType(QtWebEngineCore.QWebEngineProfile.HttpCacheType.DiskHttpCache)
        return cls._profile

    def __init__(self, parent=None):
        super().__init__(parent)
        _ensure_ckeditor()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.view = QtWebEngineWidgets.QWebEngineView()
        page = _EditorPage(self._get_profile(), self.view)
        self.view.setPage(page)
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
        self._current_file = None
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
        self._current_file = file_path
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
        default_name = os.path.basename(self._current_file) if self._current_file else "page.html"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export HTML", default_name,
            "HTML files (*.html);;All files (*)"
        )
        if not path:
            return
        self._export_path = path
        self.view.page().runJavaScript("getEditorContentClean()", self._on_export_result)

    def _on_export_result(self, html):
        html = html.strip()
        if not html:
            self.status_label.setText("Nothing to export")
            return
        path = getattr(self, '_export_path', None)
        if not path:
            self.status_label.setText("No export path set")
            return
        try:
            if self._current_file and os.path.exists(self._current_file):
                with open(self._current_file, encoding="utf-8") as f:
                    orig = f.read()
            else:
                orig = None
        except Exception:
            orig = None
        try:
            if orig is not None and re.search(r'<main[^>]*>', orig, re.DOTALL | re.IGNORECASE):
                result = re.sub(
                    r'(<main[^>]*>).*?(</main>)',
                    lambda m: m.group(1) + '\n' + html + '\n' + m.group(2),
                    orig, count=1, flags=re.DOTALL | re.IGNORECASE
                )
            else:
                style_css = content_css = ""
                for fn in ("style.css", "content.css"):
                    fp = os.path.join(SITE_DIR, fn)
                    try:
                        with open(fp, encoding="utf-8") as f:
                            css = f.read()
                    except Exception:
                        css = ""
                    if css:
                        style_css += f"<style>\n{css}\n</style>\n"
                result = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page</title>
{style_css}</head>
<body>
  <main>
{html}
  </main>
</body>
</html>"""
            with open(path, "w", encoding="utf-8") as f:
                f.write(result)
            self.status_label.setText(f"Exported to {os.path.basename(path)}")
        except Exception as e:
            self.status_label.setText(f"Error writing file: {e}")
