#!/usr/bin/env python3
import os, subprocess
from PyQt5 import QtWidgets, QtCore, QtGui

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
STYLE_FILE = os.path.join(SITE_DIR, "style.css")

from themes import THEMES, FONTS, CSS_TEMPLATE

NAME_MAP = {
    "Dark": "Dark (default)",
    "Light": "Light",
    "Ocean": "Ocean Blue",
    "Forest": "Forest Green",
    "Sunset": "Sunset Warm",
    "Nord": "Nord Arctic",
    "Dracula": "Dracula Purple",
    "Monokai": "Monokai Code",
    "GitHub": "GitHub",
    "Midnight": "Midnight Dark",
}

SWATCH_KEYS = [
    ("header_bg", "Header"),
    ("sidebar_bg", "Sidebar"),
    ("accent", "Accent"),
    ("body_bg", "Page BG"),
    ("card_bg", "Card BG"),
    ("dark_body_bg", "Dark BG"),
    ("dark_accent", "Dark Accent"),
]


class ThemeCustomizerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QLabel { color: #e0e0e0; }
            QLabel.dim { color: #999; font-size: 11px; }
            QLabel.heading { font-size: 15px; font-weight: bold; color: #eee; padding-top: 4px; }
            QComboBox {
                background: #2a2a2a; color: #e0e0e0; border: 1px solid #333;
                border-radius: 6px; padding: 8px 10px; font-size: 14px;
            }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow { image: none; border-left: 6px solid #999; border-top: 5px solid transparent; border-bottom: 5px solid transparent; }
            QComboBox QAbstractItemView {
                background: #2a2a2a; color: #e0e0e0; selection-background-color: #555;
                border: 1px solid #333; outline: none;
            }
            QPushButton {
                background: #555; color: #fff; border: none;
                border-radius: 8px; padding: 10px 24px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #666; }
            QPushButton:disabled { background: #333; color: #666; }
            QPushButton.primary { background: #1a6b3c; }
            QPushButton.primary:hover { background: #218c4e; }
            QTextEdit {
                background: #2a2a2a; color: #a0a0a0; border: 1px solid #333;
                border-radius: 6px; padding: 6px; font-size: 11px; font-family: monospace;
            }
        """)

        self.current_theme = "Dark"

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        heading = QtWidgets.QLabel("Site Theme")
        heading.setProperty("class", "heading")
        layout.addWidget(heading)

        desc = QtWidgets.QLabel("Choose a preset theme to style the entire site (header, sidebar, cards, buttons, dark mode).")
        desc.setProperty("class", "dim")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Theme selector
        selector_row = QtWidgets.QHBoxLayout()
        self.theme_combo = QtWidgets.QComboBox()
        for key in THEMES:
            self.theme_combo.addItem(NAME_MAP.get(key, key), key)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        selector_row.addWidget(self.theme_combo, 1)

        apply_btn = QtWidgets.QPushButton("Apply Theme")
        apply_btn.setProperty("class", "primary")
        apply_btn.setMinimumHeight(40)
        apply_btn.clicked.connect(self.apply_theme)
        selector_row.addWidget(apply_btn)
        layout.addLayout(selector_row)

        # Font selector
        font_row = QtWidgets.QHBoxLayout()
        font_label = QtWidgets.QLabel("Font:")
        font_label.setStyleSheet("color: #999; font-size: 12px;")
        font_row.addWidget(font_label)
        self.font_combo = QtWidgets.QComboBox()
        for name in FONTS:
            self.font_combo.addItem(name)
        self.font_combo.setCurrentIndex(0)
        self.font_combo.currentIndexChanged.connect(self.on_theme_changed)
        font_row.addWidget(self.font_combo, 1)
        layout.addLayout(font_row)

        # Color swatches
        swatch_label = QtWidgets.QLabel("Color preview:")
        swatch_label.setProperty("class", "dim")
        layout.addWidget(swatch_label)

        self.swatch_grid = QtWidgets.QWidget()
        self.swatch_grid.setStyleSheet("background: transparent;")
        sw_layout = QtWidgets.QGridLayout(self.swatch_grid)
        sw_layout.setSpacing(6)
        self.swatch_widgets = []
        for col, (key, label) in enumerate(SWATCH_KEYS):
            sw = QtWidgets.QFrame()
            sw.setFixedSize(36, 36)
            sw.setToolTip(label)
            sw_layout.addWidget(sw, 0, col)
            lbl = QtWidgets.QLabel(label)
            lbl.setStyleSheet("color: #999; font-size: 10px;")
            sw_layout.addWidget(lbl, 1, col, alignment=QtCore.Qt.AlignCenter)
            self.swatch_widgets.append((sw, key))
        layout.addWidget(self.swatch_grid)

        # Current theme name
        self.current_label = QtWidgets.QLabel("")
        self.current_label.setProperty("class", "dim")
        layout.addWidget(self.current_label)

        # Preview log
        self.preview = QtWidgets.QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Theme preview will appear here...")
        self.preview.setMaximumHeight(160)
        layout.addWidget(self.preview, 1)

        # Status
        self.status = QtWidgets.QLabel("")
        self.status.setProperty("class", "dim")
        layout.addWidget(self.status)

        self.update_preview()

    def on_theme_changed(self, idx):
        self.update_preview()

    def theme_key(self):
        return self.theme_combo.currentData()

    def theme_colors(self):
        return THEMES[self.theme_key()]

    def update_preview(self):
        t = self.theme_colors()
        name = self.theme_combo.currentText()
        font_name = self.font_combo.currentText()
        self.current_label.setText(f"Theme: {name}  |  Font: {font_name}")

        for sw, key in self.swatch_widgets:
            color = t.get(key, "#000")
            sw.setStyleSheet(f"background: {color}; border-radius: 4px; border: 1px solid #555;")

        lines = []
        for key, label in SWATCH_KEYS:
            lines.append(f"  {label}: {t.get(key, '?')}")
        lines.append(f"  Font: {font_name}")
        self.preview.setPlainText(f"Theme: {name}\n" + "\n".join(lines))

    def apply_theme(self):
        t = dict(self.theme_colors())
        name = self.theme_combo.currentText()
        font_name = self.font_combo.currentText()
        t["font_family"] = FONTS[font_name]
        self.status.setText(f"Applying {name} with {font_name}...")
        QtWidgets.QApplication.processEvents()

        css = CSS_TEMPLATE.substitute(**t)
        try:
            with open(STYLE_FILE, 'w') as f:
                f.write(css)
        except Exception as e:
            self.status.setText(f"Error writing CSS: {e}")
            return

        self.status.setText(f"Applied {name}. Running generate...")
        QtWidgets.QApplication.processEvents()

        r = subprocess.run(
            [sys.executable, os.path.join(SITE_DIR, 'generate.py')],
            cwd=SITE_DIR, capture_output=True, text=True)
        output = r.stdout.strip() or r.stderr.strip()
        self.status.setText(output.split('\n')[-1] if output else f"Theme '{name}' / '{font_name}' applied")
