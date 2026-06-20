from collections.abc import Callable
from dataclasses import dataclass

from tree_sitter import Node


@dataclass(frozen=True)
class LanguageConfig:
    comment_types: set[str]
    docstring_types: set[str]
    docstring_detector: Callable[[Node], bool] | None = None


def _is_python_docstring(node: Node) -> bool:
    if node.type != "expression_statement":
        return False
    if not node.children or node.children[0].type != "string":
        return False
    parent = node.parent
    if parent is None or parent.type not in ("module", "block"):
        return False
    for child in parent.children:
        # Skip anonymous nodes (e.g., ":" in blocks) and comments
        if not child.is_named or child.type == "comment":
            continue
        return child == node
    return False


LANGUAGE_MAP: dict[str, LanguageConfig] = {
    ".py": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
        docstring_detector=_is_python_docstring,
    ),
    ".js": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".ts": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".tsx": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".html": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".css": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".go": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".rs": LanguageConfig(
        comment_types={"line_comment", "block_comment"},
        docstring_types=set(),
    ),
    ".c": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".cpp": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".java": LanguageConfig(
        comment_types={"comment", "line_comment", "block_comment"},
        docstring_types=set(),
    ),
    ".rb": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".php": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".sh": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".json": LanguageConfig(
        comment_types=set(),
        docstring_types=set(),
    ),
    ".lua": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".swift": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".kt": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".toml": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".dockerfile": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".cs": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
    ".zig": LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    ),
}


def get_language_config(ext: str) -> LanguageConfig:
    if ext in LANGUAGE_MAP:
        return LANGUAGE_MAP[ext]
    return LanguageConfig(
        comment_types={"comment"},
        docstring_types=set(),
    )
