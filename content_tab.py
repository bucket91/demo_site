import os, sys
from PyQt5 import QtWidgets, QtCore

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))


class ContentWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        container = QtWidgets.QWidget()
        container.setStyleSheet("background: transparent;")
        cl = QtWidgets.QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        import docx2html
        docx2html.SITE_DIR = SITE_DIR
        self.import_widget = docx2html.ImportWidget()
        cl.addWidget(self.import_widget)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setStyleSheet("background: #333; max-height: 1px;")
        cl.addWidget(sep)

        import ref_manager
        ref_manager.SITE_DIR = SITE_DIR
        import sidebar_util
        sidebar_util.SITE_DIR = SITE_DIR
        self.mgr_widget = ref_manager.RefManagerWidget()
        cl.addWidget(self.mgr_widget)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        self.import_widget.navigate_to_management.connect(
            lambda path, cat: self.mgr_widget.refresh_all())
