# qt-parameters

This is a collection of Qt parameter widgets and forms for Python.
It is designed to provide an efficient way for creating a parameter interface for your
application. The parameter widgets use a unified interface and work with complex data
types such as `Enum` and Qt types like `QPoint`, `QColor`, etc.

This package uses Material Icons from
[qt-material-icons](https://github.com/beatreichenbach/qt-material-icons).


![Header](https://raw.githubusercontent.com/beatreichenbach/qt-parameters/refs/heads/main/.github/assets/header.png)

## Installation

Install using pip:
```shell
pip install qt-parameters
```

## Usage

```python
from PySide6 import QtWidgets
import qt_parameters

app = QtWidgets.QApplication()

editor = qt_parameters.ParameterEditor()

# Add simple parameters
editor.add_parameter(qt_parameters.FloatParameter('float'))
editor.add_parameter(qt_parameters.StringParameter('string'))
editor.add_parameter(qt_parameters.PathParameter('path'))

# Customize parameter properties
parm = qt_parameters.PointFParameter('pointf')
parm.set_line_min(1)
parm.set_line_max(7)
parm.set_decimals(3)
editor.add_parameter(parm)

editor.show()

# Access the parameter values
print(editor.values())

app.exec()
```

For more examples see the [examples](examples) directory.

### Generic

Parameters are generic over their value type, so `value()` and `set_value()` are typed.
Parameters that work with arbitrary data take a type argument:

```python
from enum import Enum

from qt_parameters import ComboParameter, EnumParameter


class Vehicle(Enum):
    Bicycle = 'Bicycle'
    Car = 'Car'
    Plane = 'Plane'


parm = EnumParameter[Vehicle]('vehicle')
parm.set_enum(Vehicle)
value = parm.value()  # Vehicle | None

parm = ComboParameter[int]('level')
parm.set_items({'Low': 1, 'Medium': 2, 'High': 3})
value = parm.value()  # int | None
```

## Screenshots

<details>
<summary>Editor</summary>

![Editor](https://raw.githubusercontent.com/beatreichenbach/qt-parameters/refs/heads/main/.github/assets/editor.png)

</details>

<details>
<summary>Numbers</summary>

![Numbers](https://raw.githubusercontent.com/beatreichenbach/qt-parameters/refs/heads/main/.github/assets/numbers.png)

</details>

<details>
<summary>Strings</summary>

![Strings](https://raw.githubusercontent.com/beatreichenbach/qt-parameters/refs/heads/main/.github/assets/strings.png)

</details>

<details>
<summary>Combos</summary>

![Combos](https://raw.githubusercontent.com/beatreichenbach/qt-parameters/refs/heads/main/.github/assets/combos.png)

</details>

<details>
<summary>Qt Types</summary>

![Qt Types](https://raw.githubusercontent.com/beatreichenbach/qt-parameters/refs/heads/main/.github/assets/qt_types.png)

</details>

<details>
<summary>Multi Combos</summary>

![Multi Combos](https://raw.githubusercontent.com/beatreichenbach/qt-parameters/refs/heads/main/.github/assets/multi_combos.png)

</details>

<details>
<summary>Lists</summary>

![Lists](https://raw.githubusercontent.com/beatreichenbach/qt-parameters/refs/heads/main/.github/assets/lists.png)

</details>

<details>
<summary>Tab Data</summary>

![Tab Data](https://raw.githubusercontent.com/beatreichenbach/qt-parameters/refs/heads/main/.github/assets/tabdata.png)

</details>

<details>
<summary>Breadcrumbs</summary>

![Breadcrumbs](https://raw.githubusercontent.com/beatreichenbach/qt-parameters/refs/heads/main/.github/assets/breadcrumbs.png)

</details>

## Contributing

To contribute please refer to the [Contributing Guide](CONTRIBUTING.md).

## License

MIT License. Copyright 2024 - Beat Reichenbach.
See the [License file](LICENSE) for details.
