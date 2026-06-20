import unittest

from strip_comments.languages import LANGUAGE_MAP
from strip_comments.parser import load_language, parse
from strip_comments.stripper import strip_comments


class TestStripper(unittest.TestCase):
    def setUp(self) -> None:
        self.lang = load_language(".py")
        self.config = LANGUAGE_MAP[".py"]

    def test_strip_line_comments(self) -> None:
        source = "x = 1  # comment\n"
        tree = parse(source, self.lang)
        result = strip_comments(tree, self.config, source)
        self.assertNotIn("# comment", result)
        self.assertIn("x = 1", result)

    def test_strip_module_docstring(self) -> None:
        source = '"""Module docstring."""\nimport os\n'
        tree = parse(source, self.lang)
        result = strip_comments(tree, self.config, source)
        self.assertNotIn("Module docstring", result)
        self.assertIn("import os", result)
        self.assertEqual(result, "import os\n")

    def test_strip_function_docstring(self) -> None:
        source = 'def foo():\n    """Docstring."""\n    pass\n'
        tree = parse(source, self.lang)
        result = strip_comments(tree, self.config, source)
        self.assertNotIn("Docstring", result)
        self.assertIn("def foo():", result)
        self.assertIn("pass", result)
        self.assertEqual(result, "def foo():\n    pass\n")

    def test_fixture_full_strip(self) -> None:
        with open("tests/fixtures/py/sample.py") as f:
            source = f.read()
        tree = parse(source, self.lang)
        result = strip_comments(tree, self.config, source)
        self.assertNotIn("Module docstring", result)
        self.assertNotIn("Function docstring", result)
        self.assertNotIn("Class docstring", result)
        self.assertNotIn("line comment", result)
        self.assertNotIn("inline comment", result)
        self.assertNotIn("method comment", result)
        self.assertIn("def hello", result)
        self.assertIn("class Greeter", result)
        self.assertIn("import os", result)
        expected = (
            "import os\n"
            "import sys\n"
            "x = 1\n"
            "def hello(name: str) -> None:\n"
            '    print(f"Hello, {name}")\n'
            "class Greeter:\n"
            "    def greet(self) -> str:\n"
            '        return "hi"\n'
        )
        self.assertEqual(result, expected)

    def test_no_blank_line_after_line_comment(self) -> None:
        source = "x = 1\n# a comment\ny = 2\n"
        tree = parse(source, self.lang)
        result = strip_comments(tree, self.config, source)
        self.assertNotIn("# a comment", result)
        self.assertEqual(result, "x = 1\ny = 2\n")

    def test_removes_blank_lines(self) -> None:
        source = "a = 1\n\nb = 2\n"
        tree = parse(source, self.lang)
        result = strip_comments(tree, self.config, source)
        self.assertEqual(result, "a = 1\nb = 2\n")

    def test_class_docstring_with_existing_blank_line(self) -> None:
        source = 'class Greeter:\n    """Class docstring."""\n\n    def greet(self):\n        pass\n'
        tree = parse(source, self.lang)
        result = strip_comments(tree, self.config, source)
        self.assertNotIn("Class docstring", result)
        self.assertIn("class Greeter:", result)
        self.assertIn("def greet(self):", result)
        expected = "class Greeter:\n    def greet(self):\n        pass\n"
        self.assertEqual(result, expected)
