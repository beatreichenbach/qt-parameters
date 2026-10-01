from __future__ import annotations

from qtpy import QtCore, QtWidgets

LayoutRequest = QtCore.QEvent.Type.LayoutRequest
ScrollBarExtent = QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent
ScrollBarAlwaysOff = QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff


class VerticalScrollArea(QtWidgets.QScrollArea):
    """ScrollArea widget that has a minimum width based on its content."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        viewport = QtWidgets.QWidget(self)
        self.setViewport(viewport)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if watched == self.widget() and event.type() == LayoutRequest:
            self._refresh_minimum_width()
        return super().eventFilter(watched, event)

    def setWidget(self, widget: QtWidgets.QWidget) -> None:
        super().setWidget(widget)
        widget.setAutoFillBackground(False)
        widget.installEventFilter(self)
        self._refresh_minimum_width()

    def sizeHint(self) -> QtCore.QSize:
        widget = self.widget() or super()
        return widget.sizeHint()

    def _refresh_minimum_width(self) -> None:
        if widget := self.widget():
            min_width = widget.minimumSizeHint().width()
            if self.verticalScrollBarPolicy() != ScrollBarAlwaysOff:
                scroll_bar = self.verticalScrollBar()
                min_width += self.style().pixelMetric(ScrollBarExtent, None, scroll_bar)
            self.setMinimumWidth(min_width)
