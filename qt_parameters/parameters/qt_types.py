from __future__ import annotations

from collections.abc import Sequence

from qtpy import QtCore, QtGui, QtWidgets

from ._multi import _MultiFloatBase, _MultiIntBase


class PointParameter(_MultiIntBase[QtCore.QPoint]):
    value_changed = QtCore.Signal(QtCore.QPoint)

    _value: QtCore.QPoint = QtCore.QPoint(0, 0)
    _default: QtCore.QPoint = QtCore.QPoint(0, 0)
    _slider_visible: bool = False
    _ratio_visible: bool = False

    def _init_ui(self) -> None:
        super()._init_ui()
        self.set_slider_visible(self._slider_visible)
        self.set_ratio_visible(self._ratio_visible)

    def _cast_to_tuple(self, value: QtCore.QPoint) -> tuple[int, ...]:
        return value.x(), value.y()

    def _cast_to_type(self, values: Sequence[int]) -> QtCore.QPoint:
        return QtCore.QPoint(*values[:2])


class PointFParameter(_MultiFloatBase[QtCore.QPointF]):
    value_changed = QtCore.Signal(QtCore.QPointF)

    _value: QtCore.QPointF = QtCore.QPointF(0, 0)
    _default: QtCore.QPointF = QtCore.QPointF(0, 0)
    _slider_visible: bool = False
    _ratio_visible: bool = False

    def _init_ui(self) -> None:
        super()._init_ui()
        self.set_slider_visible(self._slider_visible)
        self.set_ratio_visible(self._ratio_visible)

    def _cast_to_tuple(self, value: QtCore.QPointF) -> tuple[float, ...]:
        return value.x(), value.y()

    def _cast_to_type(self, values: Sequence[float]) -> QtCore.QPointF:
        return QtCore.QPointF(*values[:2])


class SizeParameter(_MultiIntBase[QtCore.QSize]):
    value_changed = QtCore.Signal(QtCore.QSize)

    _value: QtCore.QSize = QtCore.QSize(0, 0)
    _default: QtCore.QSize = QtCore.QSize(0, 0)

    def _cast_to_tuple(self, value: QtCore.QSize) -> tuple[int, ...]:
        return value.width(), value.height()

    def _cast_to_type(self, values: Sequence[int]) -> QtCore.QSize:
        return QtCore.QSize(*values[:2])


class SizeFParameter(_MultiFloatBase[QtCore.QSizeF]):
    value_changed = QtCore.Signal(QtCore.QSizeF)

    _value: QtCore.QSizeF = QtCore.QSizeF(0, 0)
    _default: QtCore.QSizeF = QtCore.QSizeF(0, 0)

    def _cast_to_tuple(self, value: QtCore.QSizeF) -> tuple[float, ...]:
        return value.width(), value.height()

    def _cast_to_type(self, values: Sequence[float]) -> QtCore.QSizeF:
        return QtCore.QSizeF(*values[:2])


class ColorParameter(_MultiFloatBase[QtGui.QColor]):
    value_changed = QtCore.Signal(QtGui.QColor)

    _count: int = 3
    _value: QtGui.QColor = QtGui.QColor(0, 0, 0)
    _default: QtGui.QColor = QtGui.QColor(0, 0, 0)
    _color_min: float = 0
    _color_max: float = 1
    _decimals: int = 2

    def _init_ui(self) -> None:
        super()._init_ui()

        for line in self.lines:
            line.set_maximum(self._color_max)

        self.button = QtWidgets.QPushButton()
        self.button.clicked.connect(self.select_color)
        self.button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        size = self.button.sizeHint()
        self.button.setMaximumWidth(size.height())
        self._layout.insertWidget(self._layout.count() - 1, self.button)

    def color_min(self) -> float:
        return self._color_min

    def color_max(self) -> float:
        return self._color_max

    def set_color_min(self, color_min: float) -> None:
        self._color_min = color_min
        for line in self.lines:
            line.set_minimum(self._color_min)

    def set_color_max(self, color_max: float) -> None:
        self._color_max = color_max
        for line in self.lines:
            line.set_maximum(self._color_max)

    def select_color(self) -> None:
        options = QtWidgets.QColorDialog.ColorDialogOption.DontUseNativeDialog
        color = QtWidgets.QColorDialog.getColor(initial=self._value, options=options)
        if color.isValid():
            super().set_value(color)
            values = self._cast_to_tuple(color)
            self._set_line_values(values)
            self._set_button_value(color)

    def value(self) -> QtGui.QColor:
        return super().value()

    def set_value(self, value: QtGui.QColor | Sequence[float]) -> None:
        super().set_value(value)
        self._set_button_value(self._value)

    def _cast_to_tuple(self, value: QtGui.QColor) -> tuple[float, ...]:
        return value.redF(), value.greenF(), value.blueF()

    def _cast_to_type(self, values: Sequence[float]) -> QtGui.QColor:
        return QtGui.QColor.fromRgbF(*values[:3])

    def _line_value_changed(self, value: float) -> None:
        super()._line_value_changed(value)
        self._set_button_value(self._value)

    def _slider_value_changed(self, value: float) -> None:
        super()._slider_value_changed(value)
        self._set_button_value(self._value)

    def _set_button_value(self, value: QtGui.QColor) -> None:
        self.button.setPalette(QtGui.QPalette(value))
