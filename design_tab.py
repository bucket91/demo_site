import os, sys, json, webbrowser
from PyQt5 import QtWidgets, QtCore

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SITE_DIR, "config.json")


class DesignWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
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
        local_btn = QtWidgets.QPushButton("Preview Site Locally")
        local_btn.clicked.connect(self._preview_local)
        title_row.addWidget(local_btn)
        online_btn = QtWidgets.QPushButton("Preview on GitHub Pages")
        online_btn.clicked.connect(self._preview_online)
        title_row.addWidget(online_btn)
        cl.addLayout(title_row)

        self.preview_status = QtWidgets.QLabel("")
        self.preview_status.setProperty("class", "dim")
        self.preview_status.setStyleSheet("color: #6e7681; margin: 0 16px 8px;")
        cl.addWidget(self.preview_status)

        font_row = QtWidgets.QHBoxLayout()
        font_row.setContentsMargins(16, 0, 16, 4)
        font_label = QtWidgets.QLabel("UI Font Size:")
        font_label.setStyleSheet("color: #6e7681;")
        font_row.addWidget(font_label)
        self.font_size_spin = QtWidgets.QSpinBox()
        self.font_size_spin.setRange(10, 24)
        self.font_size_spin.setValue(cfg.get("gui_font_size", 14))
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        font_row.addWidget(self.font_size_spin)
        font_row.addStretch()
        cl.addLayout(font_row)

        # ── Owner ──
        import owner_tab
        owner_tab.SITE_DIR = SITE_DIR
        self.owner_widget = owner_tab.OwnerWidget()
        cl.addWidget(self.owner_widget)

        sep1 = QtWidgets.QFrame()
        sep1.setFrameShape(QtWidgets.QFrame.HLine)
        sep1.setStyleSheet("background: #30363d; max-height: 1px;")
        cl.addWidget(sep1)

        # ── Theme ──
        import theme_customizer
        theme_customizer.SITE_DIR = SITE_DIR
        self.theme_widget = theme_customizer.ThemeCustomizerWidget()
        cl.addWidget(self.theme_widget)

        sep2 = QtWidgets.QFrame()
        sep2.setFrameShape(QtWidgets.QFrame.HLine)
        sep2.setStyleSheet("background: #30363d; max-height: 1px;")
        cl.addWidget(sep2)

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

    @QtCore.pyqtSlot(int)
    def _on_font_size_changed(self, size):
        self._save_cfg({"gui_font_size": size})
        import gui_theme
        gui_theme.apply()

    def _preview_local(self):
        index = os.path.join(SITE_DIR, "index.html")
        if not os.path.exists(index):
            import generate
            generate.run_generate_captured()
        if os.path.exists(index):
            webbrowser.open(f'file://{os.path.abspath(index)}')
            self.preview_status.setText("Opened local site in browser")

    def _preview_online(self):
        cfg = self._load_cfg()
        url = cfg.get("git_remote_url", "")
        if not url or 'github.com/' not in url:
            self.preview_status.setText("No GitHub remote URL configured in Settings")
            return
        after = url.split('github.com/', 1)[1]
        if after.endswith('.git'):
            after = after[:-4]
        if '/' in after:
            user, repo = after.split('/', 1)
            if repo == f'{user}.github.io':
                base = f"https://{user}.github.io/"
            else:
                base = f"https://{user}.github.io/{repo}/"
            webbrowser.open(base)
            self.preview_status.setText(f"Opened {base} in browser")
