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

    def _load_editor_with_config(self):
        editor_path = os.path.join(_APP_DIR, "ckeditor", "editor.html")
        base_url = QtCore.QUrl.fromLocalFile(os.path.join(_APP_DIR, "ckeditor") + "/")
        try:
            with open(editor_path, encoding="utf-8") as f:
                html = f.read()
        except Exception as e:
            self.status_label.setText(f"Error reading editor.html: {e}")
            return

        from generate import load_config as _load_cfg
        _cfg = _load_cfg()
        lang = _cfg.get("site_lang", "en")
        dir_ = _cfg.get("site_dir", "ltr")

        custom_fonts = []
        bundled_fonts = []
        font_face_css = ""

        fonts_file = os.path.join(SITE_DIR, "fonts", "fonts.json")
        if os.path.exists(fonts_file):
            try:
                with open(fonts_file, encoding="utf-8") as f:
                    customs = json.load(f)
                for cf in customs:
                    custom_fonts.append(cf["name"])
                    fp = os.path.join(SITE_DIR, cf["file"])
                    if os.path.exists(fp):
                        ext = os.path.splitext(cf["file"])[1].lower()
                        fmt = {"ttf": "truetype", "otf": "opentype", "woff": "woff", "woff2": "woff2"}.get(ext.lstrip('.'), "truetype")
                        fu = QtCore.QUrl.fromLocalFile(fp).toString()
                        font_face_css += f"@font-face {{ font-family: '{cf['name']}'; src: url('{fu}') format('{fmt}'); }}\n"
            except Exception:
                pass

        try:
            from themes import BUNDLED_FONTS
            for bf_name, bf_info in BUNDLED_FONTS.items():
                bf_path = os.path.join(SITE_DIR, "fonts", bf_info.get("filename", ""))
                if os.path.exists(bf_path):
                    bundled_fonts.append(bf_name)
                    ext = os.path.splitext(bf_path)[1].lower()
                    fmt = {"ttf": "truetype", "otf": "opentype", "woff": "woff", "woff2": "woff2"}.get(ext.lstrip('.'), "truetype")
                    fu = QtCore.QUrl.fromLocalFile(bf_path).toString()
                    font_face_css += f"@font-face {{ font-family: '{bf_name}'; src: url('{fu}') format('{fmt}'); }}\n"
        except Exception:
            pass

        # Inject site theme CSS variables + content.css for WYSIWYG content area
        _wysiwyg_css = ""
        _cfg_json_path = os.path.join(_APP_DIR, "settings", "config.json")
        try:
            with open(_cfg_json_path, encoding="utf-8") as _f:
                _raw_cfg = json.load(_f)
            _theme_key = _raw_cfg.get("selected_theme", "Dark")
            from themes import THEMES
            if _theme_key == "Custom":
                _t = dict(THEMES.get("Dark", {}))
                _t.update(_raw_cfg.get("custom_theme", {}))
            else:
                _t = dict(THEMES.get(_theme_key, THEMES.get("Dark", {})))
            _vars = []
            for _vk in ("body_bg", "text", "hero_bg", "card_bg", "card_border",
                         "input_bg", "input_border", "label", "muted",
                         "accent", "accent_hover", "accent_text"):
                _css_key = _vk.replace("_", "-")
                _vars.append(f"  --{_css_key}: {_t.get(_vk, 'inherit')};")
            _wysiwyg_css = ":root {\n" + "\n".join(_vars) + "\n}\n"
            _wysiwyg_css += ".ck.ck-editor__editable_inline { background-color: var(--body-bg); }\n"
            _content_css_path = os.path.join(SITE_DIR, "content.css")
            if os.path.exists(_content_css_path):
                with open(_content_css_path, encoding="utf-8") as _f:
                    _wysiwyg_css += _f.read()
        except Exception:
            pass

        config = {
            "lang": lang,
            "dir": dir_,
            "customFonts": custom_fonts + bundled_fonts,
        }
        config_js = f"<script>window.__ckEditorConfig = {json.dumps(config)};</script>\n"
        inj = ""
        if font_face_css:
            inj += f"<style>\n{font_face_css}\n</style>\n"
        if _wysiwyg_css:
            inj += f"<style>\n{_wysiwyg_css}\n</style>\n"
        html = html.replace("</head>", config_js + inj + "</head>")

        self.view.setHtml(html, base_url)

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
        self._load_editor_with_config()
        layout.addWidget(self.view, 1)

        bar = QtWidgets.QWidget()
        bar.setStyleSheet("background: #161b22; border-top: 1px solid #30363d;")
        bl = QtWidgets.QHBoxLayout(bar)
        bl.setContentsMargins(12, 8, 12, 8)

        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("color: #6e7681; font-size: 12px;")
        bl.addWidget(self.status_label, 1)

        import_btn = QtWidgets.QPushButton("Import")
        import_btn.clicked.connect(self._import_file)
        bl.addWidget(import_btn)

        save_btn = QtWidgets.QPushButton("Save")
        save_btn.setStyleSheet("background: #3fb950; color: #fff; border: none; border-radius: 6px; padding: 8px 20px;")
        save_btn.clicked.connect(self._save)
        bl.addWidget(save_btn)

        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.clicked.connect(self._clear)
        bl.addWidget(clear_btn)

        export_btn = QtWidgets.QPushButton("Export HTML")
        export_btn.setProperty("class", "primary")
        export_btn.setStyleSheet("background: #58a6ff; color: #fff; border: none; border-radius: 6px; padding: 8px 20px;")
        export_btn.clicked.connect(self._export)
        bl.addWidget(export_btn)

        layout.addWidget(bar)

        warning = QtWidgets.QLabel("⚠ Under construction — may not function properly")
        warning.setStyleSheet("color: #f0883e; background: #161b22; padding: 6px 12px; font-size: 12px;")
        layout.addWidget(warning)

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

    def _import_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import File", "",
            "Supported files (*.zip *.mht *.mhtml *.html);;Zip files (*.zip);;MHT files (*.mht *.mhtml);;HTML files (*.html)")
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext == '.html':
            self.load_file(path)
        else:
            try:
                from docx2html import convert_file
                result, err = convert_file(path)
                if err:
                    self.status_label.setText(f"Import error: {err}")
                    return
                if not result.get('ok'):
                    self.status_label.setText(f"Import error: {result.get('error', 'Unknown')}")
                    return
                html = result['html']
                self._current_file = None
                js_content = json.dumps(html)
                self.view.page().runJavaScript(f"setEditorContent({js_content})")
                self.status_label.setText(f"Imported: {os.path.basename(path)}")
            except Exception as e:
                self.status_label.setText(f"Import error: {e}")

    def _save(self):
        if not self._ready:
            self.status_label.setText("Editor not ready yet")
            return
        if self._current_file:
            self._export_path = self._current_file
            self.view.page().runJavaScript("getEditorContent()", self._on_save_result)
        else:
            self._export()

    def _on_save_result(self, html):
        self._on_export_result(html)
        path = getattr(self, '_export_path', None)
        if path:
            self.status_label.setText(f"Saved to {os.path.basename(path)}")
            self._current_file = path

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
        self.view.page().runJavaScript("getEditorContent()", self._on_export_result)

    def _on_export_result(self, html):
        html = html.strip()
        if not html:
            self.status_label.setText("Nothing to export")
            return
        path = getattr(self, '_export_path', None)
        if not path:
            self.status_label.setText("No export path set")
            return
        from generate import load_config as _load_cfg
        _cfg = _load_cfg()
        try:
            export_in_site = os.path.commonpath(
                [os.path.abspath(path), os.path.abspath(SITE_DIR)]
            ) == os.path.abspath(SITE_DIR)
        except Exception:
            export_in_site = False

        try:
            if export_in_site:
                title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
                title = title_match.group(1).strip() if title_match else "Page"
                minimal = f"""<!DOCTYPE html>
<html><head><title>{title}</title></head>
<body><main>
{html}
</main></body></html>"""
                with open(path, "w", encoding="utf-8") as f:
                    f.write(minimal)
                from generate import build_page as _build_page, scan_categories as _scan_cats, clear_config_cache as _clear_cache
                _clear_cache()
                import generate as _gen
                _gen.CONFIG.update(_gen.load_config())
                cats = _scan_cats()
                _build_page(path, cats)
            else:
                style_css = ""
                for fn in ("style.css", "content.css"):
                    fp = os.path.join(SITE_DIR, fn)
                    try:
                        with open(fp, encoding="utf-8") as f:
                            css = f.read()
                    except Exception:
                        css = ""
                    if css:
                        style_css += f"<style>\n{css}\n</style>\n"
                lang = _cfg.get("site_lang", "en")
                dir_attr = _cfg.get("site_dir", "ltr")
                padding = _cfg.get("site_padding", 20)
                result = f"""<!DOCTYPE html>
<html lang="{lang}" dir="{dir_attr}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page</title>
{style_css}</head>
<body>
  <main class="ck-content" style="padding-left:{padding}px;padding-right:{padding}px;">
{html}
  </main>
</body>
</html>"""
                with open(path, "w", encoding="utf-8") as f:
                    f.write(result)
            self.status_label.setText(f"Exported to {os.path.basename(path)}")
        except Exception as e:
            self.status_label.setText(f"Error writing file: {e}")
