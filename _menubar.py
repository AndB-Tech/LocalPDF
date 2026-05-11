from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from datetime import datetime
import os

from copy import copy
from pypdf import PdfReader, PdfWriter, Transformation

class MenuBar:
    def __init__(self, parent):
        self.parent = parent
        
        self.menu = self.parent.menuBar()

        self.add_actions()

    def add_actions(self):
        ''' Add menu actions '''
        # Action definitions: (icon_path, name, tooltip, handler)
        actions_file = [
            ("icon/folder-horizontal-open.png", "Open PDF...", "Open a PDF file", self.open_pdf),
            ("icon/disk-black.png", "Save PDF...", "Save the current PDF file", self.save_pdf),
        ]
        action_edit = [
            ("icon/folder--plus.png", "Add PDF...", "Add a PDF file to the current workspace", self.add_pdf),
            ("icon/bin-metal-full.png", "Remove PDF...", "Remove all Pages from a PDF from the Workspace", self.delete_pdf),
        ]

        file_menu = self.menu.addMenu("File")
        for icon_path, name, tip, func in actions_file:
            action = QAction(name, self.parent)
            action.setIcon(QIcon(self.parent.resource_path(icon_path)))
            action.setStatusTip(tip)
            action.triggered.connect(func)
            file_menu.addAction(action)

        edit_menu = self.menu.addMenu("Edit")
        for icon_path, name, tip, func in action_edit:
            action = QAction(name, self.parent)
            action.setIcon(QIcon(self.parent.resource_path(icon_path)))
            action.setStatusTip(tip)
            action.triggered.connect(func)
            edit_menu.addAction(action)

    # region ########## Action Handlers #############
    def open_pdf(self) -> None:
        """ Open a PDF file and display it in the viewer """
        # Open file dialog from lookup_path and get selected file path
        fname = QFileDialog.getOpenFileName(
            self.parent,
            "Open File",
            self.parent.get_lookup(),
            "PDF Files (*.pdf)",
        )
        if not fname[0]: return
        self.parent.update_settings(lookup_path=os.path.dirname(fname[0]))

        # change to the viewer and show the PDF file
        if self.parent.isEmpty:
            self.parent.central.hide()
            self.parent.setCentralWidget(self.parent.viewer)
            self.parent.viewer.show()
            self.parent.toolbar.show()
            self.parent.isEmpty = False

        self.parent.viewer.clearImages()  # Clear existing images before loading new PDF
        self.parent.clear_temp_images(self.parent.img_wd)  # Clear temp images before loading new PDF
        self.parent.clear_image_lib()  # Clear the image library for the new PDF
        key = datetime.now().strftime('%H%M%S%f')
        self.parent.image_lib[key] = fname[0]  # Add the new PDF to the image library with a unique key
        self.parent.extract_images(key, fname[0])  # Extract images from the PDF amd add them to the viewer
        self.parent.isModified = False

    def save_pdf(self) -> None:
        """ Save the current PDF """
        fname = QFileDialog.getSaveFileName(
            self.parent,
            "Save File",
            self.parent.get_lookup(),
            "PDF Files (*.pdf)",
        )
        if not fname[0]: return
        self.parent.update_settings(lookup_path=os.path.dirname(fname[0]))

        merger = PdfWriter()
        reader = {}
        order = self.parent.viewer.get_order()

        # iterate through the order of images in the viewer and add the corresponding pages to the merger
        for img_path in order:
            basename = os.path.basename(img_path)
            key = basename.split("_page_")[0]
            page = int(basename.split("_page_")[1].split(".png")[0])
            file = self.parent.image_lib[key]
            if key not in reader:
                if not os.path.isfile(file):
                    QMessageBox.warning(self.parent, "Missing PDF",
                                        f"PDF file could not be found:\n{file}")
                    return

                reader[key] = PdfReader(file)

                if reader[key].is_encrypted:
                    try:
                        reader[key].decrypt("")
                    except Exception:
                        pass

                    if reader[key].is_encrypted:
                        QMessageBox.warning(
                            self.parent,
                            "Encrypted PDF",
                            f"PDF is encrypted and cannot be processed:\n{file}"
                        )
                        return
                    
            new_page = copy(reader[key].pages[page])

            if self.parent.isModified:
                if key in self.parent.changes_made["rotate"]:
                    if page in self.parent.changes_made["rotate"][key]:
                        rotation = self.parent.changes_made["rotate"][key][page]
                        if rotation != 0:
                            new_page.rotate(rotation)

            new_page = self.normalize_page_to_a4(new_page)
            merger.add_page(new_page)
            
        # save the merged PDF to the selected file path
        with open(fname[0], "wb") as f:
            merger.write(f)
        merger.close()

        dlg = QMessageBox(self.parent)
        dlg.setWindowTitle("PDF Saved")
        dlg.setText(f"PDF saved successfully to:\n{fname[0]}")
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.exec()

        # TODO: add option to reduce size to specific MB if file is too large

    def add_pdf(self) -> None:
        """ Add a PDF file to the current workspace and display it in the viewer """
        fname = QFileDialog.getOpenFileName(
            self.parent,
            "Add PDF File",
            self.parent.get_lookup(),
            "PDF Files (*.pdf)",
        )
        if not fname[0]:  return
        self.parent.update_settings(lookup_path=os.path.dirname(fname[0]))

        key = datetime.now().strftime('%H%M%S%f')
        self.parent.image_lib[key] = fname[0]  # Add the new PDF to the image library with a unique key
        self.parent.extract_images(key, fname[0])  # Extract images from the PDF amd add them to the viewer
    
    def delete_pdf(self) -> None:
        """ Remove all pages from a PDF from the workspace """
        files = list(self.parent.image_lib.keys())
        if not files: return
        print(files) # TODO: replace with a proper selection dialog
    # endregion

    # region ########## Helper Functions #############
    def normalize_page_to_a4(self, page): # TODO: make this toggleable in a settings menu
        """Apply A4 scaling/centering transform to a page."""
        A4_WIDTH = 595.28
        A4_HEIGHT = 841.89

        page = copy(page)

        orig_width = float(page.mediabox.width)
        orig_height = float(page.mediabox.height)

        if orig_width == 0 or orig_height == 0:
            return page

        scale = min(A4_WIDTH / orig_width, A4_HEIGHT / orig_height)

        tx = (A4_WIDTH - orig_width * scale) / 2
        ty = (A4_HEIGHT - orig_height * scale) / 2

        page.add_transformation(
            Transformation().scale(scale).translate(tx, ty)
        )

        page.mediabox.lower_left = (0, 0)
        page.mediabox.upper_right = (A4_WIDTH, A4_HEIGHT)

        return page
    
    # endregion