import sys, os, subprocess, fitz

from PyQt6.QtCore import (
    QSize, 
    Qt,
    pyqtSlot
)
from PyQt6.QtGui import (
    QIcon,
    QKeySequence,
    QShortcut
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
    QGraphicsOpacityEffect,
    QLineEdit,
    QDoubleSpinBox,
    QMessageBox
)

class BaseWindow(QMainWindow):
    """Base window class with shared setup."""
    def __init__(self, title: str, width: int):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedWidth(width)
        self.setWindowIcon(QIcon("./icon/document-pdf-text.png"))
        self.setStatusBar(QStatusBar(self))

class ResizePdfWindow(BaseWindow):
    def __init__(self, parent=None):
        super().__init__("Resize PDFs", 500)
        self.parent_window = parent

        # Initialize variables
        self.fname_link = None
        self.output_folder = "C:/Users/USER/Downloads"
        self.output_name = None
        self.full_output = "N/A"
        self.size_mb = 0.0

        # Build UI
        layout = QVBoxLayout()
        layout_explorer = QHBoxLayout()
        layout_size = QHBoxLayout()
        layout_output1 = QVBoxLayout()
        layout_output2 = QHBoxLayout()
        layout_output3 = QHBoxLayout()

        # Explore Files Button
        button_explore = QPushButton("Explore Files", self)
        button_explore.setStatusTip("Open file explorer to select PDF files to resize")   
        button_explore.clicked.connect(self.explore_files)
        button_explore.setFixedWidth(120)
        layout_explorer.addWidget(button_explore)
        # Label to show selected file
        self.label_file = QLabel("No file selected", self)
        layout_explorer.addWidget(self.label_file)

        # label with current size of pdf
        label_current_size = QLabel("Current Size: N/A MB", self)
        effect = QGraphicsOpacityEffect(label_current_size)
        effect.setOpacity(0.4)
        label_current_size.setGraphicsEffect(effect)
        layout_size.addWidget(label_current_size)
        # spin box for target size in mb with upper limit set to current size
        self.input_target_size = QDoubleSpinBox()
        self.input_target_size.setStatusTip("Set the desired target size for the resized PDF in megabytes (MB)")
        self.input_target_size.setSuffix(" MB")
        self.input_target_size.setValue(0) # default value
        self.input_target_size.setSingleStep(0.1)
        self.input_target_size.setEnabled(False)
        effect = QGraphicsOpacityEffect(self.input_target_size)
        effect.setOpacity(0.4)
        self.input_target_size.setGraphicsEffect(effect)
        layout_size.addWidget(self.input_target_size)

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
        button_start.setStatusTip("Start resizing the selected PDF to the target size")
        button_start.clicked.connect(self.resize_pdf)  
        shortcut = QShortcut(QKeySequence("Return"), self)
        shortcut.activated.connect(button_start.click)
        button_start.setFixedWidth(120)
        button_start.setEnabled(False)
        effect = QGraphicsOpacityEffect(button_start)
        effect.setOpacity(0.4)
        button_start.setGraphicsEffect(effect) 
        layout_output3.addWidget(button_start)
        # update label
        self.label_update = QLabel("", self)
        layout_output3.addWidget(self.label_update)
        layout_output1.addLayout(layout_output3)

        # assemble main layout
        layout.addLayout(layout_explorer)
        layout.addLayout(layout_size)
        layout.addLayout(layout_output1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

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
            self.update_current_size()
        else:
            self.fname_link = None
            self.label_file.setText("No file selected")
            self.hide_interface_elements()
            self.update_current_size()

    # calculate and show current size of selected pdf
    def update_current_size(self):
        if self.fname_link:
            try:
                size_bytes = os.path.getsize(self.fname_link)
                self.size_mb = size_bytes / (1024 * 1024)
                size_text = f"Current Size: {self.size_mb:.2f} MB"
                self.input_target_size.setRange(1, self.size_mb)  # 1 MB to 10,000 MB
                # find the label and update its text
                for widget in self.findChildren(QLabel):
                    if widget.text().startswith("Current Size:"):
                        widget.setText(size_text)
                        break
            except Exception as e:
                print(f"Error calculating file size: {e}")

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

    # handle window close event
    def closeEvent(self, event):
        if self.parent_window:
            self.parent_window.show()
        event.accept()

    # function to check all inputs are valid
    def clean_inputs(self, file_in, file_out, size_current, size_target):
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
        # check size_current
        try:
            size_current = float(size_current)
            if size_current <= 0:
                safe = False
        except (ValueError, TypeError):
            safe = False
        # check size_target
        try:
            size_target = float(size_target)
            if size_target <= 0 or size_target >= size_current:
                safe = False
        except (ValueError, TypeError):
            safe = False
        return safe, file_in, file_out, size_current, size_target

    # resize pdf button handler
    @pyqtSlot()
    def resize_pdf(self):
        file_in = self.fname_link
        file_out = self.full_output
        size_current = float(f"{self.size_mb:.2}")
        size_target = float(f"{self.input_target_size.value():.2}")

        # clean inputs
        safe, file_in, file_out, size_current, size_target = self.clean_inputs(file_in, file_out, size_current, size_target)
        if not safe:
            self.label_update.setText("❌ Invalid Inputs. Canceling Resizing.")
            QApplication.processEvents()  # Update UI
            return

        # Resize logic
        TARGET_SIZE = size_target * 1024 * 1024  # Convert MB to bytes
        START_DPI = 150 
        MIN_DPI = 50  # not less than 50 dpi, otherwise hardly readable

        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        os.chdir(script_dir)

        if not os.path.exists(file_in):
            self.label_update.setText(f"❌ Eingabedatei '{file_in}' nicht gefunden!")
            QApplication.processEvents()  # Update UI
            return

        self.compress_pdf_to_target(file_in, file_out, TARGET_SIZE, START_DPI, MIN_DPI)

    def compress_pdf_to_target(self, input_file, output_file, target_size, start_dpi=150, min_dpi=20):
        dpi = start_dpi

        while dpi >= min_dpi:
            doc = fitz.open(input_file)
            new_pdf = fitz.open()

            zoom = dpi / 72
            matrix = fitz.Matrix(zoom, zoom)

            for page in doc:
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                rect = fitz.Rect(0, 0, pix.width, pix.height)

                new_page = new_pdf.new_page(width=pix.width, height=pix.height)
                new_page.insert_image(rect, pixmap=pix)

            new_pdf.save(output_file, deflate=True)
            doc.close()
            new_pdf.close()

            size = os.path.getsize(output_file)

            self.label_update.setText(f"➡️ Versuch bei {dpi} DPI: {size/1024/1024:.2f} MB")
            QApplication.processEvents()  # Update UI

            if size <= target_size:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Resize PDF")
                dlg.setText(f"Successfully resized PDF to {size/1024/1024:.2f} MB at {dpi} DPI.\n\nOutput File:\n{output_file}")
                dlg.setIcon(QMessageBox.Icon.Information)
                dlg.exec()
                return True

            dpi -= 10  # Reduce DPI stepwise

        try:
            if os.path.exists(output_file):
                os.remove(output_file)  # Remove incomplete output file
        except Exception as e:
            print(f"Error removing incomplete output file: {e}")
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Resize PDF")
        dlg.setText("Could not reach target size without going below minimum DPI.")
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.exec()
        return False


    