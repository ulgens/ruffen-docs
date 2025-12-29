from __future__ import annotations

__all__ = ("CodeBlockError",)


class CodeBlockError:
    def __init__(self, offset: int, exc: Exception) -> None:
        self.offset = offset
        self.exc = exc
