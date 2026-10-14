from qtpy import QtWidgets

from qt_parameters import BoolParameter


def test_parameter_metadata(app: QtWidgets.QApplication) -> None:
    parm = BoolParameter('bool_parm')

    assert parm.name() == 'bool_parm'
    assert parm.label() == 'Bool Parm'

    parm.set_tooltip('tip')
    assert parm.tooltip() == 'tip'


def test_bool_parameter_value(app: QtWidgets.QApplication) -> None:
    parm = BoolParameter('bool')

    parm.set_value(True)
    assert parm.value() is True
    assert parm.checkbox.isChecked()
