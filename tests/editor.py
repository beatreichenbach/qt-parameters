import json
import logging

import qt_themes
from qtpy import QtCore, QtGui, QtWidgets

from qt_parameters import (
    BoolParameter,
    ColorParameter,
    ComboParameter,
    FloatParameter,
    IntParameter,
    MultiFloatParameter,
    MultiIntParameter,
    ParameterEditor,
    ParameterForm,
    PointFParameter,
    PointParameter,
    SizeFParameter,
    SizeParameter,
    StringParameter,
)
from tests import application


class Editor(ParameterEditor):
    def __init__(self, name: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(name=name, parent=parent)

    def init_ui(self) -> None:
        # Numbers
        form = ParameterForm('numbers')
        box = self.add_form(form)

        action = QtGui.QAction('Reset', form)
        action.triggered.connect(form.reset)
        box.addAction(action)

        parm = IntParameter('int')
        parm.set_default(20)
        form.add_parameter(parm)

        parm = FloatParameter('float')
        parm.set_default(0.20)
        form.add_parameter(parm)

        # Strings
        form = ParameterForm('strings')
        self.add_form(form)

        parm = StringParameter('string')
        form.add_parameter(parm)

        # Nested Group
        form = ParameterForm('nested_strings')
        box = self.add_form(form)
        try:
            parm = StringParameter('string')
            form.add_parameter(parm)
        except ValueError:
            logging.info(f'Unique names validated successfully.')
            self.remove_form(form)
            self.remove_widget(box)

        # Flat
        form = ParameterForm('flat')
        form.set_flat(True)
        self.add_form(form)

        parm = IntParameter('flat_int')
        form.add_parameter(parm)

        parm = FloatParameter('flat_float')
        form.add_parameter(parm)

        # Options
        parm = BoolParameter('bool')
        self.add_parameter(parm)

        parm = ComboParameter('combo')
        self.add_parameter(parm)

        # Multi
        multi_form = ParameterForm('multi_numbers')

        parm = MultiIntParameter('multi_int')
        multi_form.add_parameter(parm)
        parm = MultiFloatParameter('multi_float')
        multi_form.add_parameter(parm)

        # Qt
        qt_form = ParameterForm('qt')

        parm = PointParameter('qpoint')
        qt_form.add_parameter(parm)
        parm = PointFParameter('qpointf')
        qt_form.add_parameter(parm)
        parm = SizeParameter('qsize')
        qt_form.add_parameter(parm)
        parm = SizeFParameter('qsizef')
        qt_form.add_parameter(parm)
        parm = ColorParameter('qcolor')
        qt_form.add_parameter(parm)

        # TabWidget
        self.add_forms((multi_form, qt_form))

        # RadioTabWidget
        form_tab_1 = ParameterForm('tab_1')
        parm = StringParameter('string')
        form_tab_1.add_parameter(parm)

        form_tab_2 = ParameterForm('tab_2')
        parm = StringParameter('string')
        form_tab_2.add_parameter(parm)

        self.add_forms((form_tab_1, form_tab_2), radio=True)

        # Options
        self.add_separator()

        button = QtWidgets.QRadioButton('Radio Button')
        self.add_widget(button)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QPushButton('Ok'))
        layout.addWidget(QtWidgets.QPushButton('Cancel'))
        self.add_layout(layout)


class EditorGallery(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

        values = {
            'numbers': {'int': 50, 'float': 3.14159},
            'strings': {'string': 'some text'},
            'flat_int': 12,
            'flat_float': 1.414,
            'bool': True,
            'multi_numbers': {'multi_int': (4, 2), 'multi_float': (0.1, 0.2)},
            'qt': {
                'qpoint': QtCore.QPoint(1, 2),
                'qpointf': QtCore.QPointF(0.1, 0.2),
                'qcolor': QtGui.QColor(234, 12, 40),
            },
        }
        self.editors[1].set_values(values)

        for editor in self.editors:
            values = editor.values()
            logging.debug(json.dumps(values, indent=4, default=lambda x: str(x)))

    def _init_ui(self) -> None:
        self.setWindowTitle('Parameter Editors')
        self.resize(640, 840)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.editors = []

        # Editor 1
        editor = Editor()
        editor.init_ui()
        layout.addWidget(editor)
        self.editors.append(editor)

        # Editor 2
        editor = Editor()
        editor.set_unique_names(True)
        editor.init_ui()
        layout.addWidget(editor)
        self.editors.append(editor)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        editor = EditorGallery()
        editor.show()


if __name__ == '__main__':
    main()
