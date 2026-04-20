from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import numpy as np

from bsm.phase02.asset_environment import AssetBundle
from bsm.phase02.front_end_bundle import DirectionGrid, FrontEndBundle
from bsm.phase02.residual_solver import (
    FCRMixerResidualSolver,
    LossWeights,
    ResidualSolverConfig,
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


if __name__ == "__main__":
    unittest.main()
