from __future__ import annotations

from functools import partial
from typing import Generic, TypeVar, cast

from qtpy import QtCore, QtGui, QtWidgets

from ..widgets import ComboBox
from .base import ParameterWidget

T = TypeVar('T')
ModelIndex = QtCore.QModelIndex | QtCore.QPersistentModelIndex


class CrumbComboBox(ComboBox):
    remove_triggered = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent=parent)

        # NOTE: The QCompleter widget does not accept a RootModelIndex. Instead, refresh
        #       a QStringListModel with items when needed.
        self._completer_model = QtCore.QStringListModel()
        self._completer = QtWidgets.QCompleter()
        self._completer.setWidget(self)
        self._completer.setModel(self._completer_model)
        self._completer.setCompletionMode(
            QtWidgets.QCompleter.CompletionMode.PopupCompletion
        )
        self._completer.setModelSorting(
            QtWidgets.QCompleter.ModelSorting.CaseInsensitivelySortedModel
        )
        self._completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)

        self.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.setMaxVisibleItems(20)
        size = self.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SmallIconSize)
        self.setIconSize(QtCore.QSize(size, size))

    def setEditable(self, editable: bool) -> None:
        if editable != self.isEditable():
            super().setEditable(editable)
            if editable:
                self.setCompleter(self._completer)
                self.blockSignals(True)
                self.setCurrentIndex(-1)
                self.blockSignals(False)

                model = self.model()
                if model.rowCount(self.rootModelIndex()):
                    placeholder = 'Select ...'
                else:
                    placeholder = ''
                if line_edit := self.lineEdit():
                    line_edit.setPlaceholderText(placeholder)
        self.show()
        self.setFocus()

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        super().setModel(model)
        self._completer.setModel(self._completer_model)

    def setRootModelIndex(self, index: ModelIndex) -> None:
        super().setRootModelIndex(index)
        self.refresh_completer()

    def focusNextPrevChild(self, next_: bool) -> bool:
        return False

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if not self.isEditable():
            return super().keyPressEvent(event)

        # Switch focus to next widget
        if event.key() in (
            QtCore.Qt.Key.Key_Tab,
            QtCore.Qt.Key.Key_Enter,
            QtCore.Qt.Key.Key_Return,
        ):
            if not self.count():
                return super().keyPressEvent(event)

        # Accept auto complete
        if event.key() in (
            QtCore.Qt.Key.Key_Tab,
            QtCore.Qt.Key.Key_Enter,
            QtCore.Qt.Key.Key_Return,
            QtCore.Qt.Key.Key_Space,
            QtCore.Qt.Key.Key_Slash,
        ):
            if completer := self.completer():
                popup = completer.popup()
                selected_indexes = popup.selectedIndexes() if popup is not None else ()
                if selected_indexes:
                    index = selected_indexes[0]
                    completion = index.data()
                else:
                    completion = completer.currentCompletion()

                index = self.findText(completion)
                if index >= 0:
                    self.setCurrentIndex(index)
                    self.clearFocus()
                return None

        # Remove the CrumbCombo
        if event.key() in (QtCore.Qt.Key.Key_Backspace, QtCore.Qt.Key.Key_Delete):
            if not self.currentText():
                self.remove_triggered.emit()
                return None

        return super().keyPressEvent(event)

    def refresh_completer(self) -> None:
        strings = tuple(self.itemText(i) for i in range(self.count()))
        self._completer_model.setStringList(strings)


class CrumbParameter(ParameterWidget[T | None], Generic[T]):
    value_changed = QtCore.Signal(object)

    _value: T | None = None
    _default: T | None = None
    _model: QtCore.QAbstractItemModel
    _max_items: int = 0

    def _init_ui(self) -> None:
        super()._init_ui()
        self.set_model(QtGui.QStandardItemModel())

    def sizeHint(self) -> QtCore.QSize:
        size_hint = super().sizeHint()
        size_hint = size_hint.expandedTo(QtCore.QSize(256, 0))
        return size_hint

    def max_items(self) -> int:
        return self._max_items

    def set_max_items(self, max_items: int) -> None:
        max_items = max(max_items, 0)
        if self._max_items != max_items:
            self._max_items = max_items
            for _ in range(self._layout.count() - self._max_items):
                self.remove_combo()

    def model(self) -> QtCore.QAbstractItemModel:
        return self._model

    def set_model(self, model: QtCore.QAbstractItemModel) -> None:
        self._model = model
        self._reset()

    def value(self) -> T | None:
        if item := self._layout.itemAt(self._layout.count() - 2):
            combo = item.widget()
            if isinstance(combo, CrumbComboBox):
                return cast('T | None', combo.currentData())
        return None

    def set_value(self, value: T | None) -> None:
        if self._value != value:
            self._reset()
            if value is not None:
                index = self._find_index(value, QtCore.Qt.ItemDataRole.UserRole)
                self._set_index(index)
        super().set_value(value)

    def current_combo(self) -> CrumbComboBox | None:
        if item := self._layout.itemAt(self._layout.count() - 1):
            widget = item.widget()
            if isinstance(widget, CrumbComboBox):
                return widget
        return None

    def remove_combo(self) -> None:
        if self._layout.count() > 1:
            if current_combo := self.current_combo():
                self._layout.removeWidget(current_combo)
                current_combo.deleteLater()
                self._refresh_stretch()
        if current_combo := self.current_combo():
            current_combo.setEditable(True)
        super().set_value(self.value())

    def _add_level(self, index: QtCore.QModelIndex | None = None) -> CrumbComboBox:
        """Add a new level by appending a new editable CrumbComboBox."""

        if not index:
            index = QtCore.QModelIndex()

        # Parent the widget on init because setRootModelIndex shows the widget early.
        combo = CrumbComboBox(self)
        combo.setModel(self._model)
        combo.setRootModelIndex(index)
        combo.setEditable(True)
        combo.currentIndexChanged.connect(partial(self._combo_changed, combo))
        combo.remove_triggered.connect(self.remove_combo)
        self._layout.addWidget(combo)
        self._refresh_tab_order()
        self._refresh_stretch()
        return combo

    def _can_add_level(self) -> bool:
        return not self._max_items or self._layout.count() < self._max_items

    def _clear(self) -> None:
        while item := self._layout.takeAt(0):
            if widget := item.widget():
                widget.deleteLater()

    def _remove_to_combo(self, combo: CrumbComboBox) -> None:
        for i in reversed(range(self._layout.count())):
            item = self._layout.itemAt(i)
            if item is None:
                continue
            if widget := item.widget():
                if widget == combo:
                    return
                self._layout.removeWidget(widget)
                widget.deleteLater()

    def _reset(self) -> None:
        """Clear the widget and add an initial level. Preserve the tab order."""

        prev = None
        while item := self._layout.takeAt(0):
            if widget := item.widget():
                if prev is None:
                    prev = get_previous_widget(widget)
                widget.deleteLater()

        combo = self._add_level()
        if prev:
            self.setTabOrder(prev, combo)

    def _combo_changed(self, combo: CrumbComboBox, index: int) -> None:
        value = cast('T | None', combo.itemData(index, QtCore.Qt.ItemDataRole.UserRole))
        self._remove_to_combo(combo)
        combo.setEditable(False)
        model_index = self._model.index(index, 0, combo.rootModelIndex())
        if self._can_add_level():
            self._add_level(model_index)
        super().set_value(value)

        # To open the next combo box automatically:
        # QtWidgets.QApplication.processEvents()
        # current_combo.showPopup()

    def _find_index(
        self,
        value: object,
        role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole,
        parent: QtCore.QModelIndex | None = None,
    ) -> QtCore.QModelIndex:
        if parent is None:
            parent = QtCore.QModelIndex()
        index = QtCore.QModelIndex()
        for row in range(self._model.rowCount(parent)):
            index = self._model.index(row, 0, parent)
            if not index.isValid():
                continue
            if value == self._model.data(index, role):
                break
            index = self._find_index(value, role, index)
            if index.isValid():
                break
        return index

    def _set_index(self, index: QtCore.QModelIndex) -> None:
        indexes = []
        while index.isValid():
            indexes.insert(0, index)
            index = index.parent()

        for index in indexes:
            combo = self.current_combo()
            if isinstance(combo, CrumbComboBox):
                combo.setEditable(False)
                combo.blockSignals(True)
                combo.setCurrentIndex(index.row())
                combo.blockSignals(False)
                if self._can_add_level():
                    self._add_level(index)

    def _refresh_tab_order(self) -> None:
        first: QtWidgets.QWidget | None = None
        for i in range(self._layout.count()):
            if item := self._layout.itemAt(i):
                if widget := item.widget():
                    if first:
                        self.setTabOrder(first, widget)
                    first = widget

    def _refresh_stretch(self) -> None:
        count = self._layout.count()
        for i in range(count):
            self._layout.setStretch(i, int(i == count - 1))


def get_previous_widget(widget: QtWidgets.QWidget) -> QtWidgets.QWidget | None:
    """Return the previous widget in the tab order."""

    start = widget
    current: QtWidgets.QWidget | None = widget.nextInFocusChain()
    prev: QtWidgets.QWidget | None = None
    while current != start and current is not None:
        if current.focusPolicy() & QtCore.Qt.FocusPolicy.TabFocus:
            prev = current
        current = current.nextInFocusChain()
    return prev
