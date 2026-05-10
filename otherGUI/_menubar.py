from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from datetime import datetime
import os

from pypdf import PdfReader, PdfWriter

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
                if os.path.isfile(file):
                    reader[key] = PdfReader(file)
                if reader[key].is_encrypted:
                    try:
                        reader[key].decrypt("")  # returns 0 if failed, 1/2 if success depending on pypdf version
                    except Exception:
                        pass

                    if reader[key].is_encrypted:
                        QMessageBox.warning(self.parent, "Encrypted PDF",
                                            f"PDF is encrypted and cannot be processed:\n{file}")
                        return
                    
            new_page = reader[key].pages[page]
            merger.add_page(new_page)

            # are therer any changes made to the page that need to be applied before saving?
            if self.parent.isModified:
                # Rotation changes?
                if key in self.parent.changes_made["rotate"]:
                    if page in self.parent.changes_made["rotate"][key]:
                        if self.parent.changes_made["rotate"][key][page] != 0:
                            merger.pages[-1].rotate(self.parent.changes_made["rotate"][key][page])
            
        # save the merged PDF to the selected file path
        merger.write(fname[0])
        merger.close()

        dlg = QMessageBox(self.parent)
        dlg.setWindowTitle("PDF Saved")
        dlg.setText(f"PDF saved successfully to:\n{fname[0]}")
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.exec()

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
        files = self.parent.image_lib.keys()
        if not files: return
        print(files)
    # endregion
