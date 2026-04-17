from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bsm.phase02.asset_environment import (
    ARRAY_SH_GENERATION_COMMAND,
    AssetValidationError,
    DEFAULT_ARRAY_ID,
    DEFAULT_HRTF_ID,
    DEVICE_ATF_DOWNLOAD_URL,
    REQUIRED_ENVIRONMENT_NAME,
    generate_array_sh_asset,
    inspect_asset_bundle,
    resolve_asset_bundle,
)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("placeholder", encoding="utf-8")


class AssetEnvironmentTests(unittest.TestCase):
    def test_resolve_asset_bundle_success_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _touch(
                repo_root
                / "07_References/Open_Source_Baselines/Array2Binaural/origin_array_tf_data/Device_ATFs.h5"
            )
            _touch(
                repo_root
                / "07_References/Open_Source_Baselines/Array2Binaural/Easycom_array_32000Hz_o25_22samps_delay.npy"
            )
            _touch(
                repo_root
                / "07_References/Open_Source_Baselines/Array2Binaural/ku100_magls_sh_hrir/irsOrd5.wav"
            )

            with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": REQUIRED_ENVIRONMENT_NAME}, clear=False):
                bundle = resolve_asset_bundle(repo_root)

            self.assertEqual(bundle.array_id, DEFAULT_ARRAY_ID)
            self.assertEqual(bundle.hrtf_id, DEFAULT_HRTF_ID)
            self.assertEqual(bundle.environment_name, REQUIRED_ENVIRONMENT_NAME)
            self.assertTrue(bundle.device_atf_path.endswith("Device_ATFs.h5"))
            self.assertTrue(bundle.array_sh_path.endswith("Easycom_array_32000Hz_o25_22samps_delay.npy"))
            self.assertTrue(bundle.hrir_path.endswith("ku100_magls_sh_hrir/irsOrd5.wav"))

    def test_inspect_asset_bundle_reports_missing_assets_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _touch(
                repo_root
                / "07_References/Open_Source_Baselines/Array2Binaural/ku100_magls_sh_hrir/irsOrd5.wav"
            )

            with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": REQUIRED_ENVIRONMENT_NAME}, clear=False):
                report = inspect_asset_bundle(repo_root)

            self.assertFalse(report.ok)
            issue_codes = {issue.code for issue in report.issues}
            self.assertEqual(issue_codes, {"missing_array_sh", "missing_device_atf"})
            remediation_by_code = {issue.code: issue.remediation for issue in report.issues}
            self.assertIn(ARRAY_SH_GENERATION_COMMAND, remediation_by_code["missing_array_sh"] or "")
            self.assertIn(DEVICE_ATF_DOWNLOAD_URL, remediation_by_code["missing_device_atf"] or "")

    def test_resolve_asset_bundle_rejects_wrong_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            _touch(
                repo_root
                / "07_References/Open_Source_Baselines/Array2Binaural/origin_array_tf_data/Device_ATFs.h5"
            )
            _touch(
                repo_root
                / "07_References/Open_Source_Baselines/Array2Binaural/Easycom_array_32000Hz_o25_22samps_delay.npy"
            )
            _touch(
                repo_root
                / "07_References/Open_Source_Baselines/Array2Binaural/ku100_magls_sh_hrir/irsOrd5.wav"
            )

            with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": "base"}, clear=False):
                with self.assertRaises(AssetValidationError) as ctx:
                    resolve_asset_bundle(repo_root)

            self.assertIn(REQUIRED_ENVIRONMENT_NAME, str(ctx.exception))
            self.assertIn("base", str(ctx.exception))

    def test_generate_array_sh_asset_installs_scipy_compatibility_for_baseline_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            reference_root = repo_root / "07_References/Open_Source_Baselines/Array2Binaural"
            _touch(reference_root / "origin_array_tf_data/Device_ATFs.h5")
            script_path = reference_root / "encode_array_into_sh.py"
            script_path.parent.mkdir(parents=True, exist_ok=True)
            script_path.write_text(
                "\n".join(
                    [
                        "from pathlib import Path",
                        "import scipy.special as scyspecial",
                        'assert hasattr(scyspecial, "sph_harm")',
                        'Path("Easycom_array_32000Hz_o25_22samps_delay.npy").write_text("generated", encoding="utf-8")',
                    ]
                ),
                encoding="utf-8",
            )

            import scipy.special as scipy_special

            had_sph_harm = hasattr(scipy_special, "sph_harm")
            original_sph_harm = getattr(scipy_special, "sph_harm", None)
            if had_sph_harm:
                delattr(scipy_special, "sph_harm")

            try:
                generated_path, used_compat = generate_array_sh_asset(repo_root)
            finally:
                if had_sph_harm:
                    scipy_special.sph_harm = original_sph_harm
                elif hasattr(scipy_special, "sph_harm"):
                    delattr(scipy_special, "sph_harm")

            self.assertTrue(used_compat)
            self.assertTrue(generated_path.endswith("Easycom_array_32000Hz_o25_22samps_delay.npy"))
            self.assertTrue((reference_root / "Easycom_array_32000Hz_o25_22samps_delay.npy").exists())


if __name__ == "__main__":
    unittest.main()
