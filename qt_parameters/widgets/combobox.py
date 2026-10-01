from importlib.util import find_spec

from qtpy import QtGui, QtWidgets

HAS_PYSIDE2 = find_spec('PySide2') is not None


class ComboBox(QtWidgets.QComboBox):
    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """
        Paint the ComboBox with PlaceholderText.

        # https://bugreports.qt.io/browse/QTBUG-90595
        """

        if not HAS_PYSIDE2:
            super().paintEvent(event)
            return

        # https://code.qt.io/cgit/qt/qtbase.git/tree/src/widgets/widgets/qcombobox.cpp#n3084
        painter = QtWidgets.QStylePainter(self)
        painter.setPen(self.palette().color(QtGui.QPalette.ColorRole.Text))

        # Draw the Combobox frame, focus rect and selected etc.
        opt = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(opt)
        painter.drawComplexControl(QtWidgets.QStyle.ComplexControl.CC_ComboBox, opt)

        if self.currentIndex() < 0:
            color = opt.palette.brush(QtGui.QPalette.ColorRole.ButtonText).color()
            opt.palette.setBrush(QtGui.QPalette.ColorRole.ButtonText, color)
            if self.placeholderText():
                opt.currentText = self.placeholderText()

        # Draw the icon and text
        painter.drawControl(QtWidgets.QStyle.ControlElement.CE_ComboBoxLabel, opt)
