import sys, os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QStatusBar
)

class BaseWindow(QMainWindow):
    """Base window class with shared setup."""
    def __init__(self, title: str, width: int):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedWidth(width)
        self.setWindowIcon(QIcon(self.resource_path("icon/document-pdf-text.png")))
        self.setStatusBar(QStatusBar(self))

    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and PyInstaller"""
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            base_path = sys._MEIPASS
        else:
            # Running normally
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)