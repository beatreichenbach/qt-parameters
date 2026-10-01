from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import Any, Generic, TypeVar

from qtpy import QtCore, QtGui, QtWidgets

from .base import ParameterWidget

logger = logging.getLogger(__name__)

T = TypeVar('T')
Item = tuple[str, T]
EXCLUSIVE_ROLE = QtCore.Qt.ItemDataRole.UserRole + 2


class MultiComboBox(QtWidgets.QComboBox, Generic[T]):
    checked_changed = QtCore.Signal()
    delimiter: str = ', '

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._minimum_selection = 0
        self._maximum_selection = 0
        self._maximum_display_items = 3

        model = QtGui.QStandardItemModel(parent=self)
        self.setModel(model)

        size = self.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SmallIconSize)
        self.setIconSize(QtCore.QSize(size, size))
        self.setMaxVisibleItems(20)

        self.view().installEventFilter(self)
        self.view().viewport().installEventFilter(self)
        self._pressed = False

        # self.currentIndexChanged.connect(self.checked_changed)

    def initStyleOption(self, option: QtWidgets.QStyleOptionComboBox) -> None:
        super().initStyleOption(option)
        option.currentText = self._display_text()

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
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
            select_keys = (
                QtCore.Qt.Key.Key_Select,
                QtCore.Qt.Key.Key_Enter,
                QtCore.Qt.Key.Key_Return,
            )
            if isinstance(event, QtGui.QKeyEvent) and event.key() in select_keys:
                self._toggle_selected()
                return True
        return super().eventFilter(watched, event)

    def maximum_display_items(self) -> int:
        return self._maximum_display_items

    def set_maximum_display_items(self, maximum_display_items: int) -> None:
        self._maximum_display_items = maximum_display_items
        self.update()

    def minimum_selection(self) -> int:
        return self._minimum_selection

    def set_minimum_selection(self, minimum_selection: int) -> None:
        self._minimum_selection = minimum_selection

    def maximum_selection(self) -> int:
        return self._maximum_selection

    def set_maximum_selection(self, maximum_selection: int) -> None:
        self._maximum_selection = maximum_selection

    def items(self) -> tuple[Item[T], ...]:
        items = []
        model = self.model()
        if isinstance(model, QtGui.QStandardItemModel):
            for row in range(model.rowCount()):
                standard_item = model.item(row, 0)
                item = (standard_item.text(), standard_item.data())
                items.append(item)
        return tuple(items)

    def set_items(
        self,
        items: Mapping[str, T] | None = None,
        exclusive_items: Mapping[str, T] | None = None,
    ) -> None:
        model = self.model()
        if not isinstance(model, QtGui.QStandardItemModel):
            return

        model.clear()
        if exclusive_items:
            for label, data in exclusive_items.items():
                item = QtGui.QStandardItem()
                item.setText(label)
                item.setData(data)
                item.setData(True, EXCLUSIVE_ROLE)
                item.setCheckable(True)
                model.appendRow(item)

        if items and exclusive_items:
            separator = QtGui.QStandardItem()
            separator.setData(
                'separator', QtCore.Qt.ItemDataRole.AccessibleDescriptionRole
            )
            model.appendRow(separator)

        if items:
            for label, data in items.items():
                item = QtGui.QStandardItem()
                item.setText(label)
                item.setData(data)
                item.setCheckable(True)
                model.appendRow(item)

        self._index_changed()

    def checked_values(self) -> tuple[T, ...]:
        items = self._checked_items()
        values = [item.data() for item in items]
        return tuple(values)

    def set_checked_values(self, values: Sequence[T]) -> None:
        model = self.model()
        if not isinstance(model, QtGui.QStandardItemModel):
            return

        # self._clear()
        for value in values:
            # NOTE: Possibly unhashable item.data(), so nested linear search
            for row in range(model.rowCount()):
                item = model.item(row, 0)
                if item.data() == value:
                    self._clear(exclusive_only=not bool(item.data(EXCLUSIVE_ROLE)))
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
                    break
        self._index_changed()

    def _checked_items(self) -> tuple[QtGui.QStandardItem, ...]:
        items = []
        model = self.model()
        if isinstance(model, QtGui.QStandardItemModel):
            for row in range(model.rowCount()):
                item = model.item(row, 0)
                if item.checkState() == QtCore.Qt.CheckState.Checked:
                    items.append(item)
        return tuple(items)

    def _display_text(self) -> str:
        items = self._checked_items()
        max_items = self._maximum_display_items
        limited_items = items[:max_items] if max_items > 0 else items

        texts = [item.text() for item in limited_items]
        if len(texts) < len(items):
            texts.append('...')

        display_text = self.delimiter.join(texts)

        return display_text

    def _toggle_selected(self) -> None:
        model = self.model()
        if not isinstance(model, QtGui.QStandardItemModel):
            return

        count = len(self._checked_items())
        indexes = self.view().selectedIndexes()
        for index in indexes:
            item = model.itemFromIndex(index)
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                if count > self._minimum_selection:
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                    count -= 1
            else:
                self._clear(exclusive_only=not bool(item.data(EXCLUSIVE_ROLE)))

                if self._maximum_selection == 0 or count < self._maximum_selection:
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
                    count += 1

        self._index_changed()

    def _index_changed(self) -> None:
        """Update the text and emit a checked_changed signal."""

        # Store the selected index in the drop-down
        indexes = self.view().selectedIndexes()
        current_index = next(iter(indexes), QtCore.QModelIndex())

        # Update the combo box signal to set the text.
        self.blockSignals(True)
        if not self._checked_items():
            self.setCurrentIndex(-1)
        else:
            self.setCurrentIndex(0)
        self.blockSignals(False)
        self.update()

        # Restore the current index in the view
        self.view().selectionModel().setCurrentIndex(
            current_index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect
        )

        self.checked_changed.emit()

    def _clear(self, exclusive_only: bool = False) -> None:
        """Clear the check status on all items."""

        model = self.model()
        if isinstance(model, QtGui.QStandardItemModel):
            for row in range(model.rowCount()):
                item = model.item(row, 0)
                if not exclusive_only or item.data(EXCLUSIVE_ROLE):
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)


class MultiComboParameter(ParameterWidget[tuple[T, ...]], Generic[T]):
    _default: tuple[T, ...] = ()
    _value: tuple[T, ...] = ()
    _items: dict[str, T]
    _exclusive_items: dict[str, T]

    def __init__(self, name: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(name, parent)

        self._items = {}
        self._exclusive_items = {}
        self._pressed = False

    def _init_ui(self) -> None:
        self.combo: MultiComboBox[T] = MultiComboBox()
        self.combo.checked_changed.connect(self._checked_changed)
        self.combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )

        self._layout.addWidget(self.combo)
        self.setFocusProxy(self.combo)

    def items(self) -> tuple[Item[T], ...]:
        return tuple(self._items.items())

    def set_items(self, items: Mapping[str, T] | Sequence[Item[T] | T]) -> None:
        """
        Set the items of the parameter.

        `items` is either in the format of data, or (label, data).

        :raises ValueError: if there are duplicate labels.
        """

        self._items = items_dict(items)
        self._refresh_items()
        self.reset()

    def exclusive_items(self) -> tuple[Item[T], ...]:
        return tuple(self._exclusive_items.items())

    def set_exclusive_items(
        self, items: Mapping[str, T] | Sequence[Item[T] | T]
    ) -> None:
        """
        Set the exclusive items of the parameter. Exclusive items automatically clear
        other items and only allow one of them to be selected at any time.

        `items` is either in the format of data, or (label, data).

        :raises ValueError: if there are duplicate labels.
        """

        self._exclusive_items = items_dict(items)
        self._refresh_items()
        self.reset()

    def minimum_selection(self) -> int:
        return self.combo.minimum_selection()

    def set_minimum_selection(self, minimum_selection: int) -> None:
        self.combo.set_minimum_selection(minimum_selection)

    def maximum_selection(self) -> int:
        return self.combo.maximum_selection()

    def set_maximum_selection(self, maximum_selection: int) -> None:
        self.combo.set_maximum_selection(maximum_selection)

    def placeholder(self) -> str:
        return self.combo.placeholderText()

    def set_placeholder(self, placeholder: str) -> None:
        self.combo.setPlaceholderText(placeholder)

    def value(self) -> tuple[T, ...]:
        return super().value()

    def set_value(self, value: Sequence[T]) -> None:
        self.combo.blockSignals(True)
        self.combo.set_checked_values(value)
        self.combo.blockSignals(False)
        value = self.combo.checked_values()
        super().set_value(value)

    def clear(self) -> None:
        self.set_exclusive_items(())
        self.set_items(())

    def _checked_changed(self) -> None:
        value = self.combo.checked_values()
        super().set_value(value)

    def _refresh_items(self) -> None:
        self.combo.blockSignals(True)
        self.combo.set_items(self._items, self._exclusive_items)
        self.combo.blockSignals(False)


def items_dict(items: Mapping[str, T] | Sequence[Any]) -> dict[str, T]:
    """
    Return a dict of items in (label, data) format, keyed by unique label.

    :raises ValueError: if a label appears more than once.
    """

    if isinstance(items, Mapping):
        return dict(items)

    result: dict[str, T] = {}
    for item in items:
        label, data = item if isinstance(item, tuple) else (str(item), item)
        if label in result:
            raise ValueError(f'duplicate label: {label!r}')
        result[label] = data

    return result
