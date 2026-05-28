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

    def test_evaluation_summary_computes_task_and_run_metrics(self) -> None:
        evaluation = load_script(
            "evaluation_summary_script",
            "evaluation/scripts/summarize_results.py",
        )
        rows = [
            {
                "task_id": "task-1",
                "condition": "single_prompt",
                "run_id": 1,
                "passed": True,
                "validation_passed": True,
                "human_accepted": False,
                "regression": False,
                "rework_required": True,
                "requirements_traceability": False,
                "cycle_time_seconds": 100,
            },
            {
                "task_id": "task-1",
                "condition": "single_prompt",
                "run_id": 2,
                "passed": False,
                "validation_passed": False,
                "human_accepted": False,
                "regression": True,
                "rework_required": True,
                "requirements_traceability": False,
                "cycle_time_seconds": 120,
            },
            {
                "task_id": "task-1",
                "condition": "workflow_guided",
                "run_id": 1,
                "passed": True,
                "validation_passed": True,
                "human_accepted": True,
                "regression": False,
                "rework_required": False,
                "requirements_traceability": True,
                "cycle_time_seconds": 140,
            },
            {
                "task_id": "task-1",
                "condition": "workflow_guided",
                "run_id": 2,
                "passed": True,
                "validation_passed": True,
                "human_accepted": True,
                "regression": False,
                "rework_required": False,
                "requirements_traceability": True,
                "cycle_time_seconds": 150,
            },
        ]

        summary = evaluation.summarize(rows)

        self.assertEqual(summary["single_prompt"]["task_count"], 1)
        self.assertEqual(summary["single_prompt"]["run_count"], 2)
        self.assertEqual(summary["single_prompt"]["pass_at_1"], 1.0)
        self.assertEqual(summary["single_prompt"]["pass_hat_k"], 0.0)
        self.assertEqual(summary["single_prompt"]["regression_rate"], 0.5)
        self.assertEqual(summary["workflow_guided"]["pass_hat_k"], 1.0)
        self.assertEqual(summary["workflow_guided"]["human_acceptance_rate"], 1.0)
        self.assertEqual(summary["workflow_guided"]["requirements_traceability_rate"], 1.0)

    def test_evaluation_loader_rejects_missing_fields(self) -> None:
        evaluation = load_script(
            "evaluation_summary_loader_script",
            "evaluation/scripts/summarize_results.py",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            results = Path(tmp_dir) / "results.jsonl"
            results.write_text(
                json.dumps(
                    {
                        "task_id": "task-1",
                        "condition": "single_prompt",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                evaluation.load_results(results)

    def test_chart_score_mapping_uses_expected_normalization(self) -> None:
        chart = load_script(
            "evaluation_chart_scores_script",
            "evaluation/scripts/generate_chart_scores.py",
        )
        summary = {
            "single_prompt": {
                "pass_at_1": 0.6,
                "pass_hat_k": 0.4,
                "regression_rate": 0.3,
                "rework_rate": 0.5,
                "requirements_traceability_rate": 0.2,
            },
            "workflow_guided": {
                "pass_at_1": 0.8,
                "pass_hat_k": 0.7,
                "regression_rate": 0.1,
                "rework_rate": 0.2,
                "requirements_traceability_rate": 0.9,
            },
        }

        scores = chart.chart_scores(summary)

        self.assertEqual(scores["single_prompt"], [6, 4, 7, 5, 2])
        self.assertEqual(scores["workflow_guided"], [8, 7, 9, 8, 9])


if __name__ == "__main__":
    unittest.main()
