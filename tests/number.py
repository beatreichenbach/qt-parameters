import logging

import qt_themes
from qtpy import QtWidgets

from qt_parameters import FloatParameter, IntParameter, ParameterForm
from tests import application


class WidgetGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle('Number Widgets')
        self.resize(1280, 560)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.forms = []

        # Column 1
        parameter_form = ParameterForm()
        layout.addWidget(parameter_form)
        self.forms.append(parameter_form)

        # Int Ticks
        form = ParameterForm('int_ticks')
        parameter_form.add_form(form)

        parm = IntParameter('int_10k')
        parm.set_slider_min(0)
        parm.set_slider_max(10000)
        parm.set_default(1000)
        form.add_parameter(parm)

        parm = IntParameter('int_1k')
        parm.set_slider_min(0)
        parm.set_slider_max(1000)
        parm.set_default(100)
        form.add_parameter(parm)

        parm = IntParameter('int_100')
        parm.set_slider_min(0)
        parm.set_slider_max(100)
        parm.set_default(10)
        form.add_parameter(parm)

        parm = IntParameter('int_10')
        parm.set_slider_min(0)
        parm.set_slider_max(10)
        parm.set_default(1)
        form.add_parameter(parm)

        # Float Ticks
        form = ParameterForm('float_ticks')
        parameter_form.add_form(form)

        parm = FloatParameter('float_10k')
        parm.set_slider_min(0)
        parm.set_slider_max(10000)
        parm.set_default(1000)
        form.add_parameter(parm)

        parm = FloatParameter('float_1k')
        parm.set_slider_min(0)
        parm.set_slider_max(1000)
        parm.set_default(100)
        form.add_parameter(parm)

        parm = FloatParameter('float_100')
        parm.set_slider_min(0)
        parm.set_slider_max(100)
        parm.set_default(10)
        form.add_parameter(parm)

        parm = FloatParameter('float_10')
        parm.set_slider_min(0)
        parm.set_slider_max(10)
        parm.set_default(1)
        form.add_parameter(parm)

        parm = FloatParameter('float_0.1')
        parm.set_decimals(4)
        parm.set_slider_min(0)
        parm.set_slider_max(0.1)
        parm.set_default(0.01)
        form.add_parameter(parm)

        parm = FloatParameter('float_0.01')
        parm.set_decimals(4)
        parm.set_slider_min(0)
        parm.set_slider_max(0.01)
        parm.set_default(0.001)
        form.add_parameter(parm)

        parm = FloatParameter('float_0.001')
        parm.set_decimals(4)
        parm.set_slider_min(0)
        parm.set_slider_max(0.001)
        parm.set_default(0.0001)
        form.add_parameter(parm)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
