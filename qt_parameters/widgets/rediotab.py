from __future__ import annotations

from qtpy import QtWidgets

from ..qt_material_icons import MaterialIcon


class RadioTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._unchecked_icon = MaterialIcon('radio_button_unchecked')
        self._checked_icon = MaterialIcon('radio_button_checked')

        self.currentChanged.connect(self._current_changed)

    def tabInserted(self, index: int) -> None:
        if not self.tabIcon(index):
            self.setTabIcon(index, self._unchecked_icon)

    def _current_changed(self, index: int) -> None:
        for i in range(self.count()):
            if i == index:
                self.setTabIcon(i, self._checked_icon)
            else:
                self.setTabIcon(i, self._unchecked_icon)
