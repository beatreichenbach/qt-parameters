from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import Enum
from typing import Callable, Generic, TypeVar

from qtpy import QtWidgets

from ..widgets import utils
from .base import ParameterWidget

T = TypeVar('T')
EnumT = TypeVar('EnumT', bound=Enum)


class ComboParameter(ParameterWidget[T | None], Generic[T]):
    _value: T | None = None
    _default: T | None = None
    _items: tuple[tuple[str, T], ...] = ()

    def _init_ui(self) -> None:
        self.combo = QtWidgets.QComboBox()
        self.combo.currentIndexChanged.connect(self._current_index_changed)
        self.combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )

        self._layout.addWidget(self.combo)
        self.setFocusProxy(self.combo)

    def items(self) -> tuple[tuple[str, T], ...]:
        return self._items

    def set_items(
        self, items: Mapping[str, T] | Sequence[T] | Sequence[tuple[str, T]]
    ) -> None:
        """
        Set the items of the parameter.
        `items` is either a sequence or dictionary with format (label, data).
        """

        if isinstance(items, Mapping):
            parsed: tuple[tuple[str, T], ...] = tuple(items.items())
        else:
            parsed = tuple(i if isinstance(i, tuple) else (str(i), i) for i in items)

        self._items = parsed
        self._refresh_items()
        default = parsed[0][1] if parsed else None
        self.set_default(default)
        self.set_value(default)

    def value(self) -> T | None:
        return super().value()

    def set_value(self, value: T | None) -> None:
        index = self._index_from_value(value)
        value = self.combo.itemData(index)
        super().set_value(value)
        self.combo.blockSignals(True)
        self.combo.setCurrentIndex(index)
        self.combo.blockSignals(False)

    def _current_index_changed(self, index: int) -> None:
        value = self.combo.itemData(index)
        super().set_value(value)

    def _index_from_value(self, value: object) -> int:
        """Return the index for a value, searching text and data."""

        if value is None:
            return -1

        if isinstance(value, str):
            index = self.combo.findText(value)
        else:
            index = -1

        if index < 0:
            index = self.combo.findData(value)
        return index

    def _refresh_items(self) -> None:
        self.combo.blockSignals(True)
        for index in reversed(range(self.combo.count())):
            self.combo.removeItem(index)
        for label, data in self._items:
            self.combo.addItem(label, data)
        self.combo.blockSignals(False)


class EnumParameter(ParameterWidget[EnumT | None], Generic[EnumT]):
    _value: EnumT | None = None
    _default: EnumT | None = None
    _formatter: Callable[[EnumT], str]
    _enum: type[EnumT] | None = None

    def __init__(self, name: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(name=name, parent=parent)

        self._formatter = lambda member: utils.title(member.name)

    def _init_ui(self) -> None:
        self.combo = QtWidgets.QComboBox()
        self.combo.currentIndexChanged.connect(self._current_index_changed)
        self.combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )

        self._layout.addWidget(self.combo)
        self.setFocusProxy(self.combo)

    def enum(self) -> type[EnumT] | None:
        return self._enum

    def formatter(self) -> Callable[[EnumT], str]:
        return self._formatter

    def set_enum(self, enum: type[EnumT]) -> None:
        self._enum = enum
        self._update_items()
        default = next(iter(enum))
        self.set_default(default)
        self.set_value(default)

    def set_formatter(self, formatter: Callable[[EnumT], str]) -> None:
        self._formatter = formatter
        index = self.combo.currentIndex()
        self._update_items()
        self.combo.setCurrentIndex(index)

    def value(self) -> EnumT | None:
        return super().value()

    def set_value(self, value: object) -> None:
        enum_value = self._enum_from_value(value)
        super().set_value(enum_value)

        self.combo.blockSignals(True)
        if enum_value is None:
            index = -1
        else:
            index = self.combo.findData(enum_value.value)
        self.combo.setCurrentIndex(index)
        self.combo.blockSignals(False)

    def _current_index_changed(self, index: int) -> None:
        value = self.combo.itemData(index)
        value = self._enum_from_value(value)
        super().set_value(value)

    def _enum_from_value(self, value: object) -> EnumT | None:
        enum = self._enum
        if enum is None:
            return None

        # value is Enum
        if isinstance(value, enum):
            return value

        # value is Enum.name
        if isinstance(value, str):
            try:
                return enum[value]
            except KeyError:
                pass

        # value is Enum.value
        try:
            return enum(value)
        except (ValueError, TypeError):
            return None

    def _update_items(self) -> None:
        self.combo.blockSignals(True)
        for index in reversed(range(self.combo.count())):
            self.combo.removeItem(index)

        enum = self._enum
        if enum is not None:
            for member in enum:
                label = self._formatter(member)
                self.combo.addItem(label, member.value)
        self.combo.blockSignals(False)
