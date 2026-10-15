from qtpy import QtCore, QtTest, QtWidgets

from qt_parameters import MultiComboParameter


def test_multi_combo_set_items(app: QtWidgets.QApplication) -> None:
    parm = MultiComboParameter[str]('multi')

    parm.set_items(('apple', 'banana', 'cherry'))
    assert parm.value() == ()

    parm.set_value(('apple', 'banana'))
    assert parm.value() == ('apple', 'banana')

    parm.set_items(('banana', 'cherry'))
    assert parm.value() == ('banana',)


def test_multi_combo_separator(app: QtWidgets.QApplication) -> None:
    parm = MultiComboParameter[str]('multi_exclusive')
    parm.set_items(('apple', 'banana', 'cherry'))
    parm.set_exclusive_items(('all',))
    parm.set_default(('all',))
    parm.show()
    parm.combo.showPopup()

    view = parm.combo.view()
    model = view.model()
    separator = model.index(1, 0)  # row 1 = separator
    assert not bool(model.flags(separator) & QtCore.Qt.ItemFlag.ItemIsSelectable)

    pos = view.visualRect(separator).center()
    assert view.indexAt(pos) == separator

    button = QtCore.Qt.MouseButton.LeftButton
    QtTest.QTest.mousePress(view.viewport(), button, pos=pos)
    assert parm.value() == ('all',)

    QtTest.QTest.mouseRelease(view.viewport(), button, pos=pos)
    assert parm.value() == ('all',)
    assert view.isVisible()


def test_multi_combo_formatter(app: QtWidgets.QApplication) -> None:
    parm = MultiComboParameter[str]('multi')
    parm.set_items(('apple', 'banana', 'cherry', 'dragonfruit'))
    parm.set_value(('apple', 'banana'))

    option = QtWidgets.QStyleOptionComboBox()
    parm.combo.initStyleOption(option)
    assert option.currentText == 'apple, banana'

    parm.set_value(('apple', 'banana', 'cherry', 'dragonfruit'))
    parm.combo.initStyleOption(option)
    assert option.currentText == 'apple, banana, cherry, ...'

    parm.combo.set_formatter(lambda items, max_items: f'{len(items)} selected')
    parm.combo.initStyleOption(option)
    assert option.currentText == '4 selected'


def test_multi_combo_scroll(app: QtWidgets.QApplication) -> None:
    items = [f'item_{i:02d}' for i in range(100)]
    parm = MultiComboParameter[str]('multi')
    parm.set_items(items)
    parm.show()
    parm.combo.showPopup()
    view = parm.combo.view()
    view.setCurrentIndex(view.model().index(50, 0))
    view.scrollTo(view.currentIndex())
    row = view.currentIndex().row()
    scroll = view.verticalScrollBar().value()

    parm.set_items(items)
    assert view.currentIndex().row() == row
    assert view.verticalScrollBar().value() == scroll
