import sys, os, json

import fitz
from pypdf import PdfWriter, PdfReader

from datetime import datetime
from PyQt6 import QtCore
from PyQt6.QtCore import QEvent, Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QPalette
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QMessageBox, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QMainWindow, QToolBar, QStatusBar
)

from _viewer import PDFViewer
from _toolbar import EditToolbar
from _menubar import MenuBar

class MainWindow(QMainWindow):
    def __init__(self):
        # initiate global variables for tracking progress and status
        self.setting_file = self.resource_path("settings.json")
        self.load_settings(self.setting_file)
        self.isEmpty = True
        self.isModified = False

        self.img_wd = self.resource_path("temp_images")
        self.clear_temp_images(self.img_wd)  # Clear temp images on startup

        self.image_lib = {}  # dict to match key to pdf_file
        self.changes_made = {"rotate": {}}  # dict to track changes made to the PDF file

        # get screen size and set window size to 1/3 of it
        #   big: 1920x1032px (PC)
        #  small: 1280x752px (Laptop)
        self.screen = QApplication.primaryScreen().availableGeometry()
        if self.screen.width() < 1500:
            minWidth = self.screen.width() // 2
            minHeight = self.screen.height() // 2
        elif self.screen.width() < 2000:
            minWidth = self.screen.width() // 3
            minHeight = self.screen.height() // 3
        if self.window_size[0] is not None and self.window_size[1] is not None:
            width, height = self.window_size
        else:
            width, height = minWidth, minHeight

        super().__init__()
        self.setWindowTitle("LocalPDF")
        self.setMinimumWidth(minWidth)
        self.setMinimumHeight(minHeight)
        self.resize(width, height)
        self.setWindowIcon(QIcon(self.resource_path("icon/document-pdf-text.png")))
        self.setStatusBar(QStatusBar(self))

        if not self.isWindowed:
            super().showMaximized()  # Ensure the main window is a top-level window

        # setup complete Program
        self.menu = MenuBar(self)
        self.setGUI()

    # region ========== Work with global settings ==========
    def load_settings(self, setting_file: str) -> None:
        """ Load settings from file or set defaults """
        if os.path.exists(setting_file):
            with open(setting_file, "r") as f:
                settings = json.load(f)
                self.lookup_path = settings.get("lookup_path", "C:/Users/USER/Downloads")
                self.isWindowed = settings.get("windowed", True)
                self.viewer_icon_size = settings.get("viewer_icon_size", [300, 300])
                self.window_size = settings.get("window_size", [None, None])
        else:
            self.lookup_path = "C:/Users/USER/Downloads"
            self.isWindowed = True
            self.viewer_icon_size = [300, 300]
            self.window_size = [None, None]
            with open(setting_file, "w") as f:
                json.dump({"lookup_path": self.lookup_path, 
                           "windowed": self.isWindowed, 
                           "viewer_icon_size": self.viewer_icon_size,
                           "window_size": self.window_size}, f)

    def update_settings(self, 
                        lookup_path: str = None, 
                        windowed: bool = None, 
                        viewer_settings: dict = None,
                        window_size: list = None) -> None:
        """ Update settings and save to file """
        if lookup_path is not None:
            self.lookup_path = lookup_path
        if windowed is not None:
            self.isWindowed = windowed
        if viewer_settings is not None:
            self.viewer_icon_size = viewer_settings
        if window_size is not None:
            self.window_size = window_size

        with open(self.setting_file, "w") as f:
            json.dump({"lookup_path": self.lookup_path, 
                       "windowed": self.isWindowed, 
                       "viewer_icon_size": self.viewer_icon_size,
                       "window_size": self.window_size}, f)

    def changeEvent(self, event):
        """ Handle window state changes to update isWindowed setting """
        super().changeEvent(event)
        
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMaximized():
                self.isWindowed = False
            else:
                self.isWindowed = True
            # Save the updated setting to file
            self.update_settings(windowed=self.isWindowed)
    def resizeEvent(self, event):
        """Handle window resizing in windowed mode to update saved window size."""
        super().resizeEvent(event)

        if self.isWindowed:
            self.update_settings(window_size=[self.width(), self.height()])

    def get_lookup(self) -> str:
        """ Get the current working directory """
        return self.lookup_path
    def set_lookup(self, path: str) -> None:
        """ Set the working directory and save to settings """
        self.lookup_path = path
        self.update_settings(lookup_path=path)

    def clear_image_lib(self) -> None:
        """ Clear the image library dictionary """
        self.image_lib = {}
    # endregion

    # region ========== Setup GUI ==========
    def setGUI(self) -> None:
        """" Set GUI elements and layout """

            ########################## Set opennig screen
        self.central = QWidget()
        self.setCentralWidget(self.central)
        layout = QVBoxLayout()
        self.central.setLayout(layout)
        start_button = QPushButton("Open PDF to get started", self)
        start_button.setStatusTip("Open a PDF file to get started")
        start_button.clicked.connect(self.menu.open_pdf)
        start_button.setFixedHeight(40)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

            ########################## Viewer for showing the PDF file
        self.viewer = PDFViewer(self, wd = self.img_wd)
        self.viewer.setIconSize(QSize(self.viewer_icon_size[0], self.viewer_icon_size[1]))
        self.viewer.setGridSize(QSize(self.viewer_icon_size[0], self.viewer_icon_size[1] + 10))
        self.viewer.hide()  # Hide the viewer until a PDF is loaded

            ########################## Right toolbar for functions
        self.toolbar = EditToolbar(parent = self)
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.toolbar)

        self.toolbar.hide()  # Hide the toolbar until a PDF is loaded
    # endregion

    # region ========== File Operations ==========
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and PyInstaller"""
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            base_path = sys._MEIPASS
        else:
            # Running normally
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def clear_temp_images(self, img_wd: str) -> None:
        """ Remove all images from the temp_images folder """
        if os.path.exists(img_wd):
            for filename in os.listdir(img_wd):
                file_path = os.path.join(img_wd, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
        else:
            os.makedirs(img_wd)  # Create the folder if it doesn't exist
    # endregion

    # region ========== Viewer Operations ==========
    def extract_images(self, key: str, pdf_path: str) -> None:
        """ Extract images from the viewer and add them to the temp_folder, then return the list of image paths """
        if not pdf_path: return None
        doc = fitz.open(pdf_path)
        img_list = []
        for i in range(doc.page_count):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))  # Scale the image for better quality
            file = f"/{key}_page_{i}.png"
            img_list.append(file)
            output = f"{self.img_wd}/{file}"
            pix.save(output)
        doc.close()
        self.viewer.add_images(img_list)
        return None
    # endregion
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()