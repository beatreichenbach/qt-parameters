from qtpy import QtWidgets

from qt_parameters import CrumbParameter


def test_crumb_parameter_max_items(app: QtWidgets.QApplication) -> None:
    parm = CrumbParameter('crumb')

    parm.set_max_items(2)
    assert parm.max_items() == 2
    assert parm.value() is None
