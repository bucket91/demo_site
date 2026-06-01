#!/usr/bin/env python3
import sys, os, json, traceback
from PyQt6 import QtWidgets, QtCore

_APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(_APP_DIR, "site")
SETTINGS_DIR = os.path.join(_APP_DIR, "settings")
REMOVED_DIR = os.path.join(_APP_DIR, "removed")
ROOT_CONFIG_FILE = os.path.join(_APP_DIR, "site_tools.config")

import error_log
error_log.setup(_APP_DIR)


class _AutoGenThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(str)

    def run(self):
        import generate
        generate.CONFIG.update(generate.load_config())
        try:
            generate.generate_all(log_func=lambda m: None)
            self.finished.emit("Site generated")
        except Exception as e:
            self.finished.emit(f"Generation error: {e}")


class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._gen_thread = None
        self._migrate_old_configs()

        import bootstrap
        created = bootstrap.ensure_site_files(SITE_DIR)
        if created:
            print(f"Created missing files: {', '.join(created)}")
            from theme_customizer import regenerate_style_css
            regenerate_style_css(SITE_DIR, SETTINGS_DIR)

        self._check_secrets_in_site_dir()

        from wysiwyg_editor import _ensure_ckeditor
        _ensure_ckeditor()

        self._check_first_run()

        self.setWindowTitle("Site Tools")
        self.setMinimumSize(900, 700)

        tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(tabs)

        import design_tab
        design_tab.SITE_DIR = SITE_DIR
        self.design_widget = design_tab.DesignWidget()
        tabs.addTab(self.design_widget, "Design")

        import content_tab
        content_tab.SITE_DIR = SITE_DIR
        content_tab._APP_DIR = _APP_DIR
        self.content_widget = content_tab.ContentWidget()
        tabs.addTab(self.content_widget, "Content")

        from wysiwyg_editor import CkeditorTab
        self.ckeditor_tab = CkeditorTab()
        tabs.addTab(self.ckeditor_tab, "CKeditor")

        from preview_tab import PreviewTab
        self.preview_tab = PreviewTab()
        tabs.addTab(self.preview_tab, "Preview")

        import advanced_theme
        advanced_theme.SITE_DIR = SITE_DIR
        advanced_theme.SETTINGS_DIR = SETTINGS_DIR
        import advanced_theme_tab
        tabs.addTab(advanced_theme_tab.AdvancedThemeTab(), "Advanced")

        import setup_git
        setup_git.SITE_DIR = SITE_DIR
        tabs.addTab(setup_git.PublishingWidget(), "Publishing")

        import admin
        tabs.addTab(admin.CommentAdminWidget(), "Comments")

        import docs
        tabs.addTab(docs.DocsWidget(), "Help")

        self.statusBar().showMessage(
            "Ready. Customize your site in Design, add content in Content, preview in Preview.")
        tabs.setCurrentIndex(0)
        tabs.currentChanged.connect(self._on_tab_changed)

        self._debounce_timer = QtCore.QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._auto_generate)

        self.content_widget.mgr_widget.content_changed.connect(self._on_content_changed)
        self.content_widget.mgr_widget.open_in_ckeditor.connect(self._on_open_in_ckeditor)
        self.design_widget.settings_changed.connect(self._on_content_changed)
        self._auto_generate()

    def _migrate_old_configs(self):
        old_cfg = os.path.join(SITE_DIR, "config.json")
        new_cfg = os.path.join(SETTINGS_DIR, "config.json")
        old_local = os.path.join(SITE_DIR, "config.local.json")
        old_adv = os.path.join(SITE_DIR, "advanced_theme.json")
        new_adv = os.path.join(SETTINGS_DIR, "advanced_theme.json")

        os.makedirs(SETTINGS_DIR, exist_ok=True)
        os.makedirs(REMOVED_DIR, exist_ok=True)

        if os.path.exists(old_cfg) and not os.path.exists(new_cfg):
            with open(old_cfg, encoding="utf-8") as f:
                old_data = json.load(f)
            token_keys = {"supabase_url", "supabase_anon_key", "git_remote_url",
                           "git_user_name", "git_user_email", "github_token"}
            tokens = {k: old_data[k] for k in token_keys if k in old_data and old_data[k]}
            settings = {k: v for k, v in old_data.items() if k not in token_keys}
            with open(new_cfg, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            if tokens:
                existing = {}
                if os.path.exists(ROOT_CONFIG_FILE):
                    with open(ROOT_CONFIG_FILE, encoding="utf-8") as f:
                        existing = json.load(f)
                existing.update(tokens)
                with open(ROOT_CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(existing, f, indent=2)
            os.remove(old_cfg)

        if os.path.exists(old_local):
            with open(old_local, encoding="utf-8") as f:
                local_data = json.load(f)
            existing = {}
            if os.path.exists(ROOT_CONFIG_FILE):
                with open(ROOT_CONFIG_FILE, encoding="utf-8") as f:
                    existing = json.load(f)
            existing.update(local_data)
            with open(ROOT_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2)
            os.remove(old_local)

        if os.path.exists(old_adv) and not os.path.exists(new_adv):
            os.rename(old_adv, new_adv)

    def _check_secrets_in_site_dir(self):
        suspicious = []
        for root, _dirs, files in os.walk(SITE_DIR):
            for f in files:
                if any(pat in f.lower() for pat in ["token", "secret", "site_tools.config"]):
                    suspicious.append(os.path.join(root, f))
        if suspicious:
            msg = "WARNING: The following files containing secret-like names were found inside the site/ folder:\n\n"
            msg += "\n".join(suspicious)
            msg += "\n\nThese files will be COMMITTED to git when you publish. Move them outside site/ to keep them safe."
            print(msg)
            QtWidgets.QMessageBox.warning(self, "Security Warning", msg)

    def _check_first_run(self):
        if os.path.exists(ROOT_CONFIG_FILE):
            with open(ROOT_CONFIG_FILE, encoding="utf-8") as f:
                tokens = json.load(f)
            if tokens.get("github_token", ""):
                return

        import first_run
        first_run.SITE_DIR = SITE_DIR
        wizard = first_run.FirstRunWizard(self)
        if wizard.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self._auto_init_git()

    def _auto_init_git(self):
        from git_util import git_run
        cfg = {}
        cfg_path = os.path.join(SETTINGS_DIR, "config.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, encoding="utf-8") as f:
                cfg.update(json.load(f))
        if os.path.exists(ROOT_CONFIG_FILE):
            with open(ROOT_CONFIG_FILE, encoding="utf-8") as f:
                cfg.update(json.load(f))
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
                f.write("__pycache__/\n")
        from bootstrap import _ensure_precommit_hook
        _ensure_precommit_hook(SITE_DIR)

    def _auto_generate(self):
        if self._gen_thread and self._gen_thread.isRunning():
            return
        self.statusBar().showMessage("Generating site...")
        self._gen_thread = _AutoGenThread()
        self._gen_thread.finished.connect(self._on_gen_done)
        self._gen_thread.start()

    def _on_gen_done(self, msg):
        self.statusBar().showMessage(msg)
        self._gen_thread = None

    def closeEvent(self, event):
        if self._gen_thread and self._gen_thread.isRunning():
            self._gen_thread.quit()
            self._gen_thread.wait(2000)
        event.accept()

    def _on_content_changed(self):
        self._debounce_timer.start(400)

    def _on_open_in_ckeditor(self, file_path):
        self.ckeditor_tab.load_file(file_path)
        tabs = self.centralWidget()
        for i in range(tabs.count()):
            if tabs.tabText(i) == "CKeditor":
                tabs.setCurrentIndex(i)
                break

    def _on_tab_changed(self, idx):
        sender = self.sender()
        if sender and sender.tabText(idx) == "Preview":
            self.preview_tab.load_site()


def main():
    try:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle("Fusion")

        import gui_theme
        gui_theme.SITE_DIR = SITE_DIR
        gui_theme.apply()

        w = App()
        w.show()
        error_log.info("UI ready, entering event loop")
        sys.exit(app.exec())
    except Exception:
        error_log.critical("Fatal startup error:\n" + traceback.format_exc())
        raise

if __name__ == "__main__":
    main()
