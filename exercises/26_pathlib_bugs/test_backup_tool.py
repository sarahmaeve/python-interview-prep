"""Tests for the backup tool.

Do NOT modify this file.  Fix the bugs in backup_tool.py until every
test passes.
"""

import tempfile
import unittest
from pathlib import Path

from backup_tool import (
    backup_path,
    build_backup_name,
    iter_source_files,
    run_backup,
)

WHEN = "20260416T120000"


# ---------------------------------------------------------------------------
# build_backup_name
# ---------------------------------------------------------------------------


class TestBuildBackupName(unittest.TestCase):
    def test_simple_suffix(self):
        self.assertEqual(
            build_backup_name(Path("notes.txt"), WHEN),
            Path(f"notes.{WHEN}.bak.txt"),
        )

    def test_compound_suffix_tar_gz(self):
        """The classic .tar.gz case — the whole compound suffix must
        survive the round trip and NOT appear in the stem."""
        self.assertEqual(
            build_backup_name(Path("archive.tar.gz"), WHEN),
            Path(f"archive.{WHEN}.bak.tar.gz"),
        )

    def test_file_with_no_suffix(self):
        self.assertEqual(
            build_backup_name(Path("dotfile"), WHEN),
            Path(f"dotfile.{WHEN}.bak"),
        )

    def test_three_suffixes(self):
        self.assertEqual(
            build_backup_name(Path("log.2025.out.gz"), WHEN),
            Path(f"log.{WHEN}.bak.2025.out.gz"),
        )


# ---------------------------------------------------------------------------
# backup_path
# ---------------------------------------------------------------------------


class TestBackupPath(unittest.TestCase):
    def test_top_level_file(self):
        result = backup_path(Path("/backup"), Path("notes.txt"), WHEN)
        self.assertEqual(result, Path(f"/backup/notes.{WHEN}.bak.txt"))

    def test_nested_file(self):
        result = backup_path(Path("/backup"), Path("docs/api/notes.txt"), WHEN)
        self.assertEqual(result,
                         Path(f"/backup/docs/api/notes.{WHEN}.bak.txt"))

    def test_destination_parent_is_under_backup_root(self):
        """The destination must live under backup_root — the source file's
        own name is not part of the directory chain."""
        result = backup_path(Path("/backup"), Path("docs/notes.txt"), WHEN)
        self.assertEqual(result.parent, Path("/backup/docs"),
                         f"parent was {result.parent!r}")


# ---------------------------------------------------------------------------
# iter_source_files
# ---------------------------------------------------------------------------


class TestIterSourceFiles(unittest.TestCase):
    def _make_source(self, td: Path) -> Path:
        """Build a small fixture:

            top.txt
            docs/a.txt
            docs/deep/b.txt
            .hidden_top.txt
            .secrets/key.pem
        """
        (td / "top.txt").write_text("top")
        (td / "docs").mkdir()
        (td / "docs" / "a.txt").write_text("a")
        (td / "docs" / "deep").mkdir()
        (td / "docs" / "deep" / "b.txt").write_text("b")
        (td / ".hidden_top.txt").write_text("hidden top")
        (td / ".secrets").mkdir()
        (td / ".secrets" / "key.pem").write_text("secret")
        return td

    def test_discovers_nested_files(self):
        with tempfile.TemporaryDirectory() as td:
            src = self._make_source(Path(td))
            rels = iter_source_files(src)

        # The nested files must all be present.
        self.assertIn(Path("top.txt"), rels)
        self.assertIn(Path("docs/a.txt"), rels)
        self.assertIn(
            Path("docs/deep/b.txt"), rels,
            "iter_source_files must recurse into nested directories",
        )

    def test_skips_hidden_top_level_files(self):
        with tempfile.TemporaryDirectory() as td:
            src = self._make_source(Path(td))
            rels = iter_source_files(src)
        self.assertNotIn(Path(".hidden_top.txt"), rels)

    def test_skips_files_inside_hidden_directories(self):
        with tempfile.TemporaryDirectory() as td:
            src = self._make_source(Path(td))
            rels = iter_source_files(src)
        self.assertNotIn(
            Path(".secrets/key.pem"), rels,
            "files inside hidden directories must be skipped too",
        )

    def test_results_are_sorted(self):
        with tempfile.TemporaryDirectory() as td:
            src = self._make_source(Path(td))
            rels = iter_source_files(src)
        self.assertEqual(rels, sorted(rels))


# ---------------------------------------------------------------------------
# run_backup (end-to-end)
# ---------------------------------------------------------------------------


class TestRunBackup(unittest.TestCase):
    def test_full_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "src"
            dest = root / "backup"
            src.mkdir()
            (src / "notes.txt").write_text("hello")
            (src / "archives").mkdir()
            (src / "archives" / "data.tar.gz").write_text("gz-content")

            written = run_backup(src, dest, when=WHEN)

            # Two files written, with the expected destination paths.
            self.assertEqual(sorted(written), [
                dest / "archives" / f"data.{WHEN}.bak.tar.gz",
                dest / f"notes.{WHEN}.bak.txt",
            ])
            # Contents preserved.
            self.assertEqual((dest / f"notes.{WHEN}.bak.txt").read_text(),
                             "hello")
            self.assertEqual(
                (dest / "archives" / f"data.{WHEN}.bak.tar.gz").read_text(),
                "gz-content")

    def test_run_backup_skips_hidden(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "src"
            dest = root / "backup"
            src.mkdir()
            (src / ".hidden.txt").write_text("secret")
            (src / "normal.txt").write_text("ok")

            written = run_backup(src, dest, when=WHEN)

            self.assertEqual(written, [dest / f"normal.{WHEN}.bak.txt"])
            self.assertFalse((dest / f".hidden.{WHEN}.bak.txt").exists())


if __name__ == "__main__":
    unittest.main()
