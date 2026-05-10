import os

from PyQt6.QtCore import (
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
from PyQt6.QtWidgets import QListView, QMainWindow

class PDFViewer(QListView):
    """Custom QListView for draggable, reorderable image thumbnails."""

    def __init__(self, parent: QMainWindow = None, wd: str = "") -> None:
        super().__init__(parent)

        # create the folder for the images with a unique id provided while widget-creation
        self.wd = wd

        # Configure the view
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setMovement(QListView.Movement.Static)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setSpacing(10)
        self.setWrapping(True)
        self.setFlow(QListView.Flow.LeftToRight)
        self.setAcceptDrops(False)
        self.setDragEnabled(False)
        self.setDropIndicatorShown(False)
        self.setDragDropMode(QListView.DragDropMode.NoDragDrop)

        # Model to hold the image items
        self.model = QStandardItemModel()
        self.setModel(self.model)

        # Connect click signal
        self.clicked.connect(self.on_image_clicked)
        self.clicked_index = None  # Track clicked index for potential future use

    # region ########## Image Management #############
    def add_images(self, image_paths):
        """Add multiple images to the view."""
        for path in image_paths:
            pix = QPixmap(self.wd + path).scaled(
                1000, 1000,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            item = QStandardItem(QIcon(pix), "")
            item.setData(self.wd + path, Qt.ItemDataRole.UserRole)
            item.setEditable(False)
            self.model.appendRow(item)

    def remove_modals(self, index_list: list[QModelIndex]) -> None:
        """Remove images from model based on their indexes."""
        rows = sorted(
            {index.row() for index in index_list if index.isValid()},
            reverse=True
        )
        for row in rows:
            if 0 <= row < self.model.rowCount():
                self.model.removeRow(row)

        self.clicked_index = None
        self.parent().toolbar.enable_toolbar(False)

    def clearImages(self):
        """Remove all images from the model."""
        self.model.clear()

    def replace_image(self, index: QModelIndex, new_path: str) -> None:
        """Replace the image at the given index with a new image from new_path."""
        if not index.isValid() or not (0 <= index.row() < self.model.rowCount()):
            return

        item = self.model.itemFromIndex(index)
        if item is None:
            return

        old_path = item.data(Qt.ItemDataRole.UserRole)
        if not old_path:
            return

        # Remove old file first, then rename new file to old file name
        if os.path.exists(old_path):
            os.remove(old_path)

        os.rename(new_path, old_path)

        pix = QPixmap(old_path).scaled(
            1000, 1000,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        item.setIcon(QIcon(pix))
        item.setData(old_path, Qt.ItemDataRole.UserRole)
        
        # notify the view that the item changed
        self.model.dataChanged.emit(index, index)

        # force relayout/repaint
        self.update(index)
        self.viewport().update()
    
    def move_image_up(self, index: QModelIndex) -> None:
        """Move the image at the given index up in the order."""
        if not index.isValid() or index.row() <= 0:
            return

        row1 = index.row()
        row2 = row1 - 1
        item1 = self.model.item(row1)
        item2 = self.model.item(row2)

        if item1 is None or item2 is None:
            return

        icon1 = item1.icon()
        data1 = item1.data(Qt.ItemDataRole.UserRole)
        icon2 = item2.icon()
        data2 = item2.data(Qt.ItemDataRole.UserRole)

        item1.setIcon(icon2)
        item1.setData(data2, Qt.ItemDataRole.UserRole)
        item2.setIcon(icon1)
        item2.setData(data1, Qt.ItemDataRole.UserRole)
        new_index = self.model.indexFromItem(item2)
        self.setCurrentIndex(new_index)
        self.clicked_index = new_index  # Update clicked index to the new position
    def move_image_down(self, index: QModelIndex) -> None:
        """Move the image at the given index down in the order."""
        if not index.isValid() or index.row() >= self.model.rowCount() - 1:
            return

        row1 = index.row()
        row2 = row1 +1
        item1 = self.model.item(row1)
        item2 = self.model.item(row2)

        if item1 is None or item2 is None:
            return

        icon1 = item1.icon()
        data1 = item1.data(Qt.ItemDataRole.UserRole)
        icon2 = item2.icon()
        data2 = item2.data(Qt.ItemDataRole.UserRole)

        item1.setIcon(icon2)
        item1.setData(data2, Qt.ItemDataRole.UserRole)
        item2.setIcon(icon1)
        item2.setData(data1, Qt.ItemDataRole.UserRole)
        new_index = self.model.indexFromItem(item2)
        self.setCurrentIndex(new_index)
        self.clicked_index = new_index  # Update clicked index to the new position
    # endregion

    # region ########## Utility Methods #############
    def get_order(self):
        """Return the current order of image paths."""
        return [
            self.model.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.model.rowCount())
        ]   
    # endregion

    # region ########## Click Handling #############    
    @pyqtSlot(QModelIndex)
    def on_image_clicked(self, index):
        """Handle clicking on an image icon."""
        self.clicked_index = index  # Store clicked index for future use
        self.parent().toolbar.enable_toolbar(True)

    def get_clicked_index(self):
        """Return the QModelIndex of the currently clicked image, or None if none."""
        if self.clicked_index is not None:
            return self.clicked_index
        return None
    # endregion