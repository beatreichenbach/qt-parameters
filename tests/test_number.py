from qtpy import QtWidgets

from qt_parameters import FloatParameter, IntParameter


def test_int_parameter_syncs_line_and_slider(app: QtWidgets.QApplication) -> None:
    parm = IntParameter('int')

    parm.set_value(5)
    assert parm.value() == 5
    assert parm.line.value() == 5
    assert parm.slider.value() == 5


def test_float_parameter_decimals(app: QtWidgets.QApplication) -> None:
    parm = FloatParameter('float')

    parm.set_decimals(2)
    assert parm.decimals() == 2
