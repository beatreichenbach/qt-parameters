import logging
from enum import Enum

from qtpy import QtCore, QtGui, QtWidgets

from examples import application, save_pixmap
from qt_parameters import (
    ComboParameter,
    EnumParameter,
    ParameterForm,
)


class Vehicle(Enum):
    Bicycle = 'Bicycle'
    Car = 'Car'
    Plane = 'Plane'


class WidgetGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle('Combo Widgets')
        self.resize(720, 240)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        parameter_form = ParameterForm()
        layout.addWidget(parameter_form)

        form = ParameterForm('combos')
        parameter_form.add_form(form)

        parm = ComboParameter[str]('combo')
        parm.set_items(('Red', 'Green', 'Blue'))
        form.add_parameter(parm)

        parm = ComboParameter[int]('combo_typed')
        parm.set_items({'One': 1, 'Two': 2, 'Three': 3})
        form.add_parameter(parm)

        self.enum_parameter = parm = EnumParameter[Vehicle]('enum')
        parm.set_enum(Vehicle)
        form.add_parameter(parm)

        # Screenshot
        self.screenshot_button = QtWidgets.QPushButton('Screenshot')
        self.screenshot_button.clicked.connect(self._screenshot)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.screenshot_button)
        button_layout.addStretch()
        parameter_form.add_layout(button_layout)

    def _screenshot(self) -> None:
        """Save a screenshot with the dropdown of the last combo open."""

        self.enum_parameter.combo.showPopup()
        self.screenshot_button.hide()

        QtWidgets.QApplication.processEvents()
        pixmap = self.grab()
        popup = self.enum_parameter.combo.view().window()
        offset = popup.mapToGlobal(QtCore.QPoint()) - self.mapToGlobal(QtCore.QPoint())
        painter = QtGui.QPainter(pixmap)
        painter.drawPixmap(offset, popup.grab())
        painter.end()

        save_pixmap(pixmap, 'combos')

        self.enum_parameter.combo.hidePopup()
        self.screenshot_button.show()


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
