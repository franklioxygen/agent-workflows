#!/usr/bin/env python3
# Function Name: load_script, TestSkillScripts
# Description: Regression tests for agent-workflows bundled skill script helpers.

from __future__ import annotations

import importlib.util
import json
import random
import argparse
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

    def test_evaluation_summary_computes_per_condition_blocks(self) -> None:
        evaluation = load_script(
            "evaluation_summary_script",
            "evaluation/scripts/summarize_results.py",
        )
        env = {
            "model_provider": "test-provider",
            "model_id": "test-model",
            "model_parameters": {"temperature": 0.2, "top_p": 1.0, "seed": None},
            "repo_sha": "deadbeef",
            "tool_access": ["read", "edit"],
            "time_budget_seconds": 600,
            "prompt_template_version": "v1",
            "agent_harness_version": "test-harness",
            "kit_version": "2.1.0",
        }
        base = {
            "env": env,
            "artifact_path": "x",
            "blinded_artifact_path": "y",
            "adjudicated": False,
            "rater_ids": ["r1", "r2"],
        }
        rows = [
            {**base, "task_id": "t1", "condition": "single_prompt", "run_id": 1, "run_order": 1,
             "passed": True, "validation_passed": True, "human_accepted": False,
             "regression": False, "rework_required": True, "requirements_traceability": False,
             "cycle_time_seconds": 100},
            {**base, "task_id": "t1", "condition": "single_prompt", "run_id": 2, "run_order": 2,
             "passed": False, "validation_passed": False, "human_accepted": False,
             "regression": True, "rework_required": True, "requirements_traceability": False,
             "cycle_time_seconds": 120},
            {**base, "task_id": "t1", "condition": "workflow_guided", "run_id": 1, "run_order": 3,
             "passed": True, "validation_passed": True, "human_accepted": True,
             "regression": False, "rework_required": False, "requirements_traceability": True,
             "cycle_time_seconds": 140},
            {**base, "task_id": "t1", "condition": "workflow_guided", "run_id": 2, "run_order": 4,
             "passed": True, "validation_passed": True, "human_accepted": True,
             "regression": False, "rework_required": False, "requirements_traceability": True,
             "cycle_time_seconds": 150},
        ]

        summary = evaluation.summarize(rows, bootstrap_resamples=200, permutation_resamples=200)

        sp = summary["conditions"]["single_prompt"]
        wg = summary["conditions"]["workflow_guided"]
        self.assertEqual(sp["task_count"], 1)
        self.assertEqual(sp["run_count"], 2)
        self.assertEqual(sp["task_pass_rate"]["point"], 0.5)
        self.assertEqual(sp["reliable_pass_at_k"]["point"], 0.0)
        self.assertEqual(sp["clean_pass_rate"]["point"], 0.0)
        self.assertEqual(sp["regression_free_rate"]["point"], 0.5)
        self.assertNotIn("pass_at_1", sp)
        self.assertNotIn("validation_pass_rate", sp)
        self.assertNotIn("human_acceptance_rate", sp)
        self.assertNotIn("traceability_rate", sp)
        self.assertNotIn("median_cycle_time_seconds", sp)
        self.assertEqual(wg["task_pass_rate"]["point"], 1.0)
        self.assertEqual(wg["reliable_pass_at_k"]["point"], 1.0)
        self.assertEqual(wg["clean_pass_rate"]["point"], 1.0)
        self.assertTrue(summary["power_warning"])

    def test_evaluation_rfr_uses_locked_evaluator_checks_when_present(self) -> None:
        evaluation = load_script(
            "evaluation_locked_rfr_script",
            "evaluation/scripts/summarize_results.py",
        )
        env = {
            "model_provider": "test-provider",
            "model_id": "test-model",
            "model_parameters": {"temperature": 0.2, "top_p": 1.0, "seed": None},
            "repo_sha": "deadbeef",
            "tool_access": ["read", "edit"],
            "time_budget_seconds": 600,
            "prompt_template_version": "v1",
            "agent_harness_version": "test-harness",
            "kit_version": "2.1.0",
        }
        base = {
            "env": env,
            "artifact_path": "x",
            "blinded_artifact_path": "y",
            "adjudicated": False,
            "rater_ids": ["r1", "r2"],
            "passed": True,
            "validation_passed": True,
            "human_accepted": True,
            "regression": False,
            "rework_required": False,
            "requirements_traceability": True,
            "cycle_time_seconds": 100,
        }
        rows = [
            {**base, "task_id": "t1", "condition": "single_prompt", "run_id": 1, "run_order": 1,
             "hidden_validation_passed": False},
            {**base, "task_id": "t1", "condition": "single_prompt", "run_id": 2, "run_order": 2,
             "hidden_validation_passed": True},
            {**base, "task_id": "t1", "condition": "workflow_guided", "run_id": 1, "run_order": 3,
             "hidden_validation_passed": True},
            {**base, "task_id": "t1", "condition": "workflow_guided", "run_id": 2, "run_order": 4,
             "hidden_validation_passed": True},
        ]

        summary = evaluation.summarize(rows, bootstrap_resamples=200, permutation_resamples=200)

        self.assertEqual(
            summary["conditions"]["single_prompt"]["regression_free_rate"]["point"],
            0.5,
        )
        self.assertEqual(
            summary["conditions"]["workflow_guided"]["regression_free_rate"]["point"],
            1.0,
        )
        self.assertEqual(summary["warnings"].count(""), 0)

    def test_evaluation_loader_rejects_missing_env(self) -> None:
        evaluation = load_script(
            "evaluation_summary_loader_script",
            "evaluation/scripts/summarize_results.py",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            results = Path(tmp_dir) / "results.jsonl"
            results.write_text(
                json.dumps(
                    {
                        "task_id": "t1", "condition": "single_prompt", "run_id": 1, "run_order": 1,
                        "env": {"model_id": "m"},
                        "artifact_path": "a", "blinded_artifact_path": "b",
                        "passed": True, "validation_passed": True, "human_accepted": True,
                        "regression": False, "rework_required": False, "requirements_traceability": True,
                        "cycle_time_seconds": 1, "adjudicated": False, "rater_ids": ["r1", "r2"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                evaluation.load_results(results)

    def test_evaluation_loader_requires_two_rater_ids(self) -> None:
        evaluation = load_script(
            "evaluation_summary_rater_ids_script",
            "evaluation/scripts/summarize_results.py",
        )
        env = {
            "model_provider": "test-provider",
            "model_id": "test-model",
            "model_parameters": {"temperature": 0.2, "top_p": 1.0, "seed": None},
            "repo_sha": "deadbeef",
            "tool_access": ["read", "edit"],
            "time_budget_seconds": 600,
            "prompt_template_version": "v1",
            "agent_harness_version": "test-harness",
            "kit_version": "2.1.0",
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            results = Path(tmp_dir) / "results.jsonl"
            results.write_text(
                json.dumps(
                    {
                        "task_id": "t1", "condition": "single_prompt", "run_id": 1, "run_order": 1,
                        "env": env,
                        "artifact_path": "a", "blinded_artifact_path": "b",
                        "passed": True, "validation_passed": True, "human_accepted": True,
                        "regression": False, "rework_required": False, "requirements_traceability": True,
                        "cycle_time_seconds": 1, "adjudicated": False, "rater_ids": ["r1"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                evaluation.load_results(results)

    def test_cohens_kappa_handles_perfect_and_partial_agreement(self) -> None:
        evaluation = load_script(
            "evaluation_kappa_script",
            "evaluation/scripts/summarize_results.py",
        )
        self.assertEqual(evaluation.cohens_kappa([(1, 1), (0, 0), (1, 1)]), 1.0)
        kappa = evaluation.cohens_kappa([(1, 1), (1, 0), (0, 0), (0, 1)])
        self.assertAlmostEqual(kappa, 0.0, places=6)
        self.assertEqual(evaluation.cohens_kappa([(1, 1), (1, 1)]), 1.0)

    def test_rotating_raters_report_fleiss_kappa_and_raw_agreement(self) -> None:
        evaluation = load_script(
            "evaluation_fleiss_script",
            "evaluation/scripts/summarize_results.py",
        )
        rater_rows = [
            {"task_id": "t1", "condition": "single_prompt", "run_id": 1, "rater_id": "r1",
             "passed": True, "validation_passed": True, "human_accepted": True,
             "regression": False, "rework_required": False, "requirements_traceability": True},
            {"task_id": "t1", "condition": "single_prompt", "run_id": 1, "rater_id": "r2",
             "passed": True, "validation_passed": True, "human_accepted": True,
             "regression": False, "rework_required": False, "requirements_traceability": True},
            {"task_id": "t2", "condition": "single_prompt", "run_id": 1, "rater_id": "r2",
             "passed": False, "validation_passed": True, "human_accepted": True,
             "regression": False, "rework_required": False, "requirements_traceability": True},
            {"task_id": "t2", "condition": "single_prompt", "run_id": 1, "rater_id": "r3",
             "passed": True, "validation_passed": True, "human_accepted": True,
             "regression": False, "rework_required": False, "requirements_traceability": True},
        ]

        items = evaluation.reliability_items_for_outcome(
            rater_rows, "passed", "single_prompt"
        )
        method, kappa = evaluation.reliability_value(items)
        reliability = evaluation.reliability_with_ci(
            items, resamples=20, rng=random.Random(1)
        )

        self.assertEqual(method, "fleiss_kappa")
        self.assertIsNotNone(kappa)
        self.assertEqual(reliability["agreement_rate"], 0.5)
        self.assertEqual(reliability["positive_rate"], 0.75)

    def test_holm_bonferroni_step_down_thresholds(self) -> None:
        evaluation = load_script(
            "evaluation_holm_script",
            "evaluation/scripts/summarize_results.py",
        )
        result = evaluation.holm_bonferroni(
            {"a": 0.01, "b": 0.04, "c": 0.20}, alpha=0.05
        )
        self.assertTrue(result["a"]["rejected"])
        self.assertFalse(result["b"]["rejected"])
        self.assertFalse(result["c"]["rejected"])

    def test_chart_score_mapping_uses_honest_metric_labels(self) -> None:
        chart = load_script(
            "evaluation_chart_scores_script",
            "evaluation/scripts/generate_chart_scores.py",
        )
        summary = {
            "conditions": {
                "single_prompt": {
                    "task_pass_rate": {"point": 0.6},
                    "reliable_pass_at_k": {"point": 0.4},
                    "clean_pass_rate": {"point": 0.3},
                    "regression_free_rate": {"point": 0.7},
                    "no_rework_rate": {"point": 0.5},
                },
                "workflow_guided": {
                    "task_pass_rate": {"point": 0.8},
                    "reliable_pass_at_k": {"point": 0.7},
                    "clean_pass_rate": {"point": 0.6},
                    "regression_free_rate": {"point": 0.9},
                    "no_rework_rate": {"point": 0.8},
                },
            }
        }

        scores = chart.chart_scores(summary)

        self.assertEqual(scores["single_prompt"], [6, 4, 3, 7, 5])
        self.assertEqual(scores["workflow_guided"], [8, 7, 6, 9, 8])

    def test_chart_svg_renderer_uses_scores(self) -> None:
        chart = load_script(
            "evaluation_chart_svg_script",
            "evaluation/scripts/generate_chart_scores.py",
        )

        svg = chart.render_svg(
            {
                "single_prompt": [7, 3, 7, 3, 0],
                "workflow_guided": [10, 10, 10, 10, 10],
            },
            title="Measured Outcome Comparison",
            subtitle="Generated by test",
            y_label="Score",
            description="Test chart",
        )

        self.assertIn("<title id=\"title\">Measured Outcome Comparison</title>", svg)
        self.assertIn(">TPR<", svg)
        self.assertIn(">RP@k<", svg)
        self.assertIn(">CPR<", svg)
        self.assertIn(">RFR<", svg)
        self.assertIn(">NRR<", svg)
        self.assertNotIn(">HAR<", svg)
        self.assertNotIn(">TR<", svg)
        self.assertNotIn(">Pass@1<", svg)
        self.assertNotIn(">Validation<", svg)
        self.assertNotIn(">Human Accept<", svg)
        self.assertNotIn(">Median Cycle Time<", svg)
        self.assertIn('y="124" text-anchor="middle">10</text>', svg)
        self.assertIn(">10<", svg)

    def test_claude_runner_builds_plan_prompt_and_dry_run_artifacts(self) -> None:
        runner = load_script(
            "evaluation_claude_runner_script",
            "evaluation/scripts/run_claude_code_study.py",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source_repo = root / "repo"
            source_repo.mkdir()
            (source_repo / "README.md").write_text("sample\n", encoding="utf-8")
            tasks_path = root / "tasks.json"
            tasks_path.write_text(
                json.dumps(
                    {
                        "tasks": [
                            {
                                "task_id": "doc-001",
                                "category": "bug-fix",
                                "difficulty": "S",
                                "prompt": "Keep the README present.",
                                "brief_prompt": "README is missing from the package.",
                                "acceptance_criteria": ["README.md exists."],
                                "validation_commands": [
                                    "python3 -c \"from pathlib import Path; assert Path('README.md').exists()\""
                                ],
                                "hidden_validation_commands": [
                                    "python3 -c \"from pathlib import Path; assert Path('README.md').read_text() == 'sample\\n'\""
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            tasks = runner.load_task_manifest(tasks_path)
            plan = runner.build_run_plan(
                tasks,
                runs_per_condition=1,
                conditions=("single_prompt", "workflow_guided"),
                seed=1,
            )
            prompt = runner.build_prompt(
                tasks[0],
                condition="workflow_guided",
                workflow_root=ROOT,
            )
            lift_single_prompt = runner.build_prompt(
                tasks[0],
                condition="single_prompt",
                workflow_root=ROOT,
                prompt_mode="workflow-lift",
            )
            lift_workflow_prompt = runner.build_prompt(
                tasks[0],
                condition="workflow_guided",
                workflow_root=ROOT,
                prompt_mode="workflow-lift",
            )

            self.assertEqual(len(plan), 2)
            self.assertIn("bug-fix-agent-workflow.md", prompt)
            self.assertIn("Issue report", lift_single_prompt)
            self.assertNotIn("Acceptance criteria", lift_single_prompt)
            self.assertIn("Acceptance criteria", lift_workflow_prompt)
            self.assertIn("Requirements Traceability", lift_workflow_prompt)

            output_dir = root / "study"
            args = argparse.Namespace(
                allow_dirty_source=True,
                dry_run=True,
                claude_bin="claude",
                model="sonnet",
                allowed_tools="Read,Edit,Write,Bash",
                permission_mode="bypassPermissions",
                max_budget_usd=None,
                time_budget_seconds=30,
                validation_timeout_seconds=30,
                prompt_mode="controlled",
            )
            env = {
                "model_provider": "anthropic",
                "model_id": "sonnet",
                "model_parameters": {},
                "repo_sha": "non-git",
                "tool_access": ["Read", "Edit", "Write", "Bash"],
                "time_budget_seconds": 30,
                "prompt_template_version": "test",
                "agent_harness_version": runner.HARNESS_VERSION,
                "kit_version": "2.1.0",
            }

            row = runner.run_one_plan_item(
                plan[0],
                args=args,
                source_repo=source_repo,
                workflow_root=ROOT,
                output_dir=output_dir,
                env=env,
            )

            self.assertTrue(row["validation_passed"])
            self.assertTrue(row["public_validation_passed"])
            self.assertTrue(row["hidden_validation_passed"])
            self.assertTrue(row["needs_blinded_scoring"])
            self.assertTrue(Path(row["artifact_path"], "validation.log").exists())
            self.assertTrue(Path(row["artifact_path"], "agent_report.txt").exists())
            self.assertTrue(Path(row["blinded_artifact_path"]).exists())
            self.assertTrue((output_dir / "runs.jsonl").exists())

    def test_build_results_from_ratings_requires_adjudication_for_disagreements(self) -> None:
        builder = load_script(
            "evaluation_build_results_script",
            "evaluation/scripts/build_results_from_ratings.py",
        )
        env = {
            "model_provider": "anthropic",
            "model_id": "sonnet",
            "model_parameters": {},
            "repo_sha": "abc123",
            "tool_access": ["Read"],
            "time_budget_seconds": 30,
            "prompt_template_version": "test",
            "agent_harness_version": "test",
            "kit_version": "2.1.0",
        }
        run_rows = [
            {
                "task_id": "t1",
                "condition": "single_prompt",
                "workflow": None,
                "run_id": 1,
                "run_order": 1,
                "env": env,
                "artifact_path": "artifact",
                "blinded_artifact_path": "blinded",
                "public_validation_passed": True,
                "hidden_validation_passed": False,
                "cycle_time_seconds": 10,
            }
        ]
        base = {
            "task_id": "t1",
            "condition": "single_prompt",
            "run_id": 1,
            "validation_passed": True,
            "human_accepted": True,
            "regression": False,
            "rework_required": False,
            "requirements_traceability": False,
        }
        rater_rows = [
            {**base, "rater_id": "r1", "passed": True},
            {**base, "rater_id": "r2", "passed": False},
        ]

        with self.assertRaises(ValueError):
            builder.merge_run_and_rater_rows(run_rows, rater_rows)

        results = builder.merge_run_and_rater_rows(
            run_rows,
            rater_rows,
            [{**base, "passed": True, "adjudication_notes": "r1 rationale accepted"}],
        )

        self.assertTrue(results[0]["passed"])
        self.assertTrue(results[0]["adjudicated"])
        self.assertEqual(results[0]["rater_ids"], ["r1", "r2"])
        self.assertTrue(results[0]["public_validation_passed"])
        self.assertFalse(results[0]["hidden_validation_passed"])


if __name__ == "__main__":
    unittest.main()
