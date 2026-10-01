from __future__ import annotations

from typing import Generic, TypeVar

from qtpy import QtCore, QtWidgets

from ..widgets import utils

MIN_SLIDER_WIDTH = 200

T = TypeVar('T')


class ParameterWidget(QtWidgets.QWidget, Generic[T]):
    value_changed = QtCore.Signal(object)

    _value: T
    _default: T
    _name: str = ''
    _label: str = ''
    _tooltip: str = ''

    def __init__(self, name: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_layout()
        self._init_ui()

        if name:
            self.set_name(name)
            self.set_label(utils.title(name))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._name!r})'

    def _init_layout(self) -> None:
        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setContentsMargins(QtCore.QMargins())
        self.setLayout(self._layout)

    def _init_ui(self) -> None: ...

    def value(self) -> T:
        return self._value

    def default(self) -> T:
        return self._default

    def label(self) -> str:
        return self._label

    def name(self) -> str:
        return self._name

    def tooltip(self) -> str:
        return self._tooltip

    def set_value(self, value: T) -> None:
        if value != self._value:
            self._value = value
            self.value_changed.emit(value)

    def set_default(self, default: T) -> None:
        self.set_value(default)
        self._default = self.value()

    def set_label(self, label: str) -> None:
        self._label = label

    def set_name(self, name: str) -> None:
        self._name = name

    def set_tooltip(self, tooltip: str) -> None:
        self._tooltip = tooltip

    def reset(self) -> None:
        self.set_value(self.default())


class BoolParameter(ParameterWidget[bool]):
    value_changed = QtCore.Signal(bool)

    _value: bool = False
    _default: bool = False

    def _init_ui(self) -> None:
        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.toggled.connect(super().set_value)
        self._layout.addWidget(self.checkbox)
        self._layout.addStretch()
        self.setFocusProxy(self.checkbox)

    def value(self) -> bool:
        return super().value()

    def set_value(self, value: bool) -> None:
        super().set_value(value)
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(value)
        self.checkbox.blockSignals(False)
