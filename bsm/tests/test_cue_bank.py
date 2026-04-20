from __future__ import annotations

import importlib
import unittest

import numpy as np

from bsm.phase02.cue_bank import (
    DEFAULT_TAU_SECONDS,
    build_cue_bank,
    compute_ild_loss_torch,
    compute_itd_loss_torch,
    smoke_cue_bank,
)


def _build_synthetic_response_pair(
    *,
    fft_size: int = 1024,
) -> tuple[np.ndarray, np.ndarray]:
    direction_count = 2
    reference_time = np.zeros((direction_count, fft_size, 2), dtype=np.float64)
    estimated_time = np.zeros_like(reference_time)

    start = 64
    reference_time[0, start, 0] = 1.00
    reference_time[0, start + 3, 1] = 0.82
    reference_time[0, start + 20, 0] = 0.28
    reference_time[0, start + 23, 1] = 0.21

    estimated_time[0, start, 0] = 0.94
    estimated_time[0, start + 2, 1] = 0.80
    estimated_time[0, start + 20, 0] = 0.25
    estimated_time[0, start + 22, 1] = 0.22

    reference_time[1, start + 12, 0] = 0.74
    reference_time[1, start + 10, 1] = 1.04
    reference_time[1, start + 28, 0] = 0.20
    reference_time[1, start + 26, 1] = 0.26

    estimated_time[1, start + 12, 0] = 0.72
    estimated_time[1, start + 11, 1] = 1.00
    estimated_time[1, start + 28, 0] = 0.18
    estimated_time[1, start + 27, 1] = 0.24

    reference_response = np.fft.rfft(reference_time, n=fft_size, axis=1).astype(np.complex64)
    estimated_response = np.fft.rfft(estimated_time, n=fft_size, axis=1).astype(np.complex64)
    return reference_response, estimated_response


class CueBankTests(unittest.TestCase):
    def test_build_cue_bank_returns_expected_shapes_and_finite_metrics(self) -> None:
        reference_response, estimated_response = _build_synthetic_response_pair()

        result = build_cue_bank(
            reference_response,
            estimated_response,
            sample_rate_hz=32000,
        )

        self.assertEqual(result.ild_ref.shape, (29, 2))
        self.assertEqual(result.ild_est.shape, (29, 2))
        self.assertEqual(result.gcc_phat_ref.shape, (2, 65))
        self.assertEqual(result.gcc_phat_est.shape, (2, 65))
        self.assertEqual(result.tau_samples, 32)
        self.assertTrue(np.isfinite(result.ild_ref).all())
        self.assertTrue(np.isfinite(result.ild_est).all())
        self.assertTrue(np.isfinite(result.gcc_phat_ref).all())
        self.assertTrue(np.isfinite(result.gcc_phat_est).all())
        self.assertGreaterEqual(result.metrics.ild_error_db, 0.0)
        self.assertGreaterEqual(result.metrics.itd_proxy_error, 0.0)

    def test_tau_window_length_follows_requested_tau(self) -> None:
        reference_response, estimated_response = _build_synthetic_response_pair()
        tau_seconds = DEFAULT_TAU_SECONDS / 2.0

        result = build_cue_bank(
            reference_response,
            estimated_response,
            sample_rate_hz=32000,
            tau_seconds=tau_seconds,
        )

        self.assertEqual(result.tau_samples, 16)
        self.assertEqual(result.gcc_phat_ref.shape[-1], 33)
        self.assertEqual(result.gcc_phat_est.shape[-1], 33)

    def test_torch_itd_loss_supports_finite_backward_pass(self) -> None:
        try:
            torch = importlib.import_module("torch")
        except Exception as exc:  # pragma: no cover - environment dependent
            self.skipTest(f"Torch is unavailable in the active environment: {exc}")
        reference_response, estimated_response = _build_synthetic_response_pair()

        reference_tensor = torch.from_numpy(reference_response)
        estimated_tensor = torch.tensor(estimated_response, requires_grad=True)

        loss, diagnostics = compute_itd_loss_torch(
            reference_tensor,
            estimated_tensor,
            sample_rate_hz=32000,
        )
        loss.backward()

        self.assertTrue(bool(torch.isfinite(loss).item()))
        self.assertEqual(int(diagnostics["tau_samples"]), 32)
        self.assertTrue(bool(torch.isfinite(diagnostics["gcc_phat_ref"]).all().item()))
        self.assertTrue(bool(torch.isfinite(diagnostics["gcc_phat_est"]).all().item()))
        self.assertIsNotNone(estimated_tensor.grad)
        self.assertTrue(bool(torch.isfinite(estimated_tensor.grad).all().item()))

    def test_torch_ild_loss_supports_finite_backward_pass(self) -> None:
        try:
            torch = importlib.import_module("torch")
        except Exception as exc:  # pragma: no cover - environment dependent
            self.skipTest(f"Torch is unavailable in the active environment: {exc}")
        reference_response, estimated_response = _build_synthetic_response_pair()

        reference_tensor = torch.from_numpy(reference_response)
        estimated_tensor = torch.tensor(estimated_response, requires_grad=True)

        loss, diagnostics = compute_ild_loss_torch(reference_tensor, estimated_tensor)
        loss.backward()

        self.assertTrue(bool(torch.isfinite(loss).item()))
        self.assertTrue(bool(torch.isfinite(diagnostics["ild_ref_db"]).all().item()))
        self.assertTrue(bool(torch.isfinite(diagnostics["ild_est_db"]).all().item()))
        self.assertIsNotNone(estimated_tensor.grad)
        self.assertTrue(bool(torch.isfinite(estimated_tensor.grad).all().item()))

    def test_smoke_report_passes_on_simple_examples(self) -> None:
        report = smoke_cue_bank(sample_rate_hz=32000)

        self.assertTrue(report["ok"])
        self.assertEqual(report["synthetic_direction_count"], 2)
        summary = report["summary"]
        self.assertEqual(summary["tau_samples"], 32)
        self.assertEqual(summary["gcc_phat_ref_shape"], [2, 65])
        self.assertTrue(summary["finite"]["ild_ref"])
        self.assertTrue(summary["finite"]["gcc_phat_est"])


if __name__ == "__main__":
    unittest.main()
