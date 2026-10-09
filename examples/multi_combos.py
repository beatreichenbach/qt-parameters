import logging

from qtpy import QtCore, QtGui, QtWidgets

from examples import application, save_pixmap
from qt_parameters import MultiComboParameter, ParameterForm, TokenParameter


class WidgetGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle('Multi Combo Widgets')
        self.resize(720, 400)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        parameter_form = ParameterForm()
        parameter_form.parameter_changed.connect(lambda p: logging.debug(p.value()))
        layout.addWidget(parameter_form)

        items = ('apple', 'banana', 'cherry', 'dragonfruit', 'edamame', 'fig')

        parm = MultiComboParameter[str]('multi')
        parm.set_items(items)
        parameter_form.add_parameter(parm)

        parm = MultiComboParameter[str]('multi_placeholder')
        parm.set_items(items)
        parm.set_placeholder('Select produce ...')
        parameter_form.add_parameter(parm)

        parm = MultiComboParameter[str]('multi_limits')
        parm.set_items(items)
        parm.set_minimum_selection(2)
        parm.set_maximum_selection(4)
        parm.set_default(('apple', 'banana'))
        parameter_form.add_parameter(parm)

        parm = MultiComboParameter[int]('multi_int')
        parm.set_items(tuple(range(1, 10)))
        parm.set_default((2,))
        values = parm.value()
        for value in values:
            assert isinstance(value, int)
        parameter_form.add_parameter(parm)

        token_parameter = TokenParameter[str]('tokens')
        token_parameter.set_items((*items, 'apple_juice', 'banana_bread', 'cherry_pie'))
        token_parameter.set_value(('apple', 'banana'))
        parameter_form.add_parameter(token_parameter)

        self.exclusive_parameter = parm = MultiComboParameter[str]('multi_exclusive')
        parm.set_items(items)
        parm.set_exclusive_items(('all', 'none'))
        parm.set_default(('all',))
        parameter_form.add_parameter(parm)

        # Screenshot
        self.screenshot_button = QtWidgets.QPushButton('Screenshot')
        self.screenshot_button.clicked.connect(self._screenshot)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.screenshot_button)
        button_layout.addStretch()
        parameter_form.add_layout(button_layout)

    def _screenshot(self) -> None:
        """Save a screenshot with the dropdown of the last combo open."""

        self.exclusive_parameter.combo.showPopup()
        self.screenshot_button.hide()

        QtWidgets.QApplication.processEvents()
        pixmap = self.grab()
        popup = self.exclusive_parameter.combo.view().window()
        offset = popup.mapToGlobal(QtCore.QPoint()) - self.mapToGlobal(QtCore.QPoint())
        painter = QtGui.QPainter(pixmap)
        painter.drawPixmap(offset, popup.grab())
        painter.end()

        save_pixmap(pixmap, 'multi_combos')

        self.exclusive_parameter.combo.hidePopup()
        self.screenshot_button.show()


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
