from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

import numpy as np

from bsm.phase02.asset_environment import AssetBundle
from bsm.phase02.front_end_bundle import DirectionGrid, FrontEndBundle, OrientationCoefficientEntry
from bsm.phase02.residual_solver import (
    FCRMixerResidualSolver,
    LossWeights,
    ResidualSolverConfig,
    TASK08_PRODUCER_TASK_ID,
    build_solver_input_pack,
    compose_joint_coefficients,
    compute_loss_breakdown_torch,
    render_response_torch,
    run_short_optimization,
)


def _build_synthetic_front_end_bundle(
    *,
    frequency_count: int = 65,
    coefficient_count: int = 8,
    direction_count: int = 4,
) -> FrontEndBundle:
    rng = np.random.default_rng(1234)
    V = (
        rng.normal(scale=0.2, size=(direction_count, frequency_count, coefficient_count))
        + 1j * rng.normal(scale=0.2, size=(direction_count, frequency_count, coefficient_count))
    ).astype(np.complex64)
    c_target = (
        rng.normal(scale=0.25, size=(frequency_count, coefficient_count, 2))
        + 1j * rng.normal(scale=0.25, size=(frequency_count, coefficient_count, 2))
    ).astype(np.complex64)
    c_ls = (c_target * 0.85).astype(np.complex64)
    residual = (
        rng.normal(scale=0.04, size=(frequency_count, coefficient_count, 2))
        + 1j * rng.normal(scale=0.04, size=(frequency_count, coefficient_count, 2))
    ).astype(np.complex64)
    c_magls = (c_target + residual).astype(np.complex64)
    h = np.einsum("dfm,fme->dfe", V, c_target).astype(np.complex64)
    grid = DirectionGrid(
        azimuth_deg=np.linspace(-90.0, 90.0, direction_count, dtype=np.float64),
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
    )


def _with_synthetic_orientation_bank(bundle: FrontEndBundle) -> tuple[FrontEndBundle, OrientationCoefficientEntry]:
    yaw0 = OrientationCoefficientEntry(
        yaw_deg=0,
        pitch_deg=0,
        roll_deg=0,
        c_ls=bundle.c_ls,
        c_magls=bundle.c_magls,
        c_ls_source="synthetic_yaw0_ls",
        c_magls_source="synthetic_yaw0_magls",
        coefficient_axis_semantics="[frequency, microphone, ear]",
    )
    yaw90_c_magls = (bundle.c_magls * (0.5 + 0.25j)).astype(np.complex64)
    yaw90 = OrientationCoefficientEntry(
        yaw_deg=90,
        pitch_deg=0,
        roll_deg=0,
        c_ls=yaw90_c_magls.copy(),
        c_magls=yaw90_c_magls,
        c_ls_source="synthetic_yaw90_ls",
        c_magls_source="synthetic_yaw90_magls",
        coefficient_axis_semantics="[frequency, microphone, ear]",
        reference_path="synthetic_yaw90.npy",
        reference_sha256="synthetic",
    )
    return replace(bundle, orientation_coefficients={0: yaw0, 90: yaw90}), yaw90


class ResidualSolverTests(unittest.TestCase):
    def test_solver_input_pack_matches_channel_contract(self) -> None:
        bundle = _build_synthetic_front_end_bundle()

        solver_input_pack = build_solver_input_pack(bundle)

        self.assertEqual(solver_input_pack.solver_input_packed.shape, (65, 8, 14))
        self.assertEqual(len(solver_input_pack.channel_names), 14)
        self.assertEqual(solver_input_pack.c_magls_minus_c_ls.shape, bundle.c_magls.shape)
        self.assertTrue(np.isfinite(solver_input_pack.solver_input_packed).all())
        self.assertGreaterEqual(float(np.min(solver_input_pack.normalized_frequency_index)), 0.0)
        self.assertLessEqual(float(np.max(solver_input_pack.normalized_frequency_index)), 1.0)

    def test_solver_input_pack_includes_optional_energy_descriptor_channel(self) -> None:
        bundle = _build_synthetic_front_end_bundle()

        solver_input_pack = build_solver_input_pack(
            bundle,
            include_front_end_energy_descriptor=True,
        )

        self.assertEqual(solver_input_pack.solver_input_packed.shape, (65, 8, 15))
        self.assertEqual(len(solver_input_pack.channel_names), 15)
        self.assertEqual(solver_input_pack.channel_names[-1], "front_end_energy_descriptor")
        self.assertIsNotNone(solver_input_pack.front_end_energy_descriptor)
        self.assertTrue(np.isfinite(solver_input_pack.front_end_energy_descriptor).all())

    def test_solver_input_pack_c_magls_channels_reconstruct_coefficients(self) -> None:
        bundle = _build_synthetic_front_end_bundle()

        solver_input_pack = build_solver_input_pack(bundle)
        channels = {
            name: index
            for index, name in enumerate(solver_input_pack.channel_names)
        }
        reconstructed = np.stack(
            [
                solver_input_pack.solver_input_packed[..., channels["c_magls_left_re"]]
                + 1j * solver_input_pack.solver_input_packed[..., channels["c_magls_left_im"]],
                solver_input_pack.solver_input_packed[..., channels["c_magls_right_re"]]
                + 1j * solver_input_pack.solver_input_packed[..., channels["c_magls_right_im"]],
            ],
            axis=-1,
        ).astype(np.complex64)

        self.assertTrue(np.array_equal(solver_input_pack.c_magls, bundle.c_magls))
        self.assertTrue(np.allclose(reconstructed, bundle.c_magls))

    def test_orientation_selected_solver_input_reconstructs_selected_coefficients(self) -> None:
        bundle, yaw90 = _with_synthetic_orientation_bank(_build_synthetic_front_end_bundle())
        selected_bundle = replace(
            bundle,
            c_ls=yaw90.c_ls,
            c_magls=yaw90.c_magls,
            c_ls_source=yaw90.c_ls_source,
            c_magls_source=yaw90.c_magls_source,
        )

        solver_input_pack = build_solver_input_pack(
            selected_bundle,
            selected_orientation=yaw90.to_summary(),
            producer_task_id=TASK08_PRODUCER_TASK_ID,
        )
        channels = {
            name: index
            for index, name in enumerate(solver_input_pack.channel_names)
        }
        reconstructed = np.stack(
            [
                solver_input_pack.solver_input_packed[..., channels["c_magls_left_re"]]
                + 1j * solver_input_pack.solver_input_packed[..., channels["c_magls_left_im"]],
                solver_input_pack.solver_input_packed[..., channels["c_magls_right_re"]]
                + 1j * solver_input_pack.solver_input_packed[..., channels["c_magls_right_im"]],
            ],
            axis=-1,
        ).astype(np.complex64)

        self.assertEqual(solver_input_pack.producer_task_id, TASK08_PRODUCER_TASK_ID)
        self.assertEqual(solver_input_pack.selected_orientation["yaw_deg"], 90)
        self.assertTrue(np.array_equal(solver_input_pack.c_magls, yaw90.c_magls))
        self.assertTrue(np.allclose(reconstructed, yaw90.c_magls))
        self.assertFalse(np.array_equal(reconstructed, bundle.c_magls))

    def test_solver_forward_and_loss_support_finite_backward_pass(self) -> None:
        import torch

        bundle = _build_synthetic_front_end_bundle()
        solver_input_pack = build_solver_input_pack(bundle)
        solver = FCRMixerResidualSolver(
            solver_input_pack.solver_input_packed.shape[-1],
            ResidualSolverConfig(hidden_dim=12, block_count=1, rank=2),
        )
        solver_input = torch.as_tensor(solver_input_pack.solver_input_packed, dtype=torch.float32)
        c_magls = torch.as_tensor(bundle.c_magls, dtype=torch.complex64)

        delta_c, alpha = solver(solver_input)
        c_joint = compose_joint_coefficients(c_magls, delta_c, alpha)
        response_joint = render_response_torch(bundle, c_joint)
        loss_total, breakdown = compute_loss_breakdown_torch(
            bundle,
            c_joint=c_joint,
            delta_c=delta_c,
            weights=LossWeights(),
        )
        loss_total.backward()

        self.assertEqual(tuple(delta_c.shape), tuple(bundle.c_magls.shape))
        self.assertEqual(tuple(response_joint.shape), tuple(bundle.h.shape))
        self.assertTrue(bool(torch.isfinite(loss_total).item()))
        self.assertTrue(bool(torch.isfinite(breakdown["loss_itd"]).item()))
        self.assertTrue(all(param.grad is None or bool(torch.isfinite(param.grad).all().item()) for param in solver.parameters()))

    def test_short_optimization_exports_summary_and_reduces_loss(self) -> None:
        bundle = _build_synthetic_front_end_bundle()

        with tempfile.TemporaryDirectory() as tmpdir:
            export = run_short_optimization(
                bundle,
                iterations=6,
                learning_rate=2e-2,
                solver_config=ResidualSolverConfig(hidden_dim=12, block_count=1, rank=2),
                artifact_dir=Path(tmpdir),
                max_frequency_bins=None,
                max_coefficients=None,
            )

            self.assertTrue(export.loss_reduced)
            self.assertLess(export.final_loss_total, export.initial_loss_total)
            self.assertTrue(Path(export.loss_trace_path).exists())
            self.assertTrue(Path(export.artifact_refs["summary"]).exists())
            self.assertIn("ild_error", export.to_dict())
            self.assertIn("itd_proxy_error", export.to_dict())
            self.assertIn("normalized_magnitude_error", export.to_dict())
            self.assertIn("nmse", export.to_dict())

    def test_short_optimization_exports_orientation_metadata(self) -> None:
        bundle, _ = _with_synthetic_orientation_bank(_build_synthetic_front_end_bundle())

        with tempfile.TemporaryDirectory() as tmpdir:
            export = run_short_optimization(
                bundle,
                iterations=1,
                learning_rate=1e-2,
                solver_config=ResidualSolverConfig(hidden_dim=12, block_count=1, rank=2),
                artifact_dir=Path(tmpdir),
                max_frequency_bins=None,
                max_coefficients=None,
                orientation_yaw_deg=90,
                producer_task_id=TASK08_PRODUCER_TASK_ID,
            )

            self.assertEqual(export.producer_task_id, TASK08_PRODUCER_TASK_ID)
            self.assertEqual(export.selected_orientation["yaw_deg"], 90)
            self.assertEqual(export.solver_input_summary["selected_orientation"]["yaw_deg"], 90)
            self.assertEqual(export.orientation_bank_yaws_deg, [0, 90])
            self.assertTrue(export.task09_ready)
            self.assertEqual(export.blocking_issues, [])


if __name__ == "__main__":
    unittest.main()
