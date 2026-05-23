#!/usr/bin/env python3
import sys, os
from PyQt5 import QtWidgets

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Site Tools")
        self.setMinimumSize(900, 700)
        self.setStyleSheet("""
            QMainWindow { background: #1e1e1e; }
            QTabWidget::pane { background: #1e1e1e; border: none; }
            QTabBar::tab {
                background: #2a2a2a; color: #999; padding: 10px 20px;
                border: none; font-size: 13px; margin-right: 2px;
            }
            QTabBar::tab:selected { background: #1e1e1e; color: #eee; }
            QTabBar::tab:hover { color: #eee; }
        """)

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


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
