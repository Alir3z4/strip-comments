import argparse
import fnmatch
import glob
import os
import sys
from pathlib import Path

from strip_comments.compact import compact_python
from strip_comments.formatters import FileResult, format_json, format_plain
from strip_comments.languages import get_language_config
from strip_comments.parser import GrammarNotInstalledError, UnsupportedExtensionError, load_language, parse
from strip_comments.stripper import strip_comments

DEFAULT_EXCLUDES = [
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    "dist",
    "build",
    ".eggs",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "*.egg-info",
]


def _is_default_excluded(path_obj: Path) -> bool:
    for part in path_obj.parts[:-1]:
        for pattern in DEFAULT_EXCLUDES:
            if fnmatch.fnmatch(part, pattern):
                return True
    return False


def _collect_files(
    directory: str, include: list[str] | None, exclude: list[str] | None, no_default_excludes: bool = False
) -> list[str]:
    dir_path = Path(directory)

    has_recursive = False
    if include:
        has_recursive = any("**" in p for p in include)

    if has_recursive:
        all_files = [str(p) for p in dir_path.rglob("*") if p.is_file()]
    else:
        all_files = [str(dir_path / entry) for entry in os.listdir(dir_path) if (dir_path / entry).is_file()]

    files = []
    for str_path in all_files:
        path_obj = Path(str_path)

        if not no_default_excludes and _is_default_excluded(path_obj):
            continue

        if include:
            matched = any(path_obj.match(p) or fnmatch.fnmatch(path_obj.name, p) for p in include)
            if not matched:
                continue

        if exclude:
            excluded = any(path_obj.match(p) or fnmatch.fnmatch(path_obj.name, p) for p in exclude)
            if excluded:
                continue

        files.append(str_path)
    return sorted(files)


def _normalize_lang(lang: str) -> str:
    """Normalize language input to a file extension."""
    lang = lang.lower().strip()
    # Handle dot-prefixed input
    if lang.startswith("."):
        return lang
    mapping = {
        "py": ".py",
        "python": ".py",
        "js": ".js",
        "javascript": ".js",
        "ts": ".ts",
        "typescript": ".ts",
        "tsx": ".tsx",
        "html": ".html",
        "css": ".css",
        "go": ".go",
        "golang": ".go",
        "rs": ".rs",
        "rust": ".rs",
        "c": ".c",
        "cpp": ".cpp",
        "c++": ".cpp",
        "java": ".java",
        "rb": ".rb",
        "ruby": ".rb",
        "php": ".php",
        "sh": ".sh",
        "bash": ".sh",
        "json": ".json",
        "lua": ".lua",
        "swift": ".swift",
        "kt": ".kt",
        "kotlin": ".kt",
        "toml": ".toml",
        "dockerfile": ".dockerfile",
        "cs": ".cs",
        "csharp": ".cs",
        "c#": ".cs",
        "zig": ".zig",
    }
    return mapping.get(lang, f".{lang}")


def process_file(path: str, args: argparse.Namespace) -> FileResult:
    _, ext = os.path.splitext(path)

    try:
        lang = load_language(ext)
    except GrammarNotInstalledError, UnsupportedExtensionError:
        with open(path, encoding="utf-8") as f:
            source = f.read()
        note = f"Stripping not available for {ext}" if ext else "Stripping not available"
        return FileResult(path=path, content=source, note=note)

    config = get_language_config(ext)

    try:
        with open(path, encoding="utf-8") as f:
            source = f.read()
    except UnicodeDecodeError as exc:
        raise ValueError(f"Binary or non-text file: {path}") from exc

    tree = parse(source, lang)

    if ext == ".py" and getattr(args, "compact", True):
        try:
            content = compact_python(source)
        except Exception:
            # Invalid Python or unsupported syntax: fall back to tree-sitter path.
            content = strip_comments(tree, config, source)
    else:
        content = strip_comments(tree, config, source)

    return FileResult(path=path, content=content)


def process_directory(path: str, args: argparse.Namespace) -> list[FileResult]:
    files = _collect_files(path, args.include, args.exclude, args.no_default_excludes)
    results = []
    for f in files:
        try:
            results.append(process_file(f, args))
        except ValueError:
            # Skip binary files silently in directory mode
            continue
    return results


def process_stdin(args: argparse.Namespace) -> FileResult:
    ext = _normalize_lang(args.lang)
    source = sys.stdin.read()

    try:
        lang = load_language(ext)
    except GrammarNotInstalledError, UnsupportedExtensionError:
        note = f"Stripping not available for {ext}" if ext else "Stripping not available"
        return FileResult(path=args.stdin_filename, content=source, note=note)

    config = get_language_config(ext)
    tree = parse(source, lang)

    if ext == ".py" and getattr(args, "compact", True):
        try:
            content = compact_python(source)
        except Exception:
            # Invalid Python or unsupported syntax: fall back to tree-sitter path.
            content = strip_comments(tree, config, source)
    else:
        content = strip_comments(tree, config, source)

    return FileResult(path=args.stdin_filename, content=content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Strip comments and documentation from source files.",
    )
    parser.add_argument("path", nargs="*", help="File(s) or directory/ies to process")
    parser.add_argument("--json", action="store_true", default=False, help="Output as JSON")
    parser.add_argument("--include", action="append", default=None, help="Include files matching glob pattern")
    parser.add_argument("--exclude", action="append", default=None, help="Exclude files matching glob pattern")
    parser.add_argument(
        "--no-default-excludes",
        action="store_true",
        default=False,
        help="Do not exclude common directories (e.g. node_modules, __pycache__, .venv)",
    )
    parser.add_argument(
        "--no-compact",
        dest="compact",
        action="store_false",
        default=True,
        help="Disable Python whitespace compaction (keep original layout)",
    )

    # Stdin support
    parser.add_argument("--stdin", action="store_true", default=False, help="Read source from stdin")
    parser.add_argument("-l", "--lang", default=None, help="Language/extension for stdin mode (e.g. py, .py, python)")
    parser.add_argument("--stdin-filename", default="<stdin>", help="Display name for stdin output")

    args = parser.parse_args(argv)

    if args.stdin:
        if not args.lang:
            print("Error: --lang is required when using --stdin", file=sys.stderr)
            return 2
        result = process_stdin(args)
        if args.json:
            print(format_json([result]))
        else:
            # For plain stdin mode, output content directly without header
            if result.note:
                print(f"-- {result.note} --")
                print()
            print(result.content, end="")
        return 0

    if not args.path:
        parser.print_help()
        return 2

    files = []
    for path in args.path:
        if os.path.exists(path):
            if os.path.isfile(path):
                files.append(path)
            else:
                files.extend(_collect_files(path, args.include, args.exclude, args.no_default_excludes))
        else:
            matched = glob.glob(path, recursive=True)
            matched_files = [p for p in matched if os.path.isfile(p)]
            if not args.no_default_excludes:
                matched_files = [p for p in matched_files if not _is_default_excluded(Path(p))]
            if matched_files:
                files.extend(matched_files)
            else:
                print(f"Error: path not found: {path}", file=sys.stderr)
                return 2

    try:
        results = []
        for f in files:
            try:
                results.append(process_file(f, args))
            except ValueError:
                # Skip binary files silently in directory/glob mode
                continue
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not results:
        return 0

    if args.json:
        print(format_json(results))
    else:
        print(format_plain(results), end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
