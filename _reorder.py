import sys, os
from datetime import datetime
import fitz
from pypdf import PdfWriter, PdfReader
from PyQt6.QtCore import (
    QSize, 
    Qt,
    QModelIndex,
    pyqtSlot
)
from PyQt6.QtGui import (
    QIcon,
    QPixmap, 
    QStandardItemModel, 
    QStandardItem
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
    QListWidget,
    QListWidgetItem,
    QListView,
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

class ReorderableImageModel(QStandardItemModel):
    """Custom model that ensures drag-drop reordering never deletes items."""

    def dropMimeData(self, data, action, row, column, parent):
        # Always handle as a move between items, not a drop-onto
        if row == -1:
            # If dropped onto another item, place after it instead
            row = parent.row() + 1 if parent.isValid() else self.rowCount()

        return super().dropMimeData(data, Qt.DropAction.MoveAction, row, column, QModelIndex())

class ReorderableImageView(QListView):
    """Custom QListView for draggable, reorderable image thumbnails."""

    def __init__(self, image_paths = [], wd = ""):
        super().__init__()

        # create the folder for the images with a unique id provided while widget-creation
        self.wd = wd
        print(self.wd)

        # Configure the view
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setIconSize(QSize(200, 200))
        self.setMovement(QListView.Movement.Snap)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setSpacing(10)
        self.setWrapping(True)
        self.setFlow(QListView.Flow.LeftToRight)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QListView.DragDropMode.InternalMove)

        # Use our safe model
        self.model = ReorderableImageModel()
        self.setModel(self.model)

        # Add images if provided
        if image_paths:
            self.add_images(image_paths)

    def add_images(self, image_paths):
        """Add multiple images to the view."""
        for path in image_paths:
            pix = QPixmap(self.wd + path).scaled(
                200, 200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            item = QStandardItem(QIcon(pix), "")
            item.setData(self.wd + path, Qt.ItemDataRole.UserRole)
            item.setEditable(False)
            self.model.appendRow(item)

    def remove_images(self, image_paths):
        """Remove images from the model by their file paths."""
        for path in image_paths:
            for i in range(self.model.rowCount()):
                item = self.model.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == self.wd + path:
                    self.model.removeRow(i)
                    break  # important: break to avoid index shift issues

    def update_images(self, remove_paths=[], add_paths=[]):
        """
        Remove specific images and add new ones.

        Args:
            remove_paths (list): list of image paths to remove.
            add_paths (list): list of image paths to add.
        """
        if remove_paths:
            self.remove_images(remove_paths)
        if add_paths:
            self.add_images(add_paths)

    def get_order(self):
        """Return the current order of image paths."""
        return [
            self.model.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.model.rowCount())
        ]   

class ReorderPagesWindow(BaseWindow):
    def __init__(self, parent=None):
        super().__init__("Extract Pages", 840)
        self.parent_window = parent

        # Initialize variables
        self.flink_1 = None
        self.flink_2 = None
        self.image_lib = {}
        self.output_folder = "C:/Users/USER/Downloads"
        self.output_name = None
        self.full_output = "N/A"

        # Build UI
        layout = QVBoxLayout()
        layout_explorer1 = QHBoxLayout()
        layout_explorer2 = QHBoxLayout()
        layout_output1 = QVBoxLayout()
        layout_output2 = QHBoxLayout()
        layout_reorder = QHBoxLayout()

        # Entry of first PDF
        button_explore1 = QPushButton("Select 1st PDF", self)
        button_explore1.setStatusTip("Open one PDF to reorder")   
        button_explore1.clicked.connect(self.explore_1st_file)
        button_explore1.setFixedWidth(150)
        layout_explorer1.addWidget(button_explore1)
        # Label to show selected file
        self.label_file1 = QLabel("No file selected", self)
        self.label_file1.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout_explorer1.addWidget(self.label_file1)
        layout.addLayout(layout_explorer1)
        # Entry of second PDF
        button_explore2 = QPushButton("Select 2nd PDF", self)
        button_explore2.setStatusTip("Open second PDF to reorder and merge with first")   
        button_explore2.clicked.connect(self.explore_2nd_file)
        button_explore2.setFixedWidth(150)
        layout_explorer2.addWidget(button_explore2)
        # Label to show selected file
        self.label_file2 = QLabel("No file selected", self)
        self.label_file2.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout_explorer2.addWidget(self.label_file2)
        layout.addLayout(layout_explorer2)
        
        # empty space
        layout.addSpacing(10)

        # Use the custom ReorderableImageView
        # create unique session-id to save the images
        session_ident = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        img_folder = "created_images"
        wd = os.path.dirname(os.path.realpath(__file__))
        self.img_wd = "{}/{}/{}/".format(wd, img_folder, session_ident)
        os.makedirs(self.img_wd, exist_ok=True)
        self.image_view = ReorderableImageView([], self.img_wd)
        self.image_view.setFixedHeight(600)
        layout.addWidget(self.image_view)
        
        # empty space
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
        
        # empty space
        layout.addSpacing(10)

        # start reordering the pdfs
        button_reorder = QPushButton("Save current order", self)
        button_reorder.setStatusTip("Save the new order of pages to the output-file.")
        button_reorder.clicked.connect(self.reorder)
        button_reorder.setEnabled(False)
        button_reorder.setFixedWidth(130)
        effect = QGraphicsOpacityEffect(button_reorder)
        effect.setOpacity(0.4)
        button_reorder.setGraphicsEffect(effect)
        layout_reorder.addWidget(button_reorder)
        # lable for processing status
        self.label_status = QLabel("", self)
        layout_reorder.addWidget(self.label_status)
        layout.addLayout(layout_reorder)

        # Button to print current order
        #btn_print_order = QPushButton("Print Current Order")
        #btn_print_order.clicked.connect(self.print_order)
        #layout.addWidget(btn_print_order)

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
    
    # explore 1st file button handler
    @pyqtSlot()
    def explore_1st_file(self):
        set = self.flink_1 != None
        fname = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "C:/USERS/USER/DOWNLOADS",
            "PDF Files (*.pdf)",
        )
        if fname[0] != "":
            if not set:
                self.flink_1 = fname[0]
                fname_file = self.flink_1.split("/")[-1] if self.flink_1 else "No file selected"
                self.label_file1.setText(fname_file)
                self.update_images(None, self.flink_1, 1)
                set = True
                self.show_interface_elements()
            else:
                old_flink = self.flink_1
                self.flink_1 = fname[0]
                fname_file = self.flink_1.split("/")[-1] if self.flink_1 else "No file selected"
                self.label_file1.setText(fname_file)
                self.update_images(old_flink, self.flink_1, 1)
                set = True
                self.show_interface_elements()
        else:
            if not set:
                self.flink_1 = None
                self.label_file1.setText("No file selected")
                set = False
                self.hide_interface_elements()
            if set:
                old_flink = self.flink_1
                self.flink_1 = None
                self.label_file1.setText("No file selected")
                self.update_images(old_flink, None, 1)
                set = False
                self.hide_interface_elements()
    
    # explore 2nd file button handler
    @pyqtSlot()
    def explore_2nd_file(self):
        set = self.flink_2 != None
        fname = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "C:/USERS/USER/DOWNLOADS",
            "PDF Files (*.pdf)",
        )
        if fname[0] != "":
            if not set:
                self.flink_2 = fname[0]
                fname_file = self.flink_2.split("/")[-1] if self.flink_2 else "No file selected"
                self.label_file2.setText(fname_file)
                self.update_images(None, self.flink_2, 2)
                set = True
                self.show_interface_elements()
            else:
                old_flink = self.flink_2
                self.flink_2 = fname[0]
                fname_file = self.flink_2.split("/")[-1] if self.flink_2 else "No file selected"
                self.label_file2.setText(fname_file)
                self.update_images(old_flink, self.flink_2, 2)
                set = True
                self.show_interface_elements()
        else:
            if not set:
                self.flink_2 = None
                self.label_file2.setText("No file selected")
                set = False
                self.hide_interface_elements()
            if set:
                old_flink = self.flink_2
                self.flink_2 = None
                self.label_file2.setText("No file selected")
                self.update_images(old_flink, None, 2)
                set = False
                self.hide_interface_elements()

    # extract images from the selected pdf
    def extract_images(self, flink, explorer):
        if not flink: return
        doc = fitz.open(flink)
        key = f"{datetime.now().strftime('%H%M%S')}"
        self.image_lib[key] = [flink, explorer]
        img_list = []
        for i in range(doc.page_count):
            page = doc.load_page(i)
            # drastically reduce quality: scale down to 20%
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            file = f"{key}_{i+1}.png"
            img_list.append(file)
            output = f"{self.img_wd}/{file}"
            pix.save(output)
        doc.close()
        self.image_view.add_images(img_list)
        return
    
    # remove images associated with a given file
    def delete_images(self, flink, explorer):
        if not flink: return
        # find the key in self.image_lib that matches this file and explorer
        target_key = None
        for key, (stored_flink, stored_explorer) in list(self.image_lib.items()):
            if stored_flink == flink and stored_explorer == explorer:
                target_key = key
                break
        if not target_key:
            print(f"No images found for file {flink}")
            return
        
        # get all corresponding image filenames
        prefix = f"{target_key}_"
        image_files = [f for f in os.listdir(self.img_wd) if f.startswith(prefix)]

        # remove each image from disk
        for img_file in image_files:
            try:
                os.remove(os.path.join(self.img_wd, img_file))
            except Exception as e:
                print(f"Error deleting {img_file}: {e}")
        
        # remove from internal image list/view
        self.image_view.remove_images(image_files)
        del self.image_lib[target_key]

        return

    # removing or adding new images to folder
    def update_images(self, remove_link = None, add_link = None, exp = None):
        if exp:
            if remove_link:
                self.delete_images(remove_link, exp)
            if add_link:
                self.extract_images(add_link, exp)

    # show/hide interface elements
    def show_interface_elements(self):
        for widget in self.findChildren((QLineEdit, QPushButton, QLabel, QDoubleSpinBox)):
            effect = widget.graphicsEffect()
            if effect and isinstance(effect, QGraphicsOpacityEffect):
                widget.setEnabled(True)
                effect.setOpacity(1.0)
                widget.setGraphicsEffect(effect)
    def hide_interface_elements(self):
        file1 = (self.flink_1 or "").strip()
        file2 = (self.flink_2 or "").strip()
        if not file1 and not file2:
            for widget in self.findChildren((QLineEdit, QPushButton, QLabel, QDoubleSpinBox)):
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
   
    # clean inputs and validate before starting
    def clean_inputs(self, file1, file2, file_out):
        safe = True
        # normalize strings (handle None)
        file1 = (file1 or "").strip()
        file2 = (file2 or "").strip()
        file_out = (file_out or "").strip()
        # check individual inputs
        valid_file1 = isinstance(file1, str) and os.path.isfile(file1) and file1.lower().endswith(".pdf")
        valid_file2 = isinstance(file2, str) and os.path.isfile(file2) and file2.lower().endswith(".pdf")
        # must have at least one valid input file
        if not (valid_file1 or valid_file2):
            safe = False
        # check output file
        # ensure output filename ends with .pdf
        if not isinstance(file_out, str) or not file_out or not file_out.endswith(".pdf"):
            safe = False
        return safe, file1, file2, file_out

    # start the reodering of th pdfs and saving to new file
    def reorder(self):
        flink1 = self.flink_1
        flink2 = self.flink_2
        file_out = self.full_output

        # validate inputs
        self.label_status.setText("Checkig inputs...")
        QApplication.processEvents()  # Update UI
        safe, flink1, flink2, file_out = self.clean_inputs(flink1, flink2, file_out)
        if not safe:
            self.label_status.setText("❌ Ungültige Eingaben...")
            QApplication.processEvents()  # Update UI
            return
        
        # logic for reordering
        self.label_status.setText("Reordering PDFs...")
        QApplication.processEvents()  # Update UI
        if flink1: reader1 = PdfReader(flink1)
        if flink2: reader2 = PdfReader(flink2)
        merger = PdfWriter()
        # get the order of images in viewer
        pages = [f.split("/")[-1] for f in self.image_view.get_order()]
        page_order = []
        for p in pages:
            key, num = p.strip().split(".")[0].split("_")
            page_order.append((key, num))

        for key, num in page_order:
            _, exp = self.image_lib[key]
            if exp == 1:
                merger.add_page(reader1.pages[int(num)-1])
            elif exp == 2:
                merger.add_page(reader2.pages[int(num)-1])

        # save them to the new file
        self.label_status.setText("Completed ✅")
        merger.write(file_out)
        merger.close()

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Reordering Completed")
        dlg.setFixedWidth(400)
        dlg.setText(f"Reordering completed successfully!\n\nOutput file:\n{file_out}")
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.exec()

        return 