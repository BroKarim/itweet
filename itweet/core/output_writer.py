"""Output writer for tweet drafts."""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Iterable, List, Optional


class OutputWriterError(RuntimeError):
    pass


class OutputWriter:
    def __init__(self, output_dir: str = "outputs") -> None:
        self.output_dir = output_dir

    def write_text(self, lines: Iterable[str], filename: Optional[str] = None) -> str:
        self._ensure_dir()
        path = os.path.join(self.output_dir, filename or self._default_name("txt"))
        try:
            with open(path, "w", encoding="utf-8") as f:
                for line in lines:
                    f.write(line.rstrip() + "\n")
        except Exception as exc:
            raise OutputWriterError(f"Failed to write output: {exc}") from exc
        return path

    def write_json(self, items: List[str], filename: Optional[str] = None) -> str:
        self._ensure_dir()
        path = os.path.join(self.output_dir, filename or self._default_name("json"))
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            raise OutputWriterError(f"Failed to write output: {exc}") from exc
        return path

    def _ensure_dir(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def _default_name(ext: str) -> str:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"tweets_{stamp}.{ext}"
