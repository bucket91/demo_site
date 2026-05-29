#!/usr/bin/env python3
"""Owner identity tab — name, title, bio, avatar, contacts."""
import os, sys, json
from PyQt5 import QtWidgets, QtCore, QtGui

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SITE_DIR, "config.json")


def load_config():
    default = {
        "owner_name": "",
        "owner_title": "",
        "owner_bio": "",
        "owner_avatar": "",
        "owner_contacts": [],
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return {**default, **json.load(f)}
    return default


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


class OwnerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self._setup_ui()
        self._load_fields()

    def _setup_ui(self):
        self.setStyleSheet("""
            QLabel { color: #e0e0e0; }
            QLabel.dim { color: #999; }
            QLabel.heading { font-weight: bold; color: #eee; margin-top: 8px; }
            QLineEdit, QTextEdit {
                background: #2a2a2a; color: #e0e0e0; border: 1px solid #333;
                border-radius: 6px; padding: 8px 10px;
            }
            QPushButton {
                background: #555; color: #fff; border: none;
                border-radius: 6px; padding: 8px 16px;
            }
            QPushButton:hover { background: #666; }
            QPushButton.primary { background: #1a6b3c; }
            QPushButton.primary:hover { background: #218c4e; }
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
        form_container = QtWidgets.QWidget()
        form_container.setStyleSheet("background: transparent;")
        fl = QtWidgets.QFormLayout(form_container)
        fl.setSpacing(8)
        fl.setContentsMargins(0, 0, 0, 0)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Your name")
        fl.addRow("Name:", self.name_edit)

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("e.g. Software Developer")
        fl.addRow("Title:", self.title_edit)

        self.bio_edit = QtWidgets.QTextEdit()
        self.bio_edit.setPlaceholderText("A short bio about yourself…")
        self.bio_edit.setMaximumHeight(100)
        fl.addRow("Bio:", self.bio_edit)

        avatar_preview_row = QtWidgets.QHBoxLayout()
        self.avatar_preview = QtWidgets.QLabel()
        self.avatar_preview.setFixedSize(80, 80)
        self.avatar_preview.setStyleSheet("""
            border-radius: 40px;
            border: 3px solid #4a9eff;
            background: #2a2a2a;
        """)
        self.avatar_preview.setAlignment(QtCore.Qt.AlignCenter)
        avatar_preview_row.addWidget(self.avatar_preview)
        avatar_fields = QtWidgets.QVBoxLayout()
        self.avatar_path = QtWidgets.QLineEdit()
        self.avatar_path.setReadOnly(True)
        self.avatar_path.setPlaceholderText("No file selected")
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.clicked.connect(self._pick_avatar)
        avatar_fields.addWidget(self.avatar_path)
        avatar_fields.addWidget(browse_btn)
        avatar_preview_row.addLayout(avatar_fields, 1)
        fl.addRow("Avatar:", avatar_preview_row)

        self.contacts_edit = QtWidgets.QTextEdit()
        self.contacts_edit.setPlaceholderText(
            "One per line: label | url\n"
            "Example:\n"
            "GitHub | https://github.com/username\n"
            "Email | mailto:user@example.com"
        )
        self.contacts_edit.setMaximumHeight(120)
        fl.addRow("Contacts:", self.contacts_edit)

        scroll.setWidget(form_container)
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
        self.log.setStyleSheet("background: #1a1a1a; color: #999; border: 1px solid #333; font-family: monospace; padding: 6px;")
        layout.addWidget(self.log)

    def _load_fields(self):
        self.name_edit.setText(self.cfg.get("owner_name", ""))
        self.title_edit.setText(self.cfg.get("owner_title", ""))
        self.bio_edit.setPlainText(self.cfg.get("owner_bio", ""))
        avatar = self.cfg.get("owner_avatar", "")
        self.avatar_path.setText(os.path.basename(avatar) if avatar else "")
        self.avatar_path.setProperty("full_path", avatar)
        self._update_avatar_preview()
        contacts = self.cfg.get("owner_contacts", [])
        if isinstance(contacts, list):
            lines = [f"{c.get('label', '')} | {c.get('url', '')}" for c in contacts]
            self.contacts_edit.setPlainText("\n".join(lines))
        else:
            self.contacts_edit.clear()

    def _update_avatar_preview(self):
        path = self.avatar_path.property("full_path") or ""
        full = os.path.join(SITE_DIR, path) if path else ""
        if full and os.path.exists(full):
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
            ext = os.path.splitext(path)[1] or ".png"
            dst = os.path.join(SITE_DIR, f"avatar{ext}")
            try:
                copy2(path, dst)
                self.avatar_path.setText(f"avatar{ext}")
                self.avatar_path.setProperty("full_path", f"avatar{ext}")
                self._update_avatar_preview()
                self.log.append(f"✅ Avatar copied → avatar{ext}")
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

        avatar_val = self.avatar_path.property("full_path") or ""
        cfg["owner_avatar"] = avatar_val

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
