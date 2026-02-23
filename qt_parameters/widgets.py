from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from enum import Enum, EnumMeta, auto
from functools import partial
from typing import Any, Callable

from qt_material_icons import MaterialIcon
from qtpy import QtCore, QtGui, QtWidgets

from . import utils
from .inputs import (
    FloatLineEdit,
    FloatSlider,
    IntLineEdit,
    IntSlider,
    RatioButton,
    TextEdit,
)
from .resizegrip import ResizeGrip

MIN_SLIDER_WIDTH = 200


class ParameterWidget(QtWidgets.QWidget):
    value_changed = QtCore.Signal(object)

    _value: Any = None
    _default: Any = None
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

    def value(self) -> Any:
        return self._value

    def set_value(self, value: Any) -> None:
        if value != self._value:
            self._value = value
            self.value_changed.emit(value)

    def default(self) -> Any:
        return self._default

    def set_default(self, default: Any) -> None:
        self.set_value(default)
        self._default = self.value()

    def label(self) -> str:
        return self._label

    def set_label(self, label: str) -> None:
        self._label = label

    def name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name

    def tooltip(self) -> str:
        return self._tooltip

    def set_tooltip(self, tooltip: str) -> None:
        self._tooltip = tooltip

    def reset(self) -> None:
        self.set_value(self.default())


class IntParameter(ParameterWidget):
    value_changed = QtCore.Signal(int)

    _value: int = 0
    _default: int = 0
    _slider_min: int = 0
    _slider_max: int = 10
    _line_min: int | None = None
    _line_max: int | None = None
    _slider_visible: bool = True
    _commit_on_edit: bool = False
    _step_factor: int = 2

    def _init_ui(self) -> None:
        # Line
        self.line = IntLineEdit(self)
        self.line.set_value(self._value)
        self.line.value_changed.connect(self._line_value_changed)
        self._layout.addWidget(self.line)

        # Slider
        self.slider = IntSlider()
        self.slider.set_maximum(self._slider_max)
        self.slider.value_changed.connect(self._slider_value_changed)
        # Prevent any size changes when slider shows
        self.slider.setMaximumHeight(self.line.minimumSizeHint().height())
        self._layout.addWidget(self.slider)
        self._layout.setStretch(1, 1)

        self.setFocusProxy(self.line)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self._toggle_slider(True)

    def commit_on_edit(self) -> bool:
        return self._commit_on_edit

    def set_commit_on_edit(self, commit_on_edit: bool) -> None:
        self._commit_on_edit = commit_on_edit
        self.line.commit_on_edit = commit_on_edit

    def line_min(self) -> int | None:
        return self._line_min

    def set_line_min(self, line_min: int | None) -> None:
        self._line_min = line_min
        self.line.set_minimum(line_min)

    def line_max(self) -> int | None:
        return self._line_max

    def set_line_max(self, line_max: int | None) -> None:
        self._line_max = line_max
        self.line.set_maximum(line_max)

    def slider_min(self) -> int:
        return self._slider_min

    def set_slider_min(self, slider_min: int) -> None:
        self._slider_min = slider_min
        self.slider.set_minimum(slider_min)

    def slider_max(self) -> int:
        return self._slider_max

    def set_slider_max(self, slider_max: int) -> None:
        self._slider_max = slider_max
        self.slider.set_maximum(slider_max)

    def slider_visible(self) -> bool:
        return self._slider_visible

    def set_slider_visible(self, slider_visible: bool) -> None:
        self._slider_visible = slider_visible
        self._toggle_slider(slider_visible)

    def step_factor(self) -> int:
        return self._step_factor

    def set_step_factor(self, factor: int) -> None:
        self._step_factor = factor
        self.slider.set_step_factor(factor)

    def value(self) -> int:
        return super().value()

    def set_value(self, value: int) -> None:
        super().set_value(value)
        self._set_line_value(value)
        self._set_slider_value(value)

    def _line_value_changed(self, value: int) -> None:
        super().set_value(value)
        self._set_slider_value(value)

    def _slider_value_changed(self, value: int) -> None:
        super().set_value(value)
        self._set_line_value(value)

    def _set_line_value(self, value: int) -> None:
        self.line.blockSignals(True)
        self.line.set_value(value)
        self.line.blockSignals(False)

    def _set_slider_value(self, value: int) -> None:
        self.slider.blockSignals(True)
        self.slider.set_value(value)
        self.slider.blockSignals(False)

    def _toggle_slider(self, value: bool) -> None:
        has_space = self.size().width() > MIN_SLIDER_WIDTH
        self.slider.setVisible(self._slider_visible and value and has_space)


class FloatParameter(IntParameter):
    value_changed = QtCore.Signal(float)

    _value: float = 0
    _default: float = 0
    _slider_min: float = 0
    _slider_max: float = 1
    _line_min: float | None = None
    _line_max: float | None = None
    _decimals: int = 4

    def _init_ui(self) -> None:
        # line
        self.line = FloatLineEdit(self)
        self.line.value_changed.connect(self._line_value_changed)
        self.line.set_value(self._value)
        self.line.set_decimals(self._decimals)
        self._layout.addWidget(self.line)

        # slider
        self.slider = FloatSlider()
        self.slider.set_maximum(self._slider_max)
        self.slider.value_changed.connect(self._slider_value_changed)
        # prevent any size changes when slider shows
        self.slider.setMaximumHeight(self.line.minimumSizeHint().height())
        self._layout.addWidget(self.slider)
        self._layout.setStretch(1, 1)

        self.setFocusProxy(self.line)

    def decimals(self) -> int:
        return self._decimals

    def set_decimals(self, decimals: int) -> None:
        self._decimals = decimals
        self.line.set_decimals(decimals)

    def line_min(self) -> float:
        return super().line_min()

    def set_line_min(self, line_min: float | None) -> None:
        super().set_line_min(line_min)

    def line_max(self) -> float:
        return super().line_max()

    def set_line_max(self, line_max: float | None) -> None:
        super().set_line_max(line_max)

    def slider_min(self) -> float:
        return super().slider_min()

    def set_slider_min(self, slider_min: float) -> None:
        super().set_slider_min(slider_min)  # noqa

    def slider_max(self) -> float:
        return super().slider_max()

    def set_slider_max(self, slider_max: float) -> None:
        super().set_slider_max(slider_max)  # noqa

    def value(self) -> float:
        return super().value()

    def set_value(self, value: float) -> None:
        super().set_value(value)  # noqa


class StringParameter(ParameterWidget):
    class MenuMode(Enum):
        REPLACE = auto()
        TOGGLE = auto()

    value_changed = QtCore.Signal(str)

    _value: str = ''
    _default: str = ''
    _placeholder: str = ''
    _area: bool = False
    _menu: QtWidgets.QMenu | None = None
    _menu_data: Collection | None = None
    _menu_mode: MenuMode = MenuMode.REPLACE

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

    def area(self) -> bool:
        return self._area

    def set_area(self, area: bool) -> None:
        if area != self._area:
            self._area = area
            self._layout.removeWidget(self.text)
            self.text.deleteLater()
            self._init_text()

    def menu(self) -> QtWidgets.QMenu:
        if self._menu is None:
            self._menu = self._build_menu(self._menu_data)
        return self._menu

    def set_menu(self, menu: Collection | None) -> None:
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

    def menu_mode(self) -> MenuMode:
        return self._menu_mode

    def set_menu_mode(self, mode: MenuMode) -> None:
        self._menu_mode = mode

    def placeholder(self) -> str:
        return self._placeholder

    def set_placeholder(self, placeholder: str) -> None:
        self._placeholder = placeholder
        self.text.setPlaceholderText(placeholder)

    def value(self) -> str:
        return super().value()

    def set_value(self, value: str) -> None:
        super().set_value(value)
        self.text.blockSignals(True)
        if isinstance(self.text, QtWidgets.QPlainTextEdit):
            self.text.setPlainText(value)
            self._refresh_height()
        elif isinstance(self.text, QtWidgets.QLineEdit):
            self.text.setText(value)
        self.text.blockSignals(False)

    def _action_triggered(self, action: QtGui.QAction) -> None:
        data = action.data()
        value = str(data)
        if self._menu_mode == StringParameter.MenuMode.REPLACE:
            self.set_value(value)
        elif self._menu_mode == StringParameter.MenuMode.TOGGLE:
            values = self._value.split(' ')
            if value in values:
                values = (v for v in values if v != value)
            else:
                values.append(value)
            self.set_value(' '.join(values))

    def _build_menu(
        self, content: Collection, menu: QtWidgets.QMenu | None = None
    ) -> QtWidgets.QMenu:
        """Recursively build the QMenu from content."""

        if menu is None:
            menu = QtWidgets.QMenu(self)
        if isinstance(content, Sequence):
            content = {i: i for i in content}
        for label, data in content.items():
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
        if isinstance(self.text, QtWidgets.QPlainTextEdit):
            super().set_value(self.text.toPlainText())
        elif isinstance(self.text, QtWidgets.QLineEdit):
            super().set_value(self.text.text())

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


class PathParameter(ParameterWidget):
    class Method(Enum):
        OPEN_FILE = auto()
        SAVE_FILE = auto()
        EXISTING_DIR = auto()

    OPEN_FILE = Method.OPEN_FILE
    SAVE_FILE = Method.SAVE_FILE
    EXISTING_DIR = Method.EXISTING_DIR

    value_changed = QtCore.Signal(str)

    _value: str = ''
    _default: str = ''
    _dir_fallback: str = ''
    _method: Method = Method.OPEN_FILE

    def _init_ui(self) -> None:
        self.line = QtWidgets.QLineEdit()
        self.line.editingFinished.connect(self._editing_finished)
        self._layout.addWidget(self.line)

        self.button = QtWidgets.QToolButton()
        self.button.setIcon(MaterialIcon('file_open'))
        self.button.clicked.connect(self.browse)
        self._layout.addWidget(self.button)

        self._layout.setStretch(0, 1)
        self.setFocusProxy(self.line)

    def browse(self) -> None:
        start_dir = self._value or self._dir_fallback
        if self._method == PathParameter.Method.OPEN_FILE:
            path, filters = QtWidgets.QFileDialog.getOpenFileName(
                parent=self, caption='Open File', dir=start_dir
            )
        elif self._method == PathParameter.Method.SAVE_FILE:
            path, filters = QtWidgets.QFileDialog.getSaveFileName(
                parent=self, caption='Save File', dir=start_dir, filter='*.*'
            )
        elif self._method == PathParameter.Method.EXISTING_DIR:
            path = QtWidgets.QFileDialog.getExistingDirectory(
                parent=self, caption='Select Directory', dir=start_dir
            )
        else:
            return

        if path:
            self.set_value(path)

    def dir_fallback(self) -> str:
        return self._dir_fallback

    def set_dir_fallback(self, dir_fallback: str) -> None:
        self._dir_fallback = dir_fallback

    def method(self) -> Method:
        return self._method

    def set_method(self, method: Method) -> None:
        self._method = method

    def value(self) -> str:
        return super().value()

    def set_value(self, value: str) -> None:
        super().set_value(value)
        self.line.blockSignals(True)
        self.line.setText(value)
        self.line.blockSignals(False)

    def _editing_finished(self) -> None:
        value = self.line.text()
        super().set_value(value)


class ComboParameter(ParameterWidget):
    _value: Any = None
    _default: Any = None
    _items: tuple = ()

    def _init_ui(self) -> None:
        self.combo = QtWidgets.QComboBox()
        self.combo.currentIndexChanged.connect(self._current_index_changed)
        self.combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )

        self._layout.addWidget(self.combo)
        self.setFocusProxy(self.combo)

    def items(self) -> tuple:
        return self._items

    def set_items(self, items: Collection) -> None:
        if isinstance(items, Mapping):
            items = tuple(items.items())
        else:
            items = tuple(i if isinstance(i, tuple) else (i, i) for i in items)

        self._items = items
        self._refresh_items()
        try:
            default = items[0][1]
        except (IndexError, TypeError):
            default = None
        self.set_default(default)
        self.set_value(default)

    def value(self) -> Any:
        return super().value()

    def set_value(self, value: Any) -> None:
        index = self._index_from_value(value)
        value = self.combo.itemData(index)
        super().set_value(value)
        self.combo.blockSignals(True)
        self.combo.setCurrentIndex(index)
        self.combo.blockSignals(False)

    def _current_index_changed(self, index: int) -> None:
        value = self.combo.itemData(index)
        super().set_value(value)

    def _index_from_value(self, value: Any) -> int:
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


class EnumParameter(ParameterWidget):
    _value: Enum | None = None
    _default: Enum | None = None
    _formatter: Callable | None = None
    _enum: EnumMeta | None = None

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

    def enum(self) -> EnumMeta:
        return self._enum

    def set_enum(self, enum: EnumMeta) -> None:
        self._enum = enum
        self._update_items()
        if self._enum:
            default = tuple(self._enum)[0]
        else:
            default = None
        self.set_default(default)
        self.set_value(default)

    def formatter(self) -> Callable:
        return self._formatter

    def set_formatter(self, formatter: Callable) -> None:
        self._formatter = formatter
        index = self.combo.currentIndex()
        self._update_items()
        self.combo.setCurrentIndex(index)

    def value(self) -> Enum | None:
        return super().value()

    def set_value(self, value: Any) -> None:
        value = self._enum_from_value(value)
        super().set_value(value)

        self.combo.blockSignals(True)
        if value is None:
            index = -1
        else:
            index = self.combo.findData(value.value)
        self.combo.setCurrentIndex(index)
        self.combo.blockSignals(False)

    def _current_index_changed(self, index: int) -> None:
        value = self.combo.itemData(index)
        value = self._enum_from_value(value)
        super().set_value(value)

    def _enum_from_value(self, value: Any) -> Enum | None:
        try:
            # value is Enum
            if isinstance(value, self._enum):
                return value
        except TypeError:
            pass

        try:
            # value is Enum.name
            return self._enum[value]
        except KeyError:
            pass
        except TypeError:
            return None

        try:
            # value is Enum.value
            return self._enum(value)
        except (ValueError, TypeError):
            return None

    def _update_items(self) -> None:
        self.combo.blockSignals(True)
        for index in reversed(range(self.combo.count())):
            self.combo.removeItem(index)

        if isinstance(self._enum, EnumMeta):
            for member in self._enum:
                label = self._formatter(member)
                self.combo.addItem(label, member.value)
        self.combo.blockSignals(False)


class BoolParameter(ParameterWidget):
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


class MultiIntParameter(IntParameter):
    value_changed = QtCore.Signal(tuple)

    _count: int = 2
    _value: tuple[int, ...] = (0, 0)
    _default: tuple[int, ...] = (0, 0)
    _keep_ratio: bool = True
    _ratio_visible: bool = True

    def _init_ui(self) -> None:
        # Lines
        self.lines = []
        for i in range(self._count):
            line = IntLineEdit()
            line.set_value(0)
            line.value_changed.connect(self._line_value_changed)
            self._layout.addWidget(line)
            self.lines.append(line)

        # Slider
        self.slider = IntSlider()
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

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        QtWidgets.QWidget.resizeEvent(self, event)
        if self._keep_ratio:
            self._toggle_slider(True)

    def set_commit_on_edit(self, commit_on_edit: bool) -> None:
        self._commit_on_edit = commit_on_edit
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

    def set_line_min(self, line_min: int) -> None:
        self._line_min = line_min
        for line in self.lines:
            line.set_minimum(line_min)

    def set_line_max(self, line_max: int) -> None:
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

    def value(self) -> tuple[int, ...]:
        return ParameterWidget.value(self)

    def set_value(self, value: Sequence) -> None:
        if isinstance(value, Sequence):
            values = value
        else:
            values = self._cast_to_tuple(value)
        if isinstance(self, ColorParameter):
            pass
        if not all(values[0] == x for x in values):
            self.set_keep_ratio(False)
        if self._keep_ratio:
            values = (values[0],) * self._count
        ParameterWidget.set_value(self, self._cast_to_type(values))
        self._set_slider_value(values[0])
        self._set_line_values(values)

    def _line_value_changed(self, value: int) -> None:
        if self._keep_ratio:
            values = (self.lines[0].value(),) * self._count
            for line in self.lines[1:]:
                line.set_value(values[0])
        else:
            values = tuple(line.value() for line in self.lines)

        value = self._cast_to_type(values)
        ParameterWidget.set_value(self, value)
        self._set_slider_value(values[0])

    def _slider_value_changed(self, value: int) -> None:
        values = (value,) * self._count
        value = self._cast_to_type(values)
        ParameterWidget.set_value(self, value)
        self._set_line_values(values)

    def _set_line_values(self, values: tuple[int, ...]) -> None:
        for line, value in zip(self.lines, values):
            line.blockSignals(True)
            line.set_value(value)
            line.blockSignals(False)

    def _cast_to_tuple(self, values: Any) -> tuple[int, ...]:
        return values

    def _cast_to_type(self, values: tuple[int, ...]) -> Any:
        return values


class MultiFloatParameter(MultiIntParameter):
    _value: tuple[float, ...] = (0, 0)
    _default: tuple[float, ...] = (0, 0)
    _line_min: float | None = None
    _line_max: float | None = None
    _slider_min: float = 0
    _slider_max: float = 1
    _decimals: int = 4

    def _init_ui(self) -> None:
        # Lines
        self.lines = []
        for i in range(self._count):
            line = FloatLineEdit()
            line.set_value(0)
            line.set_decimals(self._decimals)
            line.value_changed.connect(self._line_value_changed)
            self._layout.addWidget(line)
            self.lines.append(line)

        # Slider
        self.slider = FloatSlider()
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

    def decimals(self) -> int:
        return self._decimals

    def set_decimals(self, decimals: int) -> None:
        self._decimals = decimals
        for line in self.lines:
            line.set_decimals(decimals)

    def line_min(self) -> float:
        return super().line_min()

    def set_line_min(self, line_min: float) -> None:
        super().set_line_min(line_min)  # noqa

    def line_max(self) -> float:
        return super().line_max()

    def set_line_max(self, line_max: float) -> None:
        super().set_line_max(line_max)  # noqa

    def slider_min(self) -> float:
        return super().slider_min()

    def set_slider_min(self, slider_min: float) -> None:
        super().set_slider_min(slider_min)  # noqa

    def slider_max(self) -> float:
        return super().slider_max()

    def set_slider_max(self, slider_max: float) -> None:
        super().set_slider_max(slider_max)  # noqa

    def value(self) -> tuple[float, ...]:
        return super().value()

    def set_value(self, value: tuple[float, ...]) -> None:
        super().set_value(value)


class PointParameter(MultiIntParameter):
    value_changed = QtCore.Signal(QtCore.QPoint)

    _value: QtCore.QPoint = QtCore.QPoint(0, 0)
    _default: QtCore.QPoint = QtCore.QPoint(0, 0)
    _slider_visible: bool = False
    _ratio_visible: bool = False

    def _init_ui(self) -> None:
        super()._init_ui()
        self.set_slider_visible(self._slider_visible)
        self.set_ratio_visible(self._ratio_visible)

    def set_value(self, value: QtCore.QPoint | Sequence) -> None:
        super().set_value(value)

    def value(self) -> QtCore.QPoint:
        return super().value()  # noqa

    def _cast_to_type(self, values: tuple[int, ...]) -> QtCore.QPoint:
        return QtCore.QPoint(*values[:2])

    def _cast_to_tuple(self, value: QtCore.QPoint) -> tuple[int, ...]:
        return value.x(), value.y()


class PointFParameter(MultiFloatParameter):
    value_changed = QtCore.Signal(QtCore.QPointF)

    _value: QtCore.QPointF = QtCore.QPointF(0, 0)
    _default: QtCore.QPointF = QtCore.QPointF(0, 0)
    _slider_visible: bool = False
    _ratio_visible: bool = False

    def _init_ui(self) -> None:
        super()._init_ui()
        self.set_slider_visible(self._slider_visible)
        self.set_ratio_visible(self._ratio_visible)

    def set_value(self, value: QtCore.QPointF | Sequence) -> None:
        super().set_value(value)  # noqa

    def value(self) -> QtCore.QPointF:
        return super().value()  # noqa

    def _cast_to_type(self, values: tuple[float, ...]) -> QtCore.QPointF:
        return QtCore.QPointF(*values[:2])

    def _cast_to_tuple(self, value: QtCore.QPointF) -> tuple[float, ...]:
        return value.x(), value.y()


class SizeParameter(MultiIntParameter):
    value_changed = QtCore.Signal(QtCore.QSize)

    _value: QtCore.QSize = QtCore.QSize(0, 0)
    _default: QtCore.QSize = QtCore.QSize(0, 0)

    def set_value(self, value: QtCore.QSize | Sequence) -> None:
        super().set_value(value)

    def value(self) -> QtCore.QSize:
        return super().value()  # noqa

    def _cast_to_type(self, values: tuple[int, ...]) -> QtCore.QSize:
        return QtCore.QSize(*values[:2])

    def _cast_to_tuple(self, value: QtCore.QSize) -> tuple[int, ...]:
        return value.width(), value.height()


class SizeFParameter(MultiFloatParameter):
    value_changed = QtCore.Signal(QtCore.QSizeF)

    _value: QtCore.QSizeF = QtCore.QSizeF(0, 0)
    _default: QtCore.QSizeF = QtCore.QSizeF(0, 0)

    def set_value(self, value: QtCore.QSizeF | Sequence) -> None:
        super().set_value(value)  # noqa

    def value(self) -> QtCore.QSizeF:
        return super().value()  # noqa

    def _cast_to_type(self, values: tuple[float, ...]) -> QtCore.QSizeF:
        return QtCore.QSizeF(*values[:2])

    def _cast_to_tuple(self, value: QtCore.QSizeF) -> tuple[float, ...]:
        return value.width(), value.height()


class ColorParameter(MultiFloatParameter):
    value_changed = QtCore.Signal(QtGui.QColor)

    _count: int = 3
    _value: QtGui.QColor = QtGui.QColor(0, 0, 0)
    _default: QtGui.QColor = QtGui.QColor(0, 0, 0)
    _color_min: float | None = 0
    _color_max: float | None = 1
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

    def set_color_min(self, color_min: float) -> None:
        self._color_min = color_min
        for line in self.lines:
            line.set_minimum(self._color_min)  # noqa

    def color_max(self) -> float:
        return self._color_max

    def set_color_max(self, color_max: float) -> None:
        self._color_max = color_max
        for line in self.lines:
            line.set_maximum(self._color_max)  # noqa

    def select_color(self) -> None:
        options = QtWidgets.QColorDialog.ColorDialogOption.DontUseNativeDialog
        color = QtWidgets.QColorDialog.getColor(initial=self._value, options=options)
        if color.isValid():
            super().set_value(color)  # noqa
            values = self._cast_to_tuple(color)
            self._set_line_values(values)  # noqa
            self._set_button_value(color)

    def value(self) -> QtGui.QColor:
        return super().value()  # noqa

    def set_value(self, value: QtGui.QColor | Sequence) -> None:
        super().set_value(value)  # noqa
        self._set_button_value(self._value)

    def _cast_to_type(self, values: tuple[float, ...]) -> QtGui.QColor:
        return QtGui.QColor.fromRgbF(*values[:3])

    def _cast_to_tuple(self, value: QtGui.QColor) -> tuple[float, ...]:
        return value.getRgbF()[:3]

    def _line_value_changed(self, value: float) -> None:
        super()._line_value_changed(value)  # noqa
        self._set_button_value(self._value)

    def _set_button_value(self, value: QtGui.QColor) -> None:
        self.button.setPalette(QtGui.QPalette(value))

    def _slider_value_changed(self, value: int) -> None:
        super()._slider_value_changed(value)
        self._set_button_value(self._value)
