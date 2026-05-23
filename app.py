#!/usr/bin/env python3
import sys, os
from PyQt5 import QtWidgets

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        import bootstrap
        created = bootstrap.ensure_site_files(SITE_DIR)
        if created:
            print(f"Created missing files: {', '.join(created)}")

        self.setWindowTitle("Site Tools")
        self.setMinimumSize(900, 700)

        tabs = QtWidgets.QTabWidget()
        tabs.tabBar().setExpanding(True)
        self.setCentralWidget(tabs)

        import gui
        tabs.addTab(gui.SiteGeneratorWidget(), "Site Generator")

        import admin
        tabs.addTab(admin.CommentAdminWidget(), "Comment Admin")

        import docx2html
        tabs.addTab(docx2html.DocxToHtmlWidget(), "Docx to HTML")

        import ref_manager
        tabs.addTab(ref_manager.RefManagerWidget(), "Reference Manager")

        import theme_customizer
        tabs.addTab(theme_customizer.ThemeCustomizerWidget(), "Theme Customizer")

        import docs
        tabs.addTab(docs.DocsWidget(), "Documentation")

        import setup_git
        tabs.addTab(setup_git.SetupGitWidget(), "Git Setup")

        import owner_tab
        tabs.addTab(owner_tab.OwnerWidget(), "Owner")


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
