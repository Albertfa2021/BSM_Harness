from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from bsm.phase02.asset_environment import AssetBundle
from bsm.phase02.baseline_renderer import render_coefficients
from bsm.phase02.front_end_bundle import DirectionGrid, FrontEndBundle, OrientationCoefficientEntry
from bsm.phase02.residual_solver import ResidualSolverConfig
from bsm.phase02.task09_runner import (
    LOSS_PROFILES,
    NormalizedLossController,
    Task09RunConfig,
    _metric_summary,
    _select_orientation_bundle,
    compare_task09_run,
    train_task09_run,
)


def _synthetic_front_end_bundle() -> FrontEndBundle:
    rng = np.random.default_rng(901)
    frequency_count = 65
    coefficient_count = 5
    direction_count = 6
    V = (
        rng.normal(scale=0.15, size=(direction_count, frequency_count, coefficient_count))
        + 1j * rng.normal(scale=0.15, size=(direction_count, frequency_count, coefficient_count))
    ).astype(np.complex64)
    c_target = (
        rng.normal(scale=0.2, size=(frequency_count, coefficient_count, 2))
        + 1j * rng.normal(scale=0.2, size=(frequency_count, coefficient_count, 2))
    ).astype(np.complex64)
    c_ls = (c_target * 0.85).astype(np.complex64)
    c_magls = (c_target * (0.95 + 0.02j)).astype(np.complex64)
    h = np.einsum("dfm,fme->dfe", V, c_target).astype(np.complex64)
    grid = DirectionGrid(
        azimuth_deg=np.linspace(-120.0, 120.0, direction_count, dtype=np.float64),
        elevation_deg=np.zeros(direction_count, dtype=np.float64),
    )
    asset_bundle = AssetBundle(
        schema_version="1",
        interface_version="1",
        producer_task_id="test",
        producer_session_id="test",
        run_config_ref="test",
        array_id="Easycom",
        hrtf_id="KU100",
        device_atf_path="test",
        array_sh_path="test",
        hrir_path="test",
        environment_name="bsm_harness_py311",
        reference_root="test",
    )
    yaw0 = OrientationCoefficientEntry(
        yaw_deg=0,
        pitch_deg=0,
        roll_deg=0,
        c_ls=c_ls,
        c_magls=c_magls,
        c_ls_source="synthetic_yaw0_ls",
        c_magls_source="synthetic_yaw0_magls",
        coefficient_axis_semantics="[frequency, microphone, ear]",
        reference_path="synthetic_yaw0.npy",
        reference_sha256="synthetic0",
    )
    yaw90_magls = (c_magls * (0.9 + 0.05j)).astype(np.complex64)
    yaw90 = OrientationCoefficientEntry(
        yaw_deg=90,
        pitch_deg=0,
        roll_deg=0,
        c_ls=(c_ls * (0.92 + 0.01j)).astype(np.complex64),
        c_magls=yaw90_magls,
        c_ls_source="synthetic_yaw90_ls",
        c_magls_source="synthetic_yaw90_magls",
        coefficient_axis_semantics="[frequency, microphone, ear]",
        reference_path="synthetic_yaw90.npy",
        reference_sha256="synthetic90",
    )
    return FrontEndBundle(
        schema_version="1",
        interface_version="1",
        producer_task_id="test",
        producer_session_id="test",
        run_config_ref="test",
        array_id="Easycom",
        hrtf_id="KU100",
        sample_rate_hz=32000,
        fft_size=(frequency_count - 1) * 2,
        grid=grid,
        optimization_grid=grid,
        V=V,
        h=h,
        c_ls=c_ls,
        c_magls=c_magls,
        asset_bundle=asset_bundle,
        orientation_coefficients={0: yaw0, 90: yaw90},
    )


class Task09RunnerTests(unittest.TestCase):
    def test_exp0004_loss_profiles_are_registered(self) -> None:
        self.assertIn("paper_ild_guarded_v1", LOSS_PROFILES)
        self.assertIn("paper_ild_push_v1", LOSS_PROFILES)
        self.assertIn("paper_ild_push_v2", LOSS_PROFILES)

    def test_normalized_loss_controller_freezes_scales_after_warmup(self) -> None:
        controller = NormalizedLossController.from_config(
            Task09RunConfig(
                run_id="test",
                orientation_yaw_deg=90,
                seed=1,
                iterations=10,
                learning_rate=1e-3,
                loss_profile="balanced_norm_v1",
                eval_every=2,
                checkpoint_every=2,
                max_frequency_bins=None,
                max_coefficients=None,
                early_stop_patience=4,
            )
        )
        for iteration in range(3):
            controller.observe_training_losses(
                iteration,
                {"mag": 2.0, "dmag": 1.0, "ild": 0.5, "itd": 0.25, "reg": 0.1},
                device="cpu",
            )

        self.assertIsNotNone(controller.scales)
        self.assertEqual(controller.frozen_iteration, 0)
        self.assertGreater(controller.composite_score(5, {"mag": 2.0, "dmag": 1.0, "ild": 0.5, "itd": 0.25, "reg": 0.1}), 0.0)

    def test_train_task09_run_exports_required_artifacts(self) -> None:
        bundle = _synthetic_front_end_bundle()
        run_config = Task09RunConfig(
            run_id="T09-test-train",
            orientation_yaw_deg=90,
            seed=3401,
            iterations=4,
            learning_rate=2e-2,
            loss_profile="balanced_norm_v1",
            eval_every=2,
            checkpoint_every=2,
            max_frequency_bins=33,
            max_coefficients=4,
            early_stop_patience=4,
        )
        solver_config = ResidualSolverConfig(hidden_dim=12, block_count=1, rank=2)

        with tempfile.TemporaryDirectory() as tmpdir:
            report = train_task09_run(bundle, run_config=run_config, solver_config=solver_config, artifact_dir=tmpdir)

            self.assertTrue(report["ok"])
            artifact_dir = Path(tmpdir)
            self.assertTrue((artifact_dir / "run_manifest.json").exists())
            self.assertTrue((artifact_dir / "summary.json").exists())
            self.assertTrue((artifact_dir / "loss_trace.jsonl").exists())
            self.assertTrue((artifact_dir / "eval_trace.jsonl").exists())
            self.assertTrue((artifact_dir / "comparison_summary.json").exists())
            self.assertTrue((artifact_dir / "checkpoints" / "last.pt").exists())
            self.assertTrue((artifact_dir / "checkpoints" / "best_loss.pt").exists())
            self.assertTrue((artifact_dir / "checkpoints" / "best_composite.pt").exists())

    def test_train_task09_run_records_energy_descriptor_in_solver_input_summary(self) -> None:
        bundle = _synthetic_front_end_bundle()
        run_config = Task09RunConfig(
            run_id="T09-test-energy-descriptor",
            orientation_yaw_deg=90,
            seed=3401,
            iterations=2,
            learning_rate=1e-2,
            loss_profile="balanced_norm_v1",
            eval_every=1,
            checkpoint_every=1,
            max_frequency_bins=33,
            max_coefficients=4,
            early_stop_patience=4,
        )
        solver_config = ResidualSolverConfig(
            hidden_dim=12,
            block_count=1,
            rank=2,
            include_front_end_energy_descriptor=True,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            train_task09_run(bundle, run_config=run_config, solver_config=solver_config, artifact_dir=tmpdir)
            manifest = json.loads((Path(tmpdir) / "run_manifest.json").read_text(encoding="utf-8"))

            self.assertTrue(manifest["solver_config"]["include_front_end_energy_descriptor"])
            self.assertEqual(manifest["solver_input_summary"]["solver_input_packed_shape"], [33, 4, 15])
            self.assertEqual(
                manifest["solver_input_summary"]["channel_names"][-1],
                "front_end_energy_descriptor",
            )
            self.assertEqual(
                manifest["solver_input_summary"]["front_end_energy_descriptor_shape"],
                [33, 1],
            )

    def test_train_task09_run_can_resume_from_last_checkpoint(self) -> None:
        bundle = _synthetic_front_end_bundle()
        solver_config = ResidualSolverConfig(hidden_dim=12, block_count=1, rank=2)

        with tempfile.TemporaryDirectory() as tmpdir:
            first_config = Task09RunConfig(
                run_id="T09-test-resume",
                orientation_yaw_deg=90,
                seed=3401,
                iterations=2,
                learning_rate=1e-2,
                loss_profile="balanced_norm_v1",
                eval_every=1,
                checkpoint_every=1,
                max_frequency_bins=33,
                max_coefficients=4,
                early_stop_patience=4,
            )
            train_task09_run(bundle, run_config=first_config, solver_config=solver_config, artifact_dir=tmpdir)

            resumed_config = Task09RunConfig(
                run_id="T09-test-resume",
                orientation_yaw_deg=90,
                seed=3401,
                iterations=4,
                learning_rate=1e-2,
                loss_profile="balanced_norm_v1",
                eval_every=1,
                checkpoint_every=1,
                max_frequency_bins=33,
                max_coefficients=4,
                early_stop_patience=4,
            )
            train_task09_run(
                bundle,
                run_config=resumed_config,
                solver_config=solver_config,
                artifact_dir=tmpdir,
                resume_from=Path(tmpdir) / "checkpoints" / "last.pt",
            )
            summary = (Path(tmpdir) / "summary.json").read_text(encoding="utf-8")
            self.assertIn('"final_iteration": 4', summary)

    def test_compare_task09_run_rewrites_comparison_summary(self) -> None:
        bundle = _synthetic_front_end_bundle()
        run_config = Task09RunConfig(
            run_id="T09-test-compare",
            orientation_yaw_deg=90,
            seed=3401,
            iterations=2,
            learning_rate=1e-2,
            loss_profile="balanced_norm_v1",
            eval_every=1,
            checkpoint_every=1,
            max_frequency_bins=33,
            max_coefficients=4,
            early_stop_patience=4,
        )
        solver_config = ResidualSolverConfig(hidden_dim=12, block_count=1, rank=2)

        with tempfile.TemporaryDirectory() as tmpdir:
            train_task09_run(bundle, run_config=run_config, solver_config=solver_config, artifact_dir=tmpdir)
            payload = compare_task09_run(
                tmpdir,
                checkpoint_ref="best_composite",
                repo_root=Path(tmpdir),
                front_end_bundle=bundle,
            )

            self.assertIn("concise_retention_verdict", payload)
            self.assertEqual(payload["retained_run_id"], "T09-test-compare")

    def test_comparison_summary_uses_full_frequency_baseline_for_sliced_training_run(self) -> None:
        bundle = _synthetic_front_end_bundle()
        run_config = Task09RunConfig(
            run_id="T09-test-full-baseline",
            orientation_yaw_deg=90,
            seed=3401,
            iterations=2,
            learning_rate=1e-2,
            loss_profile="balanced_norm_v1",
            eval_every=1,
            checkpoint_every=1,
            max_frequency_bins=33,
            max_coefficients=4,
            early_stop_patience=4,
        )
        solver_config = ResidualSolverConfig(hidden_dim=12, block_count=1, rank=2)

        full_orientation_bundle, _ = _select_orientation_bundle(bundle, yaw_deg=90)
        baseline_response = render_coefficients(full_orientation_bundle, full_orientation_bundle.c_magls)
        expected_metrics = _metric_summary(
            full_orientation_bundle,
            baseline_response,
            producer_session_id="test",
            run_config_ref="test",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            train_task09_run(bundle, run_config=run_config, solver_config=solver_config, artifact_dir=tmpdir)
            payload = compare_task09_run(
                tmpdir,
                checkpoint_ref="best_composite",
                repo_root=Path(tmpdir),
                front_end_bundle=bundle,
            )

            magls_baseline = payload["comparison_baselines"][0]["metric_summary"]
            self.assertEqual(payload["comparison_baselines"][0]["baseline_name"], "BSM-MagLS")
            for key, expected_value in expected_metrics.items():
                self.assertAlmostEqual(magls_baseline[key], expected_value, places=6)


if __name__ == "__main__":
    unittest.main()
