from enum import Enum, auto

from qtpy import QtWidgets

from qt_parameters import ComboParameter, EnumParameter


class Fruit(Enum):
    APPLE = auto()
    BANANA = auto()


def test_combo_parameter_value(app: QtWidgets.QApplication) -> None:
    parm = ComboParameter('combo')

    parm.set_items(('a', 'b', 'c'))
    assert parm.value() == 'a'

    parm.set_value('c')
    assert parm.value() == 'c'


def test_enum_parameter_formatter(app: QtWidgets.QApplication) -> None:
    parm = EnumParameter('enum')

    parm.set_enum(Fruit)
    assert parm.combo.itemText(0) == 'Apple'

    parm.set_formatter(lambda member: member.name.lower())
    assert parm.combo.itemText(0) == 'apple'


def test_enum_parameter_value_by_name(app: QtWidgets.QApplication) -> None:
    parm = EnumParameter('enum')

    parm.set_enum(Fruit)
    parm.set_value('BANANA')
    assert parm.value() is Fruit.BANANA
