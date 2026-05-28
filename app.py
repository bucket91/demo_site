#!/usr/bin/env python3
import sys, os, json
from PyQt5 import QtWidgets

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        import bootstrap
        created = bootstrap.ensure_site_files(SITE_DIR)
        if created:
            print(f"Created missing files: {', '.join(created)}")

        self._check_first_run()

        self.setWindowTitle("Site Tools")
        self.setMinimumSize(900, 700)

        tabs = QtWidgets.QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                padding: 0;
            }
            QTabBar::tab {
                padding: 8px 28px;
                margin: 0 1px;
                font-size: 13px;
            }
        """)
        self.setCentralWidget(tabs)

        import setup_git
        tabs.addTab(setup_git.SetupGitWidget(), "Setup")

        import owner_tab
        tabs.addTab(owner_tab.OwnerWidget(), "Owner")

        import docx2html
        self.docx_widget = docx2html.ImportWidget()
        tabs.addTab(self.docx_widget, "Import")

        import ref_manager
        self.ref_mgr = ref_manager.RefManagerWidget()
        tabs.addTab(self.ref_mgr, "Management")

        import theme_customizer
        tabs.addTab(theme_customizer.ThemeCustomizerWidget(), "Theme")

        import admin
        tabs.addTab(admin.CommentAdminWidget(), "Comments")

        import docs
        tabs.addTab(docs.DocsWidget(), "Help & Guide")

        self.statusBar().showMessage(
            "Welcome! Start with the Setup tab to configure git, site title, and Supabase.")
        tabs.setCurrentIndex(0)

        self.docx_widget.navigate_to_management.connect(
            lambda path: self._go_to_management(path, tabs))

    def _check_first_run(self):
        local_path = os.path.join(SITE_DIR, "config.local.json")
        if os.path.exists(local_path):
            with open(local_path) as f:
                local = json.load(f)
            if local.get("github_token", ""):
                return
        import first_run
        first_run.SITE_DIR = SITE_DIR
        wizard = first_run.FirstRunWizard(self)
        wizard.exec_()

    def _go_to_management(self, path, tabs):
        self.ref_mgr.set_file_path(path)
        tabs.setCurrentIndex(tabs.indexOf(self.ref_mgr))

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    import gui_theme
    gui_theme.apply()

    w = App()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
