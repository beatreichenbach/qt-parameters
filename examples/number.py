import logging

from qtpy import QtWidgets

from examples import application, screenshot_button
from qt_parameters import (
    FloatParameter,
    IntParameter,
    MultiFloatParameter,
    MultiIntParameter,
    ParameterForm,
)


class WidgetGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle('Number Widgets')
        self.resize(720, 560)

        outer = QtWidgets.QVBoxLayout()
        self.setLayout(outer)
        layout = QtWidgets.QHBoxLayout()
        outer.addLayout(layout)

        # Column 1 (Int)
        parameter_form = ParameterForm()
        layout.addWidget(parameter_form)

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

        # Int Step Sizes
        form = ParameterForm('int_step_sizes')
        parameter_form.add_form(form)

        parm = IntParameter('int_step_1')
        parm.set_slider_min(0)
        parm.set_slider_max(1000)
        parm.set_default(100)
        parm.set_step_factor(1)
        form.add_parameter(parm)

        parm = IntParameter('int_step_2')
        parm.set_slider_min(0)
        parm.set_slider_max(1000)
        parm.set_default(100)
        form.add_parameter(parm)

        parm = IntParameter('int_step_3')
        parm.set_slider_min(0)
        parm.set_slider_max(1000)
        parm.set_default(100)
        parm.set_step_factor(3)
        form.add_parameter(parm)

        # Multi Int
        form = ParameterForm('multi_int')
        parameter_form.add_form(form)

        parm = MultiIntParameter('multi_int')
        form.add_parameter(parm)

        parm = MultiIntParameter('multi_int_no_ratio')
        parm.set_keep_ratio(False)
        form.add_parameter(parm)

        # Column 2 (Float)
        parameter_form = ParameterForm()
        layout.addWidget(parameter_form)

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

        # Float Step Sizes
        form = ParameterForm('float_step_sizes')
        parameter_form.add_form(form)

        parm = FloatParameter('float_step_2')
        parm.set_slider_min(0)
        parm.set_slider_max(1000)
        parm.set_default(100)
        form.add_parameter(parm)

        parm = FloatParameter('float_step_3')
        parm.set_slider_min(0)
        parm.set_slider_max(1000)
        parm.set_default(100)
        parm.set_step_factor(3)
        form.add_parameter(parm)

        parm = FloatParameter('float_step_4')
        parm.set_slider_min(0)
        parm.set_slider_max(1000)
        parm.set_default(100)
        parm.set_step_factor(4)
        form.add_parameter(parm)

        # Multi Float
        form = ParameterForm('multi_float')
        parameter_form.add_form(form)

        parm = MultiFloatParameter('multi_float')
        form.add_parameter(parm)

        parm = MultiFloatParameter('multi_float_no_ratio')
        parm.set_keep_ratio(False)
        form.add_parameter(parm)

        # Screenshot
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(screenshot_button(self, 'numbers'))
        button_layout.addStretch()
        outer.addLayout(button_layout)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
