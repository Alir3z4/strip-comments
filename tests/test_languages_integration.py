import os
import unittest

from strip_comments.languages import get_language_config
from strip_comments.parser import GrammarNotInstalledError, load_language, parse
from strip_comments.stripper import strip_comments


class TestLanguageIntegration(unittest.TestCase):
    def _test_fixture(self, ext: str, fixture_name: str, comment_markers: list[str]) -> None:
        config = get_language_config(ext)
        try:
            lang = load_language(ext)
        except GrammarNotInstalledError:
            self.skipTest(f"Grammar not installed for {ext}")

        fixture_path = f"tests/fixtures/{fixture_name}/sample{ext}"
        if not os.path.exists(fixture_path):
            self.skipTest(f"Fixture not found: {fixture_path}")

        with open(fixture_path, encoding="utf-8") as f:
            source = f.read()

        tree = parse(source, lang)
        result = strip_comments(tree, config, source)

        for marker in comment_markers:
            self.assertNotIn(marker, result, f"Comment marker '{marker}' still present in {ext} output")

    def test_python(self) -> None:
        self._test_fixture(".py", "py", ["# Line comment", "# inline", "Module docstring", "Function docstring"])

    def test_javascript(self) -> None:
        self._test_fixture(".js", "js", ["// Line comment", "// inline", "JSDoc comment", "block comment"])

    def test_typescript(self) -> None:
        self._test_fixture(
            ".ts",
            "ts",
            ["// TypeScript", "// function comment", "Interface documentation", "block comment"],
        )

    def test_tsx(self) -> None:
        self._test_fixture(".tsx", "tsx", ["// TSX comment", "inline block", "// inline"])

    def test_html(self) -> None:
        self._test_fixture(".html", "html", ["head comment", "body comment"])

    def test_css(self) -> None:
        self._test_fixture(".css", "css", ["Block comment", "inline comment", "Another block"])

    def test_go(self) -> None:
        self._test_fixture(".go", "go", ["// Line comment", "// inline", "block comment"])

    def test_rust(self) -> None:
        self._test_fixture(".rs", "rust", ["/// Doc comment", "// inline", "block comment"])

    def test_c(self) -> None:
        self._test_fixture(".c", "c", ["// Line comment", "inline block", "block comment"])

    def test_cpp(self) -> None:
        self._test_fixture(".cpp", "cpp", ["// Line comment", "// inline", "block comment"])

    def test_java(self) -> None:
        self._test_fixture(".java", "java", ["// Line comment", "Javadoc comment", "// inline", "block comment"])

    def test_ruby(self) -> None:
        self._test_fixture(".rb", "ruby", ["# Line comment", "# inline", "block comment"])

    def test_php(self) -> None:
        self._test_fixture(".php", "php", ["// Line comment", "// inline", "block comment"])

    def test_bash(self) -> None:
        self._test_fixture(".sh", "bash", ["# Line comment", "# inline"])

    def test_json_unchanged(self) -> None:
        config = get_language_config(".json")
        try:
            lang = load_language(".json")
        except GrammarNotInstalledError:
            self.skipTest("Grammar not installed for .json")

        with open("tests/fixtures/json/sample.json") as f:
            source = f.read()

        tree = parse(source, lang)
        result = strip_comments(tree, config, source)
        self.assertEqual(result.strip(), source.strip())
