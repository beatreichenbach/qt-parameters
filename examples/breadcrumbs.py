from collections.abc import Mapping, Sequence

from qt_material_icons import MaterialIcon
from qtpy import QtCore, QtGui, QtWidgets

from examples import application, save_pixmap
from qt_parameters import CrumbParameter

TAXONOMY: dict[str, dict[str, tuple[str, ...]]] = {
    'Animal': {
        'Mammal': ('Dog', 'Cat', 'Horse'),
        'Bird': ('Eagle', 'Parrot', 'Penguin'),
        'Fish': ('Shark', 'Salmon', 'Clownfish'),
    },
    'Plant': {
        'Tree': ('Oak', 'Pine', 'Maple'),
        'Flower': ('Rose', 'Tulip', 'Daisy'),
    },
}

ICONS = {
    'Animal': 'pets',
    'Plant': 'eco',
}


def add_items(
    parent: QtGui.QStandardItem, items: Mapping[str, object], top: bool = False
) -> None:
    """Add a nested taxonomy to `parent` as (label, data) items."""

    for label, children in items.items():
        item = _item(label, ICONS.get(label) if top else None)
        parent.appendRow(item)
        if isinstance(children, Mapping):
            add_items(item, children)
        elif isinstance(children, Sequence):
            for child in children:
                item.appendRow(_item(child))


def _item(label: str, icon: str | None = None) -> QtGui.QStandardItem:
    item = QtGui.QStandardItem()
    item.setText(label)
    item.setData(label, QtCore.Qt.ItemDataRole.UserRole)
    item.setEditable(False)
    if icon:
        item.setIcon(MaterialIcon(icon))
    return item


class WidgetGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle('Breadcrumb Widgets')
        self.resize(720, 240)

        model = QtGui.QStandardItemModel()
        add_items(model.invisibleRootItem(), TAXONOMY, top=True)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.tree = QtWidgets.QTreeView()
        self.tree.setHeaderHidden(True)
        self.tree.setModel(model)
        self.tree.expandToDepth(0)
        layout.addWidget(self.tree)

        crumb_parameter = CrumbParameter()
        crumb_parameter.set_model(model)
        crumb_parameter.set_value('Dog')
        layout.addWidget(crumb_parameter)

        # Screenshot
        self.screenshot_button = QtWidgets.QPushButton('Screenshot')
        self.screenshot_button.clicked.connect(self._screenshot)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.screenshot_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _screenshot(self) -> None:
        """Save a screenshot with the dropdown of the last combo open."""

        self.screenshot_button.hide()
        self.tree.hide()
        self.resize(720, 120)
        QtWidgets.QApplication.processEvents()
        pixmap = self.grab()
        save_pixmap(pixmap, 'breadcrumbs')
        self.screenshot_button.show()
        self.tree.show()
        self.resize(720, 240)


def main() -> None:
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
