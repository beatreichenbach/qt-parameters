import contextlib
import sys
from collections.abc import Iterator
from pathlib import Path

import qt_themes
from qtpy import QtGui, QtWidgets

ASSETS = Path(__file__).resolve().parents[1] / '.github' / 'assets'


@contextlib.contextmanager
def application() -> Iterator[QtWidgets.QApplication]:
    theme = 'one_dark_two'
    app = QtWidgets.QApplication.instance()
    if isinstance(app, QtWidgets.QApplication):
        qt_themes.set_theme(theme)
        yield app
        return

    app = QtWidgets.QApplication(sys.argv)
    qt_themes.set_theme(theme)
    yield app
    app.exec()


def save_pixmap(pixmap: QtGui.QPixmap, name: str) -> None:
    """Save a pixmap to the "assets" directory as `name`."""

    ASSETS.mkdir(parents=True, exist_ok=True)
    pixmap.save(str(ASSETS / f'{name}.png'))


def save_screenshot(widget: QtWidgets.QWidget, name: str) -> None:
    """Save a screenshot of `widget` to the "assets" directory."""

    save_pixmap(widget.grab(), name)


def screenshot_button(widget: QtWidgets.QWidget, name: str) -> QtWidgets.QPushButton:
    """
    Return a button that saves a screenshot of `widget` as `name`.

    The button hides itself while capturing, so it does not appear in the screenshot.
    """

    button = QtWidgets.QPushButton('Screenshot')

    def _capture() -> None:
        button.hide()
        QtWidgets.QApplication.processEvents()
        save_pixmap(widget.grab(), name)
        button.show()

    button.clicked.connect(_capture)
    return button
