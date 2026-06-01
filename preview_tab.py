import os, sys
from PyQt6 import QtWidgets, QtCore, QtWebEngineWidgets, QtWebEngineCore

_APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(_APP_DIR, "site")

import sidebar_util
sidebar_util.SITE_DIR = SITE_DIR

class _RegenThread(QtCore.QThread):
    done = QtCore.pyqtSignal()

    def run(self):
        from generate import generate_all, clear_sidebar_cache, clear_config_cache, CONFIG, load_config
        discovered = sidebar_util.auto_discover()
        if discovered:
            sidebar = sidebar_util.load_sidebar()
            for d in discovered:
                for cat in sidebar:
                    if cat["category"] == d["category"]:
                        cat["entries"].append({"name": d["name"], "file": d["file"]})
                        break
                else:
                    sidebar.append({"category": d["category"], "entries": [{"name": d["name"], "file": d["file"]}]})
            sidebar_util.save_sidebar(sidebar)
        clear_sidebar_cache()
        clear_config_cache()
        CONFIG.update(load_config())
        generate_all(log_func=lambda m: None)
        self.done.emit()

MARGIN = 24
MIN_W = 200
MIN_H = 120

DEVICE_PRESETS = [
    ("Desktop", 16 / 9),
    ("Tablet", 768 / 1024),
    ("Mobile", 375 / 667),
]


class PreviewTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._aspect_ratio = 16 / 9

        self._resize_timer = QtCore.QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(80)
        self._resize_timer.timeout.connect(self._fit_to_container)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QtWidgets.QWidget()
        toolbar.setStyleSheet("background: #161b22; border-bottom: 1px solid #30363d;")
        tl = QtWidgets.QHBoxLayout(toolbar)
        tl.setContentsMargins(8, 4, 8, 4)
        tl.setSpacing(4)

        self.preset_buttons = []
        for label, ratio in DEVICE_PRESETS:
            btn = QtWidgets.QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, r=ratio, b=btn: self._set_preset(r, b))
            tl.addWidget(btn)
            self.preset_buttons.append(btn)

        self.url_input = QtWidgets.QLineEdit()
        self.url_input.setStyleSheet("""
            QLineEdit { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                        border-radius: 4px; padding: 4px 8px; }
        """)
        tl.addWidget(self.url_input, 1)

        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)
        tl.addWidget(refresh_btn)

        layout.addWidget(toolbar)

        self.container = QtWidgets.QWidget()
        self.container.setStyleSheet("background: #010409;")
        self.container_layout = QtWidgets.QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setStyleSheet("background: #ffffff;")
        self.view.settings().setAttribute(QtWebEngineCore.QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.view.settings().setAttribute(QtWebEngineCore.QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.container_layout.addWidget(self.view)

        layout.addWidget(self.container, 1)

        self._html_path = ""
        self._set_preset(16 / 9, self.preset_buttons[0])

    def load_site(self):
        index = os.path.join(SITE_DIR, "index.html")
        if os.path.exists(index):
            self._html_path = index
            self.url_input.setText(index)
            self.view.setUrl(QtCore.QUrl.fromLocalFile(index))
        else:
            self.url_input.setText("No index.html found")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_timer.start()

    def _fit_to_container(self):
        cw = self.container.width() - 2 * MARGIN
        ch = self.container.height() - 2 * MARGIN
        if cw <= 0 or ch <= 0:
            return
        ar = self._aspect_ratio
        if cw / ch > ar:
            w = int(ch * ar)
            h = ch
        else:
            w = cw
            h = int(cw / ar)
        self.view.setFixedSize(max(w, MIN_W), max(h, MIN_H))
        self.container_layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)

    def _set_preset(self, ratio, active_btn):
        self._aspect_ratio = ratio
        for btn in self.preset_buttons:
            btn.setChecked(btn == active_btn)
            btn.setProperty("class", "active" if btn == active_btn else "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._fit_to_container()
        self.view.updateGeometry()

    def _refresh(self):
        if hasattr(self, '_regen_thread') and self._regen_thread and self._regen_thread.isRunning():
            return
        self.url_input.setText("Generating...")
        self._regen_thread = _RegenThread()
        self._regen_thread.done.connect(self._on_regen_done)
        self._regen_thread.start()

    def _on_regen_done(self):
        self._regen_thread.done.disconnect(self._on_regen_done)
        self._regen_thread = None
        self.load_site()
