import os
from pypdf import PdfReader, PdfWriter, Transformation
from _baseWindow import BaseWindow
from PyQt6.QtCore import (
    Qt,
    pyqtSlot
)
from PyQt6.QtGui import (
    QShortcut,
    QKeySequence
)
from PyQt6.QtWidgets import (
    QApplication, 
    QPushButton, 
    QLabel, 
    QVBoxLayout, 
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QLineEdit,
    QGraphicsOpacityEffect,
    QMessageBox
)

class NormalizePagesWindow(BaseWindow):
    def __init__(self, parent=None):
        super().__init__("Normalize Pages", 400)
        self.parent_window = parent

        # Initialize variables
        self.fname_link = None
        self.output_folder = "C:/Users/USER/Downloads"
        self.output_name = None
        self.full_output = "N/A"

        # Build UI
        layout = QVBoxLayout()
        layout_explorer = QHBoxLayout()
        layout_output1 = QVBoxLayout()
        layout_output2 = QHBoxLayout()
        layout_output3 = QHBoxLayout()

        # Build Widgets
        # Explore Files Button
        button_explore = QPushButton("Explore Files", self)
        button_explore.setStatusTip("Open file explorer to select PDF file to normalize")   
        button_explore.clicked.connect(self.explore_files)
        button_explore.setFixedWidth(120)
        layout_explorer.addWidget(button_explore)
        # Label to show selected file
        self.label_file = QLabel("No file selected", self)
        layout_explorer.addWidget(self.label_file)
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
        button_output.setStatusTip("Select the folder to save the resized PDF")
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

        # empty space
        layout_output1.addSpacing(10)

        # button to start resizing
        button_start = QPushButton("Start Resizing", self)
        button_start.setStatusTip("Start normalizing the pages of the selected PDF")
        button_start.clicked.connect(self.normalize_pdf)  
        shortcut = QShortcut(QKeySequence("Return"), self)
        shortcut.activated.connect(button_start.click)
        button_start.setFixedWidth(120)
        button_start.setEnabled(False)
        effect = QGraphicsOpacityEffect(button_start)
        effect.setOpacity(0.4)
        button_start.setGraphicsEffect(effect) 
        layout_output3.addWidget(button_start)
        # update label
        self.label_status = QLabel("", self)
        layout_output3.addWidget(self.label_status)
        layout_output1.addLayout(layout_output3)
        layout.addLayout(layout_output1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def closeEvent(self, event):
        if self.parent_window:
            self.parent_window.show()
        event.accept()
    
    # explore files button handler
    @pyqtSlot()
    def explore_files(self):
        fname = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "C:/USERS/USER/DOWNLOADS",
            "PDF Files (*.pdf)",
        )
        if fname[0] != "":
            self.fname_link = fname[0]
            fname_file = self.fname_link.split("/")[-1] if self.fname_link else "No file selected"
            self.label_file.setText(fname_file)
            self.show_interface_elements()
        else:
            self.fname_link = None
            self.label_file.setText("No file selected")
            self.hide_interface_elements()

    # show/hide interface elements
    def show_interface_elements(self):
        for widget in self.findChildren((QLineEdit, QPushButton, QLabel)):
            effect = widget.graphicsEffect()
            if effect and isinstance(effect, QGraphicsOpacityEffect):
                widget.setEnabled(True)
                effect.setOpacity(1.0)
                widget.setGraphicsEffect(effect)
    def hide_interface_elements(self):
        for widget in self.findChildren((QLineEdit, QPushButton, QLabel)):
            effect = widget.graphicsEffect()
            if effect and isinstance(effect, QGraphicsOpacityEffect):
                widget.setEnabled(False)
                effect.setOpacity(0.4)
                widget.setGraphicsEffect(effect)

    # set output folder
    @pyqtSlot()
    def set_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            "C:/USERS/USER/DOWNLOADS",
        )
        if folder != "":
            self.output_folder = folder
        else:
            self.output_folder = "C:/Users/USER/Downloads"
        self.assemble_full_output()

    # update full output label
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
    
    # function to check all inputs are valid
    def clean_inputs(self, file_in, file_out):
        safe = True
        # check file_in
        file_in = file_in.strip()
        if not isinstance(file_in, str) or \
            not os.path.isfile(file_in) or \
            not file_in.lower().endswith(".pdf"):
            safe = False
        # check file_out
        file_out = file_out.strip()
        if not isinstance(file_out, str) or not file_out or not file_out.endswith(".pdf"):
            safe = False
        return safe, file_in, file_out

    # take the in-file and resize all pages to the same size
    def normalize_pdf(self):
        file_in = self.fname_link
        file_out = self.full_output

        # clean all inputs
        safe, file_in, file_out = self.clean_inputs(file_in, file_out)
        if not safe:
            self.label_update.setText("❌ Invalid Inputs. Canceling Normalization.")
            QApplication.processEvents()  # Update UI
            return
        
        # logic for normalization
        A4_WIDTH, A4_HEIGHT = 595,842

        reader = PdfReader(file_in)
        writer = PdfWriter()

        for page in reader.pages:
            orig_width = float(page.mediabox.width)
            orig_height = float(page.mediabox.height)

            scale = min(A4_WIDTH / orig_width, A4_HEIGHT / orig_height)

            tx = (A4_WIDTH - orig_width * scale) / 2
            ty = (A4_HEIGHT - orig_height * scale) / 2

            page.add_transformation(Transformation().scale(scale).translate(tx, ty))

            page.mediabox.upper_right = (A4_WIDTH, A4_HEIGHT)

            writer.add_page(page)

        # save them to the new file
        self.label_status.setText("Completed ✅")
        writer.write(file_out)
        writer.close()

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Reordering Completed")
        dlg.setFixedWidth(400)
        dlg.setText(f"Normalization completed successfully!\n\nOutput file:\n{file_out}")
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.exec()
        return