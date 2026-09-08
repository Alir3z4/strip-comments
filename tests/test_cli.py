import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

from strip_comments.cli import main


class TestCli(unittest.TestCase):
    def test_single_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 1  # comment\n")
            path = f.name
        try:
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([path])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertNotIn("# comment", output)
            self.assertIn("x = 1", output)
        finally:
            os.unlink(path)

    def test_file_not_found(self) -> None:
        with patch("sys.stderr", new=StringIO()) as fake_stderr:
            code = main(["/nonexistent/path.py"])
        self.assertEqual(code, 2)
        self.assertIn("not found", fake_stderr.getvalue())

    def test_directory_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "a.py"), "w") as f:
                f.write("x = 1  # comment\n")
            with open(os.path.join(tmpdir, "b.txt"), "w") as f:
                f.write("not a source file\n")

            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([tmpdir])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("a.py", output)
            self.assertIn("b.txt", output)
            self.assertIn("Stripping not available for .txt", output)
            self.assertIn("not a source file", output)

    def test_include_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test_a.py"), "w") as f:
                f.write("a = 1\n")
            with open(os.path.join(tmpdir, "other.py"), "w") as f:
                f.write("b = 2\n")

            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([tmpdir, "--include", "test_*.py"])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("test_a.py", output)
            self.assertNotIn("other.py", output)

    def test_exclude_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test_a.py"), "w") as f:
                f.write("a = 1\n")
            with open(os.path.join(tmpdir, "other.py"), "w") as f:
                f.write("b = 2\n")

            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([tmpdir, "--exclude", "test_*.py"])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertNotIn("test_a.py", output)
            self.assertIn("other.py", output)

    def test_json_output(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 1\n")
            path = f.name
        try:
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([path, "--json"])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn('"path"', output)
            self.assertIn('"content"', output)
        finally:
            os.unlink(path)

    def test_no_blank_lines_from_removed_comments(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('"""Module docstring."""\nimport os\n# comment\nx = 1\n')
            path = f.name
        try:
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([path])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("import os", output)
            self.assertIn("x = 1", output)
            self.assertNotIn("Module docstring", output)
            self.assertNotIn("# comment", output)
            # Extract content after the header.
            content = output.split(f"=== {path} ===\n\n")[1].rstrip("\n")
            self.assertEqual(content, "import os\nx = 1")
        finally:
            os.unlink(path)

    def test_multiple_files(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f1:
            f1.write("x = 1  # comment1\n")
            path1 = f1.name
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f2:
            f2.write("y = 2  # comment2\n")
            path2 = f2.name
        try:
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([path1, path2])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn(path1, output)
            self.assertIn(path2, output)
            self.assertNotIn("# comment1", output)
            self.assertNotIn("# comment2", output)
            self.assertIn("x = 1", output)
            self.assertIn("y = 2", output)
        finally:
            os.unlink(path1)
            os.unlink(path2)

    def test_glob_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test_a.py"), "w") as f:
                f.write("a = 1  # comment\n")
            with open(os.path.join(tmpdir, "test_b.py"), "w") as f:
                f.write("b = 2  # comment\n")
            with open(os.path.join(tmpdir, "other.py"), "w") as f:
                f.write("c = 3  # comment\n")

            pattern = os.path.join(tmpdir, "test_*.py")
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([pattern])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("test_a.py", output)
            self.assertIn("test_b.py", output)
            self.assertNotIn("other.py", output)
            self.assertNotIn("# comment", output)

    def test_recursive_glob_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "sub")
            os.makedirs(subdir)
            with open(os.path.join(tmpdir, "root.py"), "w") as f:
                f.write("root = 1  # comment\n")
            with open(os.path.join(subdir, "nested.py"), "w") as f:
                f.write("nested = 2  # comment\n")

            pattern = os.path.join(tmpdir, "**", "*.py")
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([pattern])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("root.py", output)
            self.assertIn("nested.py", output)
            self.assertNotIn("# comment", output)

    def test_mixed_file_and_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "dir_file.py"), "w") as f:
                f.write("dir_var = 1  # comment\n")

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write("file_var = 2  # comment\n")
                file_path = f.name

            try:
                with patch("sys.stdout", new=StringIO()) as fake_stdout:
                    code = main([file_path, tmpdir])
                self.assertEqual(code, 0)
                output = fake_stdout.getvalue()
                self.assertIn(file_path, output)
                self.assertIn("dir_file.py", output)
                self.assertNotIn("# comment", output)
            finally:
                os.unlink(file_path)

    def test_glob_no_match(self) -> None:
        with patch("sys.stderr", new=StringIO()) as fake_stderr:
            code = main(["/nonexistent/*.py"])
        self.assertEqual(code, 2)
        self.assertIn("not found", fake_stderr.getvalue())

    def test_default_excludes_recursive_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "root.py"), "w") as f:
                f.write("root = 1  # comment\n")

            node_modules = os.path.join(tmpdir, "node_modules", "pkg")
            os.makedirs(node_modules)
            with open(os.path.join(node_modules, "bad.py"), "w") as f:
                f.write("bad = 2  # comment\n")

            venv = os.path.join(tmpdir, ".venv", "lib")
            os.makedirs(venv)
            with open(os.path.join(venv, "bad.py"), "w") as f:
                f.write("bad = 3  # comment\n")

            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([tmpdir, "--include", "**/*.py"])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("root.py", output)
            self.assertNotIn("bad.py", output)
            self.assertNotIn("bad = 2", output)
            self.assertNotIn("bad = 3", output)

    def test_default_excludes_no_effect_non_recursive(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "root.py"), "w") as f:
                f.write("root = 1  # comment\n")

            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([tmpdir])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("root.py", output)

    def test_no_default_excludes_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "root.py"), "w") as f:
                f.write("root = 1  # comment\n")

            node_modules = os.path.join(tmpdir, "node_modules", "pkg")
            os.makedirs(node_modules)
            with open(os.path.join(node_modules, "inside.py"), "w") as f:
                f.write("inside = 2  # comment\n")

            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([tmpdir, "--include", "**/*.py", "--no-default-excludes"])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("root.py", output)
            self.assertIn("inside.py", output)

    def test_default_excludes_recursive_glob_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "root.py"), "w") as f:
                f.write("root = 1  # comment\n")

            node_modules = os.path.join(tmpdir, "node_modules", "pkg")
            os.makedirs(node_modules)
            with open(os.path.join(node_modules, "bad.py"), "w") as f:
                f.write("bad = 2  # comment\n")

            pattern = os.path.join(tmpdir, "**", "*.py")
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([pattern])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn("root.py", output)
            self.assertNotIn("bad.py", output)

    def test_unsupported_extension_outputs_content(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False) as f:
            f.write('key = "value"\n')
            path = f.name
        try:
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([path])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn(path, output)
            self.assertIn('key = "value"', output)
            self.assertIn("Stripping not available for .xyz", output)
        finally:
            os.unlink(path)

    def test_missing_grammar_outputs_content(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
            f.write("#!/bin/bash\n# comment\necho hello\n")
            path = f.name
        try:
            with (
                patch("sys.stdout", new=StringIO()) as fake_stdout,
                patch("strip_comments.cli.load_language") as mock_load,
            ):
                from strip_comments.parser import GrammarNotInstalledError

                mock_load.side_effect = GrammarNotInstalledError(".sh", "tree-sitter-bash")
                code = main([path])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertIn(path, output)
            self.assertIn("echo hello", output)
            self.assertIn("Stripping not available for .sh", output)
        finally:
            os.unlink(path)

    def test_unsupported_extension_json_output(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False) as f:
            f.write('key = "value"\n')
            path = f.name
        try:
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([path, "--json"])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            import json

            data = json.loads(output)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["path"], path)
            self.assertEqual(data[0]["content"], 'key = "value"\n')
            self.assertEqual(data[0]["note"], "Stripping not available for .xyz")
        finally:
            os.unlink(path)

    def test_binary_file_skipped(self) -> None:
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
            f.write(b"\x80\x81\x82\x83")
            path = f.name
        try:
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([path])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            self.assertNotIn(path, output)
        finally:
            os.unlink(path)

    def test_stdin_mode(self) -> None:
        with patch("sys.stdin", StringIO("x = 1  # comment\n")), patch("sys.stdout", new=StringIO()) as fake_stdout:
            code = main(["--stdin", "--lang", "py"])
        self.assertEqual(code, 0)
        output = fake_stdout.getvalue()
        self.assertNotIn("# comment", output)
        self.assertIn("x = 1", output)

    def test_stdin_requires_lang(self) -> None:
        with patch("sys.stderr", new=StringIO()) as fake_stderr:
            code = main(["--stdin"])
        self.assertEqual(code, 2)
        self.assertIn("--lang", fake_stderr.getvalue())

    MULTILINE_PY = (
        '"""Module docstring."""\n'
        "\n"
        "\n"
        "def make_field(\n"
        "    name: str,\n"
        "    default: int = 0,\n"
        ") -> dict:\n"
        '    """Build a field."""\n'
        "    # inline comment\n"
        "    return models.ForeignKey(\n"
        "        to=name,\n"
        "        on_delete=models.CASCADE,\n"
        "        default=default,\n"
        "    )\n"
    )

    def test_compaction_collapses_multiline_by_default(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(self.MULTILINE_PY)
            path = f.name
        try:
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([path])
            self.assertEqual(code, 0)
            content = fake_stdout.getvalue().split(f"=== {path} ===\n\n")[1]
            # The wrapped multi-arg call collapses onto a single line (no ; chaining).
            self.assertIn("return models.ForeignKey(to=name, on_delete=models.CASCADE, default=default)", content)
            self.assertNotIn(";", content)
            # Comments and docstrings are gone.
            self.assertNotIn("Module docstring", content)
            self.assertNotIn("Build a field", content)
            self.assertNotIn("inline comment", content)
            # Identifiers and type annotations are preserved.
            self.assertIn("def make_field(name: str, default: int=0) -> dict:", content)
        finally:
            os.unlink(path)

    def test_no_compact_keeps_multiline_layout(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(self.MULTILINE_PY)
            path = f.name
        try:
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([path, "--no-compact"])
            self.assertEqual(code, 0)
            content = fake_stdout.getvalue().split(f"=== {path} ===\n\n")[1]
            # Without compaction, the original multi-line layout (and spacing) is kept.
            self.assertIn("def make_field(\n", content)
            self.assertIn("    name: str,\n", content)
            self.assertIn("        on_delete=models.CASCADE,\n", content)
            # Comments and docstrings are still removed by the tree-sitter path.
            self.assertNotIn("Module docstring", content)
            self.assertNotIn("Build a field", content)
            self.assertNotIn("inline comment", content)
        finally:
            os.unlink(path)

    def test_invalid_python_falls_back_to_tree_sitter(self) -> None:
        # Syntactically-invalid Python: compaction raises, tree-sitter path takes over.
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def broken(  # comment\nx = 1\n")
            path = f.name
        try:
            with patch("sys.stdout", new=StringIO()) as fake_stdout:
                code = main([path])
            self.assertEqual(code, 0)
            output = fake_stdout.getvalue()
            # Did not raise, produced output, and stripped the comment.
            self.assertIn(path, output)
            self.assertNotIn("# comment", output)
        finally:
            os.unlink(path)

    def test_non_python_unaffected_by_compact_flag(self) -> None:
        go_source = "package main\n\n// a comment\nfunc main(\n\ta int,\n\tb int,\n) {\n}\n"
        for argv_extra in ([], ["--no-compact"]):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".go", delete=False) as f:
                f.write(go_source)
                path = f.name
            try:
                with patch("sys.stdout", new=StringIO()) as fake_stdout:
                    code = main([path, *argv_extra])
                self.assertEqual(code, 0)
                content = fake_stdout.getvalue().split(f"=== {path} ===\n\n")[1]
                # Go is never compacted: multi-line signature layout is preserved.
                self.assertIn("func main(\n", content)
                self.assertIn("\ta int,\n", content)
                self.assertNotIn("// a comment", content)
            finally:
                os.unlink(path)
