from qtpy import QtCore, QtGui, QtWidgets

from qt_parameters import ColorParameter, PointParameter, SizeParameter


def test_point_parameter_value(app: QtWidgets.QApplication) -> None:
    parm = PointParameter('point')

    parm.set_value(QtCore.QPoint(3, 4))
    assert parm.value() == QtCore.QPoint(3, 4)


def test_size_parameter_value(app: QtWidgets.QApplication) -> None:
    parm = SizeParameter('size')

    parm.set_value(QtCore.QSize(5, 6))
    assert parm.value() == QtCore.QSize(5, 6)


def test_color_parameter_value(app: QtWidgets.QApplication) -> None:
    parm = ColorParameter('color')

    parm.set_value(QtGui.QColor(255, 0, 0))
    assert parm.value() == QtGui.QColor(255, 0, 0)
