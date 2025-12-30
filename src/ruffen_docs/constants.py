from __future__ import annotations

__all__ = (
    "ON_OFF",
    "PYCON_CONTINUATION_PREFIX",
    "PYGMENTS_PY_LANGS",
    "PYTHONTEX_LANG",
)

ON_OFF = r"ruffen-docs:(on|off)"
PYCON_CONTINUATION_PREFIX = "..."
PYGMENTS_PY_LANGS = frozenset((
    "python",
    "py",
    "sage",
    "python3",
    "py3",
    "numpy",
))
PYTHONTEX_LANG = r"(?P<lang>pyblock|pycode|pyconsole|pyverbatim)"
