import sys, os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QVBoxLayout, QWidget, QStatusBar
)

from _reorder import ReorderPagesWindow
from _resize import ResizePdfWindow
from _extract import ExtractPagesWindow
from _interleave import InterleavePagesWindow
from _normalize import NormalizePagesWindow

class BaseWindow(QMainWindow):
    """Base window class with shared setup."""
    def __init__(self, title: str, width: int):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedWidth(width)
        self.setWindowIcon(QIcon("./icon/document-pdf-text.png"))
        self.setStatusBar(QStatusBar(self))

class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__("LocalPDF", 400)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self._create_label("Choose your poison"))

        # Button definitions: (label, tooltip, handler)
        buttons = [
            ("Reorder Pages", "Reorder pages in one or more PDF file", self.reorder_pages),
            ("Extract Pages", "Extract single pages from a longer PDF", self.extract_pages),
            ("Interleave Scans", "Take two PDFs and interleave their pages", self.interleave_scans),
            ("Reduce PDF Size", "Reduce the file size of a PDF to a specific target size", self.reduce_size),
            ("Normalize Pages", "Normaliez all pages of a PDF to the same height and width", self.normalize_pages),
        ]

        for text, tip, func in buttons:
            layout.addWidget(self._create_button(text, tip, func))

        button_trash = QPushButton("", self)
        button_trash.setStatusTip("Remove all unnecessary data")  
        button_trash.clicked.connect(self.remove_temp_files)
        button_trash.setFixedWidth(40)
        button_trash.setFixedHeight(40)
        button_trash.setIcon(QIcon("./icon/bin-metal-full.png"))
        layout.addWidget(button_trash)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # --- UI Helpers ---
    def _create_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setFixedHeight(40)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        return label

    def _create_button(self, text: str, tip: str, handler) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setStatusTip(tip)
        btn.clicked.connect(handler)
        return btn

    # --- Button handlers ---
    def interleave_scans(self):
        self.interleave_window = InterleavePagesWindow(self)
        self.interleave_window.show()
        self.hide()
        print("Interleaving scans...")  

    def extract_pages(self):
        self.extract_window = ExtractPagesWindow(self)
        self.extract_window.show()
        self.hide()
        print("Extracting pages...")

    def reduce_size(self):
        self.resize_window = ResizePdfWindow(self)
        self.resize_window.show()
        self.hide()
        print("Reducing PDF size...")

    def reorder_pages(self):
        self.reorder_window = ReorderPagesWindow(self)
        self.reorder_window.show()
        self.hide()
        print("Reordering pages...")
        
    def normalize_pages(self):
        self.reorder_window = NormalizePagesWindow(self)
        self.reorder_window.show()
        self.hide()
        print("Normalize pages...")

    # --- Functions --- 
    # remove all ./created_images/run_* folders
    def remove_temp_files(self):
        base_path="./created_images"
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                if item.startswith("run_"):
                    self.delete_folder(item_path)
        return

    # delete all files in the given folder
    def delete_folder(self, folder_path):
        for entry in os.listdir(folder_path):
            entry_path = os.path.join(folder_path, entry)
            os.remove(entry_path)
        os.rmdir(folder_path)
        return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()