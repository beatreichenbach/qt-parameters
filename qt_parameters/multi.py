import logging
from collections.abc import Collection, Mapping
from typing import Any, Sequence

from PySide6 import QtCore
from qtpy import QtGui, QtWidgets

from qt_parameters import ParameterWidget

logger = logging.getLogger(__name__)


class MultiComboBox(QtWidgets.QComboBox):
    checked_changed = QtCore.Signal()
    delimiter: str = ', '

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._max_display_items = 0

        model = QtGui.QStandardItemModel(parent=self)
        self.setModel(model)

        size = self.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SmallIconSize)
        self.setIconSize(QtCore.QSize(size, size))
        self.setMaxVisibleItems(20)

        self.view().installEventFilter(self)
        self.view().viewport().installEventFilter(self)
        self._pressed = False

        self.currentIndexChanged.connect(self._index_changed)

    def initStyleOption(self, option: QtWidgets.QStyleOptionComboBox) -> None:
        super().initStyleOption(option)
        option.currentText = self._display_text()

    def eventFilter(self, watched: QtCore.QObject, event: QtGui.QEvent) -> bool:
        # NOTE: Override events that would call QComboBox.hidePopup().
        if watched is self.view().viewport():
            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                self._pressed = True
            elif event.type() == QtCore.QEvent.Type.MouseButtonRelease:
                if self._pressed:
                    self._toggle_selected()
                    self._pressed = False
                    return True

        if event.type() == QtCore.QEvent.Type.ShortcutOverride:
            if event.key() in (
                QtCore.Qt.Key.Key_Select,
                QtCore.Qt.Key.Key_Enter,
                QtCore.Qt.Key.Key_Return,
            ):
                self._toggle_selected()
                return True
        return super().eventFilter(watched, event)

    def max_display_items(self) -> int:
        return self._max_display_items

    def set_max_display_items(self, max_display_items: int) -> None:
        """
        Set the maximum of items displayed in the text.
        If `max_display_items` is 0, there is no limit.
        """

        self._max_display_items = max_display_items
        self.update()

    def items(self) -> tuple[str, Any]:
        items = []
        model = self.model()
        if isinstance(model, QtGui.QStandardItemModel):
            for row in range(model.rowCount()):
                standard_item = model.item(row, 0)
                item = (standard_item.text(), standard_item.data())
                items.append(item)
        return tuple(items)

    def set_items(self, items: tuple[str, Any]) -> None:
        model = self.model()
        if isinstance(model, QtGui.QStandardItemModel):
            model.clear()
            for label, data in items:
                item = QtGui.QStandardItem()
                item.setText(label)
                item.setData(data)
                item.setCheckable(True)
                model.appendRow(item)
        self.setCurrentIndex(-1)

    def checked_items(self) -> tuple:
        items = self._checked_items()
        values = [item.data() for item in items]
        return tuple(values)

    def set_checked_items(self, values: Sequence) -> None:
        model = self.model()
        if isinstance(model, QtGui.QStandardItemModel):
            for row in range(model.rowCount()):
                item = model.item(row, 0)
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                if item.data() in values:
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
            self._index_changed()

    def _display_text(self) -> str:
        items = self._checked_items()

        if self._max_display_items > 0:
            filtered_items = items[: self._max_display_items]
        else:
            filtered_items = items

        texts = [item.text() for item in filtered_items]
        if len(texts) < len(items):
            texts.append('...')

        display_text = self.delimiter.join(texts)

        return display_text

    def _checked_items(self) -> tuple[QtGui.QStandardItem, ...]:
        items = []
        model = self.model()
        if isinstance(model, QtGui.QStandardItemModel):
            for row in range(model.rowCount()):
                item = model.item(row, 0)
                if item.checkState() == QtCore.Qt.CheckState.Checked:
                    items.append(item)
        return tuple(items)

    def _toggle_selected(self) -> None:
        model = self.model()
        if isinstance(model, QtGui.QStandardItemModel):
            indexes = self.view().selectedIndexes()
            for index in indexes:
                item = model.itemFromIndex(index)
                if item.checkState() == QtCore.Qt.CheckState.Checked:
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                else:
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
            self._index_changed()

    def _index_changed(self) -> None:
        if not self._checked_items():
            self.setCurrentIndex(-1)
        else:
            self.setCurrentIndex(0)
        self.update()
        self.checked_changed.emit()


class MultiComboParameter(ParameterWidget):
    _items: tuple[str, Any] = ()
    _placeholder: str = ''
    _default: tuple = ()
    _value: tuple = ()

    def __init__(self, name: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(name, parent)

        self._pressed = False

    def _init_ui(self) -> None:
        self.combo = MultiComboBox()
        self.combo.checked_changed.connect(self._checked_changed)
        self.combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )

        self._layout.addWidget(self.combo)
        self.setFocusProxy(self.combo)

    def items(self) -> tuple:
        return self._items

    def set_items(self, items: Collection) -> None:
        """
        Set the items of the parameter.
        `items` is either a sequence or dictionary with format (label, data).
        """

        if isinstance(items, Mapping):
            items = tuple(items.items())
        else:
            items = tuple(i if isinstance(i, tuple) else (i, i) for i in items)

        self._items = items
        self._refresh_items()
        self.reset()

    def placeholder(self) -> str:
        return self._placeholder

    def set_placeholder(self, placeholder: str) -> None:
        self._placeholder = placeholder
        self.combo.setPlaceholderText(self._placeholder)

    def value(self) -> tuple:
        return super().value()

    def set_value(self, value: Sequence) -> None:
        self.combo.blockSignals(True)
        self.combo.set_checked_items(value)
        self.combo.blockSignals(False)
        value = self.combo.checked_items()
        super().set_value(value)

    def _checked_changed(self) -> None:
        value = self.combo.checked_items()
        super().set_value(value)

    def _refresh_items(self) -> None:
        self.combo.blockSignals(True)
        self.combo.set_items(self._items)
        self.combo.blockSignals(False)
