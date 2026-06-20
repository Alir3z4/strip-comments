# strip-comments

Strip comments and documentation from source files using tree-sitter.
Blank lines are removed from the output by default, producing compact, token-efficient code.
Designed for AI coding agents to read code without comment noise.

## Installation

### pip

```bash
pip install strip-comments
```

To support additional languages, install their tree-sitter grammar:

```bash
pip install tree-sitter-javascript tree-sitter-typescript
```

Or install all supported grammars at once:

```bash
pip install strip-comments[all]
```

### uv / uvx

Run without installing:

```bash
uvx strip-comments myfile.py
```

With all languages:

```bash
uvx --with strip-comments[all] strip-comments myfile.py
```

Or install as a tool:

```bash
uv tool install strip-comments
# with all languages
uv tool install strip-comments[all]
```

## Supported Languages

The following languages are supported. Only Python is required by default;
other grammars are optional dependencies.

| Language | Extension | Install Command |
|----------|-----------|-----------------|
| Python | `.py` | (included) |
| JavaScript | `.js` | `pip install tree-sitter-javascript` |
| TypeScript | `.ts` | `pip install tree-sitter-typescript` |
| TSX | `.tsx` | `pip install tree-sitter-typescript` |
| HTML | `.html` | `pip install tree-sitter-html` |
| CSS | `.css` | `pip install tree-sitter-css` |
| Go | `.go` | `pip install tree-sitter-go` |
| Rust | `.rs` | `pip install tree-sitter-rust` |
| C | `.c` | `pip install tree-sitter-c` |
| C++ | `.cpp` | `pip install tree-sitter-cpp` |
| Java | `.java` | `pip install tree-sitter-java` |
| Ruby | `.rb` | `pip install tree-sitter-ruby` |
| PHP | `.php` | `pip install tree-sitter-php` |
| Bash | `.sh` | `pip install tree-sitter-bash` |
| JSON | `.json` | `pip install tree-sitter-json` |
| Lua | `.lua` | `pip install tree-sitter-lua` |
| Swift | `.swift` | `pip install tree-sitter-swift` |
| Kotlin | `.kt` | `pip install tree-sitter-kotlin` |
| TOML | `.toml` | `pip install tree-sitter-toml` |
| Dockerfile | `.dockerfile` | `pip install tree-sitter-dockerfile` |
| C# | `.cs` | `pip install tree-sitter-c-sharp` |
| Zig | `.zig` | `pip install tree-sitter-zig` |

## Usage

Strip comments from a single file:

```bash
strip-comments myfile.py
```

Process all files in a directory:

```bash
strip-comments src/
```

Pass glob patterns directly:

```bash
strip-comments "src/**/*.py"
strip-comments "tests/test_*.py"
```

Filter by glob pattern:

```bash
strip-comments src/ --include "*.py" --exclude "test_*.py"
```

When using recursive patterns (`**`), common noise directories are automatically excluded:
`.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `venv/`, `.tox/`, `dist/`, `build/`,
`.eggs/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.idea/`, `.vscode/`, and `*.egg-info/`.

To disable this and search all directories:

```bash
strip-comments src/ --include "**/*.py" --no-default-excludes
```

Pipe source through stdin (useful for editor integrations):

```bash
cat myfile.py | strip-comments --stdin --lang py
```

Output as JSON:

```bash
strip-comments src/ --json > output.json
```

## Coding Agent Integration

Works with any agent that reads an instructions file. Add the snippet below to
`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, or your tool's equivalent:

````markdown
## Tool: strip-comments

When reading source files to explore or understand the codebase, use
`strip-comments` instead of reading the raw file. It removes comments, docstrings,
and blank lines, giving you the same code with fewer tokens.

```bash
strip-comments <file>                     # single file
strip-comments <file1> <file2> ...        # multiple files (each under a "=== path ===" header)
strip-comments <dir> --include "**/*.py"  # directory, recursive filter
strip-comments "src/**/*.py"              # glob pattern
cat <file> | strip-comments --stdin --lang py  # pipe via stdin
```

Read the raw file instead when you are about to edit it, or when the comments or
docstrings themselves are relevant — stripped output has shifted line numbers and
omits text, so it must not be used as the basis for edits.
````

## Options

- `--json` — Output as JSON instead of plain text
- `--include PATTERN` — Include files matching glob pattern
- `--exclude PATTERN` — Exclude files matching glob pattern
- `--no-default-excludes` — Do not exclude common directories
- `--stdin` — Read source from stdin (requires `--lang`)
- `-l, --lang` — Language for stdin mode (e.g. `py`, `.py`, `python`)
- `--stdin-filename` — Display name for stdin output (default: `<stdin>`)

## Development

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

Requires Python 3.13+.
