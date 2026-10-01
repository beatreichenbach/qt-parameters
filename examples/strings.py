import logging

from qtpy import QtWidgets

from examples import application, screenshot_button
from qt_parameters import (
    ParameterForm,
    PathParameter,
    StringListParameter,
    StringParameter,
)


class WidgetGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle('String Widgets')
        self.resize(720, 320)

        outer = QtWidgets.QVBoxLayout()
        self.setLayout(outer)
        layout = QtWidgets.QHBoxLayout()
        outer.addLayout(layout)

        # Column 1
        parameter_form = ParameterForm()
        layout.addWidget(parameter_form)

        # Strings
        form = ParameterForm('strings')
        parameter_form.add_form(form)

        parm = StringParameter('string')
        parm.set_placeholder('Placeholder ...')
        form.add_parameter(parm)

        parm = StringParameter('string_menu')
        parm.set_menu({'item_1': 1, 'item_2': 2})
        parm.set_menu_mode(StringParameter.MenuMode.TOGGLE)
        form.add_parameter(parm)

        parm = StringParameter('area')
        parm.set_area(True)
        form.add_parameter(parm)

        # Path
        form = ParameterForm('paths')
        parameter_form.add_form(form)

        parm = PathParameter('path')
        parm.set_default('/qt_parameters/examples/strings.py')
        form.add_parameter(parm)

        # Column 2
        parameter_form = ParameterForm()
        layout.addWidget(parameter_form)

        # String List
        form = ParameterForm('string_lists')
        parameter_form.add_form(form)

        parm = StringListParameter('string_list_area')
        parm.set_default(('tokyo', 'london', 'paris', 'los_angeles'))
        parm.set_value(('tokyo', 'london', 'paris', 'los_angeles', 'beirut', 'nairobi'))
        form.add_parameter(parm)

        parm = StringListParameter('string_list')
        parm.set_area(False)
        parm.set_placeholder('Cities, separated by a space.')
        form.add_parameter(parm)

        parm = StringListParameter('string_list_menu')
        parm.set_area(False)
        parm.set_default(('exr', 'png'))
        parm.set_menu(('exr', 'jpg', 'png', 'gif'))
        parm.set_menu_mode(StringParameter.MenuMode.TOGGLE)
        form.add_parameter(parm)

        # Screenshot
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(screenshot_button(self, 'strings'))
        button_layout.addStretch()
        outer.addLayout(button_layout)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
