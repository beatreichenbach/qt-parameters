from __future__ import annotations

import logging
import math
from numbers import Number
from typing import Generic, TypeVar

from qt_material_icons import MaterialIcon
from qtpy import QtCore, QtGui, QtWidgets

SUCCESS = 25


N = TypeVar('N', bound=Number)


class NumberLineEdit(QtWidgets.QLineEdit, Generic[N]):
    value_changed = QtCore.Signal(int)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_validator()

        self._abs_minimum = self._validator.bottom()
        self._abs_maximum = self._validator.top()
        self._minimum = self._abs_minimum
        self._maximum = self._abs_maximum
        self._value = 0

        self.commit_on_edit = False

        self.editingFinished.connect(self.commit)
        self.textEdited.connect(self._text_edit)

    def _init_validator(self) -> None:
        self._validator = IntValidator()
        self.setValidator(self._validator)

    def value(self) -> N:
        return self._value

    def set_value(self, value: N) -> None:
        text = self._validator.fixup(str(value))
        state, text_, pos_ = self._validator.validate(text, 0)
        if state == QtGui.QValidator.State.Acceptable:
            self.setText(text)
            self.commit()

    def minimum(self) -> N:
        return self._minimum

    def set_minimum(self, minimum: N | None) -> None:
        if minimum is None:
            minimum = self._abs_minimum
        self._minimum = minimum
        self._validator.setBottom(minimum)

    def maximum(self) -> N:
        return self._maximum

    def set_maximum(self, maximum: N | None) -> None:
        if maximum is None:
            maximum = self._abs_maximum
        self._maximum = maximum
        self._validator.setTop(maximum)

    def commit(self, update_text: bool = True) -> None:
        """Commit the current text."""

        try:
            value = int(self.text())
        except ValueError:
            value = 0

        # Strip padding
        if int(value) == value:
            value = int(value)
        if value != self._value:
            self._value = value
            self.value_changed.emit(value)
        if update_text:
            self.setText(str(value))

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_Up:
            self._step(add=True)
            event.accept()
        elif event.key() == QtCore.Qt.Key.Key_Down:
            self._step(add=False)
            event.accept()
        else:
            super().keyPressEvent(event)

    def minimumSizeHint(self) -> QtCore.QSize:
        size = super().minimumSizeHint()
        size.setWidth(24)
        return size

    def sizeHint(self) -> QtCore.QSize:
        size = super().sizeHint()
        size.setWidth(60)
        return size

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        delta = event.angleDelta()
        if delta.y() > 0:
            self._step(add=True)
        elif delta.y() < 0:
            self._step(add=False)
        event.accept()

    def _step(self, add: bool) -> bool:
        """Step up or down the text based on the current cursor position."""

        self.setFocus()
        text = self.text() or '0'
        position = self.cursorPosition()
        if self.hasSelectedText():
            position = self.selectionStart()

        # Check if the cursor is on a special character
        if position < len(text) and not text[position].isdigit():
            return False

        step_index = self._step_index(text, position)
        exponent = self._step_exponent(step_index)

        # Perform a step up or down
        amount = 1 if add else -1
        step = amount * pow(10, exponent)
        value = self._value + step

        text = self._format_value(value, text, exponent)

        # Validate before setting new text
        state, text_, pos_ = self.validator().validate(text, 0)
        if state != QtGui.QValidator.State.Acceptable:
            return False
        self.setText(text)

        # Don't commit change to preserve padding
        self._value = value
        self.value_changed.emit(value)

        # Get the new position and set selection
        position = self._relative_position(step_index, text)
        self.setSelection(position, 1)
        return True

    def _text_edit(self) -> None:
        """Handle when the text has been edited."""

        if self.commit_on_edit:
            self.commit(update_text=False)

    def _format_value(self, value: int, current_text: str, exponent: int) -> str:
        """Return the text for a value, preserving the format of the current text."""

        padding = len([t for t in current_text if t.isdigit()])
        if value < 0:
            padding += 1
        text = f'{value:0{padding}}'
        return text

    def _step_exponent(self, step_index: int) -> int:
        """Return the exponent for the cursor position."""

        exponent = step_index - 1
        return exponent

    def _step_index(self, text: str, position: int) -> int:
        """
        Return the step index relative to the decimal point.
        This preserves position when the number gets larger or changes +/- sign.
        """

        step_index = len(text) - position
        # If cursor is at end, edit the first digit
        step_index = max(1, step_index)

        return step_index

    def _relative_position(self, step_index: int, text: str) -> int:
        """Return the relative position for the text at step index."""

        position = len(text) - step_index
        return position


class IntLineEdit(NumberLineEdit[int]):
    value_changed = QtCore.Signal(int)


class FloatLineEdit(NumberLineEdit[float]):
    value_changed = QtCore.Signal(float)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._decimals = self._validator.decimals()

    def _init_validator(self) -> None:
        self._validator = DoubleValidator()
        # NOTE: Using QLocale.c() fixes validation issues in non-English locales that
        # use comma decimal separators.
        self._validator.setLocale(QtCore.QLocale.c())
        self._validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        self.setValidator(self._validator)

    def commit(self, update_text: bool = True) -> None:
        """Commit the current text."""

        try:
            value = float(self.text())
        except ValueError:
            value = float(0)

        # Strip padding
        if value != self._value:
            self._value = value
            self.value_changed.emit(value)
        if update_text:
            if int(value) == value:
                value = int(value)
            self.setText(str(value))

    def decimals(self) -> int:
        return self._decimals

    def set_decimals(self, value: int) -> None:
        self._decimals = value
        self._validator.setDecimals(value)

    def _format_value(self, value: int, current_text: str, exponent: int) -> str:
        decimal_index = current_text.find('.')

        # Preserve padding
        if decimal_index == -1:
            padding_decimal = 0
        else:
            padding_decimal = len(current_text) - 1 - decimal_index
            current_text = current_text[:decimal_index]

        # Preserve padding when switching to something like 1.001 > 1.000
        padding_decimal = max(padding_decimal, -exponent)
        padding_int = len([t for t in current_text if t.isdigit()])
        # Account for minus sign
        if value < 0:
            padding_int += 1

        # padding_int needs to contain both padding for int and decimals
        padding_int += padding_decimal + 1 * bool(padding_decimal)

        value = round(value, padding_decimal)
        text = f'{value:0{padding_int}.{padding_decimal}f}'

        return text

    def _step_exponent(self, step_index: int) -> int:
        exponent = step_index
        # If the cursor is on a decimal edit the first decimal.
        if step_index >= 0:
            exponent = step_index - 1

        return exponent

    def _step_index(self, text: str, position: int) -> int:
        decimal_index = text.find('.')
        if decimal_index == -1:
            step_index = len(text) - position
        else:
            step_index = decimal_index - position
        return step_index

    def _relative_position(self, step_index: int, text: str) -> int:
        decimal_index = text.find('.')
        position = len(text) - step_index
        if decimal_index > -1:
            # If the position is on a decimal point, move to the first decimal.
            if step_index == 0:
                step_index = -1
            position = decimal_index - step_index
        return position


class IntValidator(QtGui.QIntValidator):
    def fixup(self, text: str) -> str:
        text = str(super().fixup(text))
        text = text.replace(',', '')
        try:
            text = str(max(min(int(text), self.top()), self.bottom()))
        except ValueError:
            pass
        return text


class DoubleValidator(QtGui.QDoubleValidator):
    def fixup(self, text: str) -> str:
        try:
            float(text)
        except ValueError:
            characters = '+-01234567890.'
            text = ''.join(t for t in text if t in characters)

        try:
            value = float(text)
            value = min(max(value, self.bottom()), self.top())
            value = round(value, self.decimals())
            text = '{value:.{decimals}f}'.format(value=value, decimals=self.decimals())
            return text
        except (ValueError, TypeError):
            return text


class NumberSlider(QtWidgets.QSlider, Generic[N]):
    def __init__(
        self,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(orientation, parent)

        self.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBothSides)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

    def _exponent(self) -> int:
        """Return the exponent based on the minimum and maximum."""

        num_range = abs(self.maximum() - self.minimum())
        if num_range == 0:
            num_range = 1
        exponent = math.log10(num_range)

        # Round exponent up or down with weighting towards down
        if exponent % 1 > 0.8:
            exponent = math.ceil(exponent)
        else:
            exponent = math.floor(exponent)
        return exponent


class IntSlider(NumberSlider[int]):
    value_changed = QtCore.Signal(int)

    def __init__(
        self,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(orientation, parent)

        self.valueChanged.connect(self.value_changed)

    def set_value(self, value: int) -> None:
        self.setSliderPosition(value)

    def set_minimum(self, value: int) -> None:
        self.setMinimum(value)
        self._refresh_steps()

    def set_maximum(self, value: int) -> None:
        self.setMaximum(value)
        self._refresh_steps()

    def _refresh_steps(self) -> None:
        """Refresh the slider ticks and steps based on the minimum and maximum."""

        step = pow(10, max(self._exponent() - 2, 0))

        self.setSingleStep(step)
        self.setPageStep(step * 10)
        self.setTickInterval(step * 10)


class FloatSlider(NumberSlider[float]):
    value_changed = QtCore.Signal(float)

    def __init__(
        self,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(orientation, parent)

        self._minimum = super().minimum()
        self._maximum = super().maximum()

        self.setSingleStep(1)
        self.setPageStep(10)
        self.setTickInterval(10)

        self.valueChanged.connect(self._value_changed)

    def value(self) -> float:
        value = super().value()
        float_value = self._float(value)
        return float_value

    def set_value(self, value: float) -> None:
        if math.isnan(value):
            return
        int_value = self._int(value)
        self.setSliderPosition(int_value)

    def minimum(self) -> float:
        return self._minimum

    def set_minimum(self, minimum: float) -> None:
        value = self.value()
        self._minimum = minimum
        self._refresh_steps()
        self.set_value(value)

    def maximum(self) -> float:
        return self._maximum

    def set_maximum(self, maximum: float) -> None:
        value = self.value()
        self._maximum = maximum
        self._refresh_steps()
        self.set_value(value)

    def _int(self, value: float) -> int:
        """Return an int value in slider scale."""

        try:
            percentage = (value - self._minimum) / (self._maximum - self._minimum)
        except ZeroDivisionError:
            return 0
        slider_range = super().maximum() - super().minimum()
        clamped_value = min(max(percentage, 0), 1) * slider_range + super().minimum()
        return int(clamped_value)

    def _float(self, value: int) -> float:
        """Return a float value in slider scale."""

        slider_range = super().maximum() - super().minimum()
        try:
            percentage = (value - super().minimum()) / slider_range
        except ZeroDivisionError:
            return float('nan')
        float_value = self._minimum + (self._maximum - self._minimum) * percentage
        return float_value

    def _refresh_steps(self) -> None:
        """Refresh the slider ticks and steps based on the minimum and maximum."""

        # Find a value that brings the float range into an int range
        # with step size locked to 1 and 10
        step = pow(10, -(self._exponent() - 2))

        self.blockSignals(True)
        self.setMinimum(int(self._minimum * step))
        self.setMaximum(int(self._maximum * step))
        self.blockSignals(False)

    def _value_changed(self, value: int) -> None:
        """Emit a float signal on value change."""

        value = self._float(value)
        if not math.isnan(value):
            self.value_changed.emit(value)


class RatioButton(QtWidgets.QPushButton):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self._icon_off = MaterialIcon('link_off')
        self._icon_on = MaterialIcon('link')

        self.toggled.connect(self._checked_change)
        size = self.iconSize().width()
        self.setMaximumSize(QtCore.QSize(size, size))
        self.setCheckable(True)
        self._checked_change(False)

    def _checked_change(self, checked: bool) -> None:
        # BUG: fusion style does not recognize On/Off for QIcons
        # https://bugreports.qt.io/browse/QTBUG-82110
        icon = self._icon_on if checked else self._icon_off
        super().setIcon(icon)


class TextEdit(QtWidgets.QPlainTextEdit):
    editing_finished = QtCore.Signal()

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        self.editing_finished.emit()
        return super().focusOutEvent(event)

    def sizeHint(self) -> QtCore.QSize:
        size_hint = super().sizeHint()
        size_hint.setHeight(self.minimumSizeHint().height())
        return size_hint


class Label(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._icon = None
        style = self.style()
        icon_size = style.pixelMetric(QtWidgets.QStyle.PixelMetric.PM_ButtonIconSize)
        self._icon_size = QtCore.QSize(icon_size, icon_size)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(QtCore.QMargins())
        self.setLayout(layout)

        self._icon_label = QtWidgets.QLabel()
        layout.addWidget(self._icon_label)
        self._text_label = QtWidgets.QLabel()
        self._text_label.setWordWrap(True)
        layout.addWidget(self._text_label)
        layout.setStretch(1, 1)

    def icon(self) -> QtGui.QIcon | None:
        return self._icon

    def set_icon(self, icon: QtGui.QIcon | None) -> None:
        self._icon = icon
        self._refresh_icon()

    def icon_size(self) -> QtCore.QSize:
        return self._icon_size

    def set_icon_size(self, icon_size: QtCore.QSize) -> None:
        self._icon_size = icon_size
        self._refresh_icon()

    def text(self) -> str:
        return self._text_label.text()

    def set_text(self, text: str) -> None:
        self._text_label.setText(text)

    def set_level(self, level: int) -> None:
        icon = None
        color = None
        if level >= logging.CRITICAL:
            icon = MaterialIcon('report')
            color = self._color('magenta')
        elif level >= logging.ERROR:
            icon = MaterialIcon('error')
            color = self._color('red')
        elif level >= logging.WARNING:
            icon = MaterialIcon('warning')
            color = self._color('orange')
        elif level >= SUCCESS:
            icon = MaterialIcon('check_circle')
            color = self._color('green')
        elif level >= logging.INFO:
            icon = MaterialIcon('info')

        self.set_icon(icon)
        if icon:
            # Create a custom pixmap with color.
            self._icon_label.setPixmap(icon.pixmap(size=self._icon_size, color=color))

    def _refresh_icon(self) -> None:
        if self._icon:
            self._icon_label.setPixmap(self._icon.pixmap(self._icon_size))
        else:
            self._icon_label.clear()

    @staticmethod
    def _color(name: str) -> QtGui.QColor | None:
        try:
            import qt_themes
        except ImportError:
            return None

        if theme := qt_themes.get_theme():
            return getattr(theme, name, None)
        return None
