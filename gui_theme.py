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


def make_gui_stylesheet(colors, base_size=14):
    """Build a QSS stylesheet string from a dict of web theme colors and a base font size."""
    c = colors or {}
    def v(k, fallback="#eee"):
        return c.get(k, fallback)

    dim = max(base_size - 2, 9)
    heading = base_size + 1
    checkbox = base_size - 1
    combo = base_size + 1

    qss = f"""
QMainWindow {{ background: {v("dark_body_bg", v("body_bg", "#1e1e1e"))}; }}
QTabWidget::pane {{ background: {v("dark_body_bg", v("body_bg", "#1e1e1e"))}; border: none; }}
QTabBar::tab {{
    background: {v("sidebar_bg", "#2a2a2a")}; color: {v("dark_muted", v("muted", "#999"))};
    padding: 10px 10px; border: none; font-size: {base_size}px;
}}
QTabBar::tab:selected {{ background: {v("dark_body_bg", v("body_bg", "#1e1e1e"))}; color: {v("dark_text", v("text", "#eee"))}; }}
QTabBar::tab:hover {{ color: {v("dark_text", v("text", "#eee"))}; }}
QLabel {{ color: {v("dark_text", v("text", "#eee"))}; }}
QLabel.heading {{ font-size: {heading}px; font-weight: bold; }}
QLabel.dim {{ color: {v("dark_muted", v("muted", "#888"))}; font-size: {dim}px; }}
QLineEdit, QTextEdit {{
    background: {v("dark_input_bg", v("input_bg", "#2a2a2a"))};
    color: {v("dark_text", v("text", "#eee"))};
    border: 1px solid {v("dark_input_border", v("input_border", "#444"))};
    border-radius: 6px; padding: 6px 10px; font-size: {base_size}px;
}}
QLineEdit:focus, QTextEdit:focus {{ border-color: {v("dark_accent", v("accent", "#555"))}; }}
QTextEdit[readOnly="true"] {{ color: {v("dark_muted", v("muted", "#888"))}; }}
QPushButton {{
    background: {v("dark_accent_hover", v("accent_hover", "#555"))};
    color: {v("dark_accent_text", v("accent_text", "#fff"))};
    border: none; border-radius: 6px; padding: 8px 16px; font-size: {base_size}px;
}}
QPushButton:hover {{ background: {v("dark_accent", v("accent", "#666"))}; }}
QPushButton:disabled {{ background: {v("dark_card_border", v("card_border", "#333"))}; color: {v("dark_muted", v("muted", "#666"))}; }}
QCheckBox {{ color: {v("dark_text", v("text", "#eee"))}; font-size: {checkbox}px; spacing: 8px; }}
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
    border-radius: 6px; padding: 8px 10px; font-size: {combo}px;
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
    color: {v("dark_text", v("text", "#eee"))}; font-size: {base_size}px; font-weight: bold;
    border: 1px solid {v("dark_input_border", v("input_border", "#444"))};
    border-radius: 6px; margin-top: 12px; padding: 12px 8px 8px;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; }}
QDialog {{ background: {v("dark_body_bg", v("body_bg", "#1a1a1a"))}; }}
QFrame#header {{
    background: {v("dark_header_bg", v("header_bg", "#2a2a2a"))};
    color: {v("dark_header_text", v("header_text", "#eee"))};
}}
QPushButton.primary {{ background: {v("dark_accent", v("accent", "#4a9eff"))}; }}
QPushButton.primary:hover {{ background: {v("dark_accent_hover", v("accent_hover", "#3a7acc"))}; }}
QPushButton.danger {{ background: #b71c1c; }}
QPushButton.danger:hover {{ background: #d32f2f; }}
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
    """Apply theme colors and font size to the running QApplication."""
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication.instance()
    if app is None:
        return
    if colors is None:
        colors = get_theme_colors()
    if not colors:
        return
    cfg = _cfg()
    base_size = cfg.get("gui_font_size", 14)
    app.setStyleSheet(make_gui_stylesheet(colors, base_size=base_size))
