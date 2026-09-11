import logging

from qtpy import QtWidgets

from qt_parameters import ParameterForm
from qt_parameters.multi import MultiComboParameter

from examples import application


class WidgetGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle('Parameter Widgets')
        self.resize(1280, 560)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        form = ParameterForm()
        layout.addWidget(form)

        parm = MultiComboParameter('multi')
        items = ('alice', 'bob', 'charlie')
        parm.set_items(items)
        parm.set_placeholder('Select Options ...')
        parm.set_value(('alice', 'bob'))
        parm.value_changed.connect(logging.debug)
        form.add_parameter(parm)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
