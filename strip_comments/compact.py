"""Whitespace compaction for Python source via the standard-library ``ast`` module.

Compaction collapses multi-line statements (e.g. a wrapped multi-argument call)
onto single lines, removing redundant layout tokens (newlines + indentation),
comments, docstrings and blank lines. It keeps **one logical statement per line**
with proper indentation -- no semicolon chaining.

The implementation re-serializes the parsed AST with ``ast.unparse``. Because the
output is produced by CPython's own unparser it is always valid Python and
semantically equivalent to the input (identifiers and type annotations are
preserved). Re-serialization does normalize cosmetics -- string quotes, redundant
parentheses and spacing -- which is irrelevant for the tool's read-only purpose.
"""

import ast


def _strip_docstrings(tree: ast.Module) -> None:
    """Remove docstrings (and bare leading string literals) in place."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            # Classes/functions must keep a body; modules may become empty.
            if isinstance(node, ast.Module):
                node.body = body[1:]
            else:
                node.body = body[1:] or [ast.Pass()]


def compact_python(source: str) -> str:
    """Return ``source`` with Python statements compacted onto single lines.

    Args:
        source: Python source code.

    Returns:
        The compacted source, ending with a single newline if non-empty, else "".

    Raises:
        SyntaxError: If ``source`` is not valid Python for the running interpreter.
            Callers are expected to fall back to the tree-sitter path.
    """
    tree = ast.parse(source)
    _strip_docstrings(tree)
    unparsed = ast.unparse(tree)

    # Drop blank lines (mirrors stripper.strip_comments) and end with one newline.
    lines = [line for line in unparsed.splitlines() if line.strip()]
    return "\n".join(lines) + "\n" if lines else ""
