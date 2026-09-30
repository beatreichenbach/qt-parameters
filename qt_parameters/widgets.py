from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import Enum, auto
from functools import partial
from typing import Callable, Generic, TypeVar

from qtpy import QtCore, QtGui, QtWidgets

from . import utils
from .inputs import (
    FloatLineEdit,
    FloatSlider,
    IntLineEdit,
    IntSlider,
    NumberLineEdit,
    NumberSlider,
    RatioButton,
    TextEdit,
)
from .qt_material_icons import MaterialIcon
from .resizegrip import ResizeGrip

MIN_SLIDER_WIDTH = 200

T = TypeVar('T')
E = TypeVar('E', int, float)
V = TypeVar('V')
EnumT = TypeVar('EnumT', bound=Enum)


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


class PathParameter(ParameterWidget[str]):
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

    def dir_fallback(self) -> str:
        return self._dir_fallback

    def method(self) -> Method:
        return self._method

    def set_dir_fallback(self, dir_fallback: str) -> None:
        self._dir_fallback = dir_fallback

    def set_method(self, method: Method) -> None:
        self._method = method

    def browse(self) -> None:
        start_dir = self._value or self._dir_fallback
        if self._method == PathParameter.Method.OPEN_FILE:
            path, _filters = QtWidgets.QFileDialog.getOpenFileName(
                parent=self, caption='Open File', dir=start_dir
            )
        elif self._method == PathParameter.Method.SAVE_FILE:
            path, _filters = QtWidgets.QFileDialog.getSaveFileName(
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
