# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`strip-comments` is a Python CLI tool that removes comments and docstrings from source files using tree-sitter parsers. It is designed to reduce token noise when AI agents read codebases. Only Python grammar is required; all other language grammars are optional extras.

## Development Commands

Run the full CI check (default make target):

```bash
make check        # lint + format-check + mypy + test
```

Run a single test class or method:

```bash
python -m unittest tests.test_stripper.TestStripper.test_strip_line_comments -v
```

Install with all language dependencies for development:

```bash
make install-dev   # pip install -e ".[all,dev]"
```

Other useful targets:

```bash
make test          # python -m unittest discover tests/ -v
make lint          # ruff check strip_comments/ tests/
make format        # ruff format strip_comments/ tests/
make coverage      # coverage run + report
make build         # python -m build
```

Run the CLI directly without installing:

```bash
python -m strip_comments.cli <file>
```

## Architecture

### Data Flow

The pipeline is: **file → parse (tree-sitter) → strip → format → output**.

1. `cli.py` collects files (glob include/exclude), reads each as UTF-8, and dispatches to `process_file`.
2. `parser.py` maps file extensions to tree-sitter grammar modules via `_EXTENSION_TO_MODULE`, lazily importing the language package. Raises `GrammarNotInstalledError` if the grammar is missing.
3. `languages.py` defines a `LanguageConfig` per extension, declaring which AST node types count as comments and docstrings. Docstring detection for Python uses a custom `_is_python_docstring` heuristic (string literal as first named child of module/block).
4. `stripper.py` walks the AST recursively, collects byte ranges of nodes matching the config's comment/docstring types, merges overlapping ranges, and reconstructs the source with those bytes removed. After removal, **blank lines are always stripped** and trailing whitespace is cleaned from all remaining lines, producing compact output. The final result ends with a single newline (or is empty string if nothing remains).
5. `compact.py` provides `compact_python`, which whitespace-compacts Python source by re-serializing the parsed AST with the stdlib `ast.unparse` (multi-line statements collapse onto single lines, **one logical statement per line** with no semicolon chaining; comments/docstrings/blank lines removed; identifiers and type annotations preserved). For `.py` files this is **default-on**; `process_file`/`process_stdin` consult `getattr(args, "compact", True)` and fall back to the tree-sitter `strip_comments` path on any exception (e.g. `SyntaxError` on invalid or newer-than-interpreter syntax). The `--no-compact` flag opts out. Non-Python files always use the tree-sitter path.
6. `formatters.py` renders results as plain text (`FileResult` with `=== path ===` headers) or JSON.

### Key Design Decisions

- **Byte-range removal, not AST-to-source**: The tool operates on raw source bytes using tree-sitter node byte offsets. It never re-serializes the AST, which preserves formatting and avoids tree-sitter limitations on round-tripping.
- **Per-language configs are declarative**: `LanguageConfig` uses sets of AST node type strings. Adding a new language means adding an entry to `_EXTENSION_TO_MODULE` in `parser.py` and `LANGUAGE_MAP` in `languages.py`.
- **Optional grammars**: Only `tree-sitter-python` is a hard dependency. All others are optional extras declared in `pyproject.toml`. The CLI gracefully skips files with missing grammars in directory mode.
- **Python compaction via stdlib `ast.unparse`**: Python whitespace compaction re-serializes the AST with `ast.unparse` rather than hand-rolling a minifier, so the output is always valid, semantically-equivalent Python (CPython's own unparser handles all whitespace-significance edge cases). Re-serialization normalizes cosmetics (string quotes, redundant parens/spacing), which is irrelevant for read-only use. This is Python-only because `ast.unparse` is Python-specific; the `args.compact` plumbing already spans all languages for a future tree-sitter continuation-line join.

## Project Configuration

- **Python**: Requires 3.13+ (ruff targets `py314`).
- **Versioning**: `setuptools_scm` generates `strip_comments/_version.py` from git tags. Do not edit `_version.py` manually.
- **Linting/Formatting**: Ruff is configured in `pyproject.toml` with line length 120, double quotes, and Google docstring convention. Excludes `tests/fixtures` and `_version.py`.
- **Testing**: Uses `unittest` (not pytest) in `tests/`. Tests cover per-language stripping, formatting, and CLI behavior.
