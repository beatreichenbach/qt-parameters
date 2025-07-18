import json
import logging
import os
from enum import Enum
from functools import partial

import qt_themes
from qtpy import QtGui, QtCore, QtWidgets

from qt_parameters import (
    BoolParameter,
    CollapsibleBox,
    ColorParameter,
    ComboParameter,
    EnumParameter,
    FloatParameter,
    IntParameter,
    Label,
    MultiFloatParameter,
    MultiIntParameter,
    ParameterForm,
    PathParameter,
    PointFParameter,
    PointParameter,
    SizeFParameter,
    SizeParameter,
    StringParameter,
    TabDataParameter,
)
from tests import application


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

        # Numbers
        form = ParameterForm('numbers')
        box = parameter_form.add_form(form)

        action = QtGui.QAction('Reset', form)
        action.triggered.connect(partial(form.reset, None))
        box.addAction(action)

        parm = IntParameter('int')
        parm.set_line_min(10)
        parm.set_line_max(200)
        parm.set_slider_min(10)
        parm.set_slider_max(100)
        parm.set_default(20)
        form.add_parameter(parm)

        parm = IntParameter('int_no_slider')
        parm.set_slider_visible(False)
        parm.set_default(20)
        form.add_parameter(parm)

        parm = FloatParameter('float')
        parm.set_line_min(0)
        parm.set_line_max(200)
        parm.set_default(0.20)
        form.add_parameter(parm)

        parm = FloatParameter('float_decimals')
        parm.set_slider_max(10)
        parm.set_decimals(2)
        parm.set_default(3.14159265359)
        form.add_parameter(parm)

        # Multi Number
        form = ParameterForm('multi_numbers')
        parameter_form.add_form(form)

        parm = MultiIntParameter('multi_int')
        form.add_parameter(parm)
        parm = MultiFloatParameter('multi_float')
        parm.set_keep_ratio(False)
        form.add_parameter(parm)
        parm = PointParameter('qpoint')
        parm.set_label('QPoint')
        form.add_parameter(parm)
        parm = PointFParameter('qpointf')
        parm.set_label('QPointF')
        form.add_parameter(parm)
        parm = SizeParameter('qsize')
        parm.set_label('QSize')
        parm.set_default((4, 4))
        form.add_parameter(parm)
        parm = SizeFParameter('qsizef')
        parm.set_label('QSizeF')
        parm.set_default((0.72, 0.72))
        form.add_parameter(parm)
        parm = ColorParameter('qcolor')
        parm.set_label('QColor')
        theme = qt_themes.get_theme()
        if theme:
            parm.set_default(theme.secondary)
        form.add_parameter(parm)

        # Custom Widgets
        parameter_form.add_separator()

        form = ParameterForm('custom_widgets')
        parameter_form.add_form(form)

        button_layout = QtWidgets.QHBoxLayout()
        screenshot_button = QtWidgets.QPushButton('Screenshot')
        screenshot_button.clicked.connect(self._screenshot)
        button_layout.addWidget(screenshot_button)
        button_layout.addStretch()
        form.add_layout(button_layout)

        progress_bar = QtWidgets.QProgressBar()
        progress_bar.setMaximum(0)
        progress_bar.setTextVisible(False)
        form.add_widget(progress_bar)

        # Column 2
        parameter_form = ParameterForm()
        layout.addWidget(parameter_form)
        self.forms.append(parameter_form)

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

        parm = PathParameter('path')
        parm.set_default('/qt_parameters/widgets.py')
        form.add_parameter(parm)

        label = Label()
        label.set_level(logging.WARNING)
        label.set_text(
            'This is a warning label. '
            'These labels can be used to provide information to the user.'
        )
        form.add_widget(label)

        # Options
        form = ParameterForm('options')
        box = parameter_form.add_form(form)
        box.set_collapsible(False)

        parm = ComboParameter('combo')
        parm.set_items(('Red', 'Green', 'Blue'))
        form.add_parameter(parm)

        parm = EnumParameter('enum')
        enum = Enum('Vehicle', 'Bicycle Car Plane')
        parm.set_enum(enum)
        form.add_parameter(parm)

        parm = BoolParameter('bool')
        form.add_parameter(parm)

        parm = IntParameter('tooltip')
        parm.set_tooltip(
            'This is an example tooltip. Sometimes a tooltip can be very long.'
        )
        form.add_parameter(parm)

        # Boxes
        form = ParameterForm('box_button_style')
        box = parameter_form.add_form(form)
        box.set_title('Box (Button Style)')
        box.set_box_style(CollapsibleBox.Style.BUTTON)

        parm = IntParameter('int')
        parm.set_default(10)
        form.add_parameter(parm)

        form = ParameterForm('box_no_style')
        box = parameter_form.add_form(form)
        box.set_title('Box (No Style)')
        box.set_box_style(CollapsibleBox.Style.NONE)

        parm = IntParameter('int')
        parm.set_default(10)
        form.add_parameter(parm)

        # Column 3
        parameter_form = ParameterForm()
        layout.addWidget(parameter_form)
        self.forms.append(parameter_form)

        # Checkable
        form = ParameterForm('checkable_parameters')
        box = parameter_form.add_form(form, checkable=True)
        box.set_checked(True)

        parm = IntParameter('int')
        parm.set_slider_min(10)
        parm.set_slider_max(100)
        parm.set_default(20)
        form.add_parameter(parm, checkable=True)

        parm = FloatParameter('float')
        parm.set_slider_max(10)
        parm.set_default(3.14159265359)
        form.add_parameter(parm, checkable=True)

        parm = StringParameter('string')
        parm.set_placeholder('Placeholder ...')
        form.add_parameter(parm, checkable=True)

        parm = SizeParameter('sizef')
        form.add_parameter(parm, checkable=True)
        form.checkbox(parm).set_value(True)

        # TabData
        form = ParameterForm('tabdata')
        parameter_form.add_form(form)

        data = [
            ['Sun', 696000, 198],
            ['Earth', 6371, 5973.6],
            ['Moon', 1737, 73.5],
            ['Mars', 3390, 641.85],
            ['A really big Star', 406320, 339023452345.23450],
        ]
        parm = TabDataParameter('tabdata')
        parm.set_default(data)
        parm.set_headers(['Name', 'Radius', 'Weight'])
        parm.set_types([str, int, float])
        parm.set_start_index(4)
        form.add_parameter(parm, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

        # Tab Group
        tab_1 = ParameterForm('tab_1')
        tab_2 = ParameterForm('tab_2')
        parameter_form.add_forms((tab_1, tab_2))
        tab_1.add_parameter(IntParameter('int'))
        tab_1.add_parameter(StringParameter('string'))
        tab_1.add_parameter(BoolParameter('bool'))
        tab_1.add_parameter(ComboParameter('combo'))

        # Boxes
        form = ParameterForm('collapsed_box_button')
        box = parameter_form.add_form(form)
        box.set_title('Collapsed Box (Button)')
        box.set_box_style(CollapsibleBox.Style.BUTTON)
        box.set_collapsed(True)

        form = ParameterForm('collapsed_box_simple')
        box = parameter_form.add_form(form)
        box.set_title('Collapsed Box (Simple)')
        box.set_collapsed(True)

        form.add_parameter(BoolParameter('bool'))
        label = Label()
        label.set_text('asdf')
        form.add_widget(label)

    def _screenshot(self) -> None:
        path = os.path.join('..', '.github', 'assets', f'editor.png')
        pixmap = self.grab()
        pixmap.save(path)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)
    with application():
        widget = WidgetGallery()
        widget.show()


if __name__ == '__main__':
    main()
