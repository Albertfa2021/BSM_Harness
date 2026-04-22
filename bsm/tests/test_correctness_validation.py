from __future__ import annotations

from pathlib import Path
import importlib.util
import tempfile
import unittest

import numpy as np

from bsm.phase02.asset_environment import AssetBundle
from bsm.phase02.array2binaural_emagls import (
    build_visible_raw_array2binaural_emagls_coefficients,
    compare_emagls_to_saved_reference,
    load_saved_aligned_ypr_emagls_reference,
)
from bsm.phase02.correctness_validation import (
    canonicalize_reference_coefficients,
    coefficient_difference_metrics,
    write_listening_audio_artifacts,
)
from bsm.phase02.front_end_bundle import DirectionGrid, FrontEndBundle


def _synthetic_bundle() -> FrontEndBundle:
    frequency_count = 9
    direction_count = 4
    coefficient_count = 5
    rng = np.random.default_rng(1707)
    V = (
        rng.normal(scale=0.08, size=(direction_count, frequency_count, coefficient_count))
        + 1j * rng.normal(scale=0.08, size=(direction_count, frequency_count, coefficient_count))
    ).astype(np.complex64)
    coefficients = (
        rng.normal(scale=0.15, size=(frequency_count, coefficient_count, 2))
        + 1j * rng.normal(scale=0.15, size=(frequency_count, coefficient_count, 2))
    ).astype(np.complex64)
    h = np.einsum("dfm,fme->dfe", V, coefficients).astype(np.complex64)
    grid = DirectionGrid(
        azimuth_deg=np.array([0.0, 90.0, -90.0, -180.0], dtype=np.float64),
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
        c_ls=coefficients * 0.9,
        c_magls=coefficients,
        asset_bundle=asset_bundle,
    )


class CorrectnessValidationTests(unittest.TestCase):
    def test_canonicalize_saved_reference_axes(self) -> None:
        source = np.arange(5 * 2 * 513, dtype=np.float32).reshape(5, 2, 513)

        canonical, source_axes, canonical_axes = canonicalize_reference_coefficients(source)

        self.assertEqual(canonical.shape, (513, 5, 2))
        self.assertEqual(source_axes, "[microphone, ear, frequency]")
        self.assertEqual(canonical_axes, "[frequency, microphone, ear]")
        self.assertEqual(float(canonical[7, 3, 1].real), float(source[3, 1, 7]))
        self.assertEqual(float(canonical[7, 3, 1].imag), 0.0)

    def test_load_saved_emagls_reference_axes(self) -> None:
        coefficients = load_saved_aligned_ypr_emagls_reference(Path(__file__).resolve().parents[2], yaw_deg=0)

        self.assertEqual(coefficients.shape, (513, 5, 2))
        self.assertEqual(coefficients.dtype, np.complex64)
        self.assertTrue(np.isfinite(coefficients).all())

    @unittest.skipIf(importlib.util.find_spec("spaudiopy") is None, "spaudiopy is required for raw eMagLS build")
    def test_visible_raw_array2binaural_emagls_yaw0_is_distinguished_from_saved_aligned_ypr(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        saved = load_saved_aligned_ypr_emagls_reference(repo_root, yaw_deg=0)

        raw = build_visible_raw_array2binaural_emagls_coefficients(repo_root, yaw_deg=0)
        metrics = compare_emagls_to_saved_reference(raw, saved)

        self.assertEqual(raw.coefficients.shape, (513, 5, 2))
        self.assertGreater(metrics["mean_abs"], 0.1)
        self.assertGreater(metrics["nmse"], 1.0)

    def test_coefficient_difference_metrics_reports_worst_bins(self) -> None:
        reference = np.ones((4, 5, 2), dtype=np.complex64)
        project = reference.copy()
        project[2, :, :] += 0.5

        metrics = coefficient_difference_metrics(project, reference)

        self.assertGreater(metrics["max_abs"], 0.0)
        self.assertGreater(metrics["nmse"], 0.0)
        self.assertEqual(metrics["worst_frequency_bins"][0]["frequency_bin"], 2)
        self.assertEqual(len(metrics["by_ear"]), 2)

    def test_write_listening_audio_artifacts_exports_finite_stereo_wavs(self) -> None:
        bundle = _synthetic_bundle()
        responses = {
            "project_bsm_magls": bundle.h,
            "project_bsm_magls_yaw_0": bundle.h,
            "project_bsm_magls_yaw_90": bundle.h * 0.5,
            "array2binaural_emagls_reference_yaw_0": bundle.h,
            "array2binaural_emagls_reference_yaw_90": bundle.h,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest, entries = write_listening_audio_artifacts(Path(tmpdir), bundle, responses)

            self.assertTrue(manifest["ok"])
            self.assertEqual(len(entries), 15)
            rotation_project = [
                entry
                for entry in entries
                if entry["case"] == "rotation_90" and entry["label"] == "project_bsm_magls"
            ][0]
            self.assertEqual(rotation_project["source_response"], "project_bsm_magls_yaw_90")
            for entry in entries:
                self.assertEqual(entry["channels"], 2)
                self.assertTrue(entry["finite"])
                self.assertTrue(entry["non_clipping"])
                self.assertTrue(Path(entry["file_path"]).exists())


if __name__ == "__main__":
    unittest.main()
