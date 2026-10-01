from __future__ import annotations

from qtpy import QtCore, QtGui, QtWidgets

from .parameters.base import ParameterWidget


class ParameterToolTip(QtWidgets.QFrame):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent, QtCore.Qt.WindowType.ToolTip)

        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setAutoFillBackground(True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        palette = self.palette()
        palette.setColor(
            QtGui.QPalette.ColorRole.Window,
            palette.color(QtGui.QPalette.ColorRole.Base),
        )
        self.setPalette(palette)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)

        self._title = QtWidgets.QLabel(self)
        font = self._title.font()
        font.setBold(True)
        self._title.setFont(font)
        layout.addWidget(self._title)

        separator = QtWidgets.QFrame(self)
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        layout.addWidget(separator)

        self._detail = QtWidgets.QLabel(self)
        layout.addWidget(self._detail)

        self._text = QtWidgets.QLabel(self)
        self._text.setWordWrap(True)
        self._text.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft
        )
        layout.addWidget(self._text)

    def set_widget(self, widget: ParameterWidget) -> None:
        self._title.setText(widget.label())
        typ = type(widget).__name__.replace('Parameter', '')
        self._detail.setText(f'Parameter: {widget.name()} ({typ})')
        self._text.setText(widget.tooltip())


class ParameterLabel(QtWidgets.QLabel):
    def __init__(
        self, widget: ParameterWidget, parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(widget.label(), parent)

        self._widget = widget

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.text()!r})'

    def widget(self) -> ParameterWidget:
        return self._widget


class ToolTipManager(QtCore.QObject):
    """Show a single tooltip for the label that is currently hovered."""

    _DELAY = 600

    def __init__(self) -> None:
        super().__init__()

        self._label: ParameterLabel | None = None
        self._tooltip: ParameterToolTip | None = None

        self._timer = QtCore.QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(self._DELAY)
        self._timer.timeout.connect(self._show_tooltip)

    @classmethod
    def instance(cls) -> ToolTipManager:
        global _tooltip_manager
        if _tooltip_manager is None:
            _tooltip_manager = cls()
        return _tooltip_manager

    def register(self, label: ParameterLabel) -> None:
        label.installEventFilter(self)

    def hide(self) -> None:
        """Stop the timer and hide the current tooltip."""

        self._timer.stop()
        self._label = None
        if self._tooltip is not None:
            self._tooltip.hide()

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if isinstance(watched, ParameterLabel):
            event_type = event.type()
            if event_type == QtCore.QEvent.Type.Enter:
                if watched.widget().tooltip():
                    self.hide()
                    self._label = watched
                    self._timer.start()
            elif event_type in (
                QtCore.QEvent.Type.Leave,
                QtCore.QEvent.Type.Hide,
                QtCore.QEvent.Type.MouseButtonPress,
                QtCore.QEvent.Type.Wheel,
            ):
                self.hide()
        return False

    def _show_tooltip(self) -> None:
        label = self._label
        if label is None or not label.isVisible() or not label.isEnabled():
            return
        if not label.rect().contains(label.mapFromGlobal(QtGui.QCursor.pos())):
            return

        if self._tooltip is None:
            self._tooltip = ParameterToolTip()
        tooltip = self._tooltip
        tooltip.set_widget(label.widget())
        tooltip.adjustSize()
        tooltip.move(self._position(label, tooltip))
        tooltip.show()

    @staticmethod
    def _position(label: ParameterLabel, tooltip: ParameterToolTip) -> QtCore.QPoint:
        position = label.mapToGlobal(QtCore.QPoint(0, label.height()))
        screen = QtGui.QGuiApplication.screenAt(position)
        if screen is None:
            screen = QtGui.QGuiApplication.primaryScreen()
        if screen is not None:
            bounds = screen.availableGeometry()
            x = min(max(position.x(), bounds.left()), bounds.right() - tooltip.width())
            y = min(max(position.y(), bounds.top()), bounds.bottom() - tooltip.height())
            position = QtCore.QPoint(x, y)
        return position


_tooltip_manager: ToolTipManager | None = None
