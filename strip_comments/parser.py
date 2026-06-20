import importlib
from typing import Any

from tree_sitter import Language, Parser


class GrammarNotInstalledError(Exception):
    def __init__(self, ext: str, package: str) -> None:
        self.ext = ext
        self.package = package
        super().__init__(f"Grammar for '{ext}' is not installed. Run: pip install {package}")


class UnsupportedExtensionError(Exception):
    """Raised when a file extension has no grammar mapping."""

    def __init__(self, ext: str) -> None:
        self.ext = ext
        super().__init__(f"Unsupported extension: {ext}. Supported: {', '.join(sorted(_EXTENSION_TO_MODULE.keys()))}")


_EXTENSION_TO_MODULE: dict[str, tuple[str, str, str]] = {
    ".py": ("tree_sitter_python", "language", "tree-sitter-python"),
    ".js": ("tree_sitter_javascript", "language", "tree-sitter-javascript"),
    ".ts": ("tree_sitter_typescript", "language_typescript", "tree-sitter-typescript"),
    ".tsx": ("tree_sitter_typescript", "language_tsx", "tree-sitter-typescript"),
    ".html": ("tree_sitter_html", "language", "tree-sitter-html"),
    ".css": ("tree_sitter_css", "language", "tree-sitter-css"),
    ".go": ("tree_sitter_go", "language", "tree-sitter-go"),
    ".rs": ("tree_sitter_rust", "language", "tree-sitter-rust"),
    ".c": ("tree_sitter_c", "language", "tree-sitter-c"),
    ".cpp": ("tree_sitter_cpp", "language", "tree-sitter-cpp"),
    ".java": ("tree_sitter_java", "language", "tree-sitter-java"),
    ".rb": ("tree_sitter_ruby", "language", "tree-sitter-ruby"),
    ".php": ("tree_sitter_php", "language_php", "tree-sitter-php"),
    ".sh": ("tree_sitter_bash", "language", "tree-sitter-bash"),
    ".json": ("tree_sitter_json", "language", "tree-sitter-json"),
    ".lua": ("tree_sitter_lua", "language", "tree-sitter-lua"),
    ".swift": ("tree_sitter_swift", "language", "tree-sitter-swift"),
    ".kt": ("tree_sitter_kotlin", "language", "tree-sitter-kotlin"),
    ".toml": ("tree_sitter_toml", "language", "tree-sitter-toml"),
    ".dockerfile": ("tree_sitter_dockerfile", "language", "tree-sitter-dockerfile"),
    ".cs": ("tree_sitter_c_sharp", "language", "tree-sitter-c-sharp"),
    ".zig": ("tree_sitter_zig", "language", "tree-sitter-zig"),
}


def load_language(ext: str) -> Any:
    if ext not in _EXTENSION_TO_MODULE:
        raise UnsupportedExtensionError(ext)
    module_name, attr_name, package_name = _EXTENSION_TO_MODULE[ext]
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise GrammarNotInstalledError(ext, package_name) from exc
    language_func = getattr(module, attr_name)
    return language_func()


def parse(source: str, language: Any) -> Any:
    if not isinstance(language, Language):
        language = Language(language)
    parser = Parser(language)
    return parser.parse(source.encode("utf-8"))
