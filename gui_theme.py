"""Hardcoded Midnight Dark theme for the PyQt5 GUI."""
import os, json

SITE_DIR = None

MIDNIGHT = {
    "dark_body_bg": "#0d1117",
    "dark_text": "#c9d1d9",
    "dark_muted": "#6e7681",
    "dark_accent": "#58a6ff",
    "dark_accent_hover": "#79c0ff",
    "dark_accent_text": "#0d1117",
    "dark_input_bg": "#0d1117",
    "dark_input_border": "#30363d",
    "dark_card_bg": "#161b22",
    "dark_card_border": "#30363d",
    "button_bg": "#21262d",
    "button_hover": "#30363d",
    "dark_disabled": "#484f58",
}


def make_gui_stylesheet(base_size=14):
    dim = max(base_size - 2, 9)
    heading = base_size + 1
    checkbox = base_size - 1
    combo = base_size + 1
    c = MIDNIGHT
    qss = f"""
QMainWindow {{ background: {c["dark_body_bg"]}; }}
QTabWidget::pane {{ background: {c["dark_body_bg"]}; border: none; padding: 0; }}
QTabBar::tab {{
    background: {c["dark_card_bg"]}; color: {c["dark_muted"]};
    padding: 8px 28px; margin: 0 1px; border: none; font-size: {base_size}px;
}}
QTabBar::tab:selected {{ background: {c["dark_body_bg"]}; color: {c["dark_text"]}; }}
QTabBar::tab:hover {{ color: {c["dark_text"]}; }}
QLabel {{ color: {c["dark_text"]}; }}
QLabel.heading {{ font-size: {heading}px; font-weight: bold; }}
QLabel.dim {{ color: {c["dark_muted"]}; font-size: {dim}px; }}
QLineEdit, QTextEdit {{
    background: {c["dark_input_bg"]};
    color: {c["dark_text"]};
    border: 1px solid {c["dark_input_border"]};
    border-radius: 6px; padding: 6px 10px; font-size: {base_size}px;
}}
QLineEdit:focus, QTextEdit:focus {{ border-color: {c["dark_accent"]}; }}
QTextEdit[readOnly="true"] {{ color: {c["dark_muted"]}; }}
QPushButton {{
    background: {c["button_bg"]};
    color: {c["dark_text"]};
    border: none; border-radius: 6px; padding: 8px 16px; font-size: {base_size}px;
}}
QPushButton:hover {{ background: {c["button_hover"]}; }}
QPushButton:disabled {{ background: {c["dark_card_border"]}; color: {c["dark_disabled"]}; }}
QCheckBox {{ color: {c["dark_text"]}; font-size: {checkbox}px; spacing: 8px; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border-radius: 4px;
    background: {c["dark_input_bg"]};
    border: 1px solid {c["dark_input_border"]};
}}
QCheckBox::indicator:checked {{ background: {c["dark_accent"]}; }}
QComboBox {{
    background: {c["dark_input_bg"]};
    color: {c["dark_text"]};
    border: 1px solid {c["dark_input_border"]};
    border-radius: 6px; padding: 8px 10px; font-size: {combo}px;
}}
QComboBox QAbstractItemView {{
    background: {c["dark_input_bg"]};
    color: {c["dark_text"]};
    selection-background-color: {c["dark_accent"]};
    border: 1px solid {c["dark_input_border"]};
    outline: none;
}}
QComboBox::drop-down {{ border: none; width: 30px; }}
QScrollBar:vertical {{ background: {c["dark_card_bg"]}; width: 10px; }}
QScrollBar::handle:vertical {{ background: {c["dark_disabled"]}; border-radius: 5px; }}
QScrollBar:horizontal {{ background: {c["dark_card_bg"]}; height: 10px; }}
QScrollBar::handle:horizontal {{ background: {c["dark_disabled"]}; border-radius: 5px; }}
QGroupBox {{
    color: {c["dark_text"]}; font-size: {base_size}px; font-weight: bold;
    border: 1px solid {c["dark_input_border"]};
    border-radius: 6px; margin-top: 12px; padding: 12px 8px 8px;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; }}
QDialog {{ background: {c["dark_body_bg"]}; }}
QPushButton.primary {{ background: {c["dark_accent"]}; color: #fff; }}
QPushButton.primary:hover {{ background: {c["dark_accent_hover"]}; }}
QPushButton.danger {{ background: #b71c1c; color: #fff; }}
QPushButton.danger:hover {{ background: #d32f2f; }}
"""
    return qss


def apply(colors=None):
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication.instance()
    if app is None:
        return
    cfg = {}
    if SITE_DIR:
        cf = os.path.join(SITE_DIR, "config.json")
        if os.path.exists(cf):
            with open(cf, encoding="utf-8") as f:
                cfg = json.load(f)
    base_size = cfg.get("gui_font_size", 14)
    app.setStyleSheet(make_gui_stylesheet(base_size=base_size))
