from qtpy import QtWidgets

from qt_parameters import StringListParameter, StringParameter


def test_string_parameter_value(app: QtWidgets.QApplication) -> None:
    parm = StringParameter('string')

    parm.set_value('hi')
    assert parm.value() == 'hi'
    assert isinstance(parm.text, QtWidgets.QLineEdit)
    assert parm.text.text() == 'hi'


def test_string_list_parameter_value(app: QtWidgets.QApplication) -> None:
    parm = StringListParameter('string_list')

    parm.set_value(['a', 'b'])
    assert parm.value() == ('a', 'b')
