import os, sys
from PyQt6 import QtWidgets

_APP_DIR = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(_APP_DIR, "site")


class ContentWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        import ref_manager
        ref_manager.SITE_DIR = SITE_DIR
        import sidebar_util
        sidebar_util.SITE_DIR = SITE_DIR
        self.mgr_widget = ref_manager.RefManagerWidget()
        layout.addWidget(self.mgr_widget)
