"""Black-box tests for package import behavior."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EXERCISE_DIR = Path(__file__).resolve().parent


def run_python(*arguments: str) -> subprocess.CompletedProcess[str]:
    """Run Python away from the exercise directory with the package configured."""
    environment = os.environ.copy()
    existing_path = environment.get("PYTHONPATH")
    search_path = str(EXERCISE_DIR)
    if existing_path:
        search_path = os.pathsep.join((search_path, existing_path))
    environment["PYTHONPATH"] = search_path

    with tempfile.TemporaryDirectory() as working_directory:
        return subprocess.run(
            [sys.executable, *arguments],
            cwd=working_directory,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )


class TestPackageImports(unittest.TestCase):
    def assert_success(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_importing_package_is_quiet(self):
        result = run_python("-c", "import inventory_tool")

        self.assert_success(result)
        self.assertEqual(result.stdout, "")

    def test_package_runs_as_a_module(self):
        result = run_python("-m", "inventory_tool")

        self.assert_success(result)
        self.assertEqual(result.stdout, "inventory report CLI ready\n")

    def test_models_can_be_imported_first(self):
        result = run_python(
            "-c",
            "from inventory_tool.models import Inventory; "
            "from inventory_tool.reporting import Reporter; "
            'print(Inventory(("bolts", "anchors")).render(Reporter()))',
        )

        self.assert_success(result)
        self.assertEqual(result.stdout, "anchors, bolts\n")

    def test_reporting_can_be_imported_first(self):
        result = run_python(
            "-c",
            "from inventory_tool.reporting import build_report; "
            'print(build_report(["washers", "bolts"]))',
        )

        self.assert_success(result)
        self.assertEqual(result.stdout, "bolts, washers\n")

    def test_importing_cli_does_not_run_it(self):
        result = run_python(
            "-c",
            "from inventory_tool.cli import main; print(callable(main))",
        )

        self.assert_success(result)
        self.assertEqual(result.stdout, "True\n")


if __name__ == "__main__":
    unittest.main()
