import os, fitz
from pypdf import PdfReader, PdfWriter
from datetime import datetime
from _baseWindow import BaseWindow
from PyQt6.QtCore import (
    QSize, 
    Qt,
    pyqtSlot
)
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, 
    QPushButton, 
    QLabel, 
    QVBoxLayout, 
    QHBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QListView,
    QFileDialog,
    QLineEdit,
    QGraphicsOpacityEffect,
    QMessageBox
)

class ExtractPagesWindow(BaseWindow):
    def __init__(self, parent=None):
        super().__init__("Extract Pages", 840)
        self.parent_window = parent

        # Initialize variables        
        self.fname_link = None
        self.image_lib = {}
        self.output_folder = "C:/Users/USER/Downloads"
        self.output_name = None
        self.full_output = "N/A"

        # Build UI
        layout = QVBoxLayout()
        layout_explorer = QHBoxLayout()
        layout_output1 = QVBoxLayout()
        layout_output2 = QHBoxLayout()
        layout_actions = QHBoxLayout()

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
        
        # add spacing
        layout.addSpacing(10)

        # Image view for pages
        session_ident = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        img_folder = "created_images"
        wd = os.path.dirname(os.path.realpath(__file__))
        self.img_wd = f"{wd}/{img_folder}/{session_ident}/"
        os.makedirs(self.img_wd, exist_ok=True)
        self.image_view = QListWidget()
        self.image_view.setViewMode(QListView.ViewMode.IconMode)
        self.image_view.setIconSize(QSize(200, 200))
        self.image_view.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.image_view.setResizeMode(QListView.ResizeMode.Adjust)
        self.image_view.setSpacing(10)
        self.image_view.setFixedHeight(600)
        layout.addWidget(self.image_view)

        # add spacing
        layout.addSpacing(10)

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
        layout.addLayout(layout_output1)
        
        # Extract button
        button_extract = QPushButton("Extract Selected Pages", self)
        button_extract.setStatusTip("Extract the selected pages.")
        button_extract.clicked.connect(self.extract_pages)
        layout_actions.addWidget(button_extract)

        self.label_status = QLabel("", self)
        layout_actions.addWidget(self.label_status)
        layout.addLayout(layout_actions)

        # add spacing
        layout.addSpacing(10)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def closeEvent(self, event):
        if self.parent_window:
            self.parent_window.show()
        event.accept()

    def print_order(self):
        """Print the current order of images."""
        order = self.image_view.get_order()
        print("Current order:", order)
        return order
    
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
            self.load_pdf_pages(self.fname_link)
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
    
    # set the output-folder path
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
   
    # show the images in the viewer
    def load_pdf_pages(self, flink):
        self.image_view.clear()
        doc = fitz.open(flink)
        for i in range(doc.page_count):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            out_img = os.path.join(self.img_wd, f"page_{i+1}.png")
            pix.save(out_img)

            item = QListWidgetItem(QIcon(out_img), f"Page {i+1}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.image_view.addItem(item)
        doc.close()

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

    # extract pages
    def extract_pages(self):
        file_in = self.fname_link
        file_out = self.full_output

        # clean all inputs
        safe, file_in, file_out = self.clean_inputs(file_in, file_out)
        if not safe:
            self.label_status.setText("❌ Invalid Inputs. Canceling Extraction.")
            QApplication.processEvents()  # Update UI
            return
        
        # check for selected pages
        selected_items = self.image_view.selectedItems()
        if not selected_items:
            self.label_status.setText("⚠️ No pages selected")
            QApplication.processEvents()  # Update UI
            return

        # logic for extracting pages
        self.label_status.setText("Extracting...")
        QApplication.processEvents()  # Update UI

        reader = PdfReader(self.fname_link)
        writer = PdfWriter()
        for item in selected_items:
            page_index = item.data(Qt.ItemDataRole.UserRole)
            writer.add_page(reader.pages[page_index])

        # save them to the new file
        self.label_status.setText("Completed ✅")
        writer.write(file_out)
        writer.close()

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Extraction Completed")
        dlg.setText(f"Extraction completed successfully!\n\nOutput file:\n{file_out}")
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.exec()

        return