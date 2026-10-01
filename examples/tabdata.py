import logging

from qtpy import QtCore, QtWidgets

from examples import application, screenshot_button
from qt_parameters import ParameterForm, TabDataParameter


class WidgetGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle('Tab Data Widgets')
        self.resize(720, 320)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        form = ParameterForm()
        layout.addWidget(form)

        data = [
            ['Sun', 696000, 198],
            ['Earth', 6371, 5973.6],
            ['Moon', 1737, 73.5],
            ['Mars', 3390, 641.85],
            ['A really big Star', 406320, 339023452345.23450],
        ]
        self.parm = TabDataParameter('tabdata')
        self.parm.set_default(data)
        self.parm.set_headers(['Name', 'Radius', 'Weight'])
        self.parm.set_types([str, int, float])
        self.parm.set_start_index(4)
        self.parm.add_row()
        form.add_parameter(self.parm, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

        index = self.parm.view.model().index(0, 0)
        self.parm.view.selectionModel().setCurrentIndex(
            index, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect
        )

        # Screenshot
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(screenshot_button(self, 'tabdata'))
        button_layout.addStretch()
        layout.addLayout(button_layout)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
