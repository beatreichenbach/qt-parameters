from __future__ import annotations

from enum import Enum, auto
from os import PathLike
from pathlib import Path

from qtpy import QtCore, QtWidgets

from ..qt_material_icons import MaterialIcon
from .base import ParameterWidget


class PathParameter(ParameterWidget[str]):
    class Method(Enum):
        OPEN_FILE = auto()
        SAVE_FILE = auto()
        EXISTING_DIR = auto()

    OPEN_FILE = Method.OPEN_FILE
    SAVE_FILE = Method.SAVE_FILE
    EXISTING_DIR = Method.EXISTING_DIR

    value_changed = QtCore.Signal(str)

    _value: str = ''
    _default: str = ''
    _dir_fallback: str = ''
    _method: Method = Method.OPEN_FILE

    def _init_ui(self) -> None:
        self.line = QtWidgets.QLineEdit()
        self.line.editingFinished.connect(self._editing_finished)
        self._layout.addWidget(self.line)

        self.button = QtWidgets.QToolButton()
        self.button.setIcon(MaterialIcon('file_open'))
        self.button.clicked.connect(self.browse)
        self._layout.addWidget(self.button)

        self._layout.setStretch(0, 1)
        self.setFocusProxy(self.line)

    def dir_fallback(self) -> str:
        return self._dir_fallback

    def method(self) -> Method:
        return self._method

    def path(self) -> Path:
        """Return the current value as a `pathlib.Path`."""

        return Path(self._value)

    def value(self) -> str:
        return super().value()

    def set_dir_fallback(self, dir_fallback: str | PathLike[str]) -> None:
        self._dir_fallback = str(dir_fallback)

    def set_method(self, method: Method) -> None:
        self._method = method

    def set_value(self, value: str | PathLike[str]) -> None:
        super().set_value(str(value))
        self.line.blockSignals(True)
        self.line.setText(self._value)
        self.line.blockSignals(False)

    def browse(self) -> None:
        start_dir = self._value or self._dir_fallback
        if start_dir:
            start_dir = str(Path(start_dir).expanduser())
        if self._method == PathParameter.Method.OPEN_FILE:
            path, _filters = QtWidgets.QFileDialog.getOpenFileName(
                parent=self, caption='Open File', dir=start_dir
            )
        elif self._method == PathParameter.Method.SAVE_FILE:
            path, _filters = QtWidgets.QFileDialog.getSaveFileName(
                parent=self, caption='Save File', dir=start_dir, filter='*.*'
            )
        elif self._method == PathParameter.Method.EXISTING_DIR:
            path = QtWidgets.QFileDialog.getExistingDirectory(
                parent=self, caption='Select Directory', dir=start_dir
            )
        else:
            return

        if path:
            self.set_value(path)

    def _editing_finished(self) -> None:
        value = self.line.text()
        super().set_value(value)
