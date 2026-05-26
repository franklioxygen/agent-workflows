#!/usr/bin/env python3
# Function Name: load_script, TestSkillScripts
# Description: Regression tests for agent-workflows bundled skill script helpers.

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(module_name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / rel_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load script: {rel_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSkillScripts(unittest.TestCase):
    def test_validation_script_discovery_uses_validation_terms(self) -> None:
        test_inventory = load_script(
            "test_inventory_script",
            "skills/test-strategy/scripts/test_inventory.py",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "scripts": {
                            "test": "vitest",
                            "typecheck": "tsc --noEmit",
                            "e2e": "playwright test",
                            "check": "biome check .",
                            "format": "prettier --check .",
                            "contest": "node contest.js",
                        }
                    }
                ),
                encoding="utf-8",
            )

            commands = test_inventory.discover_package_commands(root)

        self.assertEqual(
            commands["npm"],
            [
                "npm run test",
                "npm run typecheck",
                "npm run e2e",
                "npm run check",
                "npm run format",
            ],
        )

    def test_pytest_requires_pytest_configuration(self) -> None:
        test_inventory = load_script(
            "test_inventory_pytest_script",
            "skills/test-strategy/scripts/test_inventory.py",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            pyproject = root / "pyproject.toml"
            pyproject.write_text("[project]\nname = 'sample'\n", encoding="utf-8")
            self.assertNotIn("python", test_inventory.discover_package_commands(root))

            pyproject.write_text("[tool.pytest.ini_options]\naddopts = '-q'\n", encoding="utf-8")
            self.assertEqual(test_inventory.discover_package_commands(root)["python"], ["pytest"])

    def test_readme_inventory_uses_markdown_link_targets(self) -> None:
        audit = load_script(
            "audit_workflow_library_script",
            "skills/workflow-maintainer/scripts/audit_workflow_library.py",
        )

        targets = audit.markdown_link_targets(
            "Text mention only: shared/safety-rules.md\n"
            "[preflight](./shared/repository-preflight.md)\n"
            "[skill](skills/test-strategy/)\n"
        )

        self.assertIn("shared/repository-preflight.md", targets)
        self.assertIn("skills/test-strategy/", targets)
        self.assertNotIn("shared/safety-rules.md", targets)

    def test_frontmatter_parser_supports_block_values(self) -> None:
        skill_common = load_script(
            "skill_common_script",
            "skills/_shared/scripts/skill_common.py",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            skill_file = Path(tmp_dir) / "SKILL.md"
            skill_file.write_text(
                "---\n"
                "name: sample\n"
                "description: |\n"
                "  First line.\n"
                "  Second line.\n"
                "---\n",
                encoding="utf-8",
            )

            metadata = skill_common.parse_frontmatter(skill_file)

        self.assertEqual(metadata["name"], "sample")
        self.assertEqual(metadata["description"], "First line.\nSecond line.")

    def test_release_validation_reports_missing_commands(self) -> None:
        release = load_script(
            "prepare_release_report_script",
            "skills/release-prep/scripts/prepare_release_report.py",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            script = root / "skills/workflow-maintainer/scripts/audit_workflow_library.py"
            script.parent.mkdir(parents=True)
            script.write_text("", encoding="utf-8")

            suggested = release.suggested_validation_commands(root)
            missing = release.missing_validation_commands(root)

        self.assertEqual(
            suggested,
            ["python3 skills/workflow-maintainer/scripts/audit_workflow_library.py"],
        )
        self.assertEqual(
            missing,
            ["python3 skills/workflow-automation/scripts/find_workflow_library.py --json"],
        )

    def test_signal_scanner_skips_source_comments(self) -> None:
        performance = load_script(
            "performance_signal_scan_script",
            "skills/performance-review/scripts/performance_signal_scan.py",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source = root / "query.py"
            source.write_text(
                "# select * from users\n"
                "query = 'select * from users'\n",
                encoding="utf-8",
            )

            report = performance.performance_signal_scan(root)

        self.assertEqual(len(report["signals"]), 1)
        self.assertEqual(report["signals"][0]["line"], 2)


if __name__ == "__main__":
    unittest.main()
