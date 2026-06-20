import json
import unittest

from strip_comments.formatters import FileResult, format_json, format_plain


class TestFormatters(unittest.TestCase):
    def test_format_plain_single_file(self) -> None:
        result = FileResult(path="test.py", content="x = 1\n")
        output = format_plain([result])
        self.assertIn("=== test.py ===", output)
        self.assertIn("x = 1", output)

    def test_format_json(self) -> None:
        result = FileResult(
            path="test.py",
            content="x = 1\n",
        )
        output = format_json([result])
        data = json.loads(output)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["path"], "test.py")

    def test_format_plain_with_note(self) -> None:
        result = FileResult(
            path="test.toml",
            content='key = "value"\n',
            note="Stripping not available for .toml",
        )
        output = format_plain([result])
        self.assertIn("=== test.toml ===", output)
        self.assertIn("-- Stripping not available for .toml --", output)
        self.assertIn('key = "value"', output)

    def test_format_json_with_note(self) -> None:
        result = FileResult(
            path="test.toml",
            content='key = "value"\n',
            note="Stripping not available for .toml",
        )
        output = format_json([result])
        data = json.loads(output)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["path"], "test.toml")
        self.assertEqual(data[0]["note"], "Stripping not available for .toml")

    def test_format_json_no_stats_field(self) -> None:
        result = FileResult(path="test.py", content="x = 1\n")
        output = format_json([result])
        data = json.loads(output)
        self.assertNotIn("stats", data[0])
