from __future__ import annotations

import contextlib
import re
import textwrap
from bisect import bisect
from collections.abc import Generator, Sequence
from pathlib import Path
from re import Match

import black
from black import Mode

from .constants import PYGMENTS_PY_LANGS
from .errors import CodeBlockError
from .regex_patterns import (
    INDENT_RE,
    LATEX_PYCON_RE,
    LATEX_RE,
    MD_PYCON_RE,
    MD_RE,
    ON_OFF_COMMENT_RE,
    PYCON_CONTINUATION_PREFIX,
    PYCON_CONTINUATION_RE,
    PYCON_PREFIX,
    PYTHONTEX_RE,
    RST_LITERAL_BLOCKS_RE,
    RST_PYCON_RE,
    RST_RE,
    TRAILING_NL_RE,
)


class BlackFormatter:
    def __init__(self, mode: Mode) -> None:
        self.mode: Mode = mode
        self.errors: list[CodeBlockError] = []
        self.off_ranges: list[tuple[int, int]] = []

    def _within_off_range(self, code_range: tuple[int, int]) -> bool:
        index = bisect(self.off_ranges, code_range)

        try:
            off_start, off_end = self.off_ranges[index - 1]
        except IndexError:
            return False

        code_start, code_end = code_range

        return code_start >= off_start and code_end <= off_end

    @contextlib.contextmanager
    def _collect_error(self, match: Match[str]) -> Generator[None]:
        try:
            yield
        except Exception as e:  # noqa: BLE001
            self.errors.append(CodeBlockError(match.start(), e))

    def _md_match(self, match: Match[str]) -> str:
        if self._within_off_range(match.span()):
            return match[0]

        code = textwrap.dedent(match["code"])

        with self._collect_error(match):
            code = black.format_str(code, mode=self.mode)

        code = textwrap.indent(code, match["indent"])

        return f"{match['before']}{code}{match['after']}"

    def _rst_match(self, match: Match[str]) -> str:
        if self._within_off_range(match.span()):
            return match[0]
        lang = match["lang"]

        if lang is not None and lang not in PYGMENTS_PY_LANGS:
            return match[0]

        if not match["code"].strip():
            return match[0]

        min_indent = min(INDENT_RE.findall(match["code"]))
        trailing_ws_match = TRAILING_NL_RE.search(match["code"])
        assert trailing_ws_match

        trailing_ws = trailing_ws_match.group()
        code = textwrap.dedent(match["code"])

        with self._collect_error(match):
            code = black.format_str(code, mode=self.mode)

        code = textwrap.indent(code, min_indent)

        return f"{match['before']}{code.rstrip()}{trailing_ws}"

    def _rst_literal_blocks_match(self, match: Match[str]) -> str:
        if self._within_off_range(match.span()):
            return match[0]

        if not match["code"].strip():
            return match[0]

        min_indent = min(INDENT_RE.findall(match["code"]))
        trailing_ws_match = TRAILING_NL_RE.search(match["code"])
        assert trailing_ws_match

        trailing_ws = trailing_ws_match.group()
        code = textwrap.dedent(match["code"])

        with self._collect_error(match):
            code = black.format_str(code, mode=self.mode)

        code = textwrap.indent(code, min_indent)

        return f"{match['before']}{code.rstrip()}{trailing_ws}"

    def _pycon_match(self, match: Match[str]) -> str:
        code = ""
        fragment: str | None = None

        def finish_fragment() -> None:
            nonlocal code
            nonlocal fragment

            if fragment is not None:
                with self._collect_error(match):
                    fragment = black.format_str(fragment, mode=self.mode)

                fragment_lines = fragment.splitlines()
                code += f"{PYCON_PREFIX}{fragment_lines[0]}\n"

                for line in fragment_lines[1:]:
                    # Skip blank lines to handle Black adding a blank above
                    # functions within blocks. A blank line would end the REPL
                    # continuation prompt.
                    #
                    # >>> if True:
                    # ...     def f():
                    # ...         pass
                    # ...
                    if line:
                        code += f"{PYCON_CONTINUATION_PREFIX} {line}\n"

                if fragment_lines[-1].startswith(" "):
                    code += f"{PYCON_CONTINUATION_PREFIX}\n"

                fragment = None

        indentation: int | None = None

        for line in match["code"].splitlines():
            orig_line, line = line, line.lstrip()

            if indentation is None and line:
                indentation = len(orig_line) - len(line)

            continuation_match = PYCON_CONTINUATION_RE.match(line)

            if continuation_match and fragment is not None:
                fragment += line[continuation_match.end() :] + "\n"
            else:
                finish_fragment()

                if line.startswith(PYCON_PREFIX):
                    fragment = line[len(PYCON_PREFIX) :] + "\n"
                else:
                    code += orig_line[indentation:] + "\n"

        finish_fragment()

        return code

    def _md_pycon_match(self, match: Match[str]) -> str:
        if self._within_off_range(match.span()):
            return match[0]

        code = self._pycon_match(match)
        code = textwrap.indent(code, match["indent"])

        return f"{match['before']}{code}{match['after']}"

    def _rst_pycon_match(self, match: Match[str]) -> str:
        if self._within_off_range(match.span()):
            return match[0]

        code = self._pycon_match(match)

        if not code.strip():
            return match[0]

        min_indent = min(INDENT_RE.findall(match["code"]))
        code = textwrap.indent(code, min_indent)

        return f"{match['before']}{code}"

    def _latex_match(self, match: Match[str]) -> str:
        if self._within_off_range(match.span()):
            return match[0]

        code = textwrap.dedent(match["code"])

        with self._collect_error(match):
            code = black.format_str(code, mode=self.mode)

        code = textwrap.indent(code, match["indent"])

        return f"{match['before']}{code}{match['after']}"

    def _latex_pycon_match(self, match: Match[str]) -> str:
        if self._within_off_range(match.span()):
            return match[0]

        code = self._pycon_match(match)
        code = textwrap.indent(code, match["indent"])

        return f"{match['before']}{code}{match['after']}"

    def format_str(
        self,
        src: str,
        *,
        rst_literal_blocks: bool = False,
    ) -> tuple[str, Sequence[CodeBlockError]]:
        off_start = None

        for comment in re.finditer(ON_OFF_COMMENT_RE, src):
            # Check for the "off" value across the multiple (on|off) groups.
            if "off" in comment.groups():
                if off_start is None:
                    off_start = comment.start()
            else:
                if off_start is not None:
                    self.off_ranges.append((off_start, comment.end()))
                    off_start = None

        if off_start is not None:
            self.off_ranges.append((off_start, len(src)))

        src = MD_RE.sub(self._md_match, src)
        src = MD_PYCON_RE.sub(self._md_pycon_match, src)
        src = RST_RE.sub(self._rst_match, src)
        src = RST_PYCON_RE.sub(self._rst_pycon_match, src)
        if rst_literal_blocks:
            src = RST_LITERAL_BLOCKS_RE.sub(
                self._rst_literal_blocks_match,
                src,
            )
        src = LATEX_RE.sub(self._latex_match, src)
        src = LATEX_PYCON_RE.sub(self._latex_pycon_match, src)
        src = PYTHONTEX_RE.sub(self._latex_match, src)

        return src, self.errors

    def format_file(
        self,
        filename: str,
        skip_errors: bool,
        rst_literal_blocks: bool,
        check_only: bool,
    ) -> int:
        with Path(filename).open(encoding="UTF-8") as f:
            contents = f.read()

        new_contents, errors = self.format_str(
            contents,
            rst_literal_blocks=rst_literal_blocks,
        )

        for error in errors:
            lineno = contents[: error.offset].count("\n") + 1
            print(f"{filename}:{lineno}: code block parse error {error.exc}")

        if errors and not skip_errors:
            return 2

        if contents == new_contents:
            return 0

        if check_only:
            print(f"{filename}: Requires a rewrite.")
            return 1

        print(f"{filename}: Rewriting...")

        with Path(filename).open("w", encoding="UTF-8") as f:
            f.write(new_contents)

        return 1
