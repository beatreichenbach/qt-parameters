from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from qtpy import QtCore, QtGui, QtWidgets

from . import utils
from .box import CollapsibleBox
from .scrollarea import VerticalScrollArea
from .widgets import ParameterWidget, BoolParameter


class Separator(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(QtCore.QMargins(0, 9, 0, 9))
        self.setLayout(layout)

        frame = QtWidgets.QFrame(self)
        frame.setFixedHeight(1)
        frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        layout.addWidget(frame)


class ParameterToolTip(QtWidgets.QFrame):
    def __init__(
        self, widget: ParameterWidget, parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(
            QtGui.QPalette.ColorRole.Window,
            palette.color(QtGui.QPalette.ColorRole.Base),
        )
        self.setPalette(palette)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)

        title = QtWidgets.QLabel(widget.label(), self)
        font = title.font()
        font.setBold(True)
        title.setFont(font)
        self.layout().addWidget(title)

        separator = QtWidgets.QFrame(self)
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.layout().addWidget(separator)

        typ = type(widget).__name__.replace('Parameter', '')
        detail = QtWidgets.QLabel(f'Parameter: {widget.name()} ({typ})', self)
        self.layout().addWidget(detail)

        tooltip = QtWidgets.QLabel(widget.tooltip(), self)
        # tooltip.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        tooltip.setWordWrap(True)
        tooltip.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.layout().addWidget(tooltip)

    def focusOutEvent(self, event: QtCore.QEvent) -> None:
        self.hide()

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        self.hide()


class ParameterLabel(QtWidgets.QLabel):
    def __init__(
        self, widget: ParameterWidget, parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(widget.label(), parent)

        self._tooltip: ParameterToolTip | None = None
        self._widget = widget

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self.text())})'

    def enterEvent(self, event: QtGui.QEnterEvent) -> None:
        if self._widget.tooltip():
            QtCore.QTimer.singleShot(600, self.show_tooltip)
        super().enterEvent(event)

    def show_tooltip(self) -> None:
        global_position = QtGui.QCursor.pos()
        if self.geometry().contains(self.parent().mapFromGlobal(global_position)):
            if self._tooltip is None:
                self._tooltip = ParameterToolTip(self._widget)
                self._tooltip.setParent(self.window(), QtCore.Qt.WindowType.ToolTip)
            self._tooltip.move(global_position)
            self._tooltip.show()


class LabelFilter(QtCore.QObject):
    def __init__(
        self, label: QtWidgets.QLabel, parent: QtWidgets.QWidget | None = None
    ) -> None:
        if not parent:
            # Store the LabelFilter on the label, as it should be deleted with the
            # label and not the watched widget.
            parent = label
        super().__init__(parent)
        self.label = label

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if isinstance(watched, QtWidgets.QWidget):
            if event.type() == QtCore.QEvent.Type.EnabledChange:
                self.label.setEnabled(watched.isEnabled())
            elif event.type() in (QtCore.QEvent.Type.Show, QtCore.QEvent.Type.Hide):
                self.label.setVisible(watched.isVisible())
        return False


class ParameterForm(QtWidgets.QWidget):
    parameter_changed: QtCore.Signal = QtCore.Signal(ParameterWidget)

    def __init__(self, name: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._widgets: dict[str, QtWidgets.QWidget] = {}
        self._name = name
        self._root = self
        self._flat = False
        self._unique_names = False

        self._layout = QtWidgets.QGridLayout()
        self.setLayout(self._layout)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._name!r})'

    def name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name

    def flat(self) -> bool:
        return self._flat

    def set_flat(self, flat: bool) -> None:
        """
        If True, the form doesn't create a hierarchy when querying parameters or values.
        """
        self._flat = flat

    def unique_names(self) -> bool:
        return self._unique_names

    def set_unique_names(self, unique_names: bool) -> None:
        """
        If True, requires that all parameters have a unique name in the root's
        hierarchy.
        """
        self._unique_names = unique_names

    def root(self) -> ParameterForm:
        return self._root

    def set_root(self, root: ParameterForm) -> None:
        """
        Set the root which is used when checking for unique names in the hierarchy.
        """
        self._root = root

    def state(self) -> dict:
        """Return the state of the form as a dict."""

        state = {}
        if boxes := self._collapsed_boxes():
            state['collapsed_boxes'] = boxes
        for form in self.forms():
            if form_state := form.state():
                state[form.name()] = form_state
        return state

    def set_state(self, state: dict) -> None:
        """Load the state of the form from a dict."""

        boxes = state.get('collapsed_boxes')
        if boxes is not None:
            self._set_collapsed_boxes(boxes)
        for form in self.forms():
            if form_state := state.get(form.name()):
                form.set_state(form_state)

    def values(self) -> dict[str, Any]:
        """Return a dict of all values."""

        widgets = self.widgets()
        values = {}
        for name, widget in widgets.items():
            if isinstance(widget, ParameterWidget):
                values[name] = widget.value()
            elif isinstance(widget, ParameterForm):
                values[name] = widget.values()
            elif isinstance(widget, CollapsibleBox):
                values[name] = widget.checked()
        return values

    def set_values(self, values: dict) -> None:
        """Set the values of ParameterWidgets in the form."""

        widgets = self.widgets()
        for name, value in values.items():
            widget = widgets.get(name)
            if isinstance(widget, ParameterWidget):
                widget.set_value(value)
            elif isinstance(widget, ParameterForm):
                widget.set_values(value)
            elif isinstance(widget, CollapsibleBox):
                widget.set_checked(value)

    def set_defaults(self, values: dict) -> None:
        """Set the default values of ParameterWidgets in the form."""

        widgets = self.widgets()
        for name, value in values.items():
            widget = widgets.get(name)
            if isinstance(widget, ParameterWidget):
                widget.set_default(value)
            elif isinstance(widget, ParameterForm):
                widget.set_defaults(value)

    def reset(self) -> None:
        """Reset all parameters in this form to their default values."""

        widgets = self.widgets()
        for name, widget in widgets.items():
            if isinstance(widget, (ParameterWidget, ParameterForm)):
                widget.reset()
            elif isinstance(widget, CollapsibleBox):
                widget.set_checked(True)

    def add_parameter(
        self,
        widget: ParameterWidget,
        checkable: bool = False,
        alignment: QtCore.Qt.AlignmentFlag | None = None,
    ) -> ParameterWidget:
        """Add a parameter to the ParameterForm's GridLayout."""

        name = widget.name()
        self._validate_name(name)
        self._widgets[name] = widget

        row = self._layout.rowCount() - 1

        # Checkbox
        if checkable:
            checkbox_name = f'{name}_enabled'
            checkbox = BoolParameter(checkbox_name)
            self._layout.addWidget(checkbox, row, 0)
            checkbox.set_value(False)
            widget.blockSignals(True)
            widget.setEnabled(False)
            widget.blockSignals(False)
            checkbox.value_changed.connect(widget.setEnabled)
            checkbox.value_changed.connect(
                lambda: self.parameter_changed.emit(checkbox)
            )

            self._widgets[checkbox_name] = checkbox

        # Label
        if widget.label():
            label = ParameterLabel(widget, self)
            label.setEnabled(widget.isEnabled())
            self._layout.addWidget(label, row, 1)
            if alignment:
                label.setAlignment(alignment)
            label.setVisible(False)
            label_filter = LabelFilter(label)
            widget.installEventFilter(label_filter)

        # Widget
        self._layout.addWidget(widget, row, 2)
        widget.value_changed.connect(lambda: self.parameter_changed.emit(widget))

        self._refresh_stretch()
        return widget

    def add_form(self, form: ParameterForm, checkable: bool = False) -> CollapsibleBox:
        """Add a form and return the CollapsibleBox."""

        # Add ParameterForm
        name = form.name()
        self._validate_name(name)
        self._widgets[name] = form
        form.set_root(self)
        form.parameter_changed.connect(self.parameter_changed)

        # Add CollapsibleBox
        label = utils.title(name)
        box = CollapsibleBox(label)
        box.set_collapsible(True)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(QtCore.QMargins())
        layout.setSpacing(0)
        layout.addWidget(form)
        box.setLayout(layout)

        if checkable:
            box.set_checkable(checkable)
            self._widgets[f'{name}_enabled'] = box

        self.add_widget(box)

        return box

    def add_forms(self, forms: Sequence[ParameterForm]) -> QtWidgets.QTabWidget:
        """Add multiple forms and return the TabWidget."""

        # Validate the names before creating any widgets.
        for form in forms:
            self._validate_name(form.name())

        tab_widget = QtWidgets.QTabWidget()
        for form in forms:
            name = form.name()
            self._widgets[name] = form
            form.set_root(self)
            form.parameter_changed.connect(self.parameter_changed)

            label = utils.title(name)
            tab_widget.addTab(form, label)

        self.add_widget(tab_widget)

        return tab_widget

    def add_widget(
        self,
        widget: QtWidgets.QWidget,
        column: int = 1,
        column_span: int = -1,
        row: int = -1,
        row_span: int = 1,
    ) -> QtWidgets.QWidget:
        """Add a widget to the ParameterForm's GridLayout."""

        if row < 0:
            row = self._layout.rowCount() + row
        if column_span == -1 and self._layout.columnCount() < 2:
            # In case the layout doesn't have any columns yet, default to 3 columns.
            column_span = 2
        self._layout.addWidget(widget, row, column, row_span, column_span)
        self._refresh_stretch()
        return widget

    def add_separator(
        self,
        name: str = '',
        column: int = 2,
        column_span: int = -1,
        row: int = -1,
        row_span: int = 1,
    ) -> Separator:
        """Add a horizontal separator to the ParameterForm's GridLayout."""

        if row < 0:
            row = self._layout.rowCount() + row
        if name:
            label = QtWidgets.QLabel(name)
            self._layout.addWidget(label, row, 1)
            column = min(2, column)
        separator = Separator()
        self.add_widget(separator, column, column_span, row, row_span)
        return separator

    def add_layout(
        self,
        layout: QtWidgets.QLayout,
        column: int = 1,
        column_span: int = -1,
        row: int = -1,
        row_span: int = 1,
    ) -> QtWidgets.QLayout:
        """Add a layout to the ParameterForm's GridLayout."""

        if row < 0:
            row = self._layout.rowCount() + row
        if column_span == -1 and self._layout.columnCount() < 2:
            # In case the layout doesn't have any columns yet, default to 3 columns.
            column_span = 2
        self._layout.addLayout(layout, row, column, row_span, column_span)
        self._refresh_stretch()
        return layout

    def clear(self) -> None:
        """Clear the form from all parameters, widgets and forms."""

        for i in reversed(range(self._layout.count())):
            if item := self._layout.itemAt(i):
                if widget := item.widget():
                    self._layout.removeWidget(widget)
                    widget.deleteLater()
                else:
                    self._layout.removeItem(item)
        self._widgets = {}

    def remove_parameter(self, parameter: ParameterWidget) -> None:
        """Remove and delete a parameter from the form."""

        index = self._layout.indexOf(parameter)
        if index < 0:
            return
        row, column, row_span, col_span = self._layout.getItemPosition(index)
        for i in range(3):
            if item := self._layout.itemAtPosition(row, i):
                if widget := item.widget():
                    self._layout.removeWidget(widget)
                    widget.deleteLater()
        self._refresh_stretch()

    def remove_form(self, form: ParameterForm) -> None:
        """Remove a form from the form. This does not remove box or tab widgets."""
        name = form.name()
        if name in self._widgets:
            del self._widgets[name]
        box_name = f'{name}_enabled'
        if box_name in self._widgets:
            del self._widgets[box_name]

    def remove_widget(self, widget: QtWidgets.QWidget) -> None:
        """Remove and delete a widget from the form."""

        self._layout.removeWidget(widget)
        widget.deleteLater()
        self._refresh_stretch()

    def parameter(self, name: str) -> ParameterWidget | None:
        """
        Return the first ParameterWidget with name `name`.

        The `name` follows the attribute naming scheme, meaning nested parameters can
        be accessed with: name = 'parent.child'.
        """

        names = name.split('.')

        widgets = self.widgets()
        for n in names:
            widget = widgets.get(n)
            if isinstance(widget, ParameterForm):
                widgets = widget.widgets()
            elif isinstance(widget, ParameterWidget):
                return widget
            else:
                break
        return None

    def parameters(self) -> tuple[ParameterWidget, ...]:
        """Return all ParameterWidgets of this form."""

        widgets = self.widgets().values()
        parameters = tuple(w for w in widgets if isinstance(w, ParameterWidget))
        return parameters

    def form(self, name: str) -> ParameterForm | None:
        """
        Return the first ParameterForm with name `name`.

        The `name` follows the attribute naming scheme, meaning nested forms can
        be accessed with: name = 'parent.child'.
        """

        names = name.split('.')

        widgets = self.widgets()
        for n in names:
            widget = widgets.get(n)
            if isinstance(widget, ParameterForm):
                if n == names[-1]:
                    return widget
                else:
                    widgets = widget.widgets()
            else:
                break
        return None

    def forms(self) -> tuple[ParameterForm, ...]:
        """Return all ParameterForms of this form."""

        widgets = self.widgets().values()
        forms = tuple(w for w in widgets if isinstance(w, ParameterForm))
        return forms

    def boxes(self) -> tuple[CollapsibleBox, ...]:
        """Return all CollapsibleBoxes of this form."""

        boxes = []
        for i in reversed(range(self._layout.count())):
            if item := self._layout.itemAt(i):
                if widget := item.widget():
                    if isinstance(widget, CollapsibleBox):
                        boxes.append(widget)
        return tuple(boxes)

    def widgets(self) -> dict:
        """
        Return a dict with all parameter widgets of the form and its children.
        The dict will be flattened if the child forms are flat.
        """

        widgets = {}
        for name, widget in self._widgets.items():
            if isinstance(widget, ParameterForm):
                if widget.flat():
                    widgets.update(widget.widgets())
                else:
                    widgets[name] = widget
            elif isinstance(widget, ParameterWidget):
                widgets[name] = widget
            elif isinstance(widget, CollapsibleBox):
                widgets[name] = widget
        return widgets

    @staticmethod
    def checkbox(parameter: ParameterWidget) -> BoolParameter | None:
        """Return the BoolParameter for a ParameterWidget `parameter` if it exists."""

        if parent := parameter.parentWidget():
            layout = parent.layout()
            if layout and isinstance(layout, QtWidgets.QGridLayout):
                index = layout.indexOf(parameter)
                if index >= 0:
                    row, column, row_span, col_span = layout.getItemPosition(index)
                    if item := layout.itemAtPosition(row, 0):
                        if widget := item.widget():
                            if isinstance(widget, BoolParameter):
                                return widget
        return None

    @staticmethod
    def label(parameter: ParameterWidget) -> ParameterLabel | None:
        """Return the ParameterLabel for a ParameterWidget `parameter` if it exists."""

        if parent := parameter.parentWidget():
            layout = parent.layout()
            if layout and isinstance(layout, QtWidgets.QGridLayout):
                index = layout.indexOf(parameter)
                if index >= 0:
                    row, column, row_span, col_span = layout.getItemPosition(index)
                    if item := layout.itemAtPosition(row, 1):
                        if widget := item.widget():
                            if isinstance(widget, ParameterLabel):
                                return widget
        return None

    def _collapsed_boxes(self) -> tuple[str, ...]:
        """Return a tuple of all collapsed boxes."""

        boxes = []
        for box in self.boxes():
            if box.collapsed():
                boxes.append(box.title())
        return tuple(boxes)

    def _set_collapsed_boxes(self, boxes: Sequence[str]) -> None:
        """Collapse the boxes with title in `boxes`."""

        for box in self.boxes():
            if box.collapsible():
                box.set_collapsed(box.title() in boxes)

    def _refresh_stretch(self) -> None:
        """Ensure the last column and row is expanding."""

        self._layout.setColumnStretch(self._layout.columnCount() - 1, 1)
        self._layout.setRowStretch(self._layout.rowCount() - 1, 0)
        self._layout.setRowStretch(self._layout.rowCount(), 1)

    def _names(self) -> tuple[str, ...]:
        """Return a flat tuple of all child parameter's names."""

        names = []
        for name, widget in self._widgets.items():
            if isinstance(widget, ParameterForm):
                names.extend(widget._names())
            else:
                names.append(name)
        return tuple(names)

    def _validate_name(self, name: str) -> None:
        """
        Validates a parameter name, ensuring it does not already exist.

        :raises ValueError: If the name is not valid.
        """
        if not name:
            raise ValueError(f'name cannot be empty')

        if self._root._unique_names:
            names = self._root._names()
        else:
            names = self._widgets.keys()

        if name in names:
            raise ValueError(f'name {name!r} is not unique')


class ParameterEditor(ParameterForm):
    """ParameterEditor is a ParameterForm in a VerticalScrollArea."""

    def __init__(self, name: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(name=name, parent=parent)

        # Move the GridLayout to another widget first
        widget = QtWidgets.QWidget()
        widget.setLayout(self._layout)

        # Create the ScrollArea and add the widget
        self.scroll_area = VerticalScrollArea()
        self.scroll_area.setWidget(widget)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(QtCore.QMargins())
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def sizeHint(self) -> QtCore.QSize:
        return self.scroll_area.sizeHint()
