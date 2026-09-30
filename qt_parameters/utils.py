from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

Item = tuple[str, Any]


def title(text: str) -> str:
    text = re.sub(r'([a-z0-9])([A-Z])', r'\g<1> \g<2>', text).replace('_', ' ').title()
    return text


def items(
    items: Sequence[Item | str] | Mapping[str, Any],
) -> tuple[Item, ...]:
    """Return a tuple of items in (label, data) format."""

    if isinstance(items, Mapping):
        items = tuple(items.items())
    else:
        items = tuple(i if isinstance(i, tuple) else (i, i) for i in items)

    return items
