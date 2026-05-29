#!/usr/bin/env python3
"""Git setup widget for Site Tools."""
import os, sys, json
from PyQt5 import QtWidgets, QtCore
from git_util import is_git_available as _git_available, git_run as _git_run

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SITE_DIR, "config.json")
LOCAL_CONFIG_FILE = os.path.join(SITE_DIR, "config.local.json")


def load_config():
    default = {
        "supabase_url": "", "supabase_anon_key": "", "comments_enabled": True,
        "site_title": "Placeholder",
        "git_remote_url": "", "git_user_name": "", "git_user_email": "",
        "git_commit_message": "Initial site setup", "git_auto_push": True,
        "github_token": "",
    }
    cfg = default
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            cfg = {**default, **json.load(f)}
    if os.path.exists(LOCAL_CONFIG_FILE):
        with open(LOCAL_CONFIG_FILE) as f:
            cfg.update(json.load(f))
    return cfg


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def save_setup_config(url, name, email, msg, auto_push,
                      supabase_url, supabase_anon_key, comments_enabled, site_title,
                      github_token):
    # Write safe fields to config.json (pushed to repo)
    cfg = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
    cfg.update(git_remote_url=url, git_user_name=name, git_user_email=email,
               git_commit_message=msg, git_auto_push=auto_push,
               supabase_url=supabase_url, supabase_anon_key=supabase_anon_key,
               comments_enabled=comments_enabled, site_title=site_title)
    cfg.pop("github_token", None)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

    # Write token to local-only config (not pushed)
    local_cfg = {}
    if os.path.exists(LOCAL_CONFIG_FILE):
        with open(LOCAL_CONFIG_FILE) as f:
            local_cfg = json.load(f)
    local_cfg["github_token"] = github_token
    with open(LOCAL_CONFIG_FILE, "w") as f:
        json.dump(local_cfg, f, indent=2)


def _make_push_url(url, token):
    if token and url.startswith('https://'):
        return url.replace('https://', f'https://{token}@', 1)
    return url


def is_git_installed():
    return _git_available()


def is_git_repo():
    r = _git_run(["rev-parse", "--git-dir"], cwd=SITE_DIR, capture_output=True)
    return r.returncode == 0


def get_git_status():
    lines = []
    if not is_git_installed():
        return ["ERROR: git is not installed"]
    if not is_git_repo():
        lines.append("Not a git repository")
        return lines
    r = _git_run(["remote", "get-url", "origin"], cwd=SITE_DIR, capture_output=True, text=True)
    if r.returncode == 0:
        lines.append(f"Remote: {r.stdout.strip()}")
    else:
        lines.append("Remote: not set")
    r = _git_run(["config", "user.name"], cwd=SITE_DIR, capture_output=True, text=True)
    lines.append(f"User: {r.stdout.strip() or 'not set'}")
    r = _git_run(["config", "user.email"], cwd=SITE_DIR, capture_output=True, text=True)
    lines.append(f"Email: {r.stdout.strip() or 'not set'}")
    r = _git_run(["rev-list", "--count", "HEAD"], cwd=SITE_DIR, capture_output=True, text=True)
    n = r.stdout.strip()
    lines.append(f"Commits: {n}" if n.isdigit() else "Commits: 0 (no commits yet)")
    r = _git_run(["status", "--short"], cwd=SITE_DIR, capture_output=True, text=True)
    untracked = len([l for l in r.stdout.strip().split('\n') if l.strip()])
    lines.append(f"Uncommitted files: {untracked}")
    return lines


class SetupGitWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QLabel { color: #e0e0e0; }
            QLabel.dim { color: #999; font-size: 11px; }
            QLabel.heading { font-size: 14px; font-weight: bold; color: #eee; margin-top: 8px; }
            QLineEdit {
                background: #2a2a2a; color: #e0e0e0; border: 1px solid #333;
                border-radius: 6px; padding: 8px 10px; font-size: 13px;
            }
            QTextEdit {
                background: #1a1a1a; color: #ccc; border: 1px solid #333;
                border-radius: 6px; padding: 6px; font-size: 12px; font-family: monospace;
            }
            QPushButton {
                background: #555; color: #fff; border: none;
                border-radius: 6px; padding: 8px 16px; font-size: 13px;
            }
            QPushButton:hover { background: #666; }
            QPushButton:disabled { background: #333; color: #666; }
            QPushButton.primary { background: #1a6b3c; }
            QPushButton.primary:hover { background: #218c4e; }
            QPushButton.danger { background: #b71c1c; }
            QPushButton.danger:hover { background: #d32f2f; }
            QCheckBox { color: #ccc; font-size: 12px; }
            QGroupBox {
                color: #ddd; font-size: 13px; font-weight: bold;
                border: 1px solid #333; border-radius: 6px; margin-top: 12px;
                padding: 12px 8px 8px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        heading = QtWidgets.QLabel("Setup")
        heading.setProperty("class", "heading")
        layout.addWidget(heading)

        desc = QtWidgets.QLabel(
            "Configure site, Supabase, GitHub, and generate your site."
        )
        desc.setProperty("class", "dim")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        scroll_body = QtWidgets.QWidget()
        scroll_body.setStyleSheet("background: transparent;")
        sl = QtWidgets.QVBoxLayout(scroll_body)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(8)
        scroll.setWidget(scroll_body)
        layout.addWidget(scroll, stretch=1)

        cfg = load_config()

        # ── Supabase ──
        supabase_group = QtWidgets.QGroupBox("Supabase")
        sfl = QtWidgets.QFormLayout(supabase_group)
        sfl.setSpacing(6)
        sfl.setContentsMargins(10, 16, 10, 10)

        self.supabase_url = QtWidgets.QLineEdit(cfg.get("supabase_url", ""))
        self.supabase_url.setPlaceholderText("https://your-project.supabase.co")
        sfl.addRow("Project URL:", self.supabase_url)

        self.supabase_key = QtWidgets.QLineEdit(cfg.get("supabase_anon_key", ""))
        self.supabase_key.setPlaceholderText("anon public key")
        self.supabase_key.setEchoMode(QtWidgets.QLineEdit.Password)
        sfl.addRow("Anon Key:", self.supabase_key)

        self.comments_cb = QtWidgets.QCheckBox("Enable comments")
        self.comments_cb.setChecked(cfg.get("comments_enabled", True))
        sfl.addRow("", self.comments_cb)

        sl.addWidget(supabase_group)

        # ── Site ──
        site_group = QtWidgets.QGroupBox("Site")
        sifl = QtWidgets.QFormLayout(site_group)
        sifl.setSpacing(6)
        sifl.setContentsMargins(10, 16, 10, 10)

        self.site_title = QtWidgets.QLineEdit(cfg.get("site_title", "Placeholder"))
        self.site_title.setPlaceholderText("My Awesome Site")
        sifl.addRow("Site Title:", self.site_title)

        sl.addWidget(site_group)

        # ── Git ──
        git_group = QtWidgets.QGroupBox("GitHub / Git")
        gfl = QtWidgets.QFormLayout(git_group)
        gfl.setSpacing(6)
        gfl.setContentsMargins(10, 16, 10, 10)

        self.remote_input = QtWidgets.QLineEdit(cfg.get("git_remote_url", ""))
        self.remote_input.setPlaceholderText("https://github.com/user/repo.git")
        gfl.addRow("Remote URL:", self.remote_input)

        self.token_input = QtWidgets.QLineEdit(cfg.get("github_token", ""))
        self.token_input.setPlaceholderText("ghp_xxxxxxxxxxxxxxxxxxxx  (NOT a GPG key)")
        self.token_input.setEchoMode(QtWidgets.QLineEdit.Password)
        gfl.addRow("GitHub Token:", self.token_input)

        self.name_input = QtWidgets.QLineEdit(cfg.get("git_user_name", ""))
        self.name_input.setPlaceholderText("Your GitHub username")
        gfl.addRow("User name:", self.name_input)

        self.email_input = QtWidgets.QLineEdit(cfg.get("git_user_email", ""))
        self.email_input.setPlaceholderText("user@users.noreply.github.com")
        gfl.addRow("User email:", self.email_input)

        self.msg_input = QtWidgets.QLineEdit(cfg.get("git_commit_message", "Initial site setup"))
        self.msg_input.setPlaceholderText("Commit message")
        gfl.addRow("Commit msg:", self.msg_input)

        self.auto_push_cb = QtWidgets.QCheckBox("Auto-push after commit")
        self.auto_push_cb.setChecked(cfg.get("git_auto_push", True))
        gfl.addRow("", self.auto_push_cb)

        sl.addWidget(git_group)

        # ── Status box ──
        status_label = QtWidgets.QLabel("Status")
        status_label.setProperty("class", "dim")
        sl.addWidget(status_label)

        self.status_box = QtWidgets.QTextEdit()
        self.status_box.setReadOnly(True)
        self.status_box.setMaximumHeight(100)
        sl.addWidget(self.status_box)

        refresh_status_btn = QtWidgets.QPushButton("Refresh Status")
        refresh_status_btn.clicked.connect(self.check_status)
        sl.addWidget(refresh_status_btn, alignment=QtCore.Qt.AlignLeft)

        # Generate button
        gen_row = QtWidgets.QHBoxLayout()
        gen_row.addStretch()
        self.gen_btn = QtWidgets.QPushButton("Generate & Push")
        self.gen_btn.setProperty("class", "primary")
        self.gen_btn.setMinimumHeight(44)
        self.gen_btn.clicked.connect(self.on_generate)
        gen_row.addWidget(self.gen_btn)
        sl.addLayout(gen_row)

        # Output log
        log_label = QtWidgets.QLabel("Output:")
        log_label.setProperty("class", "dim")
        sl.addWidget(log_label)

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Command output will appear here...")
        sl.addWidget(self.log, 1)

        # Buttons
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(8)

        init_btn = QtWidgets.QPushButton("Initialize")
        init_btn.setMinimumHeight(36)
        init_btn.clicked.connect(self.init_repo)
        btn_row.addWidget(init_btn)

        sl.addLayout(btn_row)

        # Status bar
        self.status = QtWidgets.QLabel("Ready")
        self.status.setProperty("class", "dim")
        sl.addWidget(self.status)

        self.check_status()

    def log_msg(self, msg):
        self.log.append(msg)
        QtWidgets.QApplication.processEvents()

    def run_git(self, args, check=False):
        r = _git_run(args, cwd=SITE_DIR, capture_output=True, text=True)
        if r is None:
            self.log_msg("ERROR: git not found on PATH")
            return None
        out = r.stdout.strip() or r.stderr.strip()
        if out:
            self.log_msg(f"$ git {' '.join(args)}\n{out}")
        return r

    def save_config_fields(self):
        save_setup_config(
            self.remote_input.text().strip(),
            self.name_input.text().strip(),
            self.email_input.text().strip(),
            self.msg_input.text().strip(),
            self.auto_push_cb.isChecked(),
            self.supabase_url.text().strip(),
            self.supabase_key.text().strip(),
            self.comments_cb.isChecked(),
            self.site_title.text().strip(),
            self.token_input.text().strip(),
        )

    @QtCore.pyqtSlot()
    def on_generate(self):
        self.save_config_fields()
        self.log.clear()
        self.gen_btn.setEnabled(False)
        self.gen_btn.setText("Running...")

        new = {
            "supabase_url": self.supabase_url.text().strip(),
            "supabase_anon_key": self.supabase_key.text().strip(),
            "comments_enabled": self.comments_cb.isChecked(),
            "site_title": self.site_title.text().strip(),
            "git_remote_url": self.remote_input.text().strip(),
            "git_user_name": self.name_input.text().strip(),
            "git_user_email": self.email_input.text().strip(),
            "git_commit_message": self.msg_input.text().strip(),
            "git_auto_push": self.auto_push_cb.isChecked(),
            "github_token": self.token_input.text().strip(),
        }

        self.worker = _SetupWorker(new)
        self.worker.logged.connect(self.log_msg)
        self.worker.finished.connect(self._on_generate_done)
        self.worker.start()

    @QtCore.pyqtSlot(bool)
    def _on_generate_done(self, ok):
        self.gen_btn.setEnabled(True)
        self.gen_btn.setText("Generate & Push")
        if not ok:
            self.log_msg("[ERROR] Check output above.")

    def check_status(self):
        lines = get_git_status()
        self.status_box.setPlainText("\n".join(lines) if lines else "(no status)")
        self.status.setText("Status refreshed")

    def init_repo(self):
        self.save_config_fields()
        self.log_msg("Initializing git repository...")
        if is_git_repo():
            self.log_msg("Already a git repository")
        else:
            r = self.run_git(["init"])
            if r and r.returncode == 0:
                self.log_msg("Repository initialized")
        self.run_git(["config", "user.name", self.name_input.text().strip()])
        self.run_git(["config", "user.email", self.email_input.text().strip()])
        url = self.remote_input.text().strip()
        if url:
            r = self.run_git(["remote", "get-url", "origin"])
            if r and r.returncode == 0:
                self.run_git(["remote", "set-url", "origin", url])
            else:
                self.run_git(["remote", "add", "origin", url])
        # Ensure .gitignore exists
        gi = os.path.join(SITE_DIR, ".gitignore")
        if not os.path.exists(gi):
            with open(gi, "w") as f:
                f.write("# MS Word\n*.doc\n*.docx\n*.dot\n*.dotx\n*.docm\n*.dotm\n# Local config (contains tokens, never commit)\nconfig.local.json\n# Build\nbuild_venv/\n*.spec\ndist/\n")
            self.log_msg("Created .gitignore")
        self.check_status()
        self.status.setText("Init complete")

    def stage_commit(self):
        self.save_config_fields()
        if not is_git_repo():
            self.log_msg("Not a git repo. Click 'Init Repo' first.")
            self.status.setText("Failed: not a repo")
            return
        self.log_msg("Staging all files...")
        r = self.run_git(["add", "-A"])
        if r and r.returncode != 0:
            self.status.setText("Stage failed")
            return
        msg = self.msg_input.text().strip() or "update site"
        self.log_msg(f"Committing: {msg}")
        r = self.run_git(["commit", "-m", msg])
        if r and r.returncode == 0:
            self.status.setText("Commit succeeded")
        elif r and r.returncode != 0:
            if "nothing to commit" in (r.stdout + r.stderr):
                self.status.setText("Nothing to commit")
            else:
                self.status.setText("Commit failed")
        self.check_status()
        if self.auto_push_cb.isChecked() and r and r.returncode == 0:
            self.push()

    def push(self):
        self.save_config_fields()
        cfg = load_config()
        url = cfg.get("git_remote_url", "")
        token = cfg.get("github_token", "")
        push_url = _make_push_url(url, token)
        orig = None
        if push_url != url:
            r = _git_run(["remote", "get-url", "origin"], cwd=SITE_DIR, capture_output=True, text=True)
            if r and r.returncode == 0:
                orig = r.stdout.strip()
            self.log_msg("Using token-authenticated remote URL")
            _git_run(["remote", "set-url", "origin", push_url], cwd=SITE_DIR, capture_output=True)
        r = self.run_git(["remote", "get-url", "origin"])
        if not r or r.returncode != 0:
            self.log_msg("No remote configured. Set Remote URL first.")
            self.status.setText("Push failed: no remote")
            return
        self.log_msg("Pushing to origin...")
        r = self.run_git(["push", "-u", "origin", "HEAD"])
        if r and r.returncode == 0:
            self.status.setText("Push succeeded")
        else:
            self.status.setText("Push failed")
        if orig:
            _git_run(["remote", "set-url", "origin", orig], cwd=SITE_DIR, capture_output=True)
        self.check_status()

class _SetupWorker(QtCore.QThread):
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


def main_gui():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    w.setWindowTitle("Setup")
    w.setMinimumSize(700, 600)
    layout = QtWidgets.QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(SetupGitWidget())
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main_gui()
