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

For more examples see the `tests` directory.

## Contributing

To contribute please refer to the [Contributing Guide](CONTRIBUTING.md).

## License

MIT License. Copyright 2024 - Beat Reichenbach.
See the [License file](LICENSE) for details.
