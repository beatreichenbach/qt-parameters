from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar

from qtpy import QtCore, QtGui, QtWidgets

from ..widgets import (
    FloatLineEdit,
    FloatSlider,
    IntLineEdit,
    IntSlider,
    NumberLineEdit,
    NumberSlider,
    RatioButton,
)
from .base import MIN_SLIDER_WIDTH, ParameterWidget

E = TypeVar('E', int, float)
V = TypeVar('V')


class MultiParameterWidget(ParameterWidget[V], Generic[E, V]):
    value_changed = QtCore.Signal(object)

    _value: V
    _default: V
    _count: int = 2
    _keep_ratio: bool = True
    _ratio_visible: bool = True
    _slider_visible: bool = True
    _line_min: E | None = None
    _line_max: E | None = None
    _slider_max: E

    lines: list[NumberLineEdit[E]]
    slider: NumberSlider[E]

    def _init_ui(self) -> None:
        # Lines
        self.lines = []
        for _ in range(self._count):
            line = self._create_line()
            line.set_value(0)
            line.value_changed.connect(self._line_value_changed)
            self._layout.addWidget(line)
            self.lines.append(line)

        # Slider
        self.slider = self._create_slider()
        self.slider.set_maximum(self._slider_max)
        self.slider.value_changed.connect(self._slider_value_changed)
        # Prevent any size changes when slider shows
        line_height = self.lines[0].minimumSizeHint().height()
        self.slider.setMaximumHeight(line_height)
        self._layout.addWidget(self.slider)
        self._layout.setStretch(self._count, 1)

        # Keep ratio button
        self.keep_ratio_button = RatioButton()
        self.keep_ratio_button.setMaximumSize(line_height, line_height)
        self.keep_ratio_button.toggled.connect(self.set_keep_ratio)
        self._layout.addWidget(self.keep_ratio_button)

        self.setFocusProxy(self.lines[0])
        self.set_keep_ratio(self._keep_ratio)

    def keep_ratio(self) -> bool:
        return self._keep_ratio

    def line_min(self) -> E | None:
        return self._line_min

    def line_max(self) -> E | None:
        return self._line_max

    def ratio_visible(self) -> bool:
        return self._ratio_visible

    def set_commit_on_edit(self, commit_on_edit: bool) -> None:
        for line in self.lines:
            line.commit_on_edit = commit_on_edit

    def set_keep_ratio(self, keep_ratio: bool) -> None:
        self._keep_ratio = keep_ratio
        self.keep_ratio_button.setChecked(keep_ratio)
        for line in self.lines[1:]:
            line.setVisible(not keep_ratio)
            if line.value() != self.lines[0].value():
                line.set_value(self.lines[0].value())
        self._toggle_slider(keep_ratio)

    def set_line_min(self, line_min: E | None) -> None:
        self._line_min = line_min
        for line in self.lines:
            line.set_minimum(line_min)

    def set_line_max(self, line_max: E | None) -> None:
        self._line_max = line_max
        for line in self.lines:
            line.set_maximum(line_max)

    def set_ratio_visible(self, ratio_visible: bool) -> None:
        self._ratio_visible = ratio_visible
        self.keep_ratio_button.setVisible(ratio_visible)
        for line in self.lines[1:]:
            line.setVisible(not ratio_visible)
        if not ratio_visible:
            self.set_keep_ratio(False)

    def set_slider_visible(self, slider_visible: bool) -> None:
        self._slider_visible = slider_visible
        self._toggle_slider(slider_visible)

    def set_default(self, default: V | Sequence[E]) -> None:
        self.set_value(default)
        self._default = self.value()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        QtWidgets.QWidget.resizeEvent(self, event)
        if self._keep_ratio:
            self._toggle_slider(True)

    def set_value(self, value: V | Sequence[E]) -> None:
        if isinstance(value, Sequence):
            values = value
        else:
            values = self._cast_to_tuple(value)
        if not all(values[0] == x for x in values):
            self.set_keep_ratio(False)
        if self._keep_ratio:
            values = (values[0],) * self._count
        super().set_value(self._cast_to_type(values))
        self._set_slider_value(values[0])
        self._set_line_values(values)

    def _create_line(self) -> NumberLineEdit[E]:
        raise NotImplementedError

    def _create_slider(self) -> NumberSlider[E]:
        raise NotImplementedError

    def _cast_to_tuple(self, value: V) -> tuple[E, ...]:
        raise NotImplementedError

    def _cast_to_type(self, values: Sequence[E]) -> V:
        raise NotImplementedError

    def _line_value_changed(self, value: E) -> None:
        if self._keep_ratio:
            values = (self.lines[0].value(),) * self._count
            for line in self.lines[1:]:
                line.set_value(values[0])
        else:
            values = tuple(line.value() for line in self.lines)

        super().set_value(self._cast_to_type(values))
        self._set_slider_value(values[0])

    def _slider_value_changed(self, value: E) -> None:
        values = (value,) * self._count
        super().set_value(self._cast_to_type(values))
        self._set_line_values(values)

    def _set_line_values(self, values: Sequence[E]) -> None:
        for line, value in zip(self.lines, values):
            line.blockSignals(True)
            line.set_value(value)
            line.blockSignals(False)

    def _set_slider_value(self, value: E) -> None:
        self.slider.blockSignals(True)
        self.slider.set_value(value)
        self.slider.blockSignals(False)

    def _toggle_slider(self, value: bool) -> None:
        has_space = self.size().width() > MIN_SLIDER_WIDTH
        self.slider.setVisible(self._slider_visible and value and has_space)


class _MultiIntBase(MultiParameterWidget[int, V], Generic[V]):
    _slider_max: int = 10

    def _create_line(self) -> NumberLineEdit[int]:
        return IntLineEdit(self)

    def _create_slider(self) -> NumberSlider[int]:
        return IntSlider()


class _MultiFloatBase(MultiParameterWidget[float, V], Generic[V]):
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
        for line in self.lines:
            if isinstance(line, FloatLineEdit):
                line.set_decimals(decimals)
