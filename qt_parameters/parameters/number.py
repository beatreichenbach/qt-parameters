from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar

from qtpy import QtCore, QtGui

from ..widgets import (
    FloatLineEdit,
    FloatSlider,
    IntLineEdit,
    IntSlider,
    NumberLineEdit,
    NumberSlider,
)
from ._multi import _MultiFloatBase, _MultiIntBase
from .base import MIN_SLIDER_WIDTH, ParameterWidget

E = TypeVar('E', int, float)


class NumberParameter(ParameterWidget[E], Generic[E]):
    value_changed = QtCore.Signal(object)

    _slider_min: E
    _slider_max: E
    _line_min: E | None = None
    _line_max: E | None = None
    _slider_visible: bool = True
    _commit_on_edit: bool = False
    _step_factor: int = 2

    line: NumberLineEdit[E]
    slider: NumberSlider[E]

    def _init_ui(self) -> None:
        self.line = self._create_line()
        self.line.set_value(self._value)
        self.line.value_changed.connect(self._line_value_changed)
        self._layout.addWidget(self.line)

        self.slider = self._create_slider()
        self.slider.set_maximum(self._slider_max)
        self.slider.value_changed.connect(self._slider_value_changed)
        # Prevent any size changes when slider shows
        self.slider.setMaximumHeight(self.line.minimumSizeHint().height())
        self._layout.addWidget(self.slider)
        self._layout.setStretch(1, 1)

        self.setFocusProxy(self.line)

    def commit_on_edit(self) -> bool:
        return self._commit_on_edit

    def line_min(self) -> E | None:
        return self._line_min

    def line_max(self) -> E | None:
        return self._line_max

    def slider_min(self) -> E:
        return self._slider_min

    def slider_max(self) -> E:
        return self._slider_max

    def slider_visible(self) -> bool:
        return self._slider_visible

    def step_factor(self) -> int:
        return self._step_factor

    def set_commit_on_edit(self, commit_on_edit: bool) -> None:
        self._commit_on_edit = commit_on_edit
        self.line.commit_on_edit = commit_on_edit

    def set_line_min(self, line_min: E | None) -> None:
        self._line_min = line_min
        self.line.set_minimum(line_min)

    def set_line_max(self, line_max: E | None) -> None:
        self._line_max = line_max
        self.line.set_maximum(line_max)

    def set_slider_min(self, slider_min: E) -> None:
        self._slider_min = slider_min
        self.slider.set_minimum(slider_min)

    def set_slider_max(self, slider_max: E) -> None:
        self._slider_max = slider_max
        self.slider.set_maximum(slider_max)

    def set_slider_visible(self, slider_visible: bool) -> None:
        self._slider_visible = slider_visible
        self._toggle_slider(slider_visible)

    def set_step_factor(self, factor: int) -> None:
        self._step_factor = factor
        self.slider.set_step_factor(factor)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self._toggle_slider(True)

    def set_value(self, value: E) -> None:
        super().set_value(value)
        self._set_line_value(value)
        self._set_slider_value(value)

    def _create_line(self) -> NumberLineEdit[E]:
        raise NotImplementedError

    def _create_slider(self) -> NumberSlider[E]:
        raise NotImplementedError

    def _line_value_changed(self, value: E) -> None:
        super().set_value(value)
        self._set_slider_value(value)

    def _slider_value_changed(self, value: E) -> None:
        super().set_value(value)
        self._set_line_value(value)

    def _set_line_value(self, value: E) -> None:
        self.line.blockSignals(True)
        self.line.set_value(value)
        self.line.blockSignals(False)

    def _set_slider_value(self, value: E) -> None:
        self.slider.blockSignals(True)
        self.slider.set_value(value)
        self.slider.blockSignals(False)

    def _toggle_slider(self, value: bool) -> None:
        has_space = self.size().width() > MIN_SLIDER_WIDTH
        self.slider.setVisible(self._slider_visible and value and has_space)


class IntParameter(NumberParameter[int]):
    value_changed = QtCore.Signal(int)

    _value: int = 0
    _default: int = 0
    _slider_min: int = 0
    _slider_max: int = 10

    def _create_line(self) -> NumberLineEdit[int]:
        return IntLineEdit(self)

    def _create_slider(self) -> NumberSlider[int]:
        return IntSlider()


class FloatParameter(NumberParameter[float]):
    value_changed = QtCore.Signal(float)

    _value: float = 0
    _default: float = 0
    _slider_min: float = 0
    _slider_max: float = 1
    _decimals: int = 4

    def _create_line(self) -> NumberLineEdit[float]:
        line = FloatLineEdit(self)
        line.set_decimals(self._decimals)
        return line

    def _create_slider(self) -> NumberSlider[float]:
        return FloatSlider()

    def decimals(self) -> int:
        return self._decimals

    def set_decimals(self, decimals: int) -> None:
        self._decimals = decimals
        if isinstance(self.line, FloatLineEdit):
            self.line.set_decimals(decimals)


class MultiIntParameter(_MultiIntBase[tuple[int, ...]]):
    value_changed = QtCore.Signal(tuple)

    _value: tuple[int, ...] = (0, 0)
    _default: tuple[int, ...] = (0, 0)

    def _cast_to_tuple(self, value: tuple[int, ...]) -> tuple[int, ...]:
        return value

    def _cast_to_type(self, values: Sequence[int]) -> tuple[int, ...]:
        return tuple(values)


class MultiFloatParameter(_MultiFloatBase[tuple[float, ...]]):
    value_changed = QtCore.Signal(tuple)

    _value: tuple[float, ...] = (0, 0)
    _default: tuple[float, ...] = (0, 0)

    def _cast_to_tuple(self, value: tuple[float, ...]) -> tuple[float, ...]:
        return value

    def _cast_to_type(self, values: Sequence[float]) -> tuple[float, ...]:
        return tuple(values)
