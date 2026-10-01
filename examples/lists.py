import json
import logging

from qtpy import QtWidgets

from examples import application, screenshot_button
from qt_parameters import (
    BoolParameter,
    IntParameter,
    ListParameter,
    ParameterForm,
    StringParameter,
)


class ChildForm(ParameterForm):
    def __init__(self, name: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(name=name, parent=parent)

        self.add_parameter(BoolParameter('enabled'))
        self.add_parameter(StringParameter('label'))


class WidgetGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

        values = self.form.values()
        logging.debug(json.dumps(values, indent=4, default=lambda x: str(x)))
        self.form.parameter_changed.connect(lambda p: logging.debug(p.value()))

    def _init_ui(self) -> None:
        self.setWindowTitle('List Widgets')
        self.resize(720, 320)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.form = form = ParameterForm()
        layout.addWidget(form)

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

        # Screenshot
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(screenshot_button(self, 'lists'))
        button_layout.addStretch()
        layout.addLayout(button_layout)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
