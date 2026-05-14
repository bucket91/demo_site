#!/usr/bin/env python3
import json, os, sys
from PyQt5 import QtWidgets, QtCore, QtGui

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SITE_DIR, "config.json")

def load():
    default = {
        "supabase_url": "",
        "supabase_anon_key": "",
        "comments_enabled": True,
        "git_remote_url": "",
        "git_user_name": "",
        "git_user_email": "",
        "git_commit_message": "update site via generator",
        "git_auto_push": True,
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return {**default, **json.load(f)}
    return default

def save(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = load()
        self.setWindowTitle("Site Generator")
        self.setMinimumSize(520, 640)
        self.setStyleSheet("""
            QMainWindow { background: #1e1e1e; }
            QLabel { color: #eee; }
            QLabel.hint { color: #999; font-size: 11px; }
            QLineEdit, QTextEdit {
                background: #333; color: #eee; border: 1px solid #2a2a2a;
                border-radius: 6px; padding: 6px 10px; font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus { border-color: #555; }
            QCheckBox {
                color: #eee; font-size: 13px; spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px; height: 18px; border-radius: 4px;
                background: #333; border: 1px solid #555;
            }
            QCheckBox::indicator:checked { background: #555; }
            QPushButton {
                background: #555; color: #fff; border: none;
                border-radius: 8px; padding: 10px 24px; font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: #666; }
            QPushButton:pressed { background: #4a4a4a; }
            QPushButton:disabled { background: #333; color: #666; }
            QTextEdit.log {
                background: #333; color: #999;
                font-family: monospace; font-size: 12px;
                border-radius: 8px; padding: 8px; border: none;
            }
        """)

        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # header
        header = QtWidgets.QFrame()
        header.setStyleSheet("background: #2a2a2a; padding: 16px;")
        hl = QtWidgets.QVBoxLayout(header)
        hl.setContentsMargins(20, 12, 20, 12)

        title = QtWidgets.QLabel("Site Generator")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #eee;")
        hl.addWidget(title)

        subtitle = QtWidgets.QLabel(SITE_DIR)
        subtitle.setStyleSheet("color: #999; font-size: 11px;")
        hl.addWidget(subtitle)

        layout.addWidget(header)

        # scrollable body
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #1e1e1e; border: none; }"
                             "QScrollBar:vertical { background: #2a2a2a; width: 10px; }"
                             "QScrollBar::handle:vertical { background: #555; border-radius: 5px; }")
        body = QtWidgets.QWidget()
        body.setStyleSheet("background: #1e1e1e;")
        body_layout = QtWidgets.QVBoxLayout(body)
        body_layout.setContentsMargins(20, 10, 20, 10)
        body_layout.setSpacing(4)
        scroll.setWidget(body)
        layout.addWidget(scroll, 1)

        self.fields = {}

        def section(text):
            f = QtWidgets.QWidget()
            fl = QtWidgets.QVBoxLayout(f)
            fl.setContentsMargins(0, 12, 0, 4)
            lbl = QtWidgets.QLabel(text)
            lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #eee;")
            fl.addWidget(lbl)
            line = QtWidgets.QFrame()
            line.setFrameShape(QtWidgets.QFrame.HLine)
            line.setStyleSheet("color: #333;")
            fl.addWidget(line)
            body_layout.addWidget(f)

        def labeled(label, key, show=''):
            f = QtWidgets.QWidget()
            fl = QtWidgets.QVBoxLayout(f)
            fl.setContentsMargins(0, 6, 0, 0)
            fl.setSpacing(2)
            lbl = QtWidgets.QLabel(label)
            lbl.setStyleSheet("color: #999; font-size: 11px;")
            fl.addWidget(lbl)
            inp = QtWidgets.QLineEdit()
            inp.setText(self.cfg.get(key, ''))
            if show:
                inp.setEchoMode(QtWidgets.QLineEdit.Password)
            fl.addWidget(inp)
            body_layout.addWidget(f)
            self.fields[key] = inp

        def checkbox(label, key):
            cb = QtWidgets.QCheckBox(label)
            cb.setChecked(self.cfg.get(key, True))
            body_layout.addWidget(cb)
            self.fields[key] = cb

        section("Supabase")
        labeled("Project URL", "supabase_url")
        labeled("Anon Key", "supabase_anon_key")
        checkbox("Enable comments", "comments_enabled")

        section("GitHub")
        labeled("Remote URL", "git_remote_url")
        labeled("Git User Name", "git_user_name")
        labeled("Git User Email", "git_user_email")
        labeled("Commit Message", "git_commit_message")
        checkbox("Auto push to GitHub", "git_auto_push")

        # log output
        body_layout.addSpacing(8)
        log_label = QtWidgets.QLabel("Output")
        log_label.setStyleSheet("color: #999; font-size: 11px;")
        body_layout.addWidget(log_label)

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setProperty("class", "log")
        self.log.setMinimumHeight(140)
        body_layout.addWidget(self.log, 1)

        # bottom bar
        bottom = QtWidgets.QFrame()
        bottom.setStyleSheet("background: #2a2a2a; padding: 12px 20px;")
        bl = QtWidgets.QHBoxLayout(bottom)
        bl.setContentsMargins(20, 12, 20, 12)

        self.run_btn = QtWidgets.QPushButton("Generate & Push")
        self.run_btn.clicked.connect(self.on_run)
        self.run_btn.setMinimumHeight(44)
        bl.addWidget(self.run_btn)

        layout.addWidget(bottom)

    def log_msg(self, msg):
        self.log.append(msg)
        # auto-scroll to bottom
        sb = self.log.verticalScrollBar()
        sb.setValue(sb.maximum())
        QtWidgets.QApplication.processEvents()

    @QtCore.pyqtSlot()
    def on_run(self):
        new = {}
        for k, v in self.fields.items():
            if isinstance(v, QtWidgets.QLineEdit):
                new[k] = v.text()
            elif isinstance(v, QtWidgets.QCheckBox):
                new[k] = v.isChecked()
        save(new)

        self.log.clear()
        self.run_btn.setEnabled(False)
        self.run_btn.setText("Running...")

        # run in background thread so UI stays responsive
        self.worker = Worker(new)
        self.worker.logged.connect(self.log_msg)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    @QtCore.pyqtSlot(bool)
    def on_finished(self, ok):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("Generate & Push")
        if not ok:
            self.log_msg("[ERROR] Check output above.")

class Worker(QtCore.QThread):
    logged = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal(bool)

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

    def run(self):
        ok = True
        try:
            import generate
            generate.CONFIG.update(self.cfg)
            generate.write_comments_js()
            if not generate.generate_all(log_func=self.logged.emit):
                ok = False
            generate.git_commit_push(log_func=self.logged.emit)
        except Exception as e:
            self.logged.emit(f"Error: {e}")
            ok = False
        self.finished.emit(ok)

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
