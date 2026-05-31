#!/usr/bin/env python3
import os, sys, json
from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets

SITE_DIR = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))


class WysiwygEditor(QtWidgets.QDialog):
    def __init__(self, html_content="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Page Editor")
        self.setMinimumSize(800, 550)
        self.resize(1000, 700)
        self.setStyleSheet("""
            QDialog { background: #0d1117; }
            QPushButton {
                background: #21262d; color: #c9d1d9; border: none;
                border-radius: 6px; padding: 8px 20px;
            }
            QPushButton:hover { background: #30363d; }
            QPushButton.primary { background: #58a6ff; }
            QPushButton.primary:hover { background: #79c0ff; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        editor_path = os.path.join(SITE_DIR, "ckeditor", "editor.html")
        self.view.setUrl(QtCore.QUrl.fromLocalFile(editor_path))
        layout.addWidget(self.view, 1)

        bar = QtWidgets.QWidget()
        bar.setStyleSheet("background: #161b22; border-top: 1px solid #30363d;")
        bl = QtWidgets.QHBoxLayout(bar)
        bl.setContentsMargins(12, 8, 12, 8)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("color: #6e7681; font-size: 12px;")
        bl.addWidget(self.status_label, 1)

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        bl.addWidget(cancel_btn)

        self.save_btn = QtWidgets.QPushButton("Save & Close")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.clicked.connect(self._on_save)
        bl.addWidget(self.save_btn)

        layout.addWidget(bar)

        self._result_html = ""
        self._ready = False

        self.view.loadFinished.connect(lambda ok: self._on_loaded(ok, html_content))

    def _on_loaded(self, ok, initial_html):
        if not ok:
            self.status_label.setText("Failed to load editor")
            return
        self._ready = True
        if initial_html:
            escaped = json.dumps(initial_html)
            self.view.page().runJavaScript(f"setEditorContent({escaped})")

    def _on_save(self):
        if not self._ready:
            self.status_label.setText("Editor not ready yet")
            return
        self.save_btn.setEnabled(False)
        self.save_btn.setText("Saving...")
        self.view.page().runJavaScript("getEditorContent()", self._on_content_received)

    def _on_content_received(self, html):
        self._result_html = html.strip()
        if self._result_html:
            self.accept()
        else:
            self.status_label.setText("Content is empty — write something first")
            self.save_btn.setEnabled(True)
            self.save_btn.setText("Save & Close")

    def result_html(self):
        return self._result_html
