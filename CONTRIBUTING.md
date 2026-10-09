# Contributing Guide

## Development

To get started:

```sh
uv venv --python 3.13
uv pip install -e ".[dev]"
pre-commit install
```

Run the checks:

```sh
ruff format qt_parameters examples
ruff check --select I --fix qt_parameters examples
ruff check qt_parameters examples
ty check
pytest
```

### Updating Icons

The material icons are vendored into `qt_parameters/qt_material_icons` with
[qt-material-icons]. To regenerate them after adding or removing an icon, run:

```sh
uv run qtmaterialicons -o qt_parameters --names \
    add \
    check_circle \
    chevron_right \
    close \
    delete \
    drag_handle \
    error \
    expand_more \
    file_open \
    info \
    link \
    link_off \
    menu \
    radio_button_checked \
    radio_button_unchecked \
    remove \
    report \
    warning
```

[qt-material-icons]: https://github.com/beatreichenbach/qt-material-icons

### Screenshots

Each example gallery has a **Screenshot** button that saves the window to `.github/assets/<name>.png`.

The README header is created from `widgets.png`:

```sh
cd .github
uv run python create_images.py
```

### Releasing Changes

To version up using [python-semantic-release](https://github.com/python-semantic-release/python-semantic-release):

```sh
semantic-release version
```
