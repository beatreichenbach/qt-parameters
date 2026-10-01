from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import Enum, auto
from functools import partial
from typing import Generic, TypeVar

from qtpy import QtCore, QtGui, QtWidgets

from ..qt_material_icons import MaterialIcon
from ..widgets import ResizeGrip, TextEdit
from .base import ParameterWidget

T = TypeVar('T')


class TextParameter(ParameterWidget[T], Generic[T]):
    class MenuMode(Enum):
        REPLACE = auto()
        TOGGLE = auto()

    value_changed = QtCore.Signal(object)

    _value: T
    _default: T
    _placeholder: str = ''
    _area: bool = False
    _menu: QtWidgets.QMenu | None = None
    _menu_data: Mapping[str, object] | Sequence[object] | None = None
    _menu_mode: MenuMode = MenuMode.REPLACE

    text: QtWidgets.QLineEdit | TextEdit

    def _init_ui(self) -> None:
        self._init_text()

        self.menu_button = QtWidgets.QToolButton()
        self.menu_button.setAutoRaise(True)
        self._layout.addWidget(self.menu_button)
        self.menu_button.hide()

    def _init_text(self) -> None:
        if self._area:
            self.text = TextEdit()
            self.text.editing_finished.connect(self._editing_finished)
            resize_grip = ResizeGrip(self.text)
            # Initialize the ResizeGrip to allow resizing smaller
            _ = resize_grip.min_size
        else:
            self.text = QtWidgets.QLineEdit()
            self.text.editingFinished.connect(self._editing_finished)
        self._layout.insertWidget(0, self.text)
        self.setFocusProxy(self.text)

    def _set_text(self, value: T) -> None:
        raise NotImplementedError

    def _text_value(self) -> T:
        raise NotImplementedError

    def _action_triggered(self, action: QtGui.QAction) -> None:
        raise NotImplementedError

    def area(self) -> bool:
        return self._area

    def menu(self) -> QtWidgets.QMenu:
        if self._menu is None:
            menu = self._build_menu(self._menu_data)
            self._menu = menu
            return menu
        return self._menu

    def menu_mode(self) -> MenuMode:
        return self._menu_mode

    def placeholder(self) -> str:
        return self._placeholder

    def set_area(self, area: bool) -> None:
        if area != self._area:
            self._area = area
            self._layout.removeWidget(self.text)
            self.text.deleteLater()
            self._init_text()

    def set_menu(self, menu: Mapping[str, object] | Sequence[object] | None) -> None:
        """
        Set the menu used to populate the parameter.
        The menu can be a Sequence of values or a dictionary of label: value pairs.
        """

        self._menu_data = menu
        self._menu = None

        # Update menu
        if not self._area and self._menu_data is not None:
            if not self.menu_button.defaultAction():
                # build dynamically for optimization
                icon = MaterialIcon('expand_more')
                action = QtGui.QAction(icon, 'Fill', self)
                action.triggered.connect(self._show_menu)
                self.menu_button.setDefaultAction(action)
            self.menu_button.show()
        else:
            self.menu_button.hide()

    def set_menu_mode(self, mode: MenuMode) -> None:
        self._menu_mode = mode

    def set_placeholder(self, placeholder: str) -> None:
        self._placeholder = placeholder
        self.text.setPlaceholderText(placeholder)

    def value(self) -> T:
        return super().value()

    def set_value(self, value: T) -> None:
        super().set_value(value)
        self.text.blockSignals(True)
        self._set_text(value)
        self.text.blockSignals(False)

    def _build_menu(
        self,
        items: Mapping[str, object] | Sequence[object] | None,
        menu: QtWidgets.QMenu | None = None,
    ) -> QtWidgets.QMenu:
        """Recursively build the QMenu from content."""

        if menu is None:
            menu = QtWidgets.QMenu(self)
        if items is None:
            return menu
        if isinstance(items, Sequence):
            items = {str(item): item for item in items}
        for label, data in items.items():
            if isinstance(data, Mapping):
                sub_menu = menu.addMenu(label)
                self._build_menu(data, sub_menu)
            else:
                action = QtGui.QAction(label, self)
                action.setData(data)
                action.triggered.connect(partial(self._action_triggered, action))
                menu.addAction(action)
        return menu

    def _editing_finished(self) -> None:
        super().set_value(self._text_value())

    def _refresh_height(self) -> None:
        if isinstance(self.text, QtWidgets.QPlainTextEdit):
            line_count = self.text.document().lineCount() + 1
            metrics = self.text.fontMetrics()
            line_spacing = metrics.lineSpacing()
            height = (
                line_count * line_spacing
                + self.text.contentsMargins().top()
                + self.text.contentsMargins().bottom()
            )
            height = max(height, self.text.minimumHeight())
            self.text.setFixedHeight(height)

    def _show_menu(self) -> None:
        relative_pos = self.menu_button.rect().topRight()
        relative_pos.setX(relative_pos.x() + 2)
        position = self.menu_button.mapToGlobal(relative_pos)

        menu = self.menu()
        menu.exec_(position)
        self.menu_button.setDown(False)


class StringParameter(TextParameter[str]):
    value_changed = QtCore.Signal(str)

    _value: str = ''
    _default: str = ''

    def _set_text(self, value: str) -> None:
        if isinstance(self.text, QtWidgets.QPlainTextEdit):
            self.text.setPlainText(value)
            self._refresh_height()
        elif isinstance(self.text, QtWidgets.QLineEdit):
            self.text.setText(value)

    def _text_value(self) -> str:
        if isinstance(self.text, QtWidgets.QPlainTextEdit):
            return self.text.toPlainText()
        if isinstance(self.text, QtWidgets.QLineEdit):
            return self.text.text()
        return ''

    def _action_triggered(self, action: QtGui.QAction) -> None:
        data = action.data()
        value = str(data)
        if self._menu_mode == self.MenuMode.REPLACE:
            self.set_value(value)
        elif self._menu_mode == self.MenuMode.TOGGLE:
            values = self._value.split(' ')
            if value in values:
                values = (v for v in values if v != value)
            else:
                values.append(value)
            self.set_value(' '.join(values))


class StringListParameter(TextParameter[tuple[str, ...]]):
    _value: tuple[str, ...] = ()
    _default: tuple[str, ...] = ()
    _area: bool = True

    def set_value(self, value: Sequence[str]) -> None:
        super().set_value(tuple(value))

    def _set_text(self, value: tuple[str, ...]) -> None:
        if isinstance(self.text, QtWidgets.QPlainTextEdit):
            self.text.setPlainText('\n'.join(value))
            self._refresh_height()
        elif isinstance(self.text, QtWidgets.QLineEdit):
            self.text.setText(' '.join(value))

    def _text_value(self) -> tuple[str, ...]:
        if isinstance(self.text, QtWidgets.QPlainTextEdit):
            values = self.text.toPlainText().split('\n')
        elif isinstance(self.text, QtWidgets.QLineEdit):
            values = self.text.text().split(' ')
        else:
            return ()
        return tuple(v for v in values if v)

    def _action_triggered(self, action: QtGui.QAction) -> None:
        data = action.data()
        value = str(data)
        if self._menu_mode == self.MenuMode.REPLACE:
            self.set_value((value,))
        elif self._menu_mode == self.MenuMode.TOGGLE:
            values = self._value
            if value in values:
                values = tuple(v for v in values if v != value)
            else:
                values = (*values, value)
            self.set_value(values)
