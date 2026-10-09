from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import partial
from typing import Generic, TypeVar

from qtpy import QtCore, QtGui, QtWidgets

from ..qt_material_icons import MaterialIcon
from .base import ParameterWidget
from .multi_combos import MultiComboBox, items_dict

T = TypeVar('T')


class TokenWidget(QtWidgets.QWidget):
    """A button-like token that is removed by clicking its close icon."""

    removed = QtCore.Signal()

    def __init__(self, text: str, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._init_ui(text)

    def _init_ui(self, text: str) -> None:
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 2, 2, 2)
        layout.setSpacing(8)

        self.label = QtWidgets.QLabel(text, self)
        layout.addWidget(self.label)

        self.close_button = QtWidgets.QToolButton(self)
        self.close_button.setIcon(MaterialIcon('close'))
        self.close_button.setAutoRaise(True)
        self.close_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.close_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.close_button.clicked.connect(self._on_close_clicked)
        layout.addWidget(self.close_button)

    def text(self) -> str:
        return self.label.text()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """Draw the token as a raised push button."""

        option = QtWidgets.QStyleOptionButton()
        option.initFrom(self)
        option.state |= QtWidgets.QStyle.StateFlag.State_Raised
        painter = QtWidgets.QStylePainter(self)
        self.style().drawControl(
            QtWidgets.QStyle.ControlElement.CE_PushButton, option, painter, self
        )

    def _on_close_clicked(self) -> None:
        self.removed.emit()


class TokenComboBox(MultiComboBox[T], Generic[T]):
    """An editable combo box whose items are toggled by typing their labels."""

    remove_triggered = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setEditable(True)
        self.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.setCurrentIndex(-1)

        completer = QtWidgets.QCompleter(self.model(), self)
        completer.setWidget(self)
        completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        completer.setCompletionRole(QtCore.Qt.ItemDataRole.DisplayRole)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        completer.activated.connect(self._completion_activated)
        self.setCompleter(completer)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """
        Toggle the highlighted item or remove the last token.

        Tab, Enter, and Space toggle the highlighted item. Backspace and Delete
        remove the last token when the edit field is empty.
        """

        key = event.key()

        # Accept the completion and check its checkbox.
        if key in (
            QtCore.Qt.Key.Key_Tab,
            QtCore.Qt.Key.Key_Enter,
            QtCore.Qt.Key.Key_Return,
            QtCore.Qt.Key.Key_Space,
        ):
            text = self.currentText()
            if text:
                self._toggle_text(text)
                return None
            return super().keyPressEvent(event)

        # Remove the last token.
        if key in (QtCore.Qt.Key.Key_Backspace, QtCore.Qt.Key.Key_Delete):
            if not self.currentText():
                self.remove_triggered.emit()
                if line_edit := self.lineEdit():
                    line_edit.clear()
                self.setCurrentIndex(-1)
                return None

        return super().keyPressEvent(event)

    def set_checked_values(self, values: Sequence[T]) -> None:
        """Check the items whose data is in `values` and uncheck the rest."""

        model = self.model()
        if isinstance(model, QtGui.QStandardItemModel):
            for row in range(model.rowCount()):
                item = model.item(row, 0)
                if item is None:
                    continue
                if item.data() in values:
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
                else:
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self._index_changed()

    def set_items(
        self,
        items: Mapping[str, T] | None = None,
        exclusive_items: Mapping[str, T] | None = None,
    ) -> None:
        """Set the items and clear the current index."""

        super().set_items(items, exclusive_items)
        self.setCurrentIndex(-1)

    def _display_text(self) -> str:
        """Return an empty string so the combo box never displays an item."""

        return ''

    def _index_changed(self) -> None:
        self.update()
        self.checked_changed.emit()

    def _toggle_selected(self) -> None:
        """Toggle the selected item and close the drop-down popup."""

        super()._toggle_selected()
        self.hidePopup()

    def _hide_completer_popup(self) -> None:
        """Hide the completer popup, which is separate from the combo box popup."""

        completer = self.completer()
        if completer is not None and (popup := completer.popup()) is not None:
            popup.hide()

    def _completion_activated(self, index: QtCore.QModelIndex) -> None:
        """Toggle the item selected from the completer popup."""

        text = index.data()
        if isinstance(text, str):
            self._toggle_text(text)

    def _toggle_text(self, text: str) -> None:
        """Toggle the item with the `text`."""

        index = self.findText(text)
        if index < 0:
            return

        model = self.model()
        if isinstance(model, QtGui.QStandardItemModel):
            item = model.item(index, 0)
            if item is not None:
                if item.checkState() == QtCore.Qt.CheckState.Checked:
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                else:
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
                self._index_changed()

        if line_edit := self.lineEdit():
            line_edit.clear()
        self.setCurrentIndex(-1)
        self._hide_completer_popup()


class TokenParameter(ParameterWidget[tuple[T, ...]], Generic[T]):
    value_changed = QtCore.Signal(tuple)

    _value: tuple[T, ...] = ()
    _default: tuple[T, ...] = ()

    def _init_ui(self) -> None:
        self._tokens: list[tuple[TokenWidget, T]] = []
        self.combo: TokenComboBox[T] = TokenComboBox()
        self.combo.checked_changed.connect(self._checked_changed)
        self.combo.remove_triggered.connect(self.remove_last_token)
        self.combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )

        self._layout.addWidget(self.combo)
        self.setFocusProxy(self.combo)

    def sizeHint(self) -> QtCore.QSize:
        size_hint = super().sizeHint()
        size_hint = size_hint.expandedTo(QtCore.QSize(256, 0))
        return size_hint

    def items(self) -> tuple[tuple[str, T], ...]:
        return self.combo.items()

    def set_items(self, items: Mapping[str, T] | Sequence[tuple[str, T] | T]) -> None:
        """
        Set the items of the parameter.

        `items` is either in the format of data, or (label, data).

        :raises ValueError: if there are duplicate labels.
        """

        self.combo.set_items(items_dict(items))

    def placeholder(self) -> str:
        return self.combo.placeholderText()

    def set_placeholder(self, placeholder: str) -> None:
        self.combo.setPlaceholderText(placeholder)

    def value(self) -> tuple[T, ...]:
        return super().value()

    def set_value(self, value: Sequence[T]) -> None:
        """Clear the tokens and rebuild them from `value`."""

        self._clear_tokens()
        self.combo.blockSignals(True)
        self.combo.set_checked_values(value)
        self.combo.blockSignals(False)
        for item in value:
            self._add_token(item)

        self._refresh_stretch()
        super().set_value(self._values())

    def remove_token(self, value: T) -> None:
        """Remove the tokens with the given value."""

        for token, item in list(self._tokens):
            if item == value:
                self._remove_token(token)
        self.combo.blockSignals(True)
        self.combo.set_checked_values(self._values())
        self.combo.blockSignals(False)

        self._refresh_stretch()
        super().set_value(self._values())

    def remove_last_token(self) -> None:
        """Remove the most recently added token."""

        if self._tokens:
            self.remove_token(self._tokens[-1][1])

    def _checked_changed(self) -> None:
        """Sync the tokens with the combo box's checked items."""

        checked = self.combo.checked_values()

        # Remove tokens that are no longer checked.
        for token, value in self._tokens:
            if value not in checked:
                self._remove_token(token)

        # Append newly checked tokens, preserving the order they were checked.
        for value in checked:
            if value not in self._token_values():
                self._add_token(value)

        self._refresh_stretch()
        super().set_value(self._values())

    def _add_token(self, value: T) -> None:
        """Add a token for `value` just before the combo box."""

        token = TokenWidget(self._value_label(value), self)
        token.removed.connect(partial(self.remove_token, value))
        self._layout.insertWidget(self._layout.count() - 1, token)
        self._tokens.append((token, value))

    def _remove_token(self, token: TokenWidget) -> None:
        """Remove `token` from the layout and stop tracking it."""

        self._layout.removeWidget(token)
        token.deleteLater()
        self._tokens = [pair for pair in self._tokens if pair[0] is not token]

    def _clear_tokens(self) -> None:
        """Remove every token."""

        for token, _ in list(self._tokens):
            self._layout.removeWidget(token)
            token.deleteLater()
        self._tokens = []

    def _values(self) -> tuple[T, ...]:
        """Return the values of the current tokens."""

        return tuple(value for _, value in self._tokens)

    def _token_values(self) -> list[T]:
        """Return the values of the current tokens as a list."""

        return [value for _, value in self._tokens]

    def _value_label(self, value: T) -> str:
        """Return the label for `value`, or its string form if it is unknown."""

        for label, data in self.combo.items():
            if data == value:
                return label
        return str(value)

    def _refresh_stretch(self) -> None:
        """Give the last layout item the stretch to keep tokens left-aligned."""

        count = self._layout.count()
        for i in range(count):
            self._layout.setStretch(i, int(i == count - 1))
