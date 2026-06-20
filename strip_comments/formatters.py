import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FileResult:
    path: str
    content: str
    note: str = ""


def format_plain(files: list[FileResult]) -> str:
    parts: list[str] = []
    for f in files:
        parts.append(f"=== {f.path} ===")
        parts.append("")
        if f.note:
            parts.append(f"-- {f.note} --")
            parts.append("")
        parts.append(f.content)
        parts.append("")
    return "\n".join(parts)


def format_json(files: list[FileResult]) -> str:
    data: list[dict[str, Any]] = [
        {
            "path": f.path,
            "content": f.content,
            "note": f.note,
        }
        for f in files
    ]
    return json.dumps(data, indent=2)
