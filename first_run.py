"""First-run setup wizard for new Site Tools installations."""
import os, json
from PyQt5 import QtWidgets

SITE_DIR = None


class FirstRunWizard(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Site Tools")
        self.setMinimumWidth(520)
        self.setModal(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(28, 24, 28, 24)

        title = QtWidgets.QLabel("First-Time Setup")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #eee;")
        layout.addWidget(title)

        subtitle = QtWidgets.QLabel(
            "Enter your credentials below to get started. "
            "GitHub fields are needed to publish your site. "
            "Supabase enables comments."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #999; font-size: 13px; margin-bottom: 8px;")
        layout.addWidget(subtitle)

        fields = [
            ("GitHub Remote URL", "git_remote_url",
             "https://github.com/username/repo.git", True),
            ("GitHub Token (required to push)", "github_token",
             "ghp_...", True),
            ("Supabase URL", "supabase_url",
             "https://xxx.supabase.co", False),
            ("Supabase Anon Key", "supabase_anon_key",
             "eyJhbGciOiJIUzI1NiIs...", False),
        ]

        self.inputs = {}
        for label, key, placeholder, required in fields:
            fl = QtWidgets.QFormLayout()
            fl.setSpacing(4)
            lbl = QtWidgets.QLabel(label)
            lbl.setStyleSheet("color: #ccc; font-size: 12px;")
            inp = QtWidgets.QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setStyleSheet("""
                QLineEdit {
                    background: #333; color: #eee; border: 1px solid #555;
                    border-radius: 6px; padding: 8px 10px; font-size: 13px;
                }
                QLineEdit:focus { border-color: #777; }
            """)
            if key == "github_token":
                inp.setEchoMode(QtWidgets.QLineEdit.Password)
            fl.addRow(lbl, inp)
            layout.addLayout(fl)
            self.inputs[key] = inp

        layout.addStretch()

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()

        skip_btn = QtWidgets.QPushButton("Skip")
        skip_btn.setStyleSheet("""
            QPushButton {
                background: #444; color: #999; border: none;
                border-radius: 8px; padding: 10px 24px; font-size: 13px;
            }
            QPushButton:hover { background: #555; }
        """)
        skip_btn.clicked.connect(self.reject)
        btn_layout.addWidget(skip_btn)

        save_btn = QtWidgets.QPushButton("Save & Start")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4a9eff; color: #fff; border: none;
                border-radius: 8px; padding: 10px 28px; font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: #3a7acc; }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _save(self):
        remote = self.inputs["git_remote_url"].text().strip()
        token = self.inputs["github_token"].text().strip()
        supabase_url = self.inputs["supabase_url"].text().strip()
        supabase_key = self.inputs["supabase_anon_key"].text().strip()

        if not token:
            QtWidgets.QMessageBox.warning(
                self, "Missing Token",
                "GitHub Token is required to publish your site. "
                "You can set it later in the Setup tab."
            )
            return

        cfg_path = os.path.join(SITE_DIR, "config.json")
        local_path = os.path.join(SITE_DIR, "config.local.json")

        cfg = {}
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                cfg = json.load(f)

        cfg["git_remote_url"] = remote
        cfg["supabase_url"] = supabase_url
        cfg["supabase_anon_key"] = supabase_key
        if "github_token" in cfg:
            del cfg["github_token"]

        with open(cfg_path, "w") as f:
            json.dump(cfg, f, indent=2)

        local = {}
        if os.path.exists(local_path):
            with open(local_path) as f:
                local = json.load(f)
        local["github_token"] = token
        with open(local_path, "w") as f:
            json.dump(local, f, indent=2)

        self.accept()
