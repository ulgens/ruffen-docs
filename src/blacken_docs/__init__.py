from __future__ import annotations

import argparse
from collections.abc import Sequence

import black
from black.const import DEFAULT_LINE_LENGTH
from black.mode import TargetVersion

from .formatters import BlackFormatter


def run(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--line-length",
        type=int,
        default=DEFAULT_LINE_LENGTH,
    )
    parser.add_argument(
        "--preview",
        action="store_true",
    )
    parser.add_argument(
        "-S",
        "--skip-string-normalization",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--target-version",
        action="append",
        type=lambda v: TargetVersion[v.upper()],
        default=[],
        help=f"choices: {[v.name.lower() for v in TargetVersion]}",
        dest="target_versions",
    )
    parser.add_argument(
        "--check",
        action="store_true",
    )
    parser.add_argument(
        "-E",
        "--skip-errors",
        action="store_true",
    )
    parser.add_argument(
        "--rst-literal-blocks",
        action="store_true",
    )
    parser.add_argument(
        "--pyi",
        action="store_true",
    )
    parser.add_argument(
        "filenames",
        nargs="*",
    )
    args = parser.parse_args(argv)

    black_mode = black.Mode(
        target_versions=set(args.target_versions),
        line_length=args.line_length,
        string_normalization=not args.skip_string_normalization,
        is_pyi=args.pyi,
        preview=args.preview,
    )

    retv = 0
    for filename in args.filenames:
        formatter = BlackFormatter(mode=black_mode)
        retv |= formatter.format_file(
            filename,
            skip_errors=args.skip_errors,
            rst_literal_blocks=args.rst_literal_blocks,
            check_only=args.check,
        )
    return retv
