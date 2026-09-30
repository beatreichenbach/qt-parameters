from qtpy import QtCore, QtGui, QtWidgets


class ResizeGrip(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.can_resize_vertical = True
        self.can_resize_horizontal = False

        self._resizing = False
        self._min_size = None
        self._start_position = QtCore.QPoint()
        self._start_size = QtCore.QSize()
        self._start_size_policy = None
        self._start_max_size = None

        self.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
        self.reset()
        parent.installEventFilter(self)

    @property
    def min_size(self) -> QtCore.QSize:
        if self._min_size is None:
            parent = self.parent()
            if not isinstance(parent, QtWidgets.QWidget):
                return QtCore.QSize()

            min_size = parent.minimumSize()
            min_size_hint = parent.minimumSizeHint()
            min_width = max(min_size.width(), min_size_hint.width(), self.width())
            min_height = max(min_size.height(), min_size_hint.height(), self.height())
            self._min_size = QtCore.QSize(min_width, min_height)
        return self._min_size

    def changeEvent(self, event: QtCore.QEvent) -> None:
        parent = self.parent()
        if not isinstance(parent, QtWidgets.QWidget):
            return

        if event.type() == QtCore.QEvent.Type.ParentChange:
            self.reset()

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.Resize and obj == self.parent():
            self.reposition()
            self.resize_scroll_bars()
            return False
        return super().eventFilter(obj, event)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        opt = QtWidgets.QStyleOptionSizeGrip()
        opt.initFrom(self)
        opt.corner = QtCore.Qt.Corner.BottomRightCorner
        self.style().drawControl(
            QtWidgets.QStyle.ControlElement.CE_SizeGrip, opt, painter, self
        )

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseDoubleClickEvent(event)
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.reset()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(event)
        self._resizing = True
        self._start_position = event.globalPos()
        parent = self.parent()
        if isinstance(parent, QtWidgets.QWidget):
            self._start_size = parent.geometry().size()
            if self._start_size_policy is None:
                self._start_size_policy = parent.sizePolicy()
            if self._start_max_size is None:
                self._start_max_size = parent.maximumSize()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self._resizing:
            delta = event.globalPos() - self._start_position
            parent = self.parent()
            if isinstance(parent, QtWidgets.QWidget):
                if self.can_resize_horizontal:
                    width = self._start_size.width() + delta.x()
                    width = max(width, self.min_size.width())
                    parent.setFixedWidth(width)

                if self.can_resize_vertical:
                    height = self._start_size.height() + delta.y()
                    height = max(height, self.min_size.height())
                    parent.setFixedHeight(height)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self._resizing = False

    def reset(self) -> None:
        """Reset the Size, SizePolicy, MaximumSize and MinimumSize attributes."""

        parent = self.parent()
        if not isinstance(parent, QtWidgets.QWidget):
            return

        # Size
        size = parent.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SizeGripSize)
        self.setFixedSize(size, size)

        # SizePolicy
        if self._start_size_policy is not None:
            policy = self._start_size_policy
            self._start_size_policy = None
            parent.setSizePolicy(policy)

        # MaximumSize
        if self._start_max_size is not None:
            max_size = self._start_max_size
            self._start_max_size = None
            parent.setMaximumSize(max_size)

        # MinimumSize
        parent.setMinimumSize(parent.minimumSizeHint())
        self._min_size = None

    def reposition(self) -> None:
        """Reposition the widget to the bottom right of the parent."""

        parent = self.parent()
        if not isinstance(parent, QtWidgets.QWidget):
            return
        geometry = self.geometry()
        geometry.moveBottomRight(parent.contentsRect().bottomRight())
        self.setGeometry(geometry)

    def resize_scroll_bars(self) -> None:
        """Resize the parent's ScrollBars."""

        parent = self.parent()
        if isinstance(parent, QtWidgets.QAbstractScrollArea):
            size = parent.contentsRect().size() - self.size()
            parent.horizontalScrollBar().setMaximumWidth(size.width())
            parent.verticalScrollBar().setMaximumHeight(size.height())
