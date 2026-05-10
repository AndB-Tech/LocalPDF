from PyQt6.QtWidgets import QMainWindow, QToolBar
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QAction
import fitz, os

class EditToolbar(QToolBar):
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)

        self.add_actions()

    def add_actions(self) -> None:
        """Add toolbar actions."""
        # Action definitions: (icon_path, tooltip, handler)
        actions_icons = [
            ("icon/plus.png", "Increase Page Size", self.increase_icon_size),
            ("icon/minus.png", "Decrease Page Size", self.decrease_icon_size),
        ]
        actions_rotate = [
            ("icon/arrow-circle-225.png", "Rotate page clockwise", self.rotate_clockwise),
            ("icon/arrow-circle-315-left.png", "Rotate page counterclockwise", self.rotate_counterclockwise),
        ]
        actions_move = [
            ("icon/arrow-up.png", "Move page up", self.move_page_up),
            ("icon/arrow-down.png", "Move page down", self.move_page_down),
        ]
        actions_delete = [
            ("icon/bin-metal-full.png", "Delete page", self.delete_page),
        ]

        for icon_path, tip, func in actions_icons:
            action = QAction(QIcon(self.parent().resource_path(icon_path)), "fixed", self)
            action.setStatusTip(tip)
            action.triggered.connect(func)
            self.addAction(action)
        self.addSeparator()
        for icon_path, tip, func in actions_rotate:
            action = QAction(QIcon(self.parent().resource_path(icon_path)), "", self)
            action.setStatusTip(tip)
            action.triggered.connect(func)
            action.setEnabled(False)  # Disable rotation actions until a page is selected
            self.addAction(action)
        self.addSeparator()
        for icon_path, tip, func in actions_move:
            action = QAction(QIcon(self.parent().resource_path(icon_path)), "", self)
            action.setStatusTip(tip)
            action.triggered.connect(func)
            action.setEnabled(False)  # Disable move actions until a page is selected
            self.addAction(action)
        self.addSeparator()
        for icon_path, tip, func in actions_delete:
            action = QAction(QIcon(self.parent().resource_path(icon_path)), "", self)
            action.setStatusTip(tip)
            action.triggered.connect(func)
            action.setEnabled(False)  # Disable delete action until a page is selected
            self.addAction(action)

    # region ########## Action Handlers #############
    def increase_icon_size(self) -> None:
        """ Increase thumbnail size by 50px (50 <= size <= 1000) """
        if self.parent().viewer_icon_size[0] >= 1000 or self.parent().viewer_icon_size[1] >= 1000:
            return
        self.parent().viewer_icon_size[0] += 50
        self.parent().viewer_icon_size[1] += 50
        self.parent().viewer.setIconSize(QSize(self.parent().viewer_icon_size[0], self.parent().viewer_icon_size[1]))
        self.parent().viewer.setGridSize(QSize(self.parent().viewer_icon_size[0], self.parent().viewer_icon_size[1] + 10))
        self.parent().update_settings(viewer_settings=self.parent().viewer_icon_size)
    def decrease_icon_size(self) -> None:
        """ Decrease thumbnail size by 50px (50 <= size <= 1000) """
        if self.parent().viewer_icon_size[0] <= 50 or self.parent().viewer_icon_size[1] <= 50:
            return
        self.parent().viewer_icon_size[0] -= 50
        self.parent().viewer_icon_size[1] -= 50
        self.parent().viewer.setIconSize(QSize(self.parent().viewer_icon_size[0], self.parent().viewer_icon_size[1]))
        self.parent().viewer.setGridSize(QSize(self.parent().viewer_icon_size[0], self.parent().viewer_icon_size[1] + 10))
        self.parent().update_settings(viewer_settings=self.parent().viewer_icon_size)

    def rotate_clockwise(self) -> None:
        """ Rotate page 90 degrees clockwise """
        # check if an image is selected in the viewer
        index = self.parent().viewer.get_clicked_index()  # Get the file path of the currently clicked image
        img = index.data(Qt.ItemDataRole.UserRole) if index is not None else None
        if img is None: return

        file_name = os.path.basename(img)
        pdf_key = file_name.split("_page_")[0]
        pdf_page = int(file_name.split("_page_")[1].split(".png")[0])
        pdf_name = self.parent().image_lib[pdf_key]

        if os.path.isfile(pdf_name):
            doc = fitz.open(pdf_name)
            page = doc.load_page(pdf_page)

            # get the current rotation of the page and rotate it accordingly
            current_rotation = self.parent().changes_made["rotate"][pdf_key][pdf_page] if pdf_key in self.parent().changes_made["rotate"] and pdf_page in self.parent().changes_made["rotate"][pdf_key] else 0
            new_rotation = (current_rotation + 90) % 360

            mat = fitz.Matrix(1, 1).prerotate(new_rotation)
            pix = page.get_pixmap(matrix=mat)

            file = f"/{pdf_key}_page_{pdf_page}_new.png"
            output = f"{self.parent().img_wd}/{file}"

            pix.save(output)
            doc.close()

            self.parent().viewer.replace_image(index, output)
            self.parent().isModified = True
            self.update_rotation(pdf_key, pdf_page, 90)
            self.parent().isModified = True
    def rotate_counterclockwise(self) -> None:
        """ Rotate page 90 degrees counterclockwise """
        # check if an image is selected in the viewer
        index = self.parent().viewer.get_clicked_index()  # Get the file path of the currently clicked image
        img = index.data(Qt.ItemDataRole.UserRole) if index is not None else None
        if img is None: return
        
        file_name = os.path.basename(img)
        pdf_key = file_name.split("_page_")[0]
        pdf_page = int(file_name.split("_page_")[1].split(".png")[0])
        pdf_name = self.parent().image_lib[pdf_key]

        if os.path.isfile(pdf_name):
            doc = fitz.open(pdf_name)
            page = doc.load_page(pdf_page)

            # get the current rotation of the page and rotate it accordingly
            current_rotation = self.parent().changes_made["rotate"][pdf_key][pdf_page] if pdf_key in self.parent().changes_made["rotate"] and pdf_page in self.parent().changes_made["rotate"][pdf_key] else 0
            new_rotation = (current_rotation - 90) % 360

            mat = fitz.Matrix(1, 1).prerotate(new_rotation)
            pix = page.get_pixmap(matrix=mat)

            file = f"/{pdf_key}_page_{pdf_page}_new.png"
            output = f"{self.parent().img_wd}/{file}"

            pix.save(output)
            doc.close()

            self.parent().viewer.replace_image(index, output)
            self.parent().isModified = True
            self.update_rotation(pdf_key, pdf_page, -90)
            self.parent().isModified = True

    def move_page_up(self) -> None:
        """ Move page up in the viewer order """
        # check if an image is selected in the viewer
        index = self.parent().viewer.get_clicked_index()  # Get the file path of the currently clicked image
        if index is None: return
        self.parent().viewer.move_image_up(index)
    def move_page_down(self) -> None:
        """ Move page down in the viewer order """
        # check if an image is selected in the viewer
        index = self.parent().viewer.get_clicked_index()  # Get the file path of the currently clicked image
        if index is None: return
        self.parent().viewer.move_image_down(index)

    def delete_page(self) -> None:
        """ Delete page from viewer """
        # check if an image is selected in the viewer
        index = self.parent().viewer.get_clicked_index()  # Get the file path of the currently clicked image
        if index is None: return
        self.parent().viewer.remove_modals([index])

    def update_rotation(self, pdf_key: str, page_num: int, value: int) -> None:
        """ Update the changes_made dictionary for rotations """
        if pdf_key not in self.parent().changes_made["rotate"]:
            self.parent().changes_made["rotate"][pdf_key] = {}
        if page_num not in self.parent().changes_made["rotate"][pdf_key]:
            self.parent().changes_made["rotate"][pdf_key][page_num] = 0
        self.parent().changes_made["rotate"][pdf_key][page_num] = (self.parent().changes_made["rotate"][pdf_key][page_num] + value) % 360
    # endregion

    # region ########## Helpers #############
    def enable_toolbar(self, enabled: bool) -> None:
        """ Enable or disable the toolbar actions. """
        for action in self.actions():
            if action.text() == "fixed":  # Skip the increase/decrease icon size actions
                continue
            action.setEnabled(enabled)
    # endregion