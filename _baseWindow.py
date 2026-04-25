import sys, os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QStatusBar, QApplication
)

class BaseWindow(QMainWindow):
    """Base window class with shared setup."""
    def __init__(self, title: str):
        # get screen size and set window size to 1/3 of it
        #   big: 1920x1032px (PC)
        #  small: 1280x752px (Laptop)
        self.screen = QApplication.primaryScreen().availableGeometry()
        if self.screen.width() < 1500:
            width = self.screen.width() // 2
            height = self.screen.height() // 2
        elif self.screen.width() < 2000:
            width = self.screen.width() // 2
            height = self.screen.height() // 2

        #print(f"Screen size: {self.screen.width()}x{self.screen.height()}, Window size: {width}x{height}")

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