from __future__ import annotations

import re

from .constants import (
    ON_OFF,
    PYCON_CONTINUATION_PREFIX,
    PYGMENTS_PY_LANGS,
    PYTHONTEX_LANG,
)

__all__ = (
    "INDENT_RE",
    "LATEX_PYCON_RE",
    "LATEX_RE",
    "MD_PYCON_RE",
    "MD_RE",
    "ON_OFF_COMMENT_RE",
    "PYCON_CONTINUATION_PREFIX",
    "PYCON_CONTINUATION_RE",
    "PYCON_PREFIX",
    "PYTHONTEX_RE",
    "RST_LITERAL_BLOCKS_RE",
    "RST_PYCON_RE",
    "RST_RE",
    "TRAILING_NL_RE",
)


PYGMENTS_PY_LANGS_RE_FRAGMENT = f"({'|'.join(PYGMENTS_PY_LANGS)})"
MD_RE = re.compile(
    r"(?P<before>^(?P<indent> *)```[^\S\r\n]*"
    + PYGMENTS_PY_LANGS_RE_FRAGMENT
    + r"( .*?)?\n)"
    r"(?P<code>.*?)"
    r"(?P<after>^(?P=indent)```[^\S\r\n]*$)",
    re.DOTALL | re.MULTILINE,
)
MD_PYCON_RE = re.compile(
    r"(?P<before>^(?P<indent> *)```[^\S\r\n]*pycon( .*?)?\n)"
    r"(?P<code>.*?)"
    r"(?P<after>^(?P=indent)```[^\S\r\n]*$)",
    re.DOTALL | re.MULTILINE,
)
BLOCK_TYPES = "(code|code-block|sourcecode|ipython)"
DOCTEST_TYPES = "(testsetup|testcleanup|testcode)"
RST_RE = re.compile(
    rf"(?P<before>"
    rf"^(?P<indent> *)\.\. ("
    rf"jupyter-execute::|"
    rf"{BLOCK_TYPES}:: (?P<lang>\w+)|"
    rf"{DOCTEST_TYPES}::.*"
    rf")\n"
    rf"((?P=indent) +:.*\n)*"
    rf"( *\n)*"
    rf")"
    rf"(?P<code>(^((?P=indent) +.*)?\n)+)",
    re.MULTILINE,
)
RST_LITERAL_BLOCKS_RE = re.compile(
    r"(?P<before>"
    r"^(?! *\.\. )(?P<indent> *).*::\n"
    r"((?P=indent) +:.*\n)*"
    r"\n*"
    r")"
    r"(?P<code>(^((?P=indent) +.*)?\n)+)",
    re.MULTILINE,
)
RST_PYCON_RE = re.compile(
    r"(?P<before>"
    r"(?P<indent> *)\.\. ((code|code-block):: pycon|doctest::.*)\n"
    r"((?P=indent) +:.*\n)*"
    r"\n*"
    r")"
    r"(?P<code>(^((?P=indent) +.*)?(\n|$))+)",
    re.MULTILINE,
)
PYCON_CONTINUATION_RE = re.compile(
    rf"^{re.escape(PYCON_CONTINUATION_PREFIX)}( |$)",
)
LATEX_RE = re.compile(
    r"(?P<before>^(?P<indent> *)\\begin{minted}(\[.*?\])?{python}\n)"
    r"(?P<code>.*?)"
    r"(?P<after>^(?P=indent)\\end{minted}\s*$)",
    re.DOTALL | re.MULTILINE,
)
LATEX_PYCON_RE = re.compile(
    r"(?P<before>^(?P<indent> *)\\begin{minted}(\[.*?\])?{pycon}\n)"
    r"(?P<code>.*?)"
    r"(?P<after>^(?P=indent)\\end{minted}\s*$)",
    re.DOTALL | re.MULTILINE,
)
PYCON_PREFIX = ">>> "
PYTHONTEX_RE = re.compile(
    rf"(?P<before>^(?P<indent> *)\\begin{{{PYTHONTEX_LANG}}}\n)"
    rf"(?P<code>.*?)"
    rf"(?P<after>^(?P=indent)\\end{{(?P=lang)}}\s*$)",
    re.DOTALL | re.MULTILINE,
)
INDENT_RE = re.compile("^ +(?=[^ ])", re.MULTILINE)
TRAILING_NL_RE = re.compile(r"\n+\Z", re.MULTILINE)

ON_OFF_COMMENT_RE = re.compile(
    # Markdown
    rf"(?:^\s*<!-- {ON_OFF} -->$)|"
    # rST
    rf"(?:^\s*\.\. +{ON_OFF}$)|"
    # LaTeX
    rf"(?:^\s*% {ON_OFF}$)",
    re.MULTILINE,
)
