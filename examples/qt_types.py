import logging

from qtpy import QtCore, QtGui, QtWidgets

from examples import application, screenshot_button
from qt_parameters import (
    ColorParameter,
    ParameterForm,
    PointFParameter,
    PointParameter,
    SizeFParameter,
    SizeParameter,
)


class WidgetGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle('Qt Type Widgets')
        self.resize(720, 240)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Column 1
        parameter_form = ParameterForm()
        layout.addWidget(parameter_form)

        form = ParameterForm('qt_types')
        parameter_form.add_form(form)

        parm = PointParameter('qpoint')
        parm.set_default(QtCore.QPoint(10, 20))
        form.add_parameter(parm)

        parm = PointFParameter('qpointf')
        parm.set_decimals(3)
        parm.set_default(QtCore.QPointF(0.1, 0.2))
        form.add_parameter(parm)

        parm = SizeParameter('qsize')
        parm.set_default(QtCore.QSize(4, 4))
        form.add_parameter(parm)

        parm = SizeFParameter('qsizef')
        parm.set_decimals(3)
        parm.set_default(QtCore.QSizeF(0.72, 0.72))
        form.add_parameter(parm)

        parm = ColorParameter('qcolor')
        parm.set_default(QtGui.QColor(234, 12, 40))
        form.add_parameter(parm)

        # Screenshot
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(screenshot_button(self, 'qt_types'))
        button_layout.addStretch()
        layout.addLayout(button_layout)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
