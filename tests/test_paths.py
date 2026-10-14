from pathlib import Path

from qtpy import QtWidgets

from qt_parameters import PathParameter


def test_path_parameter_value(app: QtWidgets.QApplication) -> None:
    parm = PathParameter('path')

    parm.set_value(Path('/tmp/x'))
    assert parm.value() == '/tmp/x'
    assert parm.path() == Path('/tmp/x')


def test_path_parameter_fallback(app: QtWidgets.QApplication) -> None:
    parm = PathParameter('path')

    parm.set_dir_fallback(Path('/home'))
    assert parm.dir_fallback() == '/home'
