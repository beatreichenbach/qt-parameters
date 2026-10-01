from qt_material_icons import MaterialIcon
from qtpy import QtCore, QtGui, QtWidgets

from examples import application
from qt_parameters import CrumbParameter


def populate_items(parent: QtGui.QStandardItem, levels: int, level: int = 0) -> None:
    items = []
    for i in range(5):
        item = QtGui.QStandardItem()
        item.setText(f'level_{level}_{i}')
        item.setIcon(MaterialIcon('image'))
        items.append(item)
    parent.appendRows(items)
    level += 1
    if level < levels:
        for item in items:
            populate_items(item, levels, level)


def main() -> None:
    with application():
        model = QtGui.QStandardItemModel()

        levels = 3

        parent_item = model.invisibleRootItem()
        populate_items(parent_item, levels)

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        tree = QtWidgets.QTreeView()
        tree.setHeaderHidden(True)
        tree.setModel(model)
        layout.addWidget(tree)

        # Get a random value
        parent = QtCore.QModelIndex()
        for _ in range(3):
            index = model.index(2, 0, parent)
            parent = index
        value = model.data(index, QtCore.Qt.ItemDataRole.DisplayRole)

        crumb_parameter = CrumbParameter()
        crumb_parameter.set_model(model)
        crumb_parameter.set_value(value)
        layout.addWidget(crumb_parameter)

        widget.show()


if __name__ == '__main__':
    main()
