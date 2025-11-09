import sys, os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget

from _baseWindow import BaseWindow
from _reorder import ReorderPagesWindow
from _resize import ResizePdfWindow
from _extract import ExtractPagesWindow
from _interleave import InterleavePagesWindow
from _normalize import NormalizePagesWindow

class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__("LocalPDF", 400)

        # Layout setup
        layout = QVBoxLayout()
        layout_trash = QHBoxLayout()
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

        # button for cleaning up unnecessary data
        button_trash = QPushButton("", self)
        button_trash.setStatusTip("Remove all unnecessary data")  
        button_trash.clicked.connect(self.remove_temp_files)
        button_trash.setFixedWidth(40)
        button_trash.setFixedHeight(40)
        button_trash.setIcon(QIcon(self.resource_path("icon/bin-metal-full.png")))
        layout_trash.addWidget(button_trash)
        # label to show progress        
        self.label_status = QLabel("", self)
        layout_trash.addWidget(self.label_status)
        layout.addLayout(layout_trash)

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
        base_path = self.resource_path("created_images")
        
        #if not os.path.exists(base_path):
            #self.label_status.setText(f"No temporary folder found at:\n{base_path} ❌")
            #return

        removed_any = False
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path) and item.startswith("run_"):
                try:
                    self.delete_folder(item_path)
                    removed_any = True
                except Exception as e:
                    self.label_status.setText(f"Error deleting folder {item_path}: {e}")
        
        if removed_any:
            self.label_status.setText('<span style="color: green;">Completed ✅</span>')
        else:
            self.label_status.setText('<span style="color: red;">No temporary folders found ❌</span>')

    # Recursively delete folder contents and the folder itself.
    def delete_folder(self, folder_path):
        for entry in os.listdir(folder_path):
            entry_path = os.path.join(folder_path, entry)
            if os.path.isdir(entry_path):
                self.delete_folder(entry_path)  # recursive deletion for subfolders
            else:
                os.remove(entry_path)
        os.rmdir(folder_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()