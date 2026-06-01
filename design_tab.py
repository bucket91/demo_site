import os, sys, json
from PyQt6 import QtWidgets, QtCore

_APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(_APP_DIR, "site")
SETTINGS_DIR = os.path.join(_APP_DIR, "settings")
CONFIG_FILE = os.path.join(SETTINGS_DIR, "config.json")


class DesignWidget(QtWidgets.QWidget):
    settings_changed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        container = QtWidgets.QWidget()
        container.setStyleSheet("background: transparent;")
        cl = QtWidgets.QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        # ── Site Title ──
        heading = QtWidgets.QLabel("Site")
        heading.setProperty("class", "heading")
        heading.setStyleSheet("font-weight: bold; color: #c9d1d9; margin: 12px 16px 4px;")
        cl.addWidget(heading)

        cfg = self._load_cfg()
        title_row = QtWidgets.QHBoxLayout()
        title_row.setContentsMargins(16, 4, 16, 12)
        title_label = QtWidgets.QLabel("Title:")
        title_label.setStyleSheet("color: #6e7681;")
        title_row.addWidget(title_label)
        self.title_input = QtWidgets.QLineEdit(cfg.get("site_title", "Placeholder"))
        self.title_input.setPlaceholderText("My Awesome Site")
        self.title_input.setStyleSheet("""
            QLineEdit { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                        border-radius: 6px; padding: 8px 10px; }
        """)
        self.title_input.textChanged.connect(self._on_title_changed)
        title_row.addWidget(self.title_input, 1)
        cl.addLayout(title_row)

        opts_row = QtWidgets.QHBoxLayout()
        opts_row.setContentsMargins(16, 0, 16, 4)
        opts_row.setSpacing(16)

        font_label = QtWidgets.QLabel("UI Font Size:")
        font_label.setStyleSheet("color: #6e7681;")
        opts_row.addWidget(font_label)
        self.font_size_spin = QtWidgets.QSpinBox()
        self.font_size_spin.setRange(10, 24)
        self.font_size_spin.setValue(cfg.get("gui_font_size", 14))
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        opts_row.addWidget(self.font_size_spin)

        pad_label = QtWidgets.QLabel("Site Padding:")
        pad_label.setStyleSheet("color: #6e7681;")
        opts_row.addWidget(pad_label)
        self.padding_spin = QtWidgets.QSpinBox()
        self.padding_spin.setRange(0, 80)
        self.padding_spin.setSuffix(" px")
        self.padding_spin.setValue(cfg.get("site_padding", 0))
        self.padding_spin.valueChanged.connect(self._on_padding_changed)
        opts_row.addWidget(self.padding_spin)

        opts_row.addStretch()
        cl.addLayout(opts_row)

        # ── Owner ──
        import owner_tab
        owner_tab.SITE_DIR = SITE_DIR
        self.owner_widget = owner_tab.OwnerWidget()
        cl.addWidget(self.owner_widget)

        sep1 = QtWidgets.QFrame()
        sep1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        sep1.setStyleSheet("background: #30363d; max-height: 1px;")
        cl.addWidget(sep1)

        # ── Theme ──
        import theme_customizer
        theme_customizer.SITE_DIR = SITE_DIR
        self.theme_widget = theme_customizer.ThemeCustomizerWidget(log_widget=self.owner_widget.log)
        cl.addWidget(self.theme_widget)

        sep2 = QtWidgets.QFrame()
        sep2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        sep2.setStyleSheet("background: #30363d; max-height: 1px;")
        cl.addWidget(sep2)

        save_row = QtWidgets.QHBoxLayout()
        save_row.setContentsMargins(16, 8, 16, 8)
        save_row.addStretch()
        self.save_all_btn = QtWidgets.QPushButton("Save All")
        self.save_all_btn.setStyleSheet("""
            QPushButton { background: #3fb950; color: #fff; border: none;
                          border-radius: 6px; padding: 10px 32px;
                          font-weight: bold; font-size: 14px; }
            QPushButton:hover { background: #2ea043; }
        """)
        self.save_all_btn.clicked.connect(self._save_all)
        save_row.addWidget(self.save_all_btn)
        cl.addLayout(save_row)

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _load_cfg(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_cfg(self, update):
        cfg = self._load_cfg()
        cfg.update(update)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)

    def _on_title_changed(self, text):
        self._save_cfg({"site_title": text.strip()})
        self.settings_changed.emit()

    @QtCore.pyqtSlot(int)
    def _on_font_size_changed(self, size):
        self._save_cfg({"gui_font_size": size})
        import gui_theme
        gui_theme.apply()

    @QtCore.pyqtSlot(int)
    def _on_padding_changed(self, value):
        self._save_cfg({"site_padding": value})
        self.settings_changed.emit()

    def _save_all(self):
        self.owner_widget.save_owner()
        self.theme_widget.apply_theme()
        self.settings_changed.emit()
