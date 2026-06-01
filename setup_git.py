import os, sys, json, traceback
from PyQt6 import QtWidgets, QtCore

_APP_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(_APP_DIR, "site")
SETTINGS_DIR = os.path.join(_APP_DIR, "settings")
CONFIG_FILE = os.path.join(SETTINGS_DIR, "config.json")
ROOT_CONFIG_FILE = os.path.join(_APP_DIR, "site_tools.config")


def save_setup_config(url, token, supabase_url, supabase_anon_key,
                       user_name="", user_email=""):
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    cfg = {}
    settings_path = CONFIG_FILE
    if os.path.exists(settings_path):
        with open(settings_path, encoding="utf-8") as f:
            cfg = json.load(f)
    if user_name:
        cfg["git_user_name"] = user_name
    if user_email:
        cfg["git_user_email"] = user_email
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    tokens = {}
    if os.path.exists(ROOT_CONFIG_FILE):
        with open(ROOT_CONFIG_FILE, encoding="utf-8") as f:
            tokens = json.load(f)
    if url:
        tokens["git_remote_url"] = url
    if token:
        tokens["github_token"] = token
    if supabase_url:
        tokens["supabase_url"] = supabase_url
    if supabase_anon_key:
        tokens["supabase_anon_key"] = supabase_anon_key
    with open(ROOT_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2)


def is_git_installed():
    from git_util import is_git_available
    return is_git_available()


def is_git_repo():
    return os.path.isdir(os.path.join(SITE_DIR, ".git"))


def get_git_status():
    from git_util import git_run
    lines = []
    r = git_run(["remote", "get-url", "origin"], cwd=SITE_DIR, capture_output=True, text=True)
    lines.append(f"Remote: {r.stdout.strip() if r.returncode == 0 else '(none)'}")
    r = git_run(["rev-list", "--count", "HEAD"], cwd=SITE_DIR, capture_output=True, text=True)
    lines.append(f"Commits: {r.stdout.strip() if r.returncode == 0 else '0'}")
    r = git_run(["status", "--porcelain"], cwd=SITE_DIR, capture_output=True, text=True)
    if r.returncode == 0:
        n = len([l for l in r.stdout.strip().split('\n') if l])
        lines.append(f"Uncommitted: {n}")
    else:
        lines.append("Uncommitted: 0")
    return lines


class PublishingWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        container = QtWidgets.QWidget()
        container.setStyleSheet("background: transparent;")
        cl = QtWidgets.QVBoxLayout(container)
        cl.setContentsMargins(16, 16, 16, 16)
        cl.setSpacing(8)

        heading = QtWidgets.QLabel("Publishing")
        heading.setStyleSheet("font-size: 18px; font-weight: bold; color: #c9d1d9; margin: 0 0 8px 0;")
        cl.addWidget(heading)

        self.status_output = QtWidgets.QTextEdit()
        self.status_output.setReadOnly(True)
        self.status_output.setMaximumHeight(120)
        self.status_output.setStyleSheet("""
            QTextEdit { background: #0d1117; color: #8b949e; border: 1px solid #30363d;
                        border-radius: 6px; padding: 8px; font-family: monospace; font-size: 12px; }
        """)
        cl.addWidget(self.status_output)

        # ── Git group ──
        git_group = QtWidgets.QGroupBox("Git Repository")
        git_group.setStyleSheet("""
            QGroupBox { color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px;
                        margin-top: 12px; padding-top: 16px; }
            QGroupBox::title { color: #c9d1d9; padding: 0 8px; }
        """)
        gl = QtWidgets.QVBoxLayout(git_group)
        gl.setSpacing(8)

        url_row = QtWidgets.QHBoxLayout()
        url_label = QtWidgets.QLabel("Remote URL:")
        url_label.setStyleSheet("color: #6e7681;")
        url_row.addWidget(url_label)
        self.url_input = QtWidgets.QLineEdit()
        self.url_input.setPlaceholderText("https://github.com/user/repo.git")
        self.url_input.setStyleSheet("""
            QLineEdit { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                        border-radius: 6px; padding: 8px 10px; }
        """)
        url_row.addWidget(self.url_input, 1)
        gl.addLayout(url_row)

        token_row = QtWidgets.QHBoxLayout()
        token_label = QtWidgets.QLabel("Token:")
        token_label.setStyleSheet("color: #6e7681;")
        token_row.addWidget(token_label)
        self.token_input = QtWidgets.QLineEdit()
        self.token_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.token_input.setPlaceholderText("GitHub personal access token")
        self.token_input.setStyleSheet("""
            QLineEdit { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                        border-radius: 6px; padding: 8px 10px; }
        """)
        token_row.addWidget(self.token_input, 1)
        gl.addLayout(token_row)

        gl.addSpacing(8)
        btn_row = QtWidgets.QHBoxLayout()
        init_btn = QtWidgets.QPushButton("Init Repo")
        init_btn.clicked.connect(self.init_repo)
        btn_row.addWidget(init_btn)
        refresh_btn = QtWidgets.QPushButton("Refresh Status")
        refresh_btn.clicked.connect(self._refresh_status)
        btn_row.addWidget(refresh_btn)
        btn_row.addStretch()
        self.publish_btn = QtWidgets.QPushButton("Publish")
        self.publish_btn.setStyleSheet("""
            QPushButton { background: #3fb950; color: #fff; border: none; border-radius: 6px;
                          padding: 8px 24px; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background: #2ea043; }
            QPushButton:disabled { background: #21262d; color: #484f58; }
        """)
        self.publish_btn.clicked.connect(self._on_publish)
        btn_row.addWidget(self.publish_btn)
        gl.addLayout(btn_row)

        cl.addWidget(git_group)

        # ── Supabase group ──
        supabase_group = QtWidgets.QGroupBox("Supabase (Comments)")
        supabase_group.setStyleSheet(git_group.styleSheet())
        sl = QtWidgets.QVBoxLayout(supabase_group)
        sl.setSpacing(8)

        su_row = QtWidgets.QHBoxLayout()
        su_label = QtWidgets.QLabel("URL:")
        su_label.setStyleSheet("color: #6e7681;")
        su_row.addWidget(su_label)
        self.supabase_url = QtWidgets.QLineEdit()
        self.supabase_url.setPlaceholderText("https://xxxxx.supabase.co")
        self.supabase_url.setStyleSheet("""
            QLineEdit { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                        border-radius: 6px; padding: 8px 10px; }
        """)
        su_row.addWidget(self.supabase_url, 1)
        sl.addLayout(su_row)

        sa_row = QtWidgets.QHBoxLayout()
        sa_label = QtWidgets.QLabel("Anon Key:")
        sa_label.setStyleSheet("color: #6e7681;")
        sa_row.addWidget(sa_label)
        self.supabase_key = QtWidgets.QLineEdit()
        self.supabase_key.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.supabase_key.setPlaceholderText("anon public key")
        self.supabase_key.setStyleSheet("""
            QLineEdit { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                        border-radius: 6px; padding: 8px 10px; }
        """)
        sa_row.addWidget(self.supabase_key, 1)
        sl.addLayout(sa_row)

        cl.addWidget(supabase_group)

        # ── Output ──
        output_label = QtWidgets.QLabel("Output:")
        output_label.setStyleSheet("color: #6e7681; margin-top: 8px;")
        cl.addWidget(output_label)
        self.output_box = QtWidgets.QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setStyleSheet("""
            QTextEdit { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                        border-radius: 6px; padding: 8px; font-family: monospace; font-size: 12px; }
        """)
        cl.addWidget(self.output_box, 1)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        self._load_config_to_ui()
        self._refresh_status()

    def _load_config_to_ui(self):
        from generate import load_config
        cfg = load_config()
        self.url_input.setText(cfg.get("git_remote_url", ""))
        self.token_input.setText(cfg.get("github_token", ""))
        self.supabase_url.setText(cfg.get("supabase_url", ""))
        self.supabase_key.setText(cfg.get("supabase_anon_key", ""))

    def _refresh_status(self):
        if not is_git_repo():
            self.status_output.setText("No git repository. Click 'Init Repo' to create one.")
            return
        lines = get_git_status()
        self.status_output.setText('\n'.join(lines))

    def init_repo(self):
        from git_util import git_run
        url = self.url_input.text().strip()
        token = self.token_input.text().strip()
        su = self.supabase_url.text().strip()
        sk = self.supabase_key.text().strip()

        name = ""
        email = ""
        if url:
            parts = url.rstrip('.git').split('/')
            if len(parts) >= 2:
                name = parts[-2]
                if '/' in url:
                    email = f"{name}@users.noreply.github.com"

        save_setup_config(url, token, su, sk, name, email)

        git_run(["init"], cwd=SITE_DIR)
        if name:
            git_run(["config", "user.name", name], cwd=SITE_DIR)
        if email:
            git_run(["config", "user.email", email], cwd=SITE_DIR)
        if url:
            git_run(["remote", "remove", "origin"], cwd=SITE_DIR, capture_output=True)
            git_run(["remote", "add", "origin", url], cwd=SITE_DIR)

        gi = os.path.join(SITE_DIR, ".gitignore")
        if not os.path.exists(gi):
            with open(gi, "w", encoding="utf-8") as f:
                f.write("__pycache__/\n")

        from bootstrap import _ensure_precommit_hook
        _ensure_precommit_hook(SITE_DIR)

        self.output_box.append("Repo initialized.")
        self._refresh_status()

    def _on_publish(self):
        url = self.url_input.text().strip()
        token = self.token_input.text().strip()
        su = self.supabase_url.text().strip()
        sk = self.supabase_key.text().strip()
        save_setup_config(url, token, su, sk)

        if not is_git_repo():
            self.output_box.append("No git repo. Click 'Init Repo' first.")
            return

        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            return
        self.publish_btn.setEnabled(False)
        self.publish_btn.setText("Publishing...")
        self.output_box.append("Publishing...")
        self.worker = _PublishWorker()
        self.worker.log_msg.connect(self.output_box.append)
        self.worker.finished.connect(self._on_publish_done)
        self.worker.start()

    def _on_publish_done(self):
        self.publish_btn.setEnabled(True)
        self.publish_btn.setText("Publish")
        self.worker = None
        self._refresh_status()


class _PublishWorker(QtCore.QThread):
    log_msg = QtCore.pyqtSignal(str)

    def run(self):
        import generate
        import error_log
        try:
            generate.CONFIG.update(generate.load_config())
            generate.generate_all(log_func=lambda m: self.log_msg.emit(m))
            generate.git_commit_push(log_func=lambda m: self.log_msg.emit(m))
        except Exception:
            msg = traceback.format_exc()
            error_log.error("Publish failed:\n" + msg)
            self.log_msg.emit("Error: " + msg.split('\n')[-2])
