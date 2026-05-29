"""Map website theme colors to a PyQt5 GUI stylesheet."""
import os, json

SITE_DIR = None


def _cfg():
    if SITE_DIR:
        cf = os.path.join(SITE_DIR, "config.json")
        if os.path.exists(cf):
            with open(cf, encoding="utf-8") as f:
                return json.load(f)
    return {}


CSS_EXTRA = """
QComboBox::drop-down { border: none; width: 30px; }
QComboBox::down-arrow { image: none; border-left: 6px solid #999; border-top: 5px solid transparent; border-bottom: 5px solid transparent; }
QComboBox QAbstractItemView { selection-background-color: $accent; border: 1px solid $input_border; outline: none; }
QScrollBar:vertical { background: $sidebar_bg; width: 10px; }
QScrollBar::handle:vertical { background: $muted; border-radius: 5px; }
QScrollBar:horizontal { background: $sidebar_bg; height: 10px; }
QScrollBar::handle:horizontal { background: $muted; border-radius: 5px; }
QGroupBox { color: $text; font-size: 13px; font-weight: bold; border: 1px solid $input_border; border-radius: 6px; margin-top: 12px; padding: 12px 8px 8px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
QDialog { background: $bg; }
QLabel.heading { font-size: 14px; font-weight: bold; }
QLabel.dim { color: $muted; font-size: 11px; }
QPushButton.primary { background: $accent; }
QPushButton.primary:hover { background: $accent_hover; }
QPushButton.danger { background: #b71c1c; }
QPushButton.danger:hover { background: #d32f2f; }
"""


def make_gui_stylesheet(colors):
    """Build a QSS stylesheet string from a dict of web theme colors."""
    c = colors or {}
    def v(k, fallback="#eee"):
        return c.get(k, fallback)

    qss = f"""
QMainWindow {{ background: {v("dark_body_bg", v("body_bg", "#1e1e1e"))}; }}
QTabWidget::pane {{ background: {v("dark_body_bg", v("body_bg", "#1e1e1e"))}; border: none; }}
QTabBar::tab {{
    background: {v("sidebar_bg", "#2a2a2a")}; color: {v("dark_muted", v("muted", "#999"))};
    padding: 10px 10px; border: none; font-size: 13px;
}}
QTabBar::tab:selected {{ background: {v("dark_body_bg", v("body_bg", "#1e1e1e"))}; color: {v("dark_text", v("text", "#eee"))}; }}
QTabBar::tab:hover {{ color: {v("dark_text", v("text", "#eee"))}; }}
QLabel {{ color: {v("dark_text", v("text", "#eee"))}; }}
QLineEdit, QTextEdit {{
    background: {v("dark_input_bg", v("input_bg", "#2a2a2a"))};
    color: {v("dark_text", v("text", "#eee"))};
    border: 1px solid {v("dark_input_border", v("input_border", "#444"))};
    border-radius: 6px; padding: 6px 10px; font-size: 13px;
}}
QLineEdit:focus, QTextEdit:focus {{ border-color: {v("dark_accent", v("accent", "#555"))}; }}
QTextEdit[readOnly="true"] {{ color: {v("dark_muted", v("muted", "#888"))}; }}
QPushButton {{
    background: {v("dark_accent_hover", v("accent_hover", "#555"))};
    color: {v("dark_accent_text", v("accent_text", "#fff"))};
    border: none; border-radius: 6px; padding: 8px 16px; font-size: 13px;
}}
QPushButton:hover {{ background: {v("dark_accent", v("accent", "#666"))}; }}
QPushButton:disabled {{ background: {v("dark_card_border", v("card_border", "#333"))}; color: {v("dark_muted", v("muted", "#666"))}; }}
QCheckBox {{ color: {v("dark_text", v("text", "#eee"))}; font-size: 12px; spacing: 8px; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border-radius: 4px;
    background: {v("dark_input_bg", v("input_bg", "#333"))};
    border: 1px solid {v("dark_input_border", v("input_border", "#555"))};
}}
QCheckBox::indicator:checked {{ background: {v("dark_accent", v("accent", "#555"))}; }}
QComboBox {{
    background: {v("dark_input_bg", v("input_bg", "#2a2a2a"))};
    color: {v("dark_text", v("text", "#eee"))};
    border: 1px solid {v("dark_input_border", v("input_border", "#444"))};
    border-radius: 6px; padding: 8px 10px; font-size: 14px;
}}
QComboBox QAbstractItemView {{
    background: {v("dark_input_bg", v("input_bg", "#2a2a2a"))};
    color: {v("dark_text", v("text", "#eee"))};
    selection-background-color: {v("dark_accent", v("accent", "#555"))};
    border: 1px solid {v("dark_input_border", v("input_border", "#444"))};
    outline: none;
}}
QComboBox::drop-down {{ border: none; width: 30px; }}
QScrollBar:vertical {{ background: {v("sidebar_bg", "#2a2a2a")}; width: 10px; }}
QScrollBar::handle:vertical {{ background: {v("dark_muted", v("muted", "#555"))}; border-radius: 5px; }}
QScrollBar:horizontal {{ background: {v("sidebar_bg", "#2a2a2a")}; height: 10px; }}
QScrollBar::handle:horizontal {{ background: {v("dark_muted", v("muted", "#555"))}; border-radius: 5px; }}
QGroupBox {{
    color: {v("dark_text", v("text", "#eee"))}; font-size: 13px; font-weight: bold;
    border: 1px solid {v("dark_input_border", v("input_border", "#444"))};
    border-radius: 6px; margin-top: 12px; padding: 12px 8px 8px;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; }}
QDialog {{ background: {v("dark_body_bg", v("body_bg", "#1a1a1a"))}; }}
QFrame#header {{
    background: {v("dark_header_bg", v("header_bg", "#2a2a2a"))};
    color: {v("dark_header_text", v("header_text", "#eee"))};
}}
"""
    return qss


def get_theme_colors():
    """Load saved theme colors from config."""
    cfg = _cfg()
    custom = cfg.get("custom_theme", {})
    if custom:
        # Use custom if it has enough keys
        if len(custom) > 5:
            return custom
    theme_name = cfg.get("gui_theme", "Dark")
    try:
        from themes import THEMES
        return dict(THEMES.get(theme_name, THEMES["Dark"]))
    except ImportError:
        return {}


def apply(colors=None):
    """Apply theme colors to the running QApplication."""
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication.instance()
    if app is None:
        return
    if colors is None:
        colors = get_theme_colors()
    if not colors:
        return
    app.setStyleSheet(make_gui_stylesheet(colors))
