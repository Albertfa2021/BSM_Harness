from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np

from bsm.phase02.asset_environment import REQUIRED_ENVIRONMENT_NAME
from bsm.phase02.array2binaural_emagls import (
    load_saved_aligned_ypr_emagls_reference,
)
from bsm.phase02.front_end_bundle import (
    DEFAULT_EVALUATION_STEP_DEG,
    REPO_ROOT,
    SAVED_ALIGNED_YPR_MAGLS_SOURCE,
    SAME_AS_MAGLS_LS_SOURCE,
    inspect_front_end_bundle,
    load_evaluation_grid,
    load_optimization_grid,
    resolve_front_end_bundle,
    select_orientation_coefficients,
)


class FrontEndBundleTests(unittest.TestCase):
    def test_evaluation_grid_matches_equatorial_sweep_semantics(self) -> None:
        grid = load_evaluation_grid()
        self.assertEqual(grid.direction_count, 72)
        self.assertTrue(np.array_equal(grid.azimuth_deg, np.arange(-180, 180, DEFAULT_EVALUATION_STEP_DEG)))
        self.assertTrue(np.array_equal(grid.elevation_deg, np.zeros_like(grid.azimuth_deg)))

    def test_optimization_grid_matches_n_design_source_shape(self) -> None:
        grid = load_optimization_grid()
        self.assertEqual(grid.direction_count, 632)
        self.assertEqual(grid.cartesian_xyz.shape, (632, 3))

    def test_front_end_bundle_smoke_shapes_are_contract_consistent(self) -> None:
        with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": REQUIRED_ENVIRONMENT_NAME}, clear=False):
            report = inspect_front_end_bundle(REPO_ROOT)

        self.assertTrue(report.ok, msg=str(report.issues))
        bundle = report.bundle
        self.assertEqual(bundle.V.shape, (72, 513, 5))
        self.assertEqual(bundle.h.shape, (72, 513, 2))
        self.assertEqual(bundle.c_ls.shape, (513, 5, 2))
        self.assertEqual(bundle.c_magls.shape, (513, 5, 2))
        self.assertTrue(np.isfinite(bundle.V).all())
        self.assertTrue(np.isfinite(bundle.h).all())
        self.assertTrue(np.isfinite(bundle.c_ls).all())
        self.assertTrue(np.isfinite(bundle.c_magls).all())

    def test_front_end_bundle_uses_saved_array2binaural_magls_authority(self) -> None:
        with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": REQUIRED_ENVIRONMENT_NAME}, clear=False):
            bundle = resolve_front_end_bundle(REPO_ROOT)

        reference = load_saved_aligned_ypr_emagls_reference(REPO_ROOT, yaw_deg=0)
        self.assertTrue(np.array_equal(bundle.c_magls, reference))
        self.assertTrue(np.array_equal(bundle.c_ls, bundle.c_magls))
        self.assertEqual(bundle.c_magls_source, SAVED_ALIGNED_YPR_MAGLS_SOURCE)
        self.assertEqual(bundle.c_ls_source, SAME_AS_MAGLS_LS_SOURCE)
        self.assertEqual(bundle.emagls_reference_yaw_deg, 0)
        self.assertIn("emagls_32kHz_dft_aligned_ypr_0_0_0.npy", str(bundle.emagls_reference_path))

    def test_orientation_bank_selects_yaw90_saved_reference(self) -> None:
        with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": REQUIRED_ENVIRONMENT_NAME}, clear=False):
            bundle = resolve_front_end_bundle(REPO_ROOT)

        yaw0 = select_orientation_coefficients(bundle, yaw_deg=0)
        yaw90 = select_orientation_coefficients(bundle, yaw_deg=90)
        yaw90_reference = load_saved_aligned_ypr_emagls_reference(REPO_ROOT, yaw_deg=90)

        self.assertEqual(sorted(bundle.orientation_coefficients), [0, 90])
        self.assertTrue(np.array_equal(yaw0.c_magls, bundle.c_magls))
        self.assertTrue(np.array_equal(yaw90.c_magls, yaw90_reference))
        self.assertFalse(np.array_equal(yaw90.c_magls, bundle.c_magls))
        self.assertIn("emagls_32kHz_dft_aligned_ypr_90_0_0.npy", str(yaw90.reference_path))

    def test_resolve_front_end_bundle_returns_expected_metadata(self) -> None:
        with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": REQUIRED_ENVIRONMENT_NAME}, clear=False):
            bundle = resolve_front_end_bundle(REPO_ROOT)

        self.assertEqual(bundle.array_id, "Easycom")
        self.assertEqual(bundle.hrtf_id, "KU100")
        self.assertEqual(bundle.producer_task_id, "TASK-0003")
        self.assertEqual(bundle.producer_session_id, "SESSION-P2-0004")
        summary = bundle.to_summary()
        self.assertEqual(summary["c_magls_source"], SAVED_ALIGNED_YPR_MAGLS_SOURCE)
        self.assertEqual(summary["emagls_compute_sample_rate_hz"], 48000)
        self.assertEqual(summary["emagls_nfft"], 1536)
        self.assertEqual(summary["orientation_bank_yaws_deg"], [0, 90])


if __name__ == "__main__":
    unittest.main()
