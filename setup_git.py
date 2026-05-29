#!/usr/bin/env python3
"""Git setup widget for Site Tools."""
import os, sys, json
from PyQt5 import QtWidgets, QtCore
from git_util import is_git_available as _git_available, git_run as _git_run, _make_push_url, _extract_github_user
from generate import load_config, save_config

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SITE_DIR, "config.json")
LOCAL_CONFIG_FILE = os.path.join(SITE_DIR, "config.local.json")


def save_setup_config(url, token, supabase_url, supabase_anon_key):
    cfg = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as f:
            cfg = json.load(f)
    cfg.update(git_remote_url=url,
               supabase_url=supabase_url, supabase_anon_key=supabase_anon_key)
    cfg.pop("github_token", None)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    local_cfg = {}
    if os.path.exists(LOCAL_CONFIG_FILE):
        with open(LOCAL_CONFIG_FILE, encoding="utf-8") as f:
            local_cfg = json.load(f)
    local_cfg["github_token"] = token
    with open(LOCAL_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(local_cfg, f, indent=2)


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
            QLabel { color: #c9d1d9; }
            QLabel.dim { color: #6e7681; }
            QLabel.heading { font-weight: bold; color: #c9d1d9; margin-top: 8px; }
            QLineEdit {
                background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; padding: 8px 10px;
            }
            QTextEdit {
                background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; padding: 6px; font-family: monospace;
            }
            QPushButton {
                background: #21262d; color: #c9d1d9; border: none;
                border-radius: 6px; padding: 8px 16px;
            }
            QPushButton:hover { background: #30363d; }
            QPushButton:disabled { background: #30363d; color: #484f58; }
            QPushButton.primary { background: #58a6ff; }
            QPushButton.primary:hover { background: #79c0ff; }
            QPushButton.danger { background: #b71c1c; }
            QPushButton.danger:hover { background: #d32f2f; }
            QSpinBox {
                background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; padding: 6px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: #21262d; border: none; width: 24px;
            }
            QSpinBox::up-arrow {
                image: none; border-left: 5px solid transparent;
                border-right: 5px solid transparent; border-bottom: 6px solid #6e7681;
            }
            QSpinBox::down-arrow {
                image: none; border-left: 5px solid transparent;
                border-right: 5px solid transparent; border-top: 6px solid #6e7681;
            }
            QCheckBox { color: #c9d1d9; }
            QGroupBox {
                color: #c9d1d9; font-weight: bold;
                border: 1px solid #30363d; border-radius: 6px; margin-top: 12px;
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

        sl.addWidget(supabase_group)

        # ── Git ──
        git_group = QtWidgets.QGroupBox("GitHub / Git")
        gfl = QtWidgets.QFormLayout(git_group)
        gfl.setSpacing(6)
        gfl.setContentsMargins(10, 16, 10, 10)

        self.remote_input = QtWidgets.QLineEdit(cfg.get("git_remote_url", ""))
        self.remote_input.setPlaceholderText("https://github.com/user/repo.git")
        self.remote_input.textChanged.connect(self._on_remote_url_changed)
        gfl.addRow("Remote URL:", self.remote_input)

        self.token_input = QtWidgets.QLineEdit(cfg.get("github_token", ""))
        self.token_input.setPlaceholderText("ghp_xxxxxxxxxxxxxxxxxxxx  (NOT a GPG key)")
        self.token_input.setEchoMode(QtWidgets.QLineEdit.Password)
        gfl.addRow("GitHub Token:", self.token_input)

        sl.addWidget(git_group)

        # ── Side-by-side: Status + Output ──
        side = QtWidgets.QHBoxLayout()
        side.setSpacing(12)

        # Left: Status
        left = QtWidgets.QVBoxLayout()
        status_label = QtWidgets.QLabel("Status")
        status_label.setProperty("class", "dim")
        left.addWidget(status_label)
        self.status_box = QtWidgets.QTextEdit()
        self.status_box.setReadOnly(True)
        self.status_box.setMinimumHeight(130)
        left.addWidget(self.status_box, 1)
        side.addLayout(left, 1)

        # Right: Output
        right = QtWidgets.QVBoxLayout()
        log_label = QtWidgets.QLabel("Output:")
        log_label.setProperty("class", "dim")
        right.addWidget(log_label)
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Command output will appear here...")
        self.log.setMinimumHeight(130)
        right.addWidget(self.log, 1)
        side.addLayout(right, 1)

        sl.addLayout(side, 1)

        # Bottom row: Initialize | Refresh Status | Generate
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(8)

        init_btn = QtWidgets.QPushButton("Initialize")
        init_btn.setMinimumHeight(40)
        init_btn.clicked.connect(self.init_repo)
        btn_row.addWidget(init_btn)

        refresh_status_btn = QtWidgets.QPushButton("Refresh Status")
        refresh_status_btn.setMinimumHeight(40)
        refresh_status_btn.clicked.connect(self.check_status)
        btn_row.addWidget(refresh_status_btn)

        self.gen_btn = QtWidgets.QPushButton("Generate")
        self.gen_btn.setMinimumHeight(40)
        self.gen_btn.setProperty("class", "primary")
        self.gen_btn.clicked.connect(self.on_generate)
        btn_row.addWidget(self.gen_btn)

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
            self.token_input.text().strip(),
            self.supabase_url.text().strip(),
            self.supabase_key.text().strip(),
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
            "git_remote_url": self.remote_input.text().strip(),
            "github_token": self.token_input.text().strip(),
        }

        self.worker = _SetupWorker(new)
        self.worker.logged.connect(self.log_msg)
        self.worker.finished.connect(self._on_generate_done)
        self.worker.start()

    @QtCore.pyqtSlot(bool)
    def _on_generate_done(self, ok):
        self.gen_btn.setEnabled(True)
        self.gen_btn.setText("Generate")
        self.check_status()
        if not ok:
            self.log_msg("[ERROR] Check output above.")

    @QtCore.pyqtSlot(str)
    def _on_remote_url_changed(self, url):
        user = _extract_github_user(url)
        if user:
            cfg = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, encoding="utf-8") as f:
                    cfg = json.load(f)
            if not cfg.get("git_user_name") and not cfg.get("git_user_email"):
                cfg["git_user_name"] = user
                cfg["git_user_email"] = f"{user}@users.noreply.github.com"
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=2)

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
        cfg = load_config()
        name = cfg.get("git_user_name", "")
        email = cfg.get("git_user_email", "")
        if name:
            self.run_git(["config", "user.name", name])
        if email:
            self.run_git(["config", "user.email", email])
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
            with open(gi, "w", encoding="utf-8") as f:
                f.write("# MS Word\n*.doc\n*.docx\n*.dot\n*.dotx\n*.docm\n*.dotm\n# Local config (contains tokens, never commit)\nconfig.local.json\n# Build\nbuild_venv/\n*.spec\ndist/\n")
            self.log_msg("Created .gitignore")
        self.check_status()
        self.status.setText("Init complete")

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
