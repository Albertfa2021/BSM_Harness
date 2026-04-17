from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np

from bsm.phase02.asset_environment import REQUIRED_ENVIRONMENT_NAME
from bsm.phase02.baseline_renderer import (
    BASELINE_NAME_LS,
    BASELINE_NAME_MAGLS,
    REPO_ROOT,
    build_baseline_render,
    render_coefficients,
    select_baseline_coefficients,
    smoke_baseline_renderer,
)
from bsm.phase02.front_end_bundle import resolve_front_end_bundle


class BaselineRendererTests(unittest.TestCase):
    def test_select_baseline_coefficients_maps_supported_names(self) -> None:
        with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": REQUIRED_ENVIRONMENT_NAME}, clear=False):
            bundle = resolve_front_end_bundle(REPO_ROOT)

        canonical_name, coefficient_field_name, coefficients = select_baseline_coefficients(bundle, "magls")
        self.assertEqual(canonical_name, BASELINE_NAME_MAGLS)
        self.assertEqual(coefficient_field_name, "c_magls")
        self.assertEqual(coefficients.shape, bundle.c_magls.shape)

    def test_render_coefficients_rejects_shape_mismatch(self) -> None:
        with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": REQUIRED_ENVIRONMENT_NAME}, clear=False):
            bundle = resolve_front_end_bundle(REPO_ROOT)

        with self.assertRaisesRegex(ValueError, "Coefficient shape mismatch"):
            render_coefficients(bundle, bundle.c_ls[:-1])

    def test_shared_renderer_accepts_ls_and_magls_without_special_casing(self) -> None:
        with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": REQUIRED_ENVIRONMENT_NAME}, clear=False):
            bundle = resolve_front_end_bundle(REPO_ROOT)

        ls_result = build_baseline_render(bundle, baseline_name=BASELINE_NAME_LS)
        magls_result = build_baseline_render(bundle, baseline_name=BASELINE_NAME_MAGLS)

        self.assertEqual(ls_result.response.shape, bundle.h.shape)
        self.assertEqual(magls_result.response.shape, bundle.h.shape)
        self.assertTrue(np.isfinite(ls_result.response).all())
        self.assertTrue(np.isfinite(magls_result.response).all())
        self.assertEqual(ls_result.coefficients.shape, magls_result.coefficients.shape)
        self.assertEqual(ls_result.coefficients.shape, bundle.c_ls.shape)

    def test_smoke_report_renders_both_baselines(self) -> None:
        with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": REQUIRED_ENVIRONMENT_NAME}, clear=False):
            report = smoke_baseline_renderer(REPO_ROOT)

        self.assertTrue(report["ok"])
        summaries = report["baseline_results"]
        self.assertEqual([summary["baseline_name"] for summary in summaries], [BASELINE_NAME_LS, BASELINE_NAME_MAGLS])
        for summary in summaries:
            self.assertEqual(summary["response_shape"], [72, 513, 2])
            self.assertTrue(summary["finite"]["response"])
            self.assertIn("nmse_to_target", summary["metrics"])


if __name__ == "__main__":
    unittest.main()
