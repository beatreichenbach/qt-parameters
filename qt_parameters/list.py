from __future__ import annotations

import logging
from collections.abc import Sequence
from functools import partial
from typing import Callable

from qt_material_icons import MaterialIcon
from qtpy import QtCore, QtGui, QtWidgets

from .editor import ParameterForm
from .widgets import ParameterWidget, StringParameter

logger = logging.getLogger(__name__)


class DragItem(QtWidgets.QFrame):
    drag_started = QtCore.Signal()
    drag_ended = QtCore.Signal()
    removed = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self._widget = None

        self._init_ui()

    def _init_ui(self) -> None:
        # Force the TabFocus FocusPolicy to allow setting TabOrder.
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setAutoFillBackground(True)

        self._layout = QtWidgets.QHBoxLayout()
        self.setLayout(self._layout)

        self.drag_label = QtWidgets.QLabel()
        pixmap = MaterialIcon('drag_handle').pixmap()
        self.drag_label.setPixmap(pixmap)
        self._layout.addWidget(self.drag_label)
        self._layout.setStretch(0, 0)

        self._widget = QtWidgets.QWidget()
        self._layout.addWidget(self._widget)
        self._layout.setStretch(1, 1)

        remove_button = QtWidgets.QToolButton()
        remove_button.setIcon(MaterialIcon('delete'))
        remove_button.clicked.connect(self.removed)
        remove_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._layout.addWidget(remove_button)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.childAt(event.pos()) == self.drag_label:
            self.drag_started.emit()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.drag_ended.emit()
        super().mouseReleaseEvent(event)

    def widget(self) -> QtWidgets.QWidget:
        return self._widget

    def set_widget(self, widget: QtWidgets.QWidget) -> None:
        if self._widget:
            self._layout.removeWidget(self._widget)
            self._widget.deleteLater()
        self._widget = widget
        self._layout.insertWidget(1, self._widget)
        self._layout.setStretch(1, 1)
        self.setFocusProxy(self._widget)


class DragWidget(QtWidgets.QWidget):
    item_added = QtCore.Signal(DragItem)
    item_removed = QtCore.Signal()
    item_moved = QtCore.Signal(DragItem)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._factory = QtWidgets.QWidget
        self._placeholder = None
        self._drag_item = None
        self._drag_offset = 0
        self._drag_start_index = -1

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.setLayout(layout)

        self._item_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self._item_layout)

        add_frame = QtWidgets.QFrame()
        layout.addWidget(add_frame)

        add_layout = QtWidgets.QHBoxLayout()
        add_frame.setLayout(add_layout)

        add_layout.addStretch()

        add_button = QtWidgets.QToolButton()
        add_button.setIcon(MaterialIcon('add'))
        add_button.clicked.connect(self.add_item)
        add_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        add_layout.addWidget(add_button)

        layout.addStretch()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._drag_item:
            self._drag_move(event.pos())

    def factory(self) -> type[QtWidgets.QWidget] | Callable[[], QtWidgets.QWidget]:
        return self._factory

    def set_factory(
        self, factory: type[QtWidgets.QWidget] | Callable[[], QtWidgets.QWidget]
    ) -> None:
        self._factory = factory

    def add_item(self) -> DragItem:
        """Add a new item to the layout."""

        item = DragItem()
        item.drag_started.connect(partial(self._drag_started, item))
        item.drag_ended.connect(self._drag_ended)
        item.removed.connect(partial(self._remove_item, item))

        widget = self._factory()
        item.set_widget(widget)

        self._item_layout.addWidget(item)
        self.item_added.emit(item)
        return item

    def items(self) -> tuple[DragItem, ...]:
        """Return all DragItems in the layout."""

        items = []
        for i in range(self._item_layout.count()):
            if item := self._item_layout.itemAt(i):
                widget = item.widget()
                if isinstance(widget, DragItem):
                    items.append(widget)
        return tuple(items)

    def clear(self) -> None:
        """Clear the layout."""

        while item := self._item_layout.takeAt(0):
            if widget := item.widget():
                widget.deleteLater()

    def _remove_item(self, item: DragItem) -> None:
        self._item_layout.removeWidget(item)
        item.deleteLater()
        self.item_removed.emit()

    def _drag_started(self, item: DragItem) -> None:
        """
        Handle the start of a drag event. Store the current offset and create a
        placeholder.
        """

        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.SizeAllCursor))

        self._drag_item = item
        local_position = self.mapFromGlobal(QtGui.QCursor.pos())
        self._drag_offset = item.y() - local_position.y()

        # Create placeholder
        self._placeholder = QtWidgets.QWidget()
        self._placeholder.setMinimumHeight(item.height())
        index = self._item_layout.indexOf(item)
        self._drag_start_index = index
        if index >= 0:
            self._item_layout.insertWidget(index, self._placeholder)

        # Float the DragItem
        self._item_layout.removeWidget(item)
        item.raise_()

    def _drag_move(self, position: QtCore.QPoint) -> None:
        """
        Handle the move of the drag event. Move the DragItem with the mouse and keep
        the placeholder underneath the mouse.
        """

        pos_y = position.y() + self._drag_offset
        self._drag_item.move(self._drag_item.x(), pos_y)

        index = self._get_index(position)
        if index >= 0:
            self._move_item(self._placeholder, index)

    def _drag_ended(self) -> None:
        """
        Handle the end of a drag event. Remove the placeholder and re-insert the
        DragItem.
        """

        if not self._drag_item:
            # This was not a drag event.
            return

        index = -1
        if self._placeholder:
            index = self._item_layout.indexOf(self._placeholder)
            self._item_layout.removeWidget(self._placeholder)
            self._placeholder.deleteLater()
            self._placeholder = None

        if index < 0:
            index = self._drag_start_index
        # Ensure the DragItem is always inserted back into the layout.
        index = max(0, index)
        self._item_layout.insertWidget(index, self._drag_item)
        self._drag_item = None

        self._refresh_tab_order()
        self.unsetCursor()

        if index != self._drag_start_index:
            self.item_moved.emit(self._drag_item)
        self._drag_start_index = -1

    def _get_index(self, position: QtCore.QPoint) -> int:
        """Return the index in the layout for a position."""

        i = -1
        for i in range(self._item_layout.count()):
            if widget := self._item_layout.itemAt(i).widget():
                if position.y() < widget.y() + widget.height():
                    return i
        return i

    def _move_item(self, widget: QtWidgets.QWidget, index: int) -> None:
        """Move the widget to the given index, but only if needed."""

        current_index = self._item_layout.indexOf(widget)
        if current_index != index:
            self._item_layout.insertWidget(index, widget)

    def _refresh_tab_order(self) -> None:
        """Refresh the TabOrder from start to the end of the layout."""

        first = None
        for i in range(self._item_layout.count()):
            if item := self._item_layout.itemAt(i):
                if widget := item.widget():
                    if first:
                        self.setTabOrder(first, widget)
                    first = widget


class ListParameter(ParameterWidget):
    _value: tuple = ()
    _default: tuple = ()
    _factory: type[ParameterWidget | ParameterForm] | None = None

    def _init_ui(self) -> None:
        self.drag = DragWidget()
        self.drag.item_added.connect(self._item_added)
        self.drag.item_removed.connect(self._items_changed)
        self.drag.item_moved.connect(lambda: self._items_changed())
        self.setFocusProxy(self.drag)
        self._layout.addWidget(self.drag)

    def factory(self) -> type[ParameterWidget | ParameterForm] | None:
        return self._factory

    def set_factory(self, factory: type[ParameterWidget | ParameterForm]) -> None:
        self._factory = factory
        self.drag.set_factory(factory)
        self.drag.clear()

    def value(self) -> tuple:
        return super().value()

    def set_value(self, value: Sequence) -> None:
        self.drag.clear()
        for v in value:
            item = self.drag.add_item()
            widget = item.widget()
            widget.blockSignals(True)
            if isinstance(widget, ParameterWidget):
                widget.set_value(v)
            elif isinstance(widget, ParameterForm):
                widget.set_values(v)
            widget.blockSignals(False)

        if not isinstance(value, tuple):
            value = tuple(value)
        super().set_value(value)

    def _item_added(self, item: DragItem) -> None:
        widget = item.widget()
        if isinstance(widget, ParameterWidget):
            widget.value_changed.connect(self._items_changed)
        elif isinstance(widget, ParameterForm):
            widget.parameter_changed.connect(self._items_changed)

    def _items_changed(self) -> None:
        values = self._get_values()
        super().set_value(values)

    def _get_values(self) -> tuple:
        """Return the values of all items in the DragWidget as a tuple."""

        values = []
        for item in self.drag.items():
            widget = item.widget()
            if isinstance(widget, ParameterWidget):
                values.append(widget.value())
            elif isinstance(widget, ParameterForm):
                values.append(widget.values())
        return tuple(values)


class StringListParameter(StringParameter):
    _value: tuple[str, ...] = ()
    _default: tuple[str, ...] = ()
    _area: bool = True

    def value(self) -> tuple[str, ...]:
        return super().value()

    def set_value(self, value: Sequence[str]) -> None:
        if not isinstance(value, tuple):
            value = tuple(value)
        ParameterWidget.set_value(self, value)

        self.text.blockSignals(True)
        if isinstance(self.text, QtWidgets.QPlainTextEdit):
            text = '\n'.join(value)
            self.text.setPlainText(text)
            self._refresh_height()
        elif isinstance(self.text, QtWidgets.QLineEdit):
            text = ' '.join(value)
            self.text.setText(text)
        self.text.blockSignals(False)

    def _action_triggered(self, action: QtGui.QAction) -> None:
        data = action.data()
        value = str(data)
        if self._menu_mode == StringParameter.MenuMode.REPLACE:
            self.set_value((value,))
        elif self._menu_mode == StringParameter.MenuMode.TOGGLE:
            values = self._value
            if value in values:
                values = (v for v in values if v != value)
            else:
                values = (*values, value)
            self.set_value(values)

    def _editing_finished(self) -> None:
        if isinstance(self.text, QtWidgets.QPlainTextEdit):
            values = self.text.toPlainText().split('\n')
        elif isinstance(self.text, QtWidgets.QLineEdit):
            values = self.text.text().split(' ')
        else:
            return

        values = tuple(v for v in values if v)
        ParameterWidget.set_value(self, values)
