from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np

from bsm.phase02.asset_environment import REQUIRED_ENVIRONMENT_NAME
from bsm.phase02.front_end_bundle import (
    DEFAULT_EVALUATION_STEP_DEG,
    REPO_ROOT,
    inspect_front_end_bundle,
    load_evaluation_grid,
    load_optimization_grid,
    resolve_front_end_bundle,
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

    def test_resolve_front_end_bundle_returns_expected_metadata(self) -> None:
        with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": REQUIRED_ENVIRONMENT_NAME}, clear=False):
            bundle = resolve_front_end_bundle(REPO_ROOT)

        self.assertEqual(bundle.array_id, "Easycom")
        self.assertEqual(bundle.hrtf_id, "KU100")
        self.assertEqual(bundle.producer_task_id, "TASK-0003")
        self.assertEqual(bundle.producer_session_id, "SESSION-P2-0004")


if __name__ == "__main__":
    unittest.main()
