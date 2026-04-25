import os
from datetime import datetime
import fitz
from pypdf import PdfWriter, PdfReader
from _baseWindow import BaseWindow
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
    QPushButton, 
    QLabel, 
    QVBoxLayout, 
    QHBoxLayout,
    QWidget,
    QListView,
    QFileDialog,
    QGraphicsOpacityEffect,
    QLineEdit,
    QDoubleSpinBox,
    QMessageBox
)

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
        #print(self.wd)

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
        super().__init__("Extract Pages")
        self.parent_window = parent

        # Initialize variables
        self.wd = "C:/Users/USER/Downloads"
        self.flink = {}
        self.label_list = {"placefolder": None} # to keep track of the labels for the selected files
        self.image_lib = {}
        self.output_folder = "C:/Users/USER/Downloads"
        self.output_name = None
        self.full_output = "N/A"

        # create the folder for the images with a unique id provided while widget-creation
        session_ident = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        img_folder = "created_images"
        wd = os.path.dirname(os.path.realpath(__file__))
        self.img_wd = "{}/{}/{}/".format(wd, img_folder, session_ident)
        os.makedirs(self.img_wd, exist_ok=True)

        self.build_ui()

    def build_ui(self) -> None:
        # Layouts
        layout = QVBoxLayout()
        layout_fileSelection = QHBoxLayout()
        self.layout_selectedFiles = QVBoxLayout()
        layout_output = QHBoxLayout()
        layout_reorder = QHBoxLayout()
        

        # File selection and presentation for PDFs
        button_explorer = QPushButton("Select PDF", self)
        button_explorer.setStatusTip("Select a PDF file to reorder")
        button_explorer.clicked.connect(self.explore_file)
        button_explorer.setFixedWidth(150)

        choosen_file_label = QLabel("No file selected", self)
        choosen_file_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_list["placefolder"] = choosen_file_label

        layout_fileSelection.addWidget(button_explorer)
        self.layout_selectedFiles.addWidget(choosen_file_label)
        layout_fileSelection.addLayout(self.layout_selectedFiles)
        layout.addLayout(layout_fileSelection)
        # empty space
        layout.addSpacing(10)

        # Custom ReorderableImageView for displaying page thumbnails and allowing drag-drop reordering
        self.image_view = ReorderableImageView([], self.img_wd)
        self.image_view.setFixedHeight(int(QApplication.primaryScreen().availableGeometry().height() * 0.5))
        
        layout.addWidget(self.image_view)
        
        # empty space
        layout.addSpacing(10)

        # label and button for choosing the output folder and output name
        label_output = QLabel("Output:", self)
        effect = QGraphicsOpacityEffect(label_output)
        effect.setOpacity(0.4)
        label_output.setGraphicsEffect(effect)

        button_output = QPushButton("Output Folder", self)
        button_output.clicked.connect(self.set_output_folder)
        button_output.setStatusTip("Select the folder to save the reordered PDF")
        button_output.setEnabled(False)
        effect = QGraphicsOpacityEffect(button_output)
        effect.setOpacity(0.4)
        button_output.setGraphicsEffect(effect)

        input_output_name = QLineEdit()
        input_output_name.setPlaceholderText("Output File Name")
        input_output_name.setStatusTip("Enter the desired name for the output PDF file")
        input_output_name.textChanged.connect(lambda text: self.assemble_full_output(text))
        input_output_name.setEnabled(False)
        effect = QGraphicsOpacityEffect(input_output_name)
        effect.setOpacity(0.4)
        input_output_name.setGraphicsEffect(effect)

        layout_output.addWidget(label_output)
        layout_output.addWidget(button_output)
        layout_output.addWidget(input_output_name)
        layout.addLayout(layout_output)

        # label for whole output path
        self.label_full_output = QLabel("N/A", self)
        self.label_full_output.setAlignment(Qt.AlignmentFlag.AlignRight)
        effect = QGraphicsOpacityEffect(self.label_full_output)
        effect.setOpacity(0.4)
        self.label_full_output.setGraphicsEffect(effect) 
        layout.addWidget(self.label_full_output)
        
        # empty space
        layout.addSpacing(10)

        # button and label for reordering the pdfs
        button_reorder = QPushButton("Save current order", self)
        button_reorder.setStatusTip("Save the new order of pages to the output-file.")
        button_reorder.clicked.connect(self.reorder)
        button_reorder.setEnabled(False)
        button_reorder.setFixedWidth(130)
        effect = QGraphicsOpacityEffect(button_reorder)
        effect.setOpacity(0.4)
        button_reorder.setGraphicsEffect(effect)
        
        self.label_status = QLabel("", self)
        
        layout_reorder.addWidget(button_reorder)
        layout_reorder.addWidget(self.label_status)
        layout.addLayout(layout_reorder)

        # Button to print current order
        #btn_print_order = QPushButton("Print Current Order")
        #btn_print_order.clicked.connect(self.print_order)
        #layout.addWidget(btn_print_order)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # region ======================= HELPER FUNCTIONS =======================
    def closeEvent(self, event) -> None:
        """Handle window close to show parent window."""
        if self.parent_window:
            self.parent_window.show()
        event.accept()
    def print_order(self) -> list:
        """Print the current order of images."""
        order = self.image_view.get_order()
        # print("Current order:", order)
        return order
    def update_wd(self, fname: str) -> None:
        """When choosing a new file, grab the folder and open the explorer there"""
        if fname:
            self.wd = os.path.dirname(fname)
        return None
    def get_wd(self) -> str:
        """Get the current working directory for the explorer"""
        return self.wd
    def show_interface_elements(self):
        """Enable and show the interface elements once a file is selected."""
        for widget in self.findChildren((QLineEdit, QPushButton, QLabel, QDoubleSpinBox)):
            effect = widget.graphicsEffect()
            if effect and isinstance(effect, QGraphicsOpacityEffect):
                widget.setEnabled(True)
                effect.setOpacity(1.0)
                widget.setGraphicsEffect(effect)
    def hide_interface_elements(self):
        """Disable and hide the interface elements when no file is selected."""
        for widget in self.findChildren((QLineEdit, QPushButton, QLabel, QDoubleSpinBox)):
            effect = widget.graphicsEffect()
            if effect and isinstance(effect, QGraphicsOpacityEffect):
                widget.setEnabled(False)
                effect.setOpacity(0.4)
                widget.setGraphicsEffect(effect)
    def assemble_full_output(self, text: str = None):
        '''Assemble the full output path from the output folder and output name, and update the label.'''
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

    # endregion

    # region ======================= ReorderableImageView Helpers =======================
    def update_label_and_images(self, key: str) -> None:
        """When choosing a new file, update the label and extract the images to show in the viewer."""
        if key in self.flink.keys():
            fname = self.flink[key]

            self.label_status.setText("Extracting pages...")
            QApplication.processEvents()  # Update UI

            self.extract_images(fname, key)
            self.add_file_to_label(fname, key)
            QApplication.processEvents()  # Update UI

            self.label_status.setText("")
            QApplication.processEvents()  # Update UI
        return None
    def extract_images(self, fname: str, key: str) -> None:
        if not fname: return None
        doc = fitz.open(fname)
        key = key
        self.image_lib[key] = fname
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
        return None
    def add_file_to_label(self, fname: str, key: str) -> None:
        """When choosing a new file, update the label to show the filename."""
        fname_file = os.path.basename(fname)

        placeholder = self.label_list.get("placefolder")
        if placeholder is not None:
            placeholder.hide()  # hide the placeholder label if it exists
            self.show_interface_elements()  # show interface elements since a file is now selected

        layout_fname = QHBoxLayout()
        label = QLabel(fname_file, self)
        button = QPushButton("X", self)
        button.setFixedSize(20, 20)
        button.clicked.connect(lambda: self.remove_file_from_label(key))
        self.label_list[key] = layout_fname
        layout_fname.addWidget(label)
        layout_fname.addWidget(button)
        layout_fname.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout_selectedFiles.addLayout(layout_fname)

        #print(f"fname_file: {fname_file} | key: {key}")
        return None
    def remove_file_from_label(self, key: str) -> None:
        """When clicking the 'X' button on a file label, remove the label and the corresponding images."""
        layout = self.label_list.get(key)
        if layout is not None:
            # Remove all widgets from the layout
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # Remove the layout itself from the parent layout
            self.layout_selectedFiles.removeItem(layout)
            del self.label_list[key]
            if len(self.label_list) == 1:  # if only the placeholder is left
                placeholder = self.label_list.get("placefolder")
                if placeholder is not None:
                    placeholder.show()  # show the placeholder label again
                    self.hide_interface_elements()  # hide interface elements since no file is selected
            # Remove corresponding images
            self.delete_images(key)
        return None
    def delete_images(self, key:str) -> None:
        if not key: return None

        prefix = f"{key}_"
        image_files = [f for f in os.listdir(self.img_wd) if f.startswith(prefix)]
        for img_file in image_files:
            try:
                os.remove(os.path.join(self.img_wd, img_file))
            except Exception as e:
                print(f"Error deleting {img_file}: {e}")

        # remove from internal image list/view
        self.image_view.remove_images(image_files)
        if key in self.image_lib:
            del self.image_lib[key]
        return None
    # endregion

    # region ======================= Explorer Functions =======================
    @pyqtSlot()
    def explore_file(self) -> None:
        """Open file exporer to sleect a file and update the ReorderableImageView with the new file's pages."""
        fname = QFileDialog.getOpenFileName(
            self,
            "Open File",
            self.get_wd(),
            "PDF Files (*.pdf)",
        )
        key = datetime.now().strftime('%H%M%S%f')  # unique key based on timestamp
        if fname[0] != "" and os.path.isfile(fname[0]):
            if not fname[0].endswith(".pdf"): return None
            self.update_wd(fname[0])    # next time the explorer opens, it will start in the same folder
            self.flink[key] = fname[0]
            self.update_label_and_images(key)
    @pyqtSlot()
    def set_output_folder(self):
        '''Open file exporer to select an output folder and update the label with the new output path.'''
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.get_wd(),
        )
        if folder != "":
            self.output_folder = folder
        else:
            self.output_folder = "C:/Users/USER/Downloads"
        self.assemble_full_output()

    # endregion

    # region ======================= Reordering Logic =======================
    def validate_inputs(self) -> bool:
        """clean and validate inputs before starting the reordering process."""

        # at least one input file must be selected
        if len(self.flink) == 0: return False
        # check if all files are pdfs
        for _, path in self.flink.items():
            if not isinstance(path, str) or not path or not path.endswith(".pdf") or not os.path.isfile(path):
                return False
        # check if output path is valid
        if not isinstance(self.full_output, str) or not self.full_output or not self.full_output.endswith(".pdf"):
            return False
        # check if output folder exists
        output_folder = os.path.dirname(self.full_output)
        if not os.path.isdir(output_folder):
            return False
        # check if output file already exists
        if os.path.isfile(self.full_output):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Output File Exists")
            msg.setText(f"The output file already exists:\n{self.full_output}\n\nDo you want to overwrite it?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            response = msg.exec()
            if response == QMessageBox.StandardButton.No:
                return False
            
        # all inputs are valid
        return True
    def reorder(self) -> None:
        """Start the reordering process after validating inputs, and save the new PDF to the output path."""
        # validate inputs
        if not self.validate_inputs():
            self.label_status.setText("❌ Invalid inputs...")
            QApplication.processEvents()  # Update UI
            return None
        
        # logic for reordering
        self.label_status.setText("Reordering PDFs...")
        QApplication.processEvents()  # Update UI
        
        merger = PdfWriter()
        reader = {}
        for obj in self.image_view.get_order():
            key = os.path.basename(obj).split("_")[0]
            num = int(os.path.basename(obj).split("_")[1].split(".")[0]) - 1
            file = self.image_lib[key]
            #print(f"folder: {file} | num: {num}")

            if key not in reader:
                reader[key] = PdfReader(file)
                if reader[key].is_encrypted:
                    # try empty password first (some PDFs are "encrypted" but openable)
                    try:
                        reader[key].decrypt("")  # returns 0 if failed, 1/2 if success depending on pypdf version
                    except Exception:
                        pass

                    if reader[key].is_encrypted:
                        QMessageBox.warning(self, "Encrypted PDF",
                                            f"PDF is encrypted and cannot be processed:\n{file}")
                        return

            page = reader[key].pages[num]
            merger.add_page(page)

        # save them to the new file
        self.label_status.setText("Completed ✅")
        merger.write(self.full_output)
        merger.close()

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Reordering Completed")
        dlg.setFixedWidth(400)
        dlg.setText(f"Reordering completed successfully!\n\nOutput file:\n{self.full_output}")
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.exec()

        return None

    # endregion
