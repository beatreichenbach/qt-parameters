import json
import logging

import qt_themes
from qtpy import QtWidgets

from qt_parameters import (
    BoolParameter,
    IntParameter,
    ListParameter,
    ParameterForm,
    StringListParameter,
    StringParameter,
)
from tests import application


class ChildForm(ParameterForm):
    def __init__(self, name: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(name=name, parent=parent)

        self.add_parameter(BoolParameter('enabled'))
        self.add_parameter(StringParameter('label'))


class WidgetGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

        for form in self.forms:
            values = form.values()
            logging.debug(json.dumps(values, indent=4, default=lambda x: str(x)))
            form.parameter_changed.connect(lambda p: logging.debug(p.value()))

            state = form.state()
            form.set_state(state)

    def _init_ui(self) -> None:
        self.setWindowTitle('Parameter Widgets')
        self.resize(1280, 560)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.forms = []

        # Column 1
        parameter_form = ParameterForm()
        layout.addWidget(parameter_form)
        self.forms.append(parameter_form)

        # List Parameters
        form = ParameterForm('list_parameters')
        parameter_form.add_form(form)

        parm = ListParameter('string_list')
        parm.set_factory(StringParameter)
        values = tuple(f'item_{i}' for i in range(3))
        parm.set_default(values)
        form.add_parameter(parm)

        parm = ListParameter('int_list')
        parm.set_factory(IntParameter)
        parm.set_value(tuple(range(2)))
        form.add_parameter(parm)

        parm = ListParameter('form_list')
        parm.set_factory(ChildForm)
        parm.set_value(({'enabled': True, 'label': 'application'},) * 3)
        form.add_parameter(parm)

        # Column 2
        parameter_form = ParameterForm()
        layout.addWidget(parameter_form)
        self.forms.append(parameter_form)

        # String List Parameters
        form = ParameterForm('string_list_parameters')
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


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
