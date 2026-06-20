import unittest

from strip_comments.parser import (
    GrammarNotInstalledError,
    UnsupportedExtensionError,
    load_language,
    parse,
)


class TestParser(unittest.TestCase):
    def test_load_python_language(self) -> None:
        lang = load_language(".py")
        self.assertIsNotNone(lang)

    def test_parse_python_source(self) -> None:
        lang = load_language(".py")
        tree = parse("def foo(): pass", lang)
        self.assertIsNotNone(tree)
        self.assertEqual(tree.root_node.type, "module")

    def test_unsupported_extension(self) -> None:
        with self.assertRaises(UnsupportedExtensionError) as ctx:
            load_language(".xyz")
        self.assertIn("Unsupported extension", str(ctx.exception))

    def test_grammar_not_installed_error_message(self) -> None:
        err = GrammarNotInstalledError(".xyz", "tree-sitter-xyz")
        self.assertIn("pip install tree-sitter-xyz", str(err))
