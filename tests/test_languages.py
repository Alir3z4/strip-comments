import unittest

from strip_comments.languages import LANGUAGE_MAP, get_language_config


class TestLanguages(unittest.TestCase):
    def test_all_languages_registered(self) -> None:
        expected = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".html",
            ".css",
            ".go",
            ".rs",
            ".c",
            ".cpp",
            ".java",
            ".rb",
            ".php",
            ".sh",
            ".json",
            ".lua",
            ".swift",
            ".kt",
            ".toml",
            ".dockerfile",
            ".cs",
            ".zig",
        }
        self.assertEqual(set(LANGUAGE_MAP.keys()), expected)

    def test_python_has_docstring_detector(self) -> None:
        config = LANGUAGE_MAP[".py"]
        self.assertIsNotNone(config.docstring_detector)

    def test_unknown_extension_fallback(self) -> None:
        config = get_language_config(".xyz")
        self.assertEqual(config.comment_types, {"comment"})
        self.assertEqual(config.docstring_types, set())

    def test_javascript_config(self) -> None:
        config = LANGUAGE_MAP[".js"]
        self.assertEqual(config.comment_types, {"comment"})

    def test_rust_config(self) -> None:
        config = LANGUAGE_MAP[".rs"]
        self.assertEqual(config.comment_types, {"line_comment", "block_comment"})
