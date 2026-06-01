import os, sys
from PyQt6 import QtWidgets, QtCore, QtWebEngineWidgets, QtWebEngineCore

_APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(_APP_DIR, "site")

DEVICE_PRESETS = [
    ("Desktop", 0, 0),
    ("Tablet (768px)", 768, 1024),
    ("Mobile (375px)", 375, 667),
    ("Mobile (414px)", 414, 896),
]


class PreviewDialog(QtWidgets.QDialog):
    def __init__(self, html_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Site Preview")
        self.setMinimumSize(600, 400)
        self.resize(1200, 800)
        self.setStyleSheet("""
            QDialog { background: #0d1117; }
            QPushButton {
                background: #21262d; color: #c9d1d9; border: none;
                border-radius: 6px; padding: 6px 14px;
            }
            QPushButton:hover { background: #30363d; }
            QPushButton.active { background: #58a6ff; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QtWidgets.QWidget()
        toolbar.setStyleSheet("background: #161b22; border-bottom: 1px solid #30363d;")
        tl = QtWidgets.QHBoxLayout(toolbar)
        tl.setContentsMargins(8, 4, 8, 4)
        tl.setSpacing(4)

        self.preset_buttons = []
        for label, w, h in DEVICE_PRESETS:
            btn = QtWidgets.QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, pw=w, ph=h, b=btn: self._set_preset(pw, ph, b))
            tl.addWidget(btn)
            self.preset_buttons.append(btn)

        tl.addStretch()

        self.url_input = QtWidgets.QLineEdit()
        self.url_input.setStyleSheet("""
            QLineEdit { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                        border-radius: 4px; padding: 4px 8px; }
        """)
        self.url_input.setReadOnly(True)
        tl.addWidget(self.url_input, 1)

        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)
        tl.addWidget(refresh_btn)

        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        tl.addWidget(close_btn)

        layout.addWidget(toolbar)

        self.container = QtWidgets.QWidget()
        self.container.setStyleSheet("background: #010409;")
        self.container_layout = QtWidgets.QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setStyleSheet("background: #ffffff;")
        self.view.settings().setAttribute(QtWebEngineCore.QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.container_layout.addWidget(self.view)

        layout.addWidget(self.container, 1)

        self._html_path = html_path
        self.url_input.setText(html_path)
        self._set_preset(0, 0, self.preset_buttons[0])
        self.view.setUrl(QtCore.QUrl.fromLocalFile(html_path))

    def _set_preset(self, width, height, active_btn):
        for btn in self.preset_buttons:
            btn.setChecked(btn == active_btn)
            btn.setProperty("class", "active" if btn == active_btn else "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if width == 0 and height == 0:
            self.view.setFixedSize(16777215, 16777215)
            self.container_layout.setContentsMargins(0, 0, 0, 0)
        else:
            self.view.setFixedSize(width, height)
            self.container_layout.setContentsMargins(24, 24, 24, 24)
        self.view.updateGeometry()

    def _refresh(self):
        self.view.reload()
