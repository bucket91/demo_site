#!/usr/bin/env python3
"""Owner identity tab — name, title, bio, avatar, contacts."""
import os, sys, json
from PyQt5 import QtWidgets, QtCore, QtGui

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SITE_DIR, "config.json")

from generate import load_config, save_config


class OwnerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self._setup_ui()
        self._load_fields()

    def _setup_ui(self):
        self.setStyleSheet("""
            QLabel { color: #c9d1d9; }
            QLabel.dim { color: #6e7681; }
            QLabel.heading { font-weight: bold; color: #c9d1d9; margin-top: 8px; }
            QLineEdit, QTextEdit {
                background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; padding: 8px 10px;
            }
            QPushButton {
                background: #21262d; color: #c9d1d9; border: none;
                border-radius: 6px; padding: 8px 16px;
            }
            QPushButton:hover { background: #30363d; }
            QPushButton.primary { background: #58a6ff; }
            QPushButton.primary:hover { background: #79c0ff; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        heading = QtWidgets.QLabel("Owner")
        heading.setProperty("class", "heading")
        layout.addWidget(heading)

        desc = QtWidgets.QLabel("Set your site author identity.")
        desc.setProperty("class", "dim")
        layout.addWidget(desc)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        container = QtWidgets.QWidget()
        container.setStyleSheet("background: transparent;")
        outer = QtWidgets.QVBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(12)

        # Row 1: Name + Title (60%) | Avatar (40%)
        top_row = QtWidgets.QHBoxLayout()
        top_row.setSpacing(16)
        left_top = QtWidgets.QWidget()
        left_top.setStyleSheet("background: transparent;")
        fl = QtWidgets.QFormLayout(left_top)
        fl.setSpacing(8)
        fl.setContentsMargins(0, 0, 0, 0)
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Your name")
        fl.addRow("Name:", self.name_edit)
        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("e.g. Software Developer")
        fl.addRow("Title:", self.title_edit)
        top_row.addWidget(left_top, 3)

        avatar_side = QtWidgets.QWidget()
        avatar_side.setStyleSheet("background: transparent;")
        al = QtWidgets.QVBoxLayout(avatar_side)
        al.setContentsMargins(0, 0, 0, 0)
        al.setAlignment(QtCore.Qt.AlignCenter)
        self.avatar_preview = QtWidgets.QLabel()
        self.avatar_preview.setFixedSize(80, 80)
        self.avatar_preview.setStyleSheet("""
            border-radius: 40px;
            border: 3px solid #58a6ff;
            background: #0d1117;
        """)
        self.avatar_preview.setAlignment(QtCore.Qt.AlignCenter)
        al.addWidget(self.avatar_preview, alignment=QtCore.Qt.AlignCenter)
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._pick_avatar)
        al.addWidget(browse_btn, alignment=QtCore.Qt.AlignCenter)
        top_row.addWidget(avatar_side, 2)
        outer.addLayout(top_row)

        # Row 2: Bio (40%) | Contacts (60%)
        bot_row = QtWidgets.QHBoxLayout()
        bot_row.setSpacing(16)
        bio_w = QtWidgets.QWidget()
        bio_w.setStyleSheet("background: transparent;")
        bl = QtWidgets.QFormLayout(bio_w)
        bl.setSpacing(8)
        bl.setContentsMargins(0, 0, 0, 0)
        self.bio_edit = QtWidgets.QTextEdit()
        self.bio_edit.setPlaceholderText("A short bio about yourself…")
        self.bio_edit.setMaximumHeight(120)
        bl.addRow("Bio:", self.bio_edit)
        bot_row.addWidget(bio_w, 2)

        contacts_w = QtWidgets.QWidget()
        contacts_w.setStyleSheet("background: transparent;")
        cl = QtWidgets.QFormLayout(contacts_w)
        cl.setSpacing(8)
        cl.setContentsMargins(0, 0, 0, 0)
        self.contacts_edit = QtWidgets.QTextEdit()
        self.contacts_edit.setPlaceholderText(
            "One per line: label | url\n"
            "Example:\n"
            "GitHub | https://github.com/username\n"
            "Email | mailto:user@example.com"
        )
        self.contacts_edit.setMaximumHeight(120)
        cl.addRow("Contacts:", self.contacts_edit)
        bot_row.addWidget(contacts_w, 3)
        outer.addLayout(bot_row)

        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        self.save_btn = QtWidgets.QPushButton("Save Owner Settings")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._save)
        btn_row.addWidget(self.save_btn)
        layout.addLayout(btn_row)

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(80)
        self.log.setStyleSheet("background: #0d1117; color: #6e7681; border: 1px solid #30363d; font-family: monospace; padding: 6px;")
        layout.addWidget(self.log)

    def _load_fields(self):
        self.name_edit.setText(self.cfg.get("owner_name", ""))
        self.title_edit.setText(self.cfg.get("owner_title", ""))
        self.bio_edit.setPlainText(self.cfg.get("owner_bio", ""))
        self._update_avatar_preview()
        contacts = self.cfg.get("owner_contacts", [])
        if isinstance(contacts, list):
            lines = [f"{c.get('label', '')} | {c.get('url', '')}" for c in contacts]
            self.contacts_edit.setPlainText("\n".join(lines))
        else:
            self.contacts_edit.clear()

    def _update_avatar_preview(self):
        full = os.path.join(SITE_DIR, "avatar.png")
        if os.path.exists(full):
            pixmap = QtGui.QPixmap(full)
            if not pixmap.isNull():
                size = min(pixmap.width(), pixmap.height())
                cropped = pixmap.copy(
                    (pixmap.width() - size) // 2,
                    (pixmap.height() - size) // 2,
                    size, size
                )
                scaled = cropped.scaled(
                    74, 74, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
                )
                rounded = QtGui.QPixmap(74, 74)
                rounded.fill(QtCore.Qt.transparent)
                painter = QtGui.QPainter(rounded)
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                clip = QtGui.QPainterPath()
                clip.addEllipse(0, 0, 74, 74)
                painter.setClipPath(clip)
                painter.drawPixmap(0, 0, scaled)
                painter.end()
                self.avatar_preview.setPixmap(rounded)
                return
        self.avatar_preview.clear()

    def _pick_avatar(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Avatar Image", "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg);;All files (*)")
        if path:
            from shutil import copy2
            dst = os.path.join(SITE_DIR, "avatar.png")
            try:
                copy2(path, dst)
                self._update_avatar_preview()
                self.log.append("✅ Avatar set (avatar.png)")
            except Exception as e:
                self.log.append(f"⚠️ Copy failed: {e}")

    def _save(self):
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, encoding="utf-8") as f:
                cfg = json.load(f)

        cfg["owner_name"] = self.name_edit.text().strip()
        cfg["owner_title"] = self.title_edit.text().strip()
        cfg["owner_bio"] = self.bio_edit.toPlainText().strip()

        contacts = []
        for line in self.contacts_edit.toPlainText().strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if "|" in line:
                label, _, url = line.partition("|")
                contacts.append({"label": label.strip(), "url": url.strip()})
            else:
                contacts.append({"label": line, "url": ""})
        from generate import normalize_contact_url
        for c in contacts:
            c["url"] = normalize_contact_url(c["label"], c["url"])
        cfg["owner_contacts"] = contacts

        save_config(cfg)
        self.cfg = cfg
        self.log.append("✅ Owner settings saved — generating site...")
        self.save_btn.setEnabled(False)
        self.save_btn.setText("Saving & Generating...")
        self._worker = _OwnerWorker(cfg)
        self._worker.logged.connect(self.log.append)
        self._worker.finished.connect(self._on_generate_done)
        self._worker.start()

    def _on_generate_done(self, ok):
        self.save_btn.setEnabled(True)
        self.save_btn.setText("Save Owner Settings")
        if ok:
            self.log.append("✅ Site generated and pushed")
        else:
            self.log.append("❌ Generation failed — check output above")


class _OwnerWorker(QtCore.QThread):
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
            if not generate.generate_all(log_func=self.logged.emit):
                ok = False
            generate.git_commit_push(log_func=self.logged.emit)
        except Exception as e:
            self.logged.emit(f"Error: {e}")
            ok = False
        self.finished.emit(ok)
