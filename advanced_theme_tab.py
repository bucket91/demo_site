#!/usr/bin/env python3
import os, sys, json
from PyQt5 import QtWidgets, QtCore, QtGui

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SITE_DIR)

import advanced_theme
from advanced_theme import DEFAULT

NAME_MAP = {
    "shadows": "Shadows & Depth",
    "corners": "Rounded Corners",
    "backgrounds": "Background Effects",
    "hover_effects": "Hover Effects & Animations",
    "borders": "Borders & Dividers",
    "typography": "Typography",
    "layout": "Layout & Spacing",
    "custom_css": "Custom CSS",
}

STYLE = """
QWidget { font-size: 13px; }
QGroupBox {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 8px; margin-top: 12px; padding: 16px 12px 12px;
    font-weight: bold; color: #c9d1d9;
}
QGroupBox::title {
    subcontrol-origin: margin; subcontrol-position: top left;
    padding: 4px 10px; background: #161b22; border: 1px solid #30363d;
    border-radius: 4px; margin-left: 10px; color: #58a6ff;
}
QLabel { color: #c9d1d9; }
QLabel.dim { color: #6e7681; font-size: 12px; }
QComboBox, QSpinBox, QDoubleSpinBox {
    background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
    border-radius: 6px; padding: 6px 10px; min-height: 24px;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #0d1117; color: #c9d1d9; selection-background-color: #30363d;
    border: 1px solid #30363d;
}
QSlider::groove:horizontal {
    background: #30363d; height: 6px; border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #58a6ff; width: 16px; height: 16px;
    margin: -5px 0; border-radius: 8px;
}
QSlider::sub-page:horizontal { background: #58a6ff; border-radius: 3px; }
QCheckBox { color: #c9d1d9; spacing: 6px; }
QCheckBox::indicator {
    width: 16px; height: 16px; border-radius: 3px;
    border: 1px solid #30363d; background: #0d1117;
}
QCheckBox::indicator:checked { background: #58a6ff; border-color: #58a6ff; }
QPushButton {
    background: #21262d; color: #c9d1d9; border: none;
    border-radius: 6px; padding: 8px 16px;
}
QPushButton:hover { background: #30363d; }
QPushButton:disabled { background: #21262d; color: #484f58; }
QPushButton.primary { background: #58a6ff; color: #fff; font-weight: bold; }
QPushButton.primary:hover { background: #79c0ff; }
QPushButton.danger { background: #b71c1c; color: #fff; }
QPushButton.danger:hover { background: #d32f2f; }
QTextEdit, QPlainTextEdit {
    background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
    border-radius: 6px; padding: 6px; font-family: monospace;
}
QScrollArea { background: transparent; border: none; }
QScrollBar:vertical {
    background: #161b22; width: 8px; border: none;
}
QScrollBar::handle:vertical {
    background: #484f58; border-radius: 4px; min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


class CollapsibleSection(QtWidgets.QWidget):
    toggled = QtCore.pyqtSignal(bool)

    def __init__(self, title, expanded=True, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QtWidgets.QPushButton()
        self.header.setCursor(QtCore.Qt.PointingHandCursor)
        self.header.setStyleSheet("""
            QPushButton {
                background: #1c2128; color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; padding: 10px 14px; font-weight: bold;
                text-align: left; font-size: 14px;
            }
            QPushButton:hover { background: #21262d; }
        """)
        self._expanded = expanded
        self._title = title
        self._update_text()
        self.header.clicked.connect(self._toggle)
        layout.addWidget(self.header)

        self.content = QtWidgets.QWidget()
        self.content.setVisible(expanded)
        self.content.setStyleSheet("background: transparent;")
        self.content_layout = QtWidgets.QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(4, 8, 4, 4)
        self.content_layout.setSpacing(8)
        layout.addWidget(self.content)

    def _update_text(self):
        arrow = "\u25bc" if self._expanded else "\u25b6"
        self.header.setText(f"  {arrow}  {self._title}")

    def _toggle(self):
        self._expanded = not self._expanded
        self.content.setVisible(self._expanded)
        self._update_text()
        self.toggled.emit(self._expanded)

    def addWidget(self, widget):
        self.content_layout.addWidget(widget)

    def addLayout(self, layout):
        self.content_layout.addLayout(layout)

    def setExpanded(self, expanded):
        self._expanded = expanded
        self.content.setVisible(expanded)
        self._update_text()


class ColorButton(QtWidgets.QPushButton):
    changed = QtCore.pyqtSignal(str)

    def __init__(self, color="#000000", label="", parent=None):
        super().__init__(parent)
        self.setFixedSize(28, 28)
        self._color = color
        self._update_style()
        self.clicked.connect(self._pick)
        self.setToolTip(label or color)

    def _update_style(self):
        self.setStyleSheet(
            f"background: {self._color}; border: 1px solid #30363d; border-radius: 4px;"
        )

    def _pick(self):
        c = QtWidgets.QColorDialog.getColor(QtGui.QColor(self._color), self, "Pick color")
        if c.isValid():
            self._color = c.name()
            self._update_style()
            self.setToolTip(self._color)
            self.changed.emit(self._color)

    def color(self):
        return self._color

    def setColor(self, c):
        self._color = c
        self._update_style()
        self.setToolTip(c)


class AdvancedThemeTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(STYLE)
        self._data = advanced_theme.load()
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        heading = QtWidgets.QLabel("Advanced Theme Styling")
        heading.setStyleSheet("font-size: 16px; font-weight: bold; color: #c9d1d9;")
        layout.addWidget(heading)
        desc = QtWidgets.QLabel(
            "Extra visual polish on top of your base theme. "
            "Settings below generate a separate advanced.css file."
        )
        desc.setProperty("class", "dim")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Scroll area for sections
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_body = QtWidgets.QWidget()
        scroll_body.setStyleSheet("background: transparent;")
        self.sl = QtWidgets.QVBoxLayout(scroll_body)
        self.sl.setContentsMargins(0, 4, 0, 4)
        self.sl.setSpacing(2)

        # Build sections (expanded: first 4, collapsed: rest)
        expanded = ["shadows", "corners", "backgrounds", "hover_effects"]
        collapsed = ["borders", "typography", "layout", "custom_css"]
        self.sections = {}

        for key in expanded + collapsed:
            sec = CollapsibleSection(NAME_MAP[key], expanded=(key in expanded))
            self.sections[key] = sec
            self._build_section(key, sec)
            self.sl.addWidget(sec)

        self.sl.addStretch()
        scroll.setWidget(scroll_body)
        layout.addWidget(scroll, 1)

        # Buttons bar
        btn_bar = QtWidgets.QHBoxLayout()
        btn_bar.setSpacing(8)

        self.status = QtWidgets.QLabel("")
        self.status.setProperty("class", "dim")
        btn_bar.addWidget(self.status, 1)

        reset_btn = QtWidgets.QPushButton("Reset All")
        reset_btn.setProperty("class", "danger")
        reset_btn.clicked.connect(self._reset)
        btn_bar.addWidget(reset_btn)

        self.apply_btn = QtWidgets.QPushButton("Apply & Generate")
        self.apply_btn.setProperty("class", "primary")
        self.apply_btn.setMinimumHeight(38)
        self.apply_btn.clicked.connect(self._apply)
        btn_bar.addWidget(self.apply_btn)

        layout.addLayout(btn_bar)

    def _build_section(self, key, sec):
        builders = {
            "shadows": self._build_shadows,
            "corners": self._build_corners,
            "backgrounds": self._build_backgrounds,
            "hover_effects": self._build_hover_effects,
            "borders": self._build_borders,
            "typography": self._build_typography,
            "layout": self._build_layout,
            "custom_css": self._build_custom_css,
        }
        builders.get(key, lambda s: None)(sec)

    # --- Helpers ---
    def _add_checkbox(self, layout, label, key, subkey, default=True):
        cb = QtWidgets.QCheckBox(label)
        cb.setChecked(default)
        cb.toggled.connect(lambda v: self._set(subkey, key, v))
        layout.addWidget(cb)
        return cb

    def _add_slider(self, layout, label, key, subkey, minimum, maximum, default, suffix="", scale=1):
        row = QtWidgets.QHBoxLayout()
        lb = QtWidgets.QLabel(label)
        lb.setStyleSheet("color: #6e7681;")
        row.addWidget(lb)
        row.addStretch()
        sl = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        sl.setRange(minimum, maximum)
        sl.setValue(int(default * scale))
        sl.setFixedWidth(140)
        val = QtWidgets.QLabel(f"{default}{suffix}")
        val.setStyleSheet("color: #c9d1d9; min-width: 40px;")
        sl.valueChanged.connect(
            lambda v, lb=val, sf=suffix: lb.setText(f"{v}{sf}" if sf else f"{v}")
        )
        sl.valueChanged.connect(lambda v, sk=subkey, k=key: self._set(sk, k, v, scale))
        row.addWidget(sl)
        row.addWidget(val)
        layout.addLayout(row)
        return sl, val

    def _add_combo(self, layout, label, key, subkey, items):
        row = QtWidgets.QHBoxLayout()
        lb = QtWidgets.QLabel(label)
        lb.setStyleSheet("color: #6e7681;")
        row.addWidget(lb)
        row.addStretch()
        cb = QtWidgets.QComboBox()
        for val, text in items:
            cb.addItem(text, val)
        cb.currentIndexChanged.connect(
            lambda i, sk=subkey, k=key: self._set(sk, k, cb.itemData(i))
        )
        row.addWidget(cb)
        layout.addLayout(row)
        return cb

    def _add_color(self, layout, label, key, subkey, default):
        row = QtWidgets.QHBoxLayout()
        lb = QtWidgets.QLabel(label)
        lb.setStyleSheet("color: #6e7681;")
        row.addWidget(lb)
        row.addStretch()
        btn = ColorButton(default, label)
        btn.changed.connect(lambda c, sk=subkey, k=key: self._set(sk, k, c))
        row.addWidget(btn)
        layout.addLayout(row)
        return btn

    def _set(self, subkey, key, value, scale=1):
        if scale != 1:
            value = int(value / scale)
        if key not in self._data:
            self._data[key] = {}
        if isinstance(value, float) and value == int(value):
            value = int(value)
        # For checkboxes, value is bool
        self._data[key][subkey] = value

    def _load_data(self):
        pass  # Widgets load from their own defaults when used

    # --- Section Builders ---
    def _build_shadows(self, sec):
        d = self._data.get("shadows", {})
        self._add_checkbox(sec.content_layout, "Enable shadows", "shadows", "enabled", d.get("enabled", False))
        self._add_combo(sec.content_layout, "Shadow preset", "shadows", "preset",
                        [("none", "None"), ("subtle", "Subtle"), ("medium", "Medium"), ("deep", "Deep")])
        self._add_color(sec.content_layout, "Shadow color", "shadows", "color", d.get("color", "#000000"))
        self._add_slider(sec.content_layout, "Light opacity %", "shadows", "opacity_light", 0, 100, d.get("opacity_light", 10), "%")
        self._add_slider(sec.content_layout, "Dark opacity %", "shadows", "opacity_dark", 0, 100, d.get("opacity_dark", 45), "%")

        apply_label = QtWidgets.QLabel("Apply to:")
        apply_label.setStyleSheet("color: #6e7681; margin-top: 4px;")
        sec.content_layout.addWidget(apply_label)
        apply_row = QtWidgets.QHBoxLayout()
        for lbl, sk in [("Cards", "apply_cards"), ("Header", "apply_header"), ("Sidebar", "apply_sidebar"),
                         ("Images", "apply_images"), ("Headings", "apply_headings")]:
            cb = QtWidgets.QCheckBox(lbl)
            cb.setChecked(d.get(sk, True))
            cb.toggled.connect(lambda v, k=sk: self._set(k, "shadows", v))
            apply_row.addWidget(cb)
        apply_row.addStretch()
        sec.content_layout.addLayout(apply_row)

        self._add_slider(sec.content_layout, "Hover lift (px)", "shadows", "hover_lift", 0, 20, d.get("hover_lift", 6), "px")
        self._add_slider(sec.content_layout, "Transition (ms)", "shadows", "transition_speed", 0, 1000, d.get("transition_speed", 300), "ms")

    def _build_corners(self, sec):
        d = self._data.get("corners", {})
        self._add_checkbox(sec.content_layout, "Enable rounded corners", "corners", "enabled", d.get("enabled", False))
        for lbl, sk in [("Card radius", "card"), ("Button radius", "button"), ("Input radius", "input"),
                         ("Image radius", "image"), ("Avatar radius", "avatar"),
                         ("Header radius", "header"), ("Sidebar radius", "sidebar")]:
            self._add_slider(sec.content_layout, lbl, "corners", sk, 0, 50, d.get(sk, 0), "px")

    def _build_backgrounds(self, sec):
        d = self._data.get("backgrounds", {})
        self._add_checkbox(sec.content_layout, "Enable background effects", "backgrounds", "enabled", d.get("enabled", False))
        self._add_combo(sec.content_layout, "Background type", "backgrounds", "type",
                        [("solid", "Solid"), ("gradient", "Gradient"), ("pattern", "Pattern")])

        # Light gradient colors
        light_label = QtWidgets.QLabel("Light mode colors:")
        light_label.setStyleSheet("color: #8b949e; font-size: 12px; margin-top: 4px;")
        sec.content_layout.addWidget(light_label)
        lr = QtWidgets.QHBoxLayout()
        light_btns = []
        lc = d.get("light_colors", ["#e8ecf0", "#dce0e8"])
        for i in range(4):
            col = lc[i] if i < len(lc) else "#ffffff"
            btn = ColorButton(col, f"Color {i+1}")
            btn.idx = i
            btn.changed.connect(lambda c, idx=i: self._update_gradient_color("light_colors", idx, c))
            lr.addWidget(btn)
            light_btns.append(btn)
        lr.addStretch()
        sec.content_layout.addLayout(lr)

        # Dark gradient colors
        dark_label = QtWidgets.QLabel("Dark mode colors:")
        dark_label.setStyleSheet("color: #8b949e; font-size: 12px; margin-top: 4px;")
        sec.content_layout.addWidget(dark_label)
        dr = QtWidgets.QHBoxLayout()
        dc = d.get("dark_colors", ["#161b22", "#0d1117"])
        for i in range(4):
            col = dc[i] if i < len(dc) else "#000000"
            btn = ColorButton(col, f"Color {i+1}")
            btn.idx = i
            btn.changed.connect(lambda c, idx=i: self._update_gradient_color("dark_colors", idx, c))
            dr.addWidget(btn)
        dr.addStretch()
        sec.content_layout.addLayout(dr)

        self._add_combo(sec.content_layout, "Direction", "backgrounds", "direction",
                        [("to bottom", "Top to Bottom"), ("to right", "Left to Right"),
                         ("to bottom right", "Diagonal"), ("135deg", "Angle")])
        self._add_combo(sec.content_layout, "Animation speed", "backgrounds", "animation",
                        [("none", "Off"), ("slow", "Slow"), ("normal", "Normal"), ("fast", "Fast")])
        self._add_combo(sec.content_layout, "Pattern overlay", "backgrounds", "pattern",
                        [("none", "None"), ("dots", "Dots"), ("grid", "Grid"),
                         ("stripes", "Stripes"), ("diagonal", "Diagonal lines")])
        self._add_slider(sec.content_layout, "Pattern opacity %", "backgrounds", "pattern_opacity", 0, 100, d.get("pattern_opacity", 15), "%")
        self._add_color(sec.content_layout, "Pattern color", "backgrounds", "pattern_color", d.get("pattern_color", "#000000"))

        # Background image upload
        img_row = QtWidgets.QHBoxLayout()
        img_label = QtWidgets.QLabel("Background image:")
        img_label.setStyleSheet("color: #6e7681;")
        img_row.addWidget(img_label)
        self.bg_image_path = QtWidgets.QLineEdit()
        self.bg_image_path.setPlaceholderText("Optional image file...")
        self.bg_image_path.textChanged.connect(lambda t: self._set("bg_image", "backgrounds", t))
        img_row.addWidget(self.bg_image_path, 1)
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_bg_image)
        img_row.addWidget(browse_btn)
        sec.content_layout.addLayout(img_row)
        self._add_combo(sec.content_layout, "Image size", "backgrounds", "bg_size",
                        [("cover", "Cover"), ("contain", "Contain"), ("auto", "Auto")])

    def _build_hover_effects(self, sec):
        d = self._data.get("hover_effects", {})
        self._add_checkbox(sec.content_layout, "Enable hover effects", "hover_effects", "enabled", d.get("enabled", False))
        self._add_combo(sec.content_layout, "Page load animation", "hover_effects", "page_load",
                        [("none", "None"), ("fade", "Fade In"), ("slide", "Slide Up"), ("scale", "Scale In")])
        self._add_combo(sec.content_layout, "Card hover effect", "hover_effects", "card_hover",
                        [("none", "None"), ("lift", "Lift"), ("glow", "Glow"), ("border", "Border"), ("scale", "Scale")])
        self._add_combo(sec.content_layout, "Button hover effect", "hover_effects", "button_hover",
                        [("none", "None"), ("darken", "Darken"), ("lift", "Lift"), ("fill", "Fill"), ("glow", "Glow")])
        self._add_combo(sec.content_layout, "Link hover effect", "hover_effects", "link_hover",
                        [("none", "None"), ("underline", "Underline"), ("color", "Color shift"), ("animated", "Animated underline")])
        self._add_combo(sec.content_layout, "Image hover effect", "hover_effects", "image_hover",
                        [("none", "None"), ("zoom", "Zoom"), ("overlay", "Brighten"), ("grayscale", "Grayscale")])

        extra_row = QtWidgets.QHBoxLayout()
        sc = QtWidgets.QCheckBox("Smooth scrolling")
        sc.setChecked(d.get("smooth_scroll", True))
        sc.toggled.connect(lambda v: self._set("smooth_scroll", "hover_effects", v))
        extra_row.addWidget(sc)
        sr = QtWidgets.QCheckBox("Scroll reveal")
        sr.setChecked(d.get("scroll_reveal", False))
        sr.toggled.connect(lambda v: self._set("scroll_reveal", "hover_effects", v))
        extra_row.addWidget(sr)
        extra_row.addStretch()
        sec.content_layout.addLayout(extra_row)

    def _build_borders(self, sec):
        d = self._data.get("borders", {})
        self._add_checkbox(sec.content_layout, "Enable custom borders", "borders", "enabled", d.get("enabled", False))
        self._add_slider(sec.content_layout, "Card border width", "borders", "card_width", 0, 5, d.get("card_width", 1), "px")
        self._add_combo(sec.content_layout, "Card border style", "borders", "card_style",
                        [("solid", "Solid"), ("dashed", "Dashed"), ("dotted", "Dotted")])
        self._add_combo(sec.content_layout, "Card border color", "borders", "card_color_mode",
                        [("theme", "Use theme color"), ("custom", "Custom color")])
        self._add_color(sec.content_layout, "Custom border color", "borders", "card_custom_color", d.get("card_custom_color", "#cccccc"))
        self._add_slider(sec.content_layout, "Input border width", "borders", "input_width", 0, 5, d.get("input_width", 1), "px")
        self._add_combo(sec.content_layout, "Separator style", "borders", "separator_style",
                        [("none", "None"), ("solid", "Solid"), ("dashed", "Dashed"), ("gradient", "Gradient")])
        self._add_slider(sec.content_layout, "Separator thickness", "borders", "separator_width", 1, 5, d.get("separator_width", 1), "px")

    def _build_typography(self, sec):
        d = self._data.get("typography", {})
        self._add_checkbox(sec.content_layout, "Enable typography tweaks", "typography", "enabled", d.get("enabled", False))
        self._add_slider(sec.content_layout, "Heading letter-spacing", "typography", "heading_letter_spacing", -2, 10, d.get("heading_letter_spacing", 0), "px")
        self._add_slider(sec.content_layout, "Body letter-spacing", "typography", "body_letter_spacing", -1, 5, d.get("body_letter_spacing", 0), "px")
        self._add_slider(sec.content_layout, "Body line-height", "typography", "body_line_height", 100, 250, int(d.get("body_line_height", 1.7) * 100), scale=100)
        s = self._add_slider(sec.content_layout, "Heading line-height", "typography", "heading_line_height", 80, 200, int(d.get("heading_line_height", 1.3) * 100), scale=100)
        self._add_combo(sec.content_layout, "Link style", "typography", "link_style",
                        [("colored", "Colored"), ("underline", "Underline"), ("animated", "Animated underline")])
        self._add_combo(sec.content_layout, "Blockquote style", "typography", "blockquote_style",
                        [("border", "Border"), ("icon", "Large quote icon"), ("background", "Background card"), ("stylized", "Stylized")])
        self._add_color(sec.content_layout, "Selection color", "typography", "selection_color", d.get("selection_color", "#3399ff"))
        self._add_slider(sec.content_layout, "Base font size", "typography", "base_font_size", 10, 24, d.get("base_font_size", 16), "px")
        self._add_slider(sec.content_layout, "h1 size multiplier", "typography", "h1_size", 100, 400, int(d.get("h1_size", 2.0) * 100), scale=100)
        self._add_slider(sec.content_layout, "h2 size multiplier", "typography", "h2_size", 100, 300, int(d.get("h2_size", 1.5) * 100), scale=100)
        self._add_slider(sec.content_layout, "h3 size multiplier", "typography", "h3_size", 100, 250, int(d.get("h3_size", 1.25) * 100), scale=100)

    def _build_layout(self, sec):
        d = self._data.get("layout", {})
        self._add_checkbox(sec.content_layout, "Enable layout tweaks", "layout", "enabled", d.get("enabled", False))
        self._add_slider(sec.content_layout, "Page max-width", "layout", "page_max_width", 600, 1400, d.get("page_max_width", 1100), "px")
        self._add_slider(sec.content_layout, "Sidebar width", "layout", "sidebar_width", 180, 350, d.get("sidebar_width", 250), "px")
        self._add_slider(sec.content_layout, "Content padding", "layout", "content_padding", 0, 60, d.get("content_padding", 20), "px")
        self._add_combo(sec.content_layout, "Header position", "layout", "header_position",
                        [("static", "Static"), ("sticky", "Sticky"), ("fixed", "Fixed")])

    def _build_custom_css(self, sec):
        self.custom_css_edit = QtWidgets.QPlainTextEdit()
        self.custom_css_edit.setPlaceholderText("/* Write custom CSS here */\n/* It gets appended to advanced.css */")
        self.custom_css_edit.setMinimumHeight(120)
        d = self._data.get("custom_css", "")
        self.custom_css_edit.setPlainText(d)
        self.custom_css_edit.textChanged.connect(self._on_custom_css_changed)
        sec.addWidget(self.custom_css_edit)

    def _on_custom_css_changed(self):
        self._data["custom_css"] = self.custom_css_edit.toPlainText()

    def _update_gradient_color(self, key, idx, color):
        if key not in self._data.get("backgrounds", {}):
            self._data.setdefault("backgrounds", {}).setdefault(key, [])
        cols = list(self._data["backgrounds"].get(key, []))
        while len(cols) <= idx:
            cols.append("#ffffff")
        cols[idx] = color
        self._data["backgrounds"][key] = cols

    def _browse_bg_image(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Background Image", "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp *.svg)")
        if p:
            import shutil
            dst_dir = os.path.join(SITE_DIR, "images")
            os.makedirs(dst_dir, exist_ok=True)
            dst = os.path.join(dst_dir, os.path.basename(p))
            try:
                shutil.copy2(p, dst)
                rel = os.path.relpath(dst, SITE_DIR).replace("\\", "/")
                self.bg_image_path.setText(rel)
            except Exception as e:
                self.status.setText(f"Error copying image: {e}")

    def _gather_data(self):
        return dict(self._data)

    def _apply(self):
        self.status.setText("Applying & generating...")
        QtWidgets.QApplication.processEvents()

        data = self._gather_data()
        advanced_theme.save(data)

        ok = advanced_theme.regenerate(data)
        if not ok:
            self.status.setText("Error writing advanced.css")
            return

        import generate
        generate.SITE_DIR = SITE_DIR
        generate.CONFIG.update(generate.load_config())
        try:
            generate.generate_all()
            self.status.setText("Applied. advanced.css generated, all pages rebuilt.")
        except Exception as e:
            self.status.setText(f"Generate error: {e}")

    def _reset(self):
        reply = QtWidgets.QMessageBox.question(
            self, "Reset", "Reset all advanced styling to defaults?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply != QtWidgets.QMessageBox.Yes:
            return
        self._data = dict(DEFAULT)
        advanced_theme.save(self._data)
        # Reload tab
        self._rebuild_ui()

    def _rebuild_ui(self):
        # Clear and rebuild
        for i in reversed(range(self.layout().count())):
            w = self.layout().itemAt(i).widget()
            if w:
                w.deleteLater()
        self._build_ui()
        self._load_data()


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QMainWindow()
    w.setStyleSheet("QMainWindow { background: #0d1117; }")
    w.setCentralWidget(AdvancedThemeTab())
    w.resize(600, 800)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
