"""First-run setup wizard for new Site Tools installations."""
import os, json
from PyQt6 import QtWidgets
from git_util import _extract_github_user

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
        title.setStyleSheet("font-weight: bold; color: #c9d1d9;")
        layout.addWidget(title)

        subtitle = QtWidgets.QLabel(
            "Enter your credentials below to get started. "
            "GitHub fields are needed to publish your site. "
            "Supabase enables comments."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #6e7681; margin-bottom: 8px;")
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
        self._extracted_user = ""
        for label, key, placeholder, required in fields:
            fl = QtWidgets.QFormLayout()
            fl.setSpacing(4)
            lbl = QtWidgets.QLabel(label)
            lbl.setStyleSheet("color: #c9d1d9;")
            inp = QtWidgets.QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setStyleSheet("""
                QLineEdit {
                    background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                    border-radius: 6px; padding: 8px 10px;
                }
                QLineEdit:focus { border-color: #58a6ff; }
            """)
            if key == "github_token":
                inp.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            fl.addRow(lbl, inp)
            layout.addLayout(fl)
            self.inputs[key] = inp

        self.inputs["git_remote_url"].textChanged.connect(self._on_url_changed)

        layout.addStretch()

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()

        skip_btn = QtWidgets.QPushButton("Skip")
        skip_btn.setStyleSheet("""
            QPushButton {
                background: #21262d; color: #6e7681; border: none;
                border-radius: 8px; padding: 10px 24px;
            }
            QPushButton:hover { background: #30363d; }
        """)
        skip_btn.clicked.connect(self.reject)
        btn_layout.addWidget(skip_btn)

        save_btn = QtWidgets.QPushButton("Save & Start")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #58a6ff; color: #fff; border: none;
                border-radius: 8px; padding: 10px 28px;
                font-weight: bold;
            }
            QPushButton:hover { background: #79c0ff; }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _on_url_changed(self, url):
        self._extracted_user = _extract_github_user(url)

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

        from setup_git import save_setup_config
        save_setup_config(remote, token, supabase_url, supabase_key)

        if self._extracted_user:
            cfg_path = os.path.join(SITE_DIR, "config.json")
            cfg = {}
            if os.path.exists(cfg_path):
                with open(cfg_path, encoding="utf-8") as f:
                    cfg = json.load(f)
            cfg["git_user_name"] = self._extracted_user
            cfg["git_user_email"] = f"{self._extracted_user}@users.noreply.github.com"
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)

        self.accept()
