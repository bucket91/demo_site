#!/usr/bin/env python3
import sys, os, json
from PyQt5 import QtWidgets, QtCore

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        import bootstrap
        created = bootstrap.ensure_site_files(SITE_DIR)
        if created:
            print(f"Created missing files: {', '.join(created)}")

        from wysiwyg_editor import _ensure_ckeditor
        _ensure_ckeditor()

        self._check_first_run()

        self.setWindowTitle("Site Tools")
        self.setMinimumSize(900, 700)

        tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(tabs)

        import design_tab
        design_tab.SITE_DIR = SITE_DIR
        tabs.addTab(design_tab.DesignWidget(), "Design")

        import content_tab
        content_tab.SITE_DIR = SITE_DIR
        self.content_widget = content_tab.ContentWidget()
        tabs.addTab(self.content_widget, "Content")

        import advanced_theme_tab
        advanced_theme_tab.SITE_DIR = SITE_DIR
        tabs.addTab(advanced_theme_tab.AdvancedThemeTab(), "Advanced")

        import setup_git
        setup_git.SITE_DIR = SITE_DIR
        tabs.addTab(setup_git.SetupGitWidget(), "Settings")

        import admin
        tabs.addTab(admin.CommentAdminWidget(), "Comments")

        import docs
        tabs.addTab(docs.DocsWidget(), "Help")

        self.statusBar().showMessage(
            "Ready. Customize your site in Design, add content in Content, configure in Settings.")
        tabs.setCurrentIndex(0)

    def _check_first_run(self):
        local_path = os.path.join(SITE_DIR, "config.local.json")
        if os.path.exists(local_path):
            with open(local_path, encoding="utf-8") as f:
                local = json.load(f)
            if local.get("github_token", ""):
                return

        # First run: wipe personal info from config.json so tabs load clean
        cfg_path = os.path.join(SITE_DIR, "config.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)
            for k in ["owner_name", "owner_bio", "owner_title",
                       "owner_contacts", "supabase_url", "supabase_anon_key",
                       "git_remote_url", "git_user_name", "git_user_email",
                       "github_token"]:
                cfg.pop(k, None)
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)

        import first_run
        first_run.SITE_DIR = SITE_DIR
        wizard = first_run.FirstRunWizard(self)
        if wizard.exec_() == QtWidgets.QDialog.Accepted:
            self._auto_init_git()

    def _auto_init_git(self):
        from git_util import git_run
        cfg_path = os.path.join(SITE_DIR, "config.json")
        if not os.path.exists(cfg_path):
            return
        with open(cfg_path, encoding="utf-8") as f:
            cfg = json.load(f)
        name = cfg.get("git_user_name", "")
        email = cfg.get("git_user_email", "")
        url = cfg.get("git_remote_url", "")
        if not name or not url:
            return
        git_run(["init"], cwd=SITE_DIR)
        if name:
            git_run(["config", "user.name", name], cwd=SITE_DIR)
        if email:
            git_run(["config", "user.email", email], cwd=SITE_DIR)
        if url:
            r = git_run(["remote", "get-url", "origin"], cwd=SITE_DIR, capture_output=True)
            if r and r.returncode == 0:
                git_run(["remote", "set-url", "origin", url], cwd=SITE_DIR)
            else:
                git_run(["remote", "add", "origin", url], cwd=SITE_DIR)
        gi = os.path.join(SITE_DIR, ".gitignore")
        if not os.path.exists(gi):
            with open(gi, "w", encoding="utf-8") as f:
                f.write("# MS Word\n*.doc\n*.docx\n*.dot\n*.dotx\n*.docm\n*.dotm\n# Local config (contains tokens, never commit)\nconfig.local.json\n# Build\nbuild_venv/\n*.spec\ndist/\n")



def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts, True)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    import gui_theme
    gui_theme.SITE_DIR = SITE_DIR
    gui_theme.apply()

    w = App()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
