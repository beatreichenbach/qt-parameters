from qtpy import QtWidgets

from qt_parameters import TabDataParameter


def test_tabdata_parameter_value(app: QtWidgets.QApplication) -> None:
    parm = TabDataParameter('tabdata')

    parm.set_value([(1, 'a'), (2, 'b')])
    assert parm.value() == ((1, 'a'), (2, 'b'))
