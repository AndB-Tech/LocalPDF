import sys, os
from pypdf import PdfWriter, PdfReader
from itertools import zip_longest
from PyQt6.QtCore import (
    QSize, 
    Qt,
    pyqtSlot
)
from PyQt6.QtGui import (
    QIcon
)
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton, 
    QLabel, 
    QVBoxLayout, 
    QHBoxLayout,
    QWidget,
    QStatusBar,
    QFileDialog,
    QLineEdit,
    QGraphicsOpacityEffect,
    QMessageBox,
    QDoubleSpinBox
)


class BaseWindow(QMainWindow):
    """Base window class with shared setup."""
    def __init__(self, title: str, width: int):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedWidth(width)
        self.setWindowIcon(QIcon("./icon/document-pdf-text.png"))
        self.setStatusBar(QStatusBar(self))

class InterleavePagesWindow(BaseWindow):
    def __init__(self, parent=None):
        super().__init__("Interleave PDFs", 500)
        self.parent_window = parent

        # Initialize variables
        self.fname_uneven_link = None
        self.fname_even_link = None
        self.output_folder = "C:/Users/USER/Downloads"
        self.output_name = None
        self.full_output = "N/A"

        # Build UI
        layout = QVBoxLayout()
        layout_explorer = QVBoxLayout()
        layout_explorer_uneven = QHBoxLayout()
        layout_explorer_even = QHBoxLayout()
        layout_output1 = QVBoxLayout()
        layout_output2 = QHBoxLayout()
        layout_interleave = QHBoxLayout()

        # Choosing pdf file with uneven pages (1,3,5,...)
        label_uneven = QLabel("PDF-Scan with uneven page numbers:", self)
        label_uneven.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_explorer_uneven.addWidget(label_uneven)
        button_explore_uneven = QPushButton("Explore files", self)
        button_explore_uneven.setStatusTip("Open file explorer to select PDF files with uneven page numbers")   
        button_explore_uneven.clicked.connect(self.explore_files_uneven)
        button_explore_uneven.setFixedWidth(120)
        layout_explorer_uneven.addWidget(button_explore_uneven)
        layout_explorer.addLayout(layout_explorer_uneven)
        self.label_uneven_file = QLabel("No file selected", self)
        self.label_uneven_file.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout_explorer.addLayout(layout_explorer_uneven)
        layout_explorer.addWidget(self.label_uneven_file)
        # Choosing pdf file with even pages (2,4,6,...)
        label_even = QLabel("PDF-Scan with even page numbers:", self)
        label_even.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_explorer_even.addWidget(label_even)
        button_explore_even = QPushButton("Explore files", self)
        button_explore_even.setStatusTip("Open file explorer to select PDF files with even page numbers")   
        button_explore_even.clicked.connect(self.explore_files_even)
        button_explore_even.setFixedWidth(120)
        layout_explorer_even.addWidget(button_explore_even) 
        layout_explorer.addLayout(layout_explorer_even)
        self.label_even_file = QLabel("No file selected", self)
        self.label_even_file.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout_explorer.addWidget(self.label_even_file)
        layout.addLayout(layout_explorer)

        # label for the button choosing the output folder and output name
        label_output = QLabel("Output:", self)
        effect = QGraphicsOpacityEffect(label_output)
        effect.setOpacity(0.4)
        label_output.setGraphicsEffect(effect)
        layout_output2.addWidget(label_output)
        # button to choose output folder and name
        button_output = QPushButton("Output Folder", self)
        button_output.clicked.connect(self.set_output_folder)
        button_output.setStatusTip("Select the folder to save the interleaved PDF")
        button_output.setEnabled(False)
        effect = QGraphicsOpacityEffect(button_output)
        effect.setOpacity(0.4)
        button_output.setGraphicsEffect(effect)
        layout_output2.addWidget(button_output)
        # input for output name
        input_output_name = QLineEdit()
        input_output_name.setPlaceholderText("Output File Name")
        input_output_name.setStatusTip("Enter the desired name for the output PDF file")
        input_output_name.textChanged.connect(self.assemble_full_output)
        input_output_name.setEnabled(False)
        effect = QGraphicsOpacityEffect(input_output_name)
        effect.setOpacity(0.4)
        input_output_name.setGraphicsEffect(effect)
        layout_output2.addWidget(input_output_name)
        layout_output1.addLayout(layout_output2)
        # label for whole output path
        self.label_full_output = QLabel("N/A", self)
        self.label_full_output.setAlignment(Qt.AlignmentFlag.AlignRight)
        effect = QGraphicsOpacityEffect(self.label_full_output)
        effect.setOpacity(0.4)
        self.label_full_output.setGraphicsEffect(effect) 
        layout_output1.addWidget(self.label_full_output)
        layout.addLayout(layout_output1)

        # label for spacing
        layout_output1.addSpacing(10)

        # button to start interleaving
        self.button_interleave = QPushButton("Interleave PDFs", self)
        self.button_interleave.setStatusTip("Start interleaving the selected PDF files")
        self.button_interleave.clicked.connect(self.start_interleaving)
        self.button_interleave.setEnabled(False)
        self.button_interleave.setFixedWidth(100)
        effect = QGraphicsOpacityEffect(self.button_interleave)
        effect.setOpacity(0.4)
        self.button_interleave.setGraphicsEffect(effect)
        layout_interleave.addWidget(self.button_interleave)
        # label for processing status
        self.label_status = QLabel("", self)
        layout_interleave.addWidget(self.label_status)
        layout.addLayout(layout_interleave)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # check if interface should be enabled
    def check_interface_elements(self):
        if self.fname_uneven_link and self.fname_even_link:
            self.show_interface_elements()
        else:
            self.hide_interface_elements()

    # explore files button handler
    @pyqtSlot()
    def explore_files_uneven(self):
        fname_uneven = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "C:/USERS/USER/DOWNLOADS",
            "PDF Files (*.pdf)",
        )
        if fname_uneven[0] != "":
            self.fname_uneven_link = fname_uneven[0]
            fname_uneven_file = self.fname_uneven_link.split("/")[-1] if self.fname_uneven_link else "No file selected"
            self.label_uneven_file.setText(fname_uneven_file)
            self.check_interface_elements()
        else:
            self.fname_uneven_link = None
            self.label_uneven_file.setText("No file selected")
            self.check_interface_elements()

    # explore files button handler
    @pyqtSlot()
    def explore_files_even(self):
        fname_even = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "C:/USERS/USER/DOWNLOADS",
            "PDF Files (*.pdf)",
        )
        if fname_even[0] != "":
            self.fname_even_link = fname_even[0]
            fname_even_file = self.fname_even_link.split("/")[-1] if self.fname_even_link else "No file selected"
            self.label_even_file.setText(fname_even_file)
            self.check_interface_elements()
        else:
            self.fname_even_link = None
            self.label_even_file.setText("No file selected")
            self.check_interface_elements()

    # set output folder button handler
    @pyqtSlot()
    def set_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            "C:/USERS/USER/DOWNLOADS"
        )
        if folder != "":
            self.output_folder = folder
        else:
            self.output_folder = "C:/Users/USER/Downloads"
        self.assemble_full_output()

    # assemble full output path and label
    def assemble_full_output(self, text: str = None):
        # If called from QLineEdit.textChanged, update internal output_name
        if text is not None:
            if text != "":
                if not text.strip().lower().endswith(".pdf"):
                    if text.strip().lower().endswith(".pd"):
                        text += "f"
                    elif text.strip().lower().endswith(".p"):
                        text += "df"
                    elif text.strip().lower().endswith("."):
                        text += "pdf"
                    else:
                        text += ".pdf"
            self.output_name = text

        # Safely build the full output path/label
        folder = self.output_folder or ""
        name = self.output_name or ""

        if not folder and not name:
            self.full_output = "N/A"
        else:
            # ensure single separator between folder and name
            sep = ""
            if folder and name:
                sep = "/" if not folder.endswith("/") else ""
            self.full_output = f"{folder}{sep}{name}"

        self.label_full_output.setText(self.full_output)

    # show/hide interface elements
    def show_interface_elements(self):
        for widget in self.findChildren((QLineEdit, QPushButton, QLabel, QDoubleSpinBox)):
            effect = widget.graphicsEffect()
            if effect and isinstance(effect, QGraphicsOpacityEffect):
                widget.setEnabled(True)
                effect.setOpacity(1.0)
                widget.setGraphicsEffect(effect)
    def hide_interface_elements(self):
        for widget in self.findChildren((QLineEdit, QPushButton, QLabel, QDoubleSpinBox)):
            effect = widget.graphicsEffect()
            if effect and isinstance(effect, QGraphicsOpacityEffect):
                widget.setEnabled(False)
                effect.setOpacity(0.4)
                widget.setGraphicsEffect(effect)

    # --- Override close event to show parent window ---
    def closeEvent(self, event):
        if self.parent_window:
            self.parent_window.show()
        event.accept()

    # clean inputs and validate before starting
    def clean_inputs(self, file_even, file_uneven, file_out):
        safe = True
        # check file_even
        file_even = file_even.strip()
        if not isinstance(file_even, str) or \
            not os.path.isfile(file_even) or \
            not file_even.lower().endswith(".pdf"):
            safe = False
        # check file_uneven
        file_uneven = file_uneven.strip()
        if not isinstance(file_uneven, str) or \
            not os.path.isfile(file_uneven) or \
            not file_uneven.lower().endswith(".pdf"):
            safe = False
        # check file_uneven != file_even
        if file_uneven == file_even:
            safe = False
        # check file_out
        file_out = file_out.strip()
        if not isinstance(file_out, str) or not file_out or not file_out.endswith(".pdf"):
            safe = False
        return safe, file_even, file_uneven, file_out

    # start interleaving button handler
    @pyqtSlot()
    def start_interleaving(self):
        file_even = self.fname_even_link
        file_uneven = self.fname_uneven_link
        file_out = self.full_output

        # Validate inputs
        self.label_status.setText("Checkig inputs...")
        QApplication.processEvents()  # Update UI
        safe, file_even, file_uneven, file_out = self.clean_inputs(file_even, file_uneven, file_out)
        if not safe:
            self.label_status.setText("❌ Ungültige Eingaben...")
            QApplication.processEvents()  # Update UI
            return

        # Interleave PDFs
        self.label_status.setText("Interleaving PDFs...")
        QApplication.processEvents()  # Update UI
        
        reader_uneven = PdfReader(file_uneven)
        reader_even = PdfReader(file_even)
        merger = PdfWriter()

        # Interleave pages (handles uneven lengths too)
        for odd, even in zip_longest(reader_uneven.pages, reader_even.pages):
            if odd:
                merger.add_page(odd)
            if even:
                merger.add_page(even)

        self.label_status.setText("Completed ✅")
        merger.write(file_out)
        merger.close()

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Interleaving Completed")
        dlg.setFixedWidth(400)
        dlg.setText(f"Interleaving completed successfully!\n\nOutput file:\n{file_out}")
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.exec()

        return