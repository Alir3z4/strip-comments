import unittest

from strip_comments.compact import compact_python


class TestCompactPython(unittest.TestCase):
    def test_collapses_multiline_call(self) -> None:
        source = 'result = some_call(\n    argument_one=1,\n    argument_two=2,\n    argument_three="hello",\n)\n'
        out = compact_python(source)
        # The wrapped call collapses onto a single line; quotes are normalized.
        self.assertEqual(out, "result = some_call(argument_one=1, argument_two=2, argument_three='hello')\n")

    def test_one_statement_per_line_no_semicolons(self) -> None:
        source = "def save():\n    a = 1\n    b = 2\n    return a + b\n"
        out = compact_python(source)
        self.assertNotIn(";", out)
        self.assertEqual(out, "def save():\n    a = 1\n    b = 2\n    return a + b\n")

    def test_removes_comments_and_docstrings(self) -> None:
        source = (
            '"""Module docstring."""\n'
            "\n"
            "def foo():\n"
            '    """Function docstring."""\n'
            "    # an inline comment\n"
            "    return 1\n"
        )
        out = compact_python(source)
        self.assertNotIn("Module docstring", out)
        self.assertNotIn("Function docstring", out)
        self.assertNotIn("inline comment", out)
        self.assertEqual(out, "def foo():\n    return 1\n")

    def test_preserves_identifiers_and_annotations(self) -> None:
        source = "def greet(name: str, count: int = 3) -> str:\n    return name * count\n"
        out = compact_python(source)
        # Identifiers and type annotations survive re-serialization.
        self.assertIn("def greet(name: str, count: int=3) -> str:", out)
        self.assertIn("return name * count", out)

    def test_keeps_significant_whitespace(self) -> None:
        out = compact_python("import os\nreturn_value = os.getcwd()\n")
        self.assertIn("import os", out)
        self.assertIn("return_value = os.getcwd()", out)

    def test_ends_with_single_newline(self) -> None:
        out = compact_python("x = 1\n")
        self.assertEqual(out, "x = 1\n")
        self.assertTrue(out.endswith("\n"))
        self.assertFalse(out.endswith("\n\n"))

    def test_empty_input_returns_empty_string(self) -> None:
        self.assertEqual(compact_python(""), "")
        self.assertEqual(compact_python('"""Only a docstring."""\n'), "")

    def test_docstring_only_function_keeps_pass(self) -> None:
        # Stripping the only statement (a docstring) must keep the body valid.
        out = compact_python('def noop():\n    """just docs"""\n')
        self.assertEqual(out, "def noop():\n    pass\n")

    def test_invalid_python_raises(self) -> None:
        # Callers rely on this to trigger the tree-sitter fallback.
        with self.assertRaises(SyntaxError):
            compact_python("def broken(  :\n")


if __name__ == "__main__":
    unittest.main()
