#!/usr/bin/env python3
import os, sys, subprocess, json
from PyQt5 import QtWidgets, QtCore, QtGui

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
STYLE_FILE = os.path.join(SITE_DIR, "style.css")
FONTS_DIR = os.path.join(SITE_DIR, "fonts")
FONTS_JSON = os.path.join(FONTS_DIR, "fonts.json")
CONFIG_FILE = os.path.join(SITE_DIR, "config.json")
TEMPLATE_FILE = os.path.join(SITE_DIR, "template.html")

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

COLOR_GROUPS = [
    ("Light Page", [
        ("body_bg", "Background"), ("text", "Text"), ("hero_bg", "Hero BG"),
    ]),
    ("Light Cards", [
        ("card_bg", "Card BG"), ("card_border", "Card Border"),
        ("label", "Label"), ("muted", "Muted"),
    ]),
    ("Light Accent", [
        ("accent", "Accent"), ("accent_hover", "Accent Hover"), ("accent_text", "Accent Text"),
    ]),
    ("Light Inputs", [
        ("input_bg", "Input BG"), ("input_border", "Input Border"),
    ]),
    ("Dark Page", [
        ("dark_body_bg", "Background"), ("dark_text", "Text"), ("dark_hero_bg", "Hero BG"),
    ]),
    ("Dark Cards", [
        ("dark_card_bg", "Card BG"), ("dark_card_border", "Card Border"),
        ("dark_label", "Label"), ("dark_muted", "Muted"),
    ]),
    ("Dark Accent", [
        ("dark_accent", "Accent"), ("dark_accent_hover", "Accent Hover"), ("dark_accent_text", "Accent Text"),
    ]),
    ("Dark Inputs", [
        ("dark_input_bg", "Input BG"), ("dark_input_border", "Input Border"),
    ]),
    ("Header", [
        ("header_bg", "Header BG"), ("header_text", "Header Text"),
    ]),
    ("Sidebar", [
        ("sidebar_bg", "Sidebar BG"), ("sidebar_text", "Sidebar Text"),
        ("sidebar_border", "Sidebar Border"), ("sidebar_hover", "Sidebar Hover"),
        ("link_muted", "Link Muted"), ("link_hover_text", "Link Hover Text"),
        ("avatar_border", "Avatar Border"),
    ]),
    ("Footer", [
        ("footer_bg", "Footer BG"), ("footer_text", "Footer Text"),
    ]),
    ("Other", [
        ("theme_border", "Theme Border"),
    ]),
]

ALL_COLOR_KEYS = [k for _, items in COLOR_GROUPS for k, _ in items]

FORMAT_MAP = {".ttf": "truetype", ".otf": "opentype", ".woff": "woff", ".woff2": "woff2"}


def load_custom_fonts():
    if os.path.exists(FONTS_JSON):
        with open(FONTS_JSON) as f:
            return json.load(f)
    return []


def save_custom_fonts(fonts):
    os.makedirs(FONTS_DIR, exist_ok=True)
    with open(FONTS_JSON, "w") as f:
        json.dump(fonts, f, indent=2)


def is_custom_font(name):
    return name not in FONTS


def get_custom_font(name):
    for cf in load_custom_fonts():
        if cf["name"] == name:
            return cf
    return None


def make_font_face_rule(cf):
    ext = os.path.splitext(cf["file"])[1].lower()
    fmt = FORMAT_MAP.get(ext, "truetype")
    url = cf["file"]
    return f"""@font-face {{
  font-family: '{cf["name"]}';
  src: url('{url}') format('{fmt}');
  font-weight: normal;
  font-style: normal;
}}"""


class CustomColorDialog(QtWidgets.QDialog):
    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Colors")
        self.setMinimumSize(580, 500)
        self.setStyleSheet("""
            QDialog { background: #1a1a1a; }
            QLabel { color: #e0e0e0; }
            QLabel.dim { color: #999; font-size: 10px; }
            QLabel.heading { color: #ccc; font-size: 11px; font-weight: bold; padding-top: 6px; }
            QPushButton {
                background: #555; color: #fff; border: none;
                border-radius: 6px; padding: 8px 20px; font-size: 13px;
            }
            QPushButton:hover { background: #666; }
            QPushButton.primary { background: #1a6b3c; }
            QPushButton.primary:hover { background: #218c4e; }
            QPushButton.danger { background: #b71c1c; }
            QPushButton.danger:hover { background: #d32f2f; }
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: #2a2a2a; width: 8px; }
            QScrollBar::handle:vertical { background: #555; border-radius: 4px; }
        """)

        self.colors = dict(colors)
        self.color_btns = {}

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)

        heading = QtWidgets.QLabel("Click any color swatch to open the picker")
        heading.setStyleSheet("font-size: 14px; font-weight: bold; color: #eee; padding-bottom: 4px;")
        layout.addWidget(heading)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        body = QtWidgets.QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QtWidgets.QVBoxLayout(body)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(2)

        for group_name, items in COLOR_GROUPS:
            gl = QtWidgets.QLabel(group_name)
            gl.setProperty("class", "heading")
            bl.addWidget(gl)

            row_w = QtWidgets.QWidget()
            row_w.setStyleSheet("background: transparent;")
            rl = QtWidgets.QHBoxLayout(row_w)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(10)
            for key, label in items:
                col_w = QtWidgets.QWidget()
                col_w.setStyleSheet("background: transparent;")
                cl = QtWidgets.QVBoxLayout(col_w)
                cl.setContentsMargins(0, 0, 0, 0)
                cl.setSpacing(1)
                btn = QtWidgets.QPushButton()
                btn.setFixedSize(32, 32)
                color = self.colors.get(key, "#000")
                btn.setStyleSheet(
                    f"background: {color}; border: 1px solid #555; border-radius: 4px;")
                btn.setToolTip(f"{key} = {color}")
                btn.color_key = key
                btn.clicked.connect(self.pick_color)
                cl.addWidget(btn, alignment=QtCore.Qt.AlignCenter)
                lb = QtWidgets.QLabel(label)
                lb.setProperty("class", "dim")
                cl.addWidget(lb, alignment=QtCore.Qt.AlignCenter)
                rl.addWidget(col_w)
                self.color_btns[key] = btn
            bl.addWidget(row_w)

        scroll.setWidget(body)
        layout.addWidget(scroll, 1)

        bottom = QtWidgets.QHBoxLayout()
        reset_btn = QtWidgets.QPushButton("Reset to Default")
        reset_btn.setProperty("class", "danger")
        reset_btn.clicked.connect(self.reset_colors)
        bottom.addWidget(reset_btn)

        bottom.addStretch()

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        bottom.addWidget(cancel_btn)

        ok_btn = QtWidgets.QPushButton("Save Colors")
        ok_btn.setProperty("class", "primary")
        ok_btn.clicked.connect(self.accept)
        bottom.addWidget(ok_btn)

        layout.addLayout(bottom)

    def pick_color(self):
        btn = self.sender()
        key = btn.color_key
        current = self.colors.get(key, "#000")
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(current), self, f"Pick {key}")
        if color.isValid():
            hex_color = color.name()
            self.colors[key] = hex_color
            btn.setStyleSheet(
                f"background: {hex_color}; border: 1px solid #555; border-radius: 4px;")
            btn.setToolTip(f"{key} = {hex_color}")

    def reset_colors(self):
        for key, val in THEMES["Dark"].items():
            if key in self.colors:
                self.colors[key] = val
        for key, btn in self.color_btns.items():
            color = self.colors.get(key, "#000")
            btn.setStyleSheet(
                f"background: {color}; border: 1px solid #555; border-radius: 4px;")
            btn.setToolTip(f"{key} = {color}")

    def get_colors(self):
        return dict(self.colors)


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
            QPushButton.danger { background: #b71c1c; }
            QPushButton.danger:hover { background: #d32f2f; }
            QTextEdit {
                background: #2a2a2a; color: #a0a0a0; border: 1px solid #333;
                border-radius: 6px; padding: 6px; font-size: 11px; font-family: monospace;
            }
            QLineEdit {
                background: #2a2a2a; color: #e0e0e0; border: 1px solid #333;
                border-radius: 6px; padding: 6px 10px; font-size: 13px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        heading = QtWidgets.QLabel("Site Theme")
        heading.setProperty("class", "heading")
        layout.addWidget(heading)

        desc = QtWidgets.QLabel(
            "Choose a preset theme to style the entire site (header, sidebar, cards, buttons, dark mode)."
        )
        desc.setProperty("class", "dim")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Theme selector
        selector_row = QtWidgets.QHBoxLayout()
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItem("Custom...", "Custom")
        self.theme_combo.insertSeparator(self.theme_combo.count())
        for key in THEMES:
            self.theme_combo.addItem(NAME_MAP.get(key, key), key)
        self.custom_colors = dict(THEMES["Dark"])
        self._ready = False
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        selector_row.addWidget(self.theme_combo, 1)

        apply_btn = QtWidgets.QPushButton("Apply Theme")
        apply_btn.setProperty("class", "primary")
        apply_btn.setMinimumHeight(40)
        apply_btn.clicked.connect(self.apply_theme)
        selector_row.addWidget(apply_btn)
        layout.addLayout(selector_row)

        # Site title
        title_row = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("Site title:")
        title_label.setStyleSheet("color: #999; font-size: 12px;")
        title_row.addWidget(title_label)
        self.site_title_input = QtWidgets.QLineEdit()
        self.load_site_title()
        title_row.addWidget(self.site_title_input, 1)
        layout.addLayout(title_row)

        # Font selector
        font_row = QtWidgets.QHBoxLayout()
        font_label = QtWidgets.QLabel("Font:")
        font_label.setStyleSheet("color: #999; font-size: 12px;")
        font_row.addWidget(font_label)
        self.font_combo = QtWidgets.QComboBox()
        self.rebuild_font_combo()
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

        # Current theme / font label
        self.current_label = QtWidgets.QLabel("")
        self.current_label.setProperty("class", "dim")
        layout.addWidget(self.current_label)

        # Customize button (visible only when Custom selected)
        self.customize_btn = QtWidgets.QPushButton("Customize Colors...")
        self.customize_btn.setMinimumHeight(36)
        self.customize_btn.setVisible(False)
        self.customize_btn.clicked.connect(self.open_color_dialog)
        layout.addWidget(self.customize_btn)

        # Preview log
        self.preview = QtWidgets.QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Theme preview will appear here...")
        self.preview.setMaximumHeight(160)
        layout.addWidget(self.preview, 1)

        # --- Custom Font Import ---
        import_heading = QtWidgets.QLabel("Import Custom Font")
        import_heading.setProperty("class", "heading")
        layout.addWidget(import_heading)

        import_file_row = QtWidgets.QHBoxLayout()
        self.import_path = QtWidgets.QLineEdit()
        self.import_path.setPlaceholderText("Select a font file (.ttf, .woff, .woff2, .otf)...")
        import_file_row.addWidget(self.import_path, 1)
        browse_font_btn = QtWidgets.QPushButton("Browse")
        browse_font_btn.clicked.connect(self.browse_font)
        import_file_row.addWidget(browse_font_btn)
        layout.addLayout(import_file_row)

        name_row = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Family name:")
        name_label.setStyleSheet("color: #999; font-size: 12px;")
        name_row.addWidget(name_label)
        self.import_name = QtWidgets.QLineEdit()
        self.import_name.setPlaceholderText("e.g. MyFont")
        name_row.addWidget(self.import_name, 1)
        import_btn = QtWidgets.QPushButton("Import")
        import_btn.clicked.connect(self.import_font)
        name_row.addWidget(import_btn)
        layout.addLayout(name_row)

        # Imported fonts list
        self.imported_list = QtWidgets.QWidget()
        self.imported_list.setStyleSheet("background: transparent;")
        self.imported_layout = QtWidgets.QVBoxLayout(self.imported_list)
        self.imported_layout.setContentsMargins(0, 0, 0, 0)
        self.imported_layout.setSpacing(4)
        layout.addWidget(self.imported_list)
        self.refresh_imported_list()

        # Status
        self.status = QtWidgets.QLabel("")
        self.status.setProperty("class", "dim")
        layout.addWidget(self.status)

        # Pick first preset theme
        self._ready = True
        self.theme_combo.setCurrentIndex(2)
        self.on_theme_changed(self.theme_combo.currentIndex())

    # --- Font combo ---

    def rebuild_font_combo(self):
        self.font_combo.blockSignals(True)
        self.font_combo.clear()
        for name in FONTS:
            self.font_combo.addItem(name)
        customs = load_custom_fonts()
        if customs:
            self.font_combo.insertSeparator(self.font_combo.count())
            for cf in customs:
                self.font_combo.addItem(cf["name"])
        self.font_combo.blockSignals(False)

    # --- Custom font import ---

    def browse_font(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Font File", "",
            "Font Files (*.ttf *.woff *.woff2 *.otf)")
        if p:
            self.import_path.setText(p)
            base = os.path.splitext(os.path.basename(p))[0]
            self.import_name.setText(base)

    def import_font(self):
        src = self.import_path.text().strip()
        name = self.import_name.text().strip()
        if not src:
            self.status.setText("Select a font file first")
            return
        if not name:
            self.status.setText("Enter a font family name")
            return
        ext = os.path.splitext(src)[1].lower()
        if ext not in FORMAT_MAP:
            self.status.setText("Unsupported font format. Use .ttf, .otf, .woff, or .woff2")
            return
        customs = load_custom_fonts()
        if any(cf["name"] == name for cf in customs):
            self.status.setText(f"Font '{name}' already imported")
            return

        os.makedirs(FONTS_DIR, exist_ok=True)
        dst = os.path.join(FONTS_DIR, os.path.basename(src))
        try:
            import shutil
            shutil.copy2(src, dst)
        except Exception as e:
            self.status.setText(f"Error copying font: {e}")
            return

        rel = os.path.relpath(dst, SITE_DIR).replace("\\", "/")
        customs.append({"name": name, "file": rel})
        save_custom_fonts(customs)

        self.rebuild_font_combo()
        idx = self.font_combo.findText(name)
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        self.refresh_imported_list()
        self.import_path.clear()
        self.import_name.clear()
        self.status.setText(f"Imported font '{name}'")

    def refresh_imported_list(self):
        for i in reversed(range(self.imported_layout.count())):
            w = self.imported_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        customs = load_custom_fonts()
        if not customs:
            lbl = QtWidgets.QLabel("No custom fonts imported")
            lbl.setProperty("class", "dim")
            self.imported_layout.addWidget(lbl)
            return
        for cf in customs:
            row = QtWidgets.QHBoxLayout()
            lbl = QtWidgets.QLabel(f"{cf['name']}  ({cf['file']})")
            lbl.setStyleSheet("color: #999; font-size: 12px;")
            row.addWidget(lbl, 1)
            rm_btn = QtWidgets.QPushButton("Remove")
            rm_btn.setProperty("class", "danger")
            rm_btn.setStyleSheet(
                "background: #b71c1c; color: #fff; border: none; border-radius: 4px; padding: 4px 10px; font-size: 11px;")
            rm_btn.cf_name = cf["name"]
            rm_btn.clicked.connect(self.remove_font)
            row.addWidget(rm_btn)
            container = QtWidgets.QWidget()
            container.setLayout(row)
            self.imported_layout.addWidget(container)

    def remove_font(self):
        btn = self.sender()
        name = btn.cf_name
        customs = load_custom_fonts()
        kept = []
        for cf in customs:
            if cf["name"] == name:
                fpath = os.path.join(SITE_DIR, cf["file"])
                if os.path.exists(fpath):
                    os.remove(fpath)
            else:
                kept.append(cf)
        save_custom_fonts(kept)
        self.rebuild_font_combo()
        self.refresh_imported_list()
        self.update_preview()
        self.status.setText(f"Removed font '{name}'")

    # --- Site title ---

    def load_site_title(self):
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
        self.site_title_input.setText(cfg.get("site_title", "Placeholder"))

    def save_site_title(self):
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
        cfg["site_title"] = self.site_title_input.text()
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)

    # --- Custom colors ---

    def load_custom_theme(self):
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
        return cfg.get("custom_theme", {})

    def save_custom_theme(self, colors):
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
        cfg["custom_theme"] = colors
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)

    def open_color_dialog(self):
        colors = dict(self.custom_colors) if self.custom_colors else dict(THEMES["Dark"])
        dlg = CustomColorDialog(colors, self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.custom_colors = dlg.get_colors()
            self.save_custom_theme(self.custom_colors)
            self.update_preview()
            self.status.setText("Custom colors updated")

    # --- Preview / apply ---

    def on_theme_changed(self, idx):
        is_custom = self.theme_key() == "Custom"
        if hasattr(self, 'customize_btn'):
            self.customize_btn.setVisible(is_custom)
        if is_custom:
            self.custom_colors = dict(THEMES["Dark"])
            saved = self.load_custom_theme()
            if saved:
                self.custom_colors.update(saved)
        self.update_preview()

    def theme_key(self):
        return self.theme_combo.currentData()

    def theme_colors(self):
        key = self.theme_key()
        if key == "Custom":
            return self.custom_colors if hasattr(self, 'custom_colors') and self.custom_colors else THEMES["Dark"]
        return THEMES[key]

    def update_preview(self):
        t = self.theme_colors()
        name = self.theme_combo.currentText()
        font_name = self.font_combo.currentText()
        site_title = self.site_title_input.text()
        self.current_label.setText(f"Theme: {name}  |  Font: {font_name}  |  Title: {site_title}")

        for sw, key in self.swatch_widgets:
            color = t.get(key, "#000")
            sw.setStyleSheet(
                f"background: {color}; border-radius: 4px; border: 1px solid #555;")

        lines = []
        for key, label in SWATCH_KEYS:
            lines.append(f"  {label}: {t.get(key, '?')}")
        lines.append(f"  Font: {font_name}")
        lines.append(f"  Site Title: {site_title}")
        if self.theme_key() == "Custom":
            lines.append("  (custom colors)")
        self.preview.setPlainText(f"Theme: {name}\n" + "\n".join(lines))

    def apply_theme(self):
        is_custom = self.theme_key() == "Custom"
        t = dict(self.theme_colors())
        name = "Custom" if is_custom else self.theme_combo.currentText()
        font_name = self.font_combo.currentText()

        # Save site title
        self.save_site_title()
        site_title = self.site_title_input.text()

        if is_custom_font(font_name):
            cf = get_custom_font(font_name)
            if cf:
                t["font_family"] = f"'{font_name}'"
                t["font_face_rules"] = make_font_face_rule(cf)
            else:
                self.status.setText(f"Custom font '{font_name}' not found")
                return
        else:
            t["font_family"] = FONTS[font_name]
            t["font_face_rules"] = ""

        self.status.setText(f"Applying {name} with {font_name} (title: {site_title})...")
        QtWidgets.QApplication.processEvents()

        css = CSS_TEMPLATE.substitute(**t)
        try:
            with open(STYLE_FILE, "w") as f:
                f.write(css)
        except Exception as e:
            self.status.setText(f"Error writing CSS: {e}")
            return

        self.status.setText(f"Applied {name}. Running generate...")
        QtWidgets.QApplication.processEvents()

        r = subprocess.run(
            [sys.executable, os.path.join(SITE_DIR, "generate.py")],
            cwd=SITE_DIR, capture_output=True, text=True)
        output = r.stdout.strip() or r.stderr.strip()
        self.status.setText(
            output.split("\n")[-1] if output else f"Applied")
