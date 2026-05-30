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
    background: #0d1117; color: #c9d1d9; selection-background-color: #58a6ff;
    border: 1px solid #30363d; outline: none; font-size: 13px;
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

        # === AVIF Optimization ===
        avif_group = QtWidgets.QGroupBox("AVIF Image Optimization")
        avif_layout = QtWidgets.QVBoxLayout(avif_group)
        avif_data = self._data.get("avif", {"enabled": False, "quality": 30})

        self.avif_cb = QtWidgets.QCheckBox("Enable AVIF format for images (~30% smaller than WebP)")
        self.avif_cb.setChecked(avif_data.get("enabled", False))
        self.avif_cb.toggled.connect(lambda v: self._set("enabled", "avif", v))
        avif_layout.addWidget(self.avif_cb)

        warn = QtWidgets.QLabel("\u26a0 AVIF conversion is slow (5\u201310 seconds per image). "
                                "Existing images are converted on next site generation.")
        warn.setWordWrap(True)
        warn.setStyleSheet("color: #f0c040; font-size: 12px; padding: 4px 8px; "
                           "background: #1c2128; border-radius: 4px;")
        avif_layout.addWidget(warn)

        quality_row = QtWidgets.QHBoxLayout()
        ql = QtWidgets.QLabel("Quality (lower = smaller file, slower encode):")
        ql.setStyleSheet("color: #6e7681;")
        quality_row.addWidget(ql)
        quality_row.addStretch()
        self.avif_quality = QtWidgets.QSpinBox()
        self.avif_quality.setRange(20, 50)
        self.avif_quality.setValue(avif_data.get("quality", 30))
        self.avif_quality.setSuffix(" CRF")
        self.avif_quality.setStyleSheet("background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; padding: 4px 8px;")
        self.avif_quality.valueChanged.connect(lambda v: self._set("quality", "avif", v))
        quality_row.addWidget(self.avif_quality)
        avif_layout.addLayout(quality_row)

        self.sl.addWidget(avif_group)
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
        cb.setView(QtWidgets.QListView())
        saved = self._data.get(key, {}).get(subkey)
        for val, text in items:
            cb.addItem(text, val)
            if saved is not None and str(val) == str(saved):
                cb.setCurrentIndex(cb.count() - 1)
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
        cl = sec.content_layout
        self._add_checkbox(cl, "Enable background effects", "backgrounds", "enabled", d.get("enabled", False))

        # === Background type ===
        self.bg_type_combo = self._add_combo(cl, "Background type", "backgrounds", "type",
            [("solid", "Solid"), ("gradient", "Gradient"), ("pattern", "Pattern"), ("image", "Image"), ("video", "Video")])

        # === Base Colors (all except Image) ===
        self.colors_group = QtWidgets.QGroupBox("Base Colors")
        cg = QtWidgets.QVBoxLayout(self.colors_group)
        lc = d.get("light_colors", ["#e8ecf0", "#dce0e8"])
        dc = d.get("dark_colors", ["#161b22", "#0d1117"])
        for label, key, defs in [("Light mode colors:", "light_colors", lc),
                                   ("Dark mode colors:", "dark_colors", dc)]:
            lb = QtWidgets.QLabel(label)
            lb.setStyleSheet("color: #8b949e; font-size: 12px;")
            cg.addWidget(lb)
            row = QtWidgets.QHBoxLayout()
            for i in range(4):
                col = defs[i] if i < len(defs) else ("#ffffff" if "Light" in label else "#000000")
                btn = ColorButton(col, f"Color {i+1}")
                btn.changed.connect(lambda c, idx=i, k=key: self._update_gradient_color(k, idx, c))
                row.addWidget(btn)
            row.addStretch()
            cg.addLayout(row)
        cl.addWidget(self.colors_group)

        # === Solid ===
        self.solid_group = QtWidgets.QGroupBox("Solid Settings")
        sg = QtWidgets.QVBoxLayout(self.solid_group)
        note = QtWidgets.QLabel("Uses first Base Color for each mode. Try the Animation section for Pulse / Breathe / Shimmer effects.")
        note.setStyleSheet("color: #8b949e; font-size: 12px;")
        note.setWordWrap(True)
        sg.addWidget(note)
        cl.addWidget(self.solid_group)

        # === Gradient ===
        self.gradient_group = QtWidgets.QGroupBox("Gradient Settings")
        gg = QtWidgets.QVBoxLayout(self.gradient_group)
        self._add_combo(gg, "Gradient type", "backgrounds", "gradient_subtype",
                        [("linear", "Linear"), ("radial", "Radial"), ("conic", "Conic")])
        self.grad_dir = self._add_combo(gg, "Direction", "backgrounds", "direction", [
            ("to bottom", "Top to Bottom"), ("to top", "Bottom to Top"),
            ("to right", "Left to Right"), ("to left", "Right to Left"),
            ("to bottom right", "Diagonal \u2198"), ("to bottom left", "Diagonal \u2199"),
            ("to top right", "Diagonal \u2197"), ("to top left", "Diagonal \u2196"),
        ])
        self._add_slider(gg, "Angle (deg)", "backgrounds", "gradient_angle", 0, 360, d.get("gradient_angle", 180), "\u00b0")
        self._add_combo(gg, "Radial shape", "backgrounds", "radial_shape",
                        [("ellipse", "Ellipse"), ("circle", "Circle")])
        self._add_combo(gg, "Radial position", "backgrounds", "radial_position", [
            ("center", "Center"), ("top left", "Top Left"), ("top right", "Top Right"),
            ("bottom left", "Bottom Left"), ("bottom right", "Bottom Right"),
        ])
        self._add_combo(gg, "Conic position", "backgrounds", "conic_position", [
            ("center", "Center"), ("top left", "Top Left"), ("top right", "Top Right"),
            ("bottom left", "Bottom Left"), ("bottom right", "Bottom Right"),
        ])
        self._add_checkbox(gg, "Repeat gradient", "backgrounds", "gradient_repeat", d.get("gradient_repeat", False))
        cl.addWidget(self.gradient_group)

        # === Pattern ===
        self.pattern_group = QtWidgets.QGroupBox("Pattern Settings")
        pg = QtWidgets.QVBoxLayout(self.pattern_group)
        self._add_combo(pg, "Pattern style", "backgrounds", "pattern", [
            ("none", "None"), ("dots", "Dots"), ("dots_large", "Large Dots"),
            ("grid", "Grid"), ("stripes", "Stripes 45\u00b0"),
            ("stripes_h", "Horizontal Stripes"), ("stripes_v", "Vertical Stripes"),
            ("diagonal", "Diagonal Lines"), ("crosshatch", "Crosshatch"),
            ("zigzag", "Zigzag"), ("waves", "Waves"),
            ("chevron", "Chevron"), ("honeycomb", "Honeycomb"), ("polka", "Polka Dots"),
        ])
        self._add_color(pg, "Pattern color", "backgrounds", "pattern_color", d.get("pattern_color", "#000000"))
        self._add_slider(pg, "Opacity %", "backgrounds", "pattern_opacity", 0, 100, d.get("pattern_opacity", 15), "%")
        self._add_slider(pg, "Size (px)", "backgrounds", "pattern_size", 5, 60, d.get("pattern_size", 20), "px")
        cl.addWidget(self.pattern_group)

        # === Image ===
        self.image_group = QtWidgets.QGroupBox("Image Settings")
        ig = QtWidgets.QVBoxLayout(self.image_group)

        img_row = QtWidgets.QHBoxLayout()
        img_label = QtWidgets.QLabel("Image:")
        img_label.setStyleSheet("color: #6e7681;")
        img_row.addWidget(img_label)
        self.bg_image_path = QtWidgets.QLineEdit()
        self.bg_image_path.setPlaceholderText("Select background image...")
        self.bg_image_path.textChanged.connect(lambda t: self._set("bg_image", "backgrounds", t))
        img_row.addWidget(self.bg_image_path, 1)
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_bg_image)
        img_row.addWidget(browse_btn)
        ig.addLayout(img_row)

        self._add_combo(ig, "Size", "backgrounds", "bg_size",
                        [("cover", "Cover"), ("contain", "Contain"), ("auto", "Auto"), ("100%", "100%")])
        self._add_combo(ig, "Position", "backgrounds", "bg_position", [
            ("center", "Center"), ("top", "Top"), ("bottom", "Bottom"),
            ("left", "Left"), ("right", "Right"),
            ("top left", "Top Left"), ("top right", "Top Right"),
            ("bottom left", "Bottom Left"), ("bottom right", "Bottom Right"),
        ])
        self._add_combo(ig, "Repeat", "backgrounds", "bg_repeat",
                        [("no-repeat", "No Repeat"), ("repeat", "Repeat"),
                         ("repeat-x", "Repeat X"), ("repeat-y", "Repeat Y"),
                         ("space", "Space"), ("round", "Round")])
        self._add_combo(ig, "Attachment", "backgrounds", "bg_attachment",
                        [("scroll", "Scroll"), ("fixed", "Fixed"), ("local", "Local")])

        sep1 = QtWidgets.QLabel()
        sep1.setFixedHeight(6)
        ig.addWidget(sep1)
        filter_lb = QtWidgets.QLabel("Filter effect")
        filter_lb.setStyleSheet("color: #8b949e; font-size: 12px;")
        ig.addWidget(filter_lb)
        self._add_combo(ig, "Type", "backgrounds", "image_filter",
                        [("none", "None"), ("grayscale", "Grayscale"), ("sepia", "Sepia"),
                         ("blur", "Blur"), ("brightness", "Brightness"),
                         ("contrast", "Contrast"), ("hue_rotate", "Hue Rotate")])
        self._add_slider(ig, "Amount", "backgrounds", "image_filter_value", 0, 100, d.get("image_filter_value", 50), "")

        sep2 = QtWidgets.QLabel()
        sep2.setFixedHeight(6)
        ig.addWidget(sep2)
        ov_lb = QtWidgets.QLabel("Overlay")
        ov_lb.setStyleSheet("color: #8b949e; font-size: 12px;")
        ig.addWidget(ov_lb)
        self._add_combo(ig, "Type", "backgrounds", "image_overlay",
                        [("none", "None"), ("color", "Solid Color"), ("gradient", "Gradient")])
        self._add_color(ig, "Overlay color", "backgrounds", "image_overlay_color", d.get("image_overlay_color", "#000000"))
        self._add_slider(ig, "Overlay opacity %", "backgrounds", "image_overlay_opacity", 0, 100, d.get("image_overlay_opacity", 30), "%")
        cl.addWidget(self.image_group)

        # === Video ===
        self.video_group = QtWidgets.QGroupBox("Video Settings")
        vg = QtWidgets.QVBoxLayout(self.video_group)

        vid_row = QtWidgets.QHBoxLayout()
        vid_label = QtWidgets.QLabel("Video:")
        vid_label.setStyleSheet("color: #6e7681;")
        vid_row.addWidget(vid_label)
        self.bg_video_path = QtWidgets.QLineEdit()
        self.bg_video_path.setPlaceholderText("Select video file...")
        self.bg_video_path.setText(d.get("bg_video", ""))
        self.bg_video_path.textChanged.connect(lambda t: self._set("bg_video", "backgrounds", t))
        vid_row.addWidget(self.bg_video_path, 1)
        browse_vid_btn = QtWidgets.QPushButton("Browse & Convert")
        browse_vid_btn.clicked.connect(self._browse_bg_video)
        vid_row.addWidget(browse_vid_btn)
        vg.addLayout(vid_row)

        self.video_size_label = QtWidgets.QLabel("")
        self.video_size_label.setStyleSheet("color: #8b949e; font-size: 12px;")
        existing_vid = d.get("bg_video", "")
        if existing_vid:
            vid_full = os.path.join(SITE_DIR, existing_vid)
            if os.path.exists(vid_full):
                size_kb = os.path.getsize(vid_full) / 1024
                size_str = f"{size_kb:.0f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
                self.video_size_label.setText(f"WebM size: {size_str}")
        vg.addWidget(self.video_size_label)

        fallback_row = QtWidgets.QHBoxLayout()
        fb_label = QtWidgets.QLabel("Fallback image:")
        fb_label.setStyleSheet("color: #6e7681;")
        fallback_row.addWidget(fb_label)
        self.video_fallback_path = QtWidgets.QLineEdit()
        self.video_fallback_path.setPlaceholderText("Optional fallback image...")
        self.video_fallback_path.setText(d.get("video_fallback", ""))
        self.video_fallback_path.textChanged.connect(lambda t: self._set("video_fallback", "backgrounds", t))
        fallback_row.addWidget(self.video_fallback_path, 1)
        fb_browse_btn = QtWidgets.QPushButton("Browse")
        fb_browse_btn.clicked.connect(self._browse_video_fallback)
        fallback_row.addWidget(fb_browse_btn)
        vg.addLayout(fallback_row)

        self._add_slider(vg, "Opacity %", "backgrounds", "video_opacity", 10, 100, d.get("video_opacity", 100), "%")

        sep_v1 = QtWidgets.QLabel()
        sep_v1.setFixedHeight(6)
        vg.addWidget(sep_v1)
        ov_lb_v = QtWidgets.QLabel("Overlay")
        ov_lb_v.setStyleSheet("color: #8b949e; font-size: 12px;")
        vg.addWidget(ov_lb_v)
        self._add_combo(vg, "Type", "backgrounds", "video_overlay",
                        [("none", "None"), ("color", "Solid Color"), ("gradient", "Gradient")])
        self._add_color(vg, "Overlay color", "backgrounds", "video_overlay_color", d.get("video_overlay_color", "#000000"))
        self._add_slider(vg, "Overlay opacity %", "backgrounds", "video_overlay_opacity", 0, 100, d.get("video_overlay_opacity", 30), "%")
        cl.addWidget(self.video_group)

        # === Animation ===
        self.anim_group = QtWidgets.QGroupBox("Animation")
        ag = QtWidgets.QVBoxLayout(self.anim_group)
        anim_row = QtWidgets.QHBoxLayout()
        anim_lb = QtWidgets.QLabel("Type")
        anim_lb.setStyleSheet("color: #6e7681;")
        anim_row.addWidget(anim_lb)
        anim_row.addStretch()
        self.anim_combo = QtWidgets.QComboBox()
        self.anim_combo.setView(QtWidgets.QListView())
        self.anim_combo.currentIndexChanged.connect(self._on_anim_changed)
        anim_row.addWidget(self.anim_combo)
        ag.addLayout(anim_row)
        self._add_slider(ag, "Speed (seconds)", "backgrounds", "animation_speed", 1, 20, d.get("animation_speed", 4), "s")
        self._add_combo(ag, "Easing", "backgrounds", "animation_easing",
                        [("ease", "Ease"), ("linear", "Linear"), ("ease-in", "Ease In"),
                         ("ease-out", "Ease Out"), ("ease-in-out", "Ease In Out")])
        cl.addWidget(self.anim_group)

        # === Advanced ===
        self.adv_bg_group = QtWidgets.QGroupBox("Advanced")
        advl = QtWidgets.QVBoxLayout(self.adv_bg_group)
        self._add_combo(advl, "Blend mode", "backgrounds", "blend_mode",
                        [("normal", "Normal"), ("multiply", "Multiply"), ("screen", "Screen"),
                         ("overlay", "Overlay"), ("darken", "Darken"), ("lighten", "Lighten"),
                         ("color-dodge", "Color Dodge"), ("saturation", "Saturation"),
                         ("color", "Color"), ("luminosity", "Luminosity")])
        self._add_slider(advl, "Overall opacity %", "backgrounds", "bg_opacity", 10, 100, d.get("bg_opacity", 100), "%")
        cl.addWidget(self.adv_bg_group)

        # Connect type combo to show/hide sections
        self.bg_type_combo.currentIndexChanged.connect(self._on_bg_type_changed)
        self._populate_anim_options()
        self._on_bg_type_changed()

    def _on_bg_type_changed(self):
        bg_type = self.bg_type_combo.currentData() if self.bg_type_combo.count() > 0 else "solid"
        self.colors_group.setVisible(bg_type not in ("image", "video"))
        self.solid_group.setVisible(bg_type == "solid")
        self.gradient_group.setVisible(bg_type == "gradient")
        self.pattern_group.setVisible(bg_type == "pattern")
        self.image_group.setVisible(bg_type == "image")
        self.video_group.setVisible(bg_type == "video")
        self._populate_anim_options()

    def _populate_anim_options(self):
        bg_type = self.bg_type_combo.currentData() if self.bg_type_combo.count() > 0 else "solid"
        current_anim = self._data.get("backgrounds", {}).get("animation", "none")
        type_opts = {
            "solid": [("none", "Off"), ("pulse", "Pulse"), ("breathe", "Breathe"), ("shimmer", "Shimmer")],
            "gradient": [("none", "Off"), ("flow", "Flowing Movement"), ("pulse", "Pulse"), ("hue_rotate", "Hue Rotation")],
            "pattern": [("none", "Off"), ("scroll", "Scroll Pattern"), ("pulse", "Pulse"), ("flow", "Flowing Movement")],
            "image": [("none", "Off"), ("ken_burns", "Ken Burns Zoom"), ("slow_zoom", "Slow Zoom"), ("slow_pan", "Slow Pan"), ("pulse", "Pulse"), ("hue_rotate", "Hue Rotation")],
            "video": [("none", "Off"), ("pulse", "Pulse"), ("hue_rotate", "Hue Rotation")],
        }
        opts = type_opts.get(bg_type, [("none", "Off")])
        self.anim_combo.blockSignals(True)
        self.anim_combo.clear()
        for val, text in opts:
            self.anim_combo.addItem(text, val)
        idx = self.anim_combo.findData(current_anim)
        if idx >= 0:
            self.anim_combo.setCurrentIndex(idx)
        else:
            self.anim_combo.setCurrentIndex(0)
            self._data.setdefault("backgrounds", {})["animation"] = self.anim_combo.itemData(0)
        self.anim_combo.blockSignals(False)

    def _on_anim_changed(self, idx):
        val = self.anim_combo.itemData(idx)
        self._data.setdefault("backgrounds", {})["animation"] = val

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

    def _browse_bg_video(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Video File", "",
            "Videos (*.mp4 *.webm *.mov *.avi *.mkv *.ogv *.m4v)")
        if not p:
            return
        import shutil
        vid_dir = os.path.join(SITE_DIR, "videos")
        os.makedirs(vid_dir, exist_ok=True)
        # Copy original
        basename = os.path.basename(p)
        dst = os.path.join(vid_dir, basename)
        try:
            shutil.copy2(p, dst)
        except Exception as e:
            self.status.setText(f"Error copying video: {e}")
            return
        # Convert to WebM
        self.status.setText("Converting to WebM (no audio)...")
        QtWidgets.QApplication.processEvents()
        ok, result = advanced_theme.convert_to_webm(dst, vid_dir)
        if ok:
            rel = os.path.relpath(result, SITE_DIR).replace("\\", "/")
            self.bg_video_path.setText(rel)
            size_kb = os.path.getsize(result) / 1024
            size_str = f"{size_kb:.0f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
            self.video_size_label.setText(f"WebM size: {size_str}")
            self.status.setText("Video converted to WebM successfully.")
        else:
            self.status.setText(f"Conversion failed: {result}")

    def _browse_video_fallback(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Fallback Image", "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp *.svg)")
        if p:
            import shutil
            dst_dir = os.path.join(SITE_DIR, "images")
            os.makedirs(dst_dir, exist_ok=True)
            dst = os.path.join(dst_dir, os.path.basename(p))
            try:
                shutil.copy2(p, dst)
                rel = os.path.relpath(dst, SITE_DIR).replace("\\", "/")
                self.video_fallback_path.setText(rel)
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
