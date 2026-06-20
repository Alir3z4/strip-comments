from collections.abc import Callable

from tree_sitter import Node, Tree

from strip_comments.languages import LanguageConfig


def walk_tree(node: Node, callback: Callable[[Node], None]) -> None:
    callback(node)
    for child in node.children:
        walk_tree(child, callback)


def _merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not ranges:
        return []
    sorted_ranges = sorted(ranges, key=lambda r: (r[0], r[1]))
    merged = [sorted_ranges[0]]
    for start, end in sorted_ranges[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def _is_whitespace_only(data: bytes, start: int, end: int) -> bool:
    return data[start:end].strip() == b""


def strip_comments(
    tree: Tree,
    config: LanguageConfig,
    source: str,
) -> str:
    source_bytes = source.encode("utf-8")
    ranges_to_remove: list[tuple[int, int]] = []

    def collect(node: Node) -> None:
        is_comment = node.type in config.comment_types
        is_docstring = node.type in config.docstring_types or (
            config.docstring_detector is not None and config.docstring_detector(node)
        )

        if not (is_comment or is_docstring):
            return

        start_byte = node.start_byte
        end_byte = node.end_byte

        line_start = start_byte
        while line_start > 0 and source_bytes[line_start - 1] != ord("\n"):
            line_start -= 1

        line_end = end_byte
        while line_end < len(source_bytes) and source_bytes[line_end] != ord("\n"):
            line_end += 1
        if line_end < len(source_bytes):
            line_end += 1

        before = _is_whitespace_only(source_bytes, line_start, start_byte)
        after = _is_whitespace_only(source_bytes, end_byte, line_end)

        if before and after:
            start_byte = line_start
            end_byte = line_end

        ranges_to_remove.append((start_byte, end_byte))

    walk_tree(tree.root_node, collect)

    if ranges_to_remove:
        merged = _merge_ranges(ranges_to_remove)
        buf = bytearray()
        prev_end = 0
        for start, end in merged:
            buf.extend(source_bytes[prev_end:start])
            prev_end = end
        buf.extend(source_bytes[prev_end:])
        text = buf.decode("utf-8")
    else:
        text = source

    # Remove blank lines and strip trailing whitespace from all remaining lines
    result_lines = []
    for line in text.splitlines():
        stripped = line.rstrip()
        if stripped:
            result_lines.append(stripped)
    return "\n".join(result_lines) + "\n" if result_lines else ""
