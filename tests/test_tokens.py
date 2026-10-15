from qtpy import QtWidgets

from qt_parameters import TokenParameter


def test_token_parameter_value(app: QtWidgets.QApplication) -> None:
    parm = TokenParameter('token')

    parm.set_items(('a', 'b', 'c'))
    parm.set_value(('a', 'b'))
    assert parm.value() == ('a', 'b')


def test_token_parameter_set_items_unchanged(app: QtWidgets.QApplication) -> None:
    parm = TokenParameter('token')

    parm.set_items(('a', 'b', 'c'))
    parm.set_value(('a', 'b'))
    parm.set_items(('a', 'b', 'c'))
    assert parm.value() == ('a', 'b')
