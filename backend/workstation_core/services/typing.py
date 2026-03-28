from __future__ import annotations

from typing import Protocol


class FileLike(Protocol):
    mimetype: str

    def read(self) -> bytes:
        ...