from __future__ import annotations

import enum
from collections.abc import Sequence

from qt_material_icons import MaterialIcon
from qtpy import QtCore, QtGui, QtWidgets

PixelMetric = QtWidgets.QStyle.PixelMetric


class CollapsibleBox(QtWidgets.QFrame):
    class Style(enum.IntEnum):
        NONE = 0
        SIMPLE = 1
        BUTTON = 2

    NONE = Style.NONE
    SIMPLE = Style.SIMPLE
    BUTTON = Style.BUTTON

    def __init__(
        self, title: str = '', parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self._maximum_height = self.maximumHeight()
        self._collapsed = False
        self._checkable = False
        self._collapsible = False
        self._style = CollapsibleBox.Style.SIMPLE

        self.header = None
        self.title_label = None
        self.menu_button = None
        self.frame = None
        self._init_ui()

        if title:
            self.set_title(title)

        self.set_box_style(self._style)

    def _init_ui(self) -> None:
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Maximum
        )

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setSpacing(0)
        super().setLayout(self._layout)

        # Header
        self.header = QtWidgets.QWidget()
        self.header.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.header.installEventFilter(self)
        self.header.setBackgroundRole(QtGui.QPalette.ColorRole.Base)
        self._layout.addWidget(self.header)

        header_layout = QtWidgets.QHBoxLayout()
        self.header.setLayout(header_layout)
        self._default_margins = header_layout.contentsMargins()

        # Expand
        size = self.style().pixelMetric(PixelMetric.PM_ButtonIconSize)
        self._expand_more_label = QtWidgets.QLabel(self.header)
        self._expand_more_label.setVisible(False)
        icon = MaterialIcon('chevron_right')
        self._expand_more_label.setPixmap(icon.pixmap(size))
        header_layout.addWidget(self._expand_more_label)

        self._expand_less_label = QtWidgets.QLabel(self.header)
        self._expand_less_label.setVisible(False)
        icon = MaterialIcon('expand_more')
        self._expand_less_label.setPixmap(icon.pixmap(size))
        header_layout.addWidget(self._expand_less_label)

        # Checkbox
        self.checkbox = QtWidgets.QCheckBox(self.header)
        self.checkbox.setVisible(False)
        header_layout.addWidget(self.checkbox)

        # Title
        self.title_label = QtWidgets.QLabel(self.header)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Menu
        self.menu_button = QtWidgets.QToolButton(self.header)
        self.menu_button.setIcon(MaterialIcon('menu'))
        self.menu_button.setAutoRaise(True)
        self.menu_button.setVisible(False)
        self.menu_button.setPopupMode(
            QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
        )
        self.menu_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.menu_button.pressed.connect(self._show_menu)
        size = self.header.style().pixelMetric(PixelMetric.PM_SmallIconSize)
        self.menu_button.setMaximumSize(QtCore.QSize(size, size))
        header_layout.addWidget(self.menu_button)

        # Frame
        self.frame = QtWidgets.QFrame(self)
        self._layout.addWidget(self.frame)
        self._layout.setStretch(1, 1)
        self.checkbox.toggled.connect(self.frame.setEnabled)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.title()!r})'

    def actionEvent(self, event: QtGui.QActionEvent) -> None:
        self.menu_button.setVisible(bool(self.actions()))
        super().actionEvent(event)

    def enterEvent(self, event: QtGui.QEnterEvent) -> None:
        self.update()
        super().enterEvent(event)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if watched == self.header and self._collapsible:
            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                event: QtCore.QEvent.Type.MouseButtonPress
                if event.button() == QtCore.Qt.MouseButton.LeftButton:
                    self.header.setAutoFillBackground(True)

            if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
                event: QtCore.QEvent.Type.MouseButtonRelease
                if event.button() == QtCore.Qt.MouseButton.LeftButton:
                    self.set_collapsed(not self._collapsed)
                    self.header.setAutoFillBackground(False)
        return super().eventFilter(watched, event)

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        self.update()
        super().leaveEvent(event)

    def layout(self) -> QtWidgets.QLayout:
        return self.frame.layout()

    def setLayout(self, layout: QtWidgets.QLayout) -> None:
        self.frame.setLayout(layout)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        if not self._style == CollapsibleBox.Style.BUTTON:
            return super().paintEvent(event)

        option = QtWidgets.QStyleOptionButton()
        option.initFrom(self)

        if not self._collapsed:
            option.state |= QtWidgets.QStyle.StateFlag.State_Sunken
        if self._collapsed and self.underMouse():
            option.state |= QtWidgets.QStyle.StateFlag.State_MouseOver

        style = self.style()
        element = QtWidgets.QStyle.PrimitiveElement.PE_PanelButtonCommand
        painter = QtGui.QPainter(self)
        style.drawPrimitive(element, option, painter, self)

    def setMaximumHeight(self, maxh: int) -> None:
        self._maximum_height = maxh
        super().setMaximumHeight(maxh)

    def setMaximumSize(self, size: QtCore.QSize) -> None:
        self._maximum_height = size.height()
        super().setMaximumSize(size)

    def box_style(self) -> Style:
        return self._style

    def checkable(self) -> bool:
        return self._checkable

    def checked(self) -> bool:
        return self._checkable and self.checkbox.isChecked()

    def collapsible(self) -> bool:
        return self._collapsible

    def collapsed(self) -> bool:
        return self._collapsible and self._collapsed

    def title(self) -> str:
        return self.title_label.text()

    def set_actions(self, actions: Sequence[QtGui.QAction]) -> None:
        for action in self.actions():
            self.removeAction(action)
        self.addActions(actions)

    def set_checkable(self, checkable: bool) -> None:
        self._checkable = checkable
        self.checkbox.setVisible(checkable)
        if checkable:
            self.frame.setEnabled(self.checkbox.isChecked())
        else:
            self.checkbox.setChecked(False)

    def set_checked(self, checked: bool) -> None:
        if self.checkable():
            self.checkbox.setChecked(checked)

    def set_collapsible(self, collapsible: bool) -> None:
        self._collapsible = collapsible

        if collapsible:
            margins = QtCore.QMargins(4, 4, 4, 4)
            self.set_collapsed(self._collapsed)
        else:
            margins = self._default_margins
            self._expand_more_label.setVisible(False)
            self._expand_less_label.setVisible(False)
        self.header.layout().setContentsMargins(margins)

    def set_collapsed(self, collapsed: bool) -> None:
        if not self.collapsible():
            return

        self._collapsed = collapsed
        if collapsed:
            self.frame.setMaximumHeight(0)
            self._expand_more_label.setVisible(True)
            self._expand_less_label.setVisible(False)
        else:
            self.frame.setMaximumHeight(self._maximum_height)
            self._expand_more_label.setVisible(False)
            self._expand_less_label.setVisible(True)

    def set_box_style(self, style: Style) -> None:
        self._style = style

        if style == CollapsibleBox.Style.SIMPLE:
            self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        else:
            self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        if style == CollapsibleBox.Style.BUTTON:
            self._layout.setContentsMargins(2, 2, 2, 2)
        else:
            self._layout.setContentsMargins(0, 0, 0, 0)

    def set_title(self, title: str) -> None:
        self.title_label.setText(title)

    def _show_menu(self) -> None:
        relative_pos = self.menu_button.rect().topRight()
        relative_pos.setX(relative_pos.x() + 2)
        position = self.menu_button.mapToGlobal(relative_pos)

        menu = QtWidgets.QMenu(self)
        menu.addActions(self.actions())
        menu.exec_(position)

        self.menu_button.setDown(False)
