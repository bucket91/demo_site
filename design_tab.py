import os, sys
from PyQt5 import QtWidgets, QtCore

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))


class DesignWidget(QtWidgets.QWidget):
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

        import owner_tab
        owner_tab.SITE_DIR = SITE_DIR
        self.owner_widget = owner_tab.OwnerWidget()
        cl.addWidget(self.owner_widget)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setStyleSheet("background: #333; max-height: 1px;")
        cl.addWidget(sep)

        import theme_customizer
        theme_customizer.SITE_DIR = SITE_DIR
        self.theme_widget = theme_customizer.ThemeCustomizerWidget()
        cl.addWidget(self.theme_widget)

        scroll.setWidget(container)
        layout.addWidget(scroll)
