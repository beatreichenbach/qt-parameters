from __future__ import annotations

import re


def title(text: str) -> str:
    text = re.sub(r'([a-z0-9])([A-Z])', r'\g<1> \g<2>', text).replace('_', ' ').title()
    return text
