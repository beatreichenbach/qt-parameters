import logging

from qtpy import QtWidgets

from examples import application
from qt_parameters import MultiComboParameter, ParameterForm


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
        form.parameter_changed.connect(lambda p: logging.debug(p.value()))
        layout.addWidget(form)

        items = ('apple', 'banana', 'cherry', 'dragonfruit', 'edamame', 'fig')

        parm = MultiComboParameter[str]('multi')
        parm.set_items(items)
        form.add_parameter(parm)

        parm = MultiComboParameter[str]('multi_exclusive')
        parm.set_items(items)
        parm.set_exclusive_items(('all', 'none'))
        form.add_parameter(parm)

        parm = MultiComboParameter[str]('multi_placeholder')
        parm.set_items(items)
        parm.set_placeholder('Select produce ...')
        form.add_parameter(parm)

        parm = MultiComboParameter[str]('multi_limits')
        parm.set_items(items)
        parm.set_minimum_selection(2)
        parm.set_maximum_selection(4)
        parm.set_default(('apple', 'banana'))
        form.add_parameter(parm)

        parm = MultiComboParameter[int]('multi_int')
        parm.set_items(tuple(range(1, 10)))
        parm.set_default((2,))
        values = parm.value()
        for value in values:
            assert isinstance(value, int)
        form.add_parameter(parm)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
