import contextlib
import sys

import qt_themes
from qtpy import QtWidgets


@contextlib.contextmanager
def application() -> QtWidgets.QApplication:
    if app := QtWidgets.QApplication.instance():
        qt_themes.set_theme('one_dark_two')
        yield app
        return

    app = QtWidgets.QApplication(sys.argv)
    qt_themes.set_theme('one_dark_two')
    yield app
    app.exec_()
