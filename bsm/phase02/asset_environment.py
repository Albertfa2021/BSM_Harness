from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import runpy
import sys

from .compat import install_scipy_sph_harm_compatibility


REQUIRED_ENVIRONMENT_NAME = "bsm_harness_py311"
DEFAULT_ARRAY_ID = "Easycom"
DEFAULT_HRTF_ID = "KU100"
DEFAULT_SCHEMA_VERSION = "1"
DEFAULT_INTERFACE_VERSION = "1"
DEFAULT_PRODUCER_TASK_ID = "TASK-0002"
DEFAULT_PRODUCER_SESSION_ID = "SESSION-P2-0003"
DEFAULT_RUN_CONFIG_REF = "phase02/default_asset_bundle"
DEVICE_ATF_DOWNLOAD_URL = "https://spear2022data.blob.core.windows.net/spear-data/Device_ATFs.h5"
ARRAY_SH_GENERATION_COMMAND = "python -m bsm.phase02.asset_environment generate-array-sh"


THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]
ARRAY2BINAURAL_ROOT = REPO_ROOT / "07_References" / "Open_Source_Baselines" / "Array2Binaural"


@dataclass(frozen=True)
class AssetBundle:
    schema_version: str
    interface_version: str
    producer_task_id: str
    producer_session_id: str
    run_config_ref: str
    array_id: str
    hrtf_id: str
    device_atf_path: str
    array_sh_path: str
    hrir_path: str
    environment_name: str
    reference_root: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    path: str | None = None
    remediation: str | None = None

    def to_dict(self) -> dict[str, str]:
        data = {"code": self.code, "message": self.message}
        if self.path is not None:
            data["path"] = self.path
        if self.remediation is not None:
            data["remediation"] = self.remediation
        return data


@dataclass(frozen=True)
class AssetValidationReport:
    ok: bool
    bundle: AssetBundle
    issues: tuple[ValidationIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "bundle": self.bundle.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
        }


class AssetValidationError(RuntimeError):
    def __init__(self, report: AssetValidationReport):
        self.report = report
        super().__init__(self._format_message(report))

    @staticmethod
    def _format_message(report: AssetValidationReport) -> str:
        return "\n".join(issue.message for issue in report.issues)


def resolve_environment_name() -> str:
    conda_env = os.getenv("CONDA_DEFAULT_ENV")
    if conda_env:
        return conda_env
    return Path(sys.prefix).name


def _require_phase01_defaults(array_id: str, hrtf_id: str) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    if array_id != DEFAULT_ARRAY_ID:
        issues.append(
            ValidationIssue(
                code="array_id_mismatch",
                message=(
                    f"array_id must remain {DEFAULT_ARRAY_ID} for Phase 01 invariants; "
                    f"received {array_id}."
                ),
            )
        )
    if hrtf_id != DEFAULT_HRTF_ID:
        issues.append(
            ValidationIssue(
                code="hrtf_id_mismatch",
                message=(
                    f"hrtf_id must remain {DEFAULT_HRTF_ID} for Phase 01 invariants; "
                    f"received {hrtf_id}."
                ),
            )
        )
    return tuple(issues)


def _build_bundle(
    repo_root: Path,
    environment_name: str,
    array_id: str,
    hrtf_id: str,
    producer_session_id: str,
    run_config_ref: str,
) -> AssetBundle:
    reference_root = repo_root / "07_References" / "Open_Source_Baselines" / "Array2Binaural"
    return AssetBundle(
        schema_version=DEFAULT_SCHEMA_VERSION,
        interface_version=DEFAULT_INTERFACE_VERSION,
        producer_task_id=DEFAULT_PRODUCER_TASK_ID,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
        array_id=array_id,
        hrtf_id=hrtf_id,
        device_atf_path=str(reference_root / "origin_array_tf_data" / "Device_ATFs.h5"),
        array_sh_path=str(reference_root / "Easycom_array_32000Hz_o25_22samps_delay.npy"),
        hrir_path=str(reference_root / "ku100_magls_sh_hrir" / "irsOrd5.wav"),
        environment_name=environment_name,
        reference_root=str(reference_root),
    )


def generate_array_sh_asset(
    repo_root: Path | str = REPO_ROOT,
) -> tuple[str, bool]:
    repo_root_path = Path(repo_root).resolve()
    reference_root = repo_root_path / "07_References" / "Open_Source_Baselines" / "Array2Binaural"
    device_atf_path = reference_root / "origin_array_tf_data" / "Device_ATFs.h5"
    script_path = reference_root / "encode_array_into_sh.py"
    output_path = reference_root / "Easycom_array_32000Hz_o25_22samps_delay.npy"

    if not device_atf_path.exists():
        raise FileNotFoundError(f"Required device ATF asset is missing: {device_atf_path}")
    if not script_path.exists():
        raise FileNotFoundError(f"Array2Binaural preprocessing script is missing: {script_path}")

    installed_compat = install_scipy_sph_harm_compatibility()
    previous_cwd = Path.cwd()
    previous_mpl_backend = os.environ.get("MPLBACKEND")
    os.environ["MPLBACKEND"] = "Agg"
    try:
        os.chdir(reference_root)
        runpy.run_path(str(script_path), run_name="__main__")
    finally:
        os.chdir(previous_cwd)
        if previous_mpl_backend is None:
            os.environ.pop("MPLBACKEND", None)
        else:
            os.environ["MPLBACKEND"] = previous_mpl_backend

    if not output_path.exists():
        raise FileNotFoundError(f"Expected encoded array SH asset was not created: {output_path}")
    return str(output_path), installed_compat


def inspect_asset_bundle(
    repo_root: Path | str = REPO_ROOT,
    *,
    array_id: str = DEFAULT_ARRAY_ID,
    hrtf_id: str = DEFAULT_HRTF_ID,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
) -> AssetValidationReport:
    repo_root_path = Path(repo_root).resolve()
    environment_name = resolve_environment_name()
    bundle = _build_bundle(
        repo_root_path,
        environment_name=environment_name,
        array_id=array_id,
        hrtf_id=hrtf_id,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
    )

    issues: list[ValidationIssue] = list(_require_phase01_defaults(array_id, hrtf_id))
    if environment_name != REQUIRED_ENVIRONMENT_NAME:
        issues.append(
            ValidationIssue(
                code="environment_mismatch",
                message=(
                    f"Active environment must resolve as {REQUIRED_ENVIRONMENT_NAME}; "
                    f"resolved {environment_name}."
                ),
            )
        )

    device_atf_path = Path(bundle.device_atf_path)
    if not device_atf_path.exists():
        issues.append(
            ValidationIssue(
                code="missing_device_atf",
                message=(
                    "Missing Easycom array transfer-function asset at "
                    f"{device_atf_path}."
                ),
                path=str(device_atf_path),
                remediation=(
                    "Download Device_ATFs.h5 into origin_array_tf_data/ as documented in "
                    f"Array2Binaural/README.md: {DEVICE_ATF_DOWNLOAD_URL}"
                ),
            )
        )

    array_sh_path = Path(bundle.array_sh_path)
    if not array_sh_path.exists():
        issues.append(
            ValidationIssue(
                code="missing_array_sh",
                message=(
                    "Missing encoded Easycom SH asset at "
                    f"{array_sh_path}."
                ),
                path=str(array_sh_path),
                remediation=(
                    "Generate the file with the baseline preprocessing step: "
                    f"{ARRAY_SH_GENERATION_COMMAND}"
                ),
            )
        )

    hrir_path = Path(bundle.hrir_path)
    if not hrir_path.exists():
        issues.append(
            ValidationIssue(
                code="missing_hrir",
                message=f"Missing KU100 MagLS HRIR asset at {hrir_path}.",
                path=str(hrir_path),
                remediation="Restore the imported Array2Binaural ku100_magls_sh_hrir asset tree.",
            )
        )

    return AssetValidationReport(ok=not issues, bundle=bundle, issues=tuple(issues))


def resolve_asset_bundle(
    repo_root: Path | str = REPO_ROOT,
    *,
    array_id: str = DEFAULT_ARRAY_ID,
    hrtf_id: str = DEFAULT_HRTF_ID,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
) -> AssetBundle:
    report = inspect_asset_bundle(
        repo_root=repo_root,
        array_id=array_id,
        hrtf_id=hrtf_id,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
    )
    if not report.ok:
        raise AssetValidationError(report)
    return report.bundle


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 02 asset resolver and environment validator.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command_name in ("report", "smoke"):
        subparser = subparsers.add_parser(command_name)
        subparser.add_argument("--repo-root", default=str(REPO_ROOT))
        subparser.add_argument("--array-id", default=DEFAULT_ARRAY_ID)
        subparser.add_argument("--hrtf-id", default=DEFAULT_HRTF_ID)
        subparser.add_argument("--producer-session-id", default=DEFAULT_PRODUCER_SESSION_ID)
        subparser.add_argument("--run-config-ref", default=DEFAULT_RUN_CONFIG_REF)
        subparser.add_argument("--indent", type=int, default=2)

    generate_parser = subparsers.add_parser("generate-array-sh")
    generate_parser.add_argument("--repo-root", default=str(REPO_ROOT))
    generate_parser.add_argument("--indent", type=int, default=2)

    return parser


def _run_cli() -> int:
    args = _build_parser().parse_args()
    if args.command == "generate-array-sh":
        output_path, installed_compat = generate_array_sh_asset(repo_root=args.repo_root)
        print(
            json.dumps(
                {
                    "generated_path": output_path,
                    "used_scipy_sph_harm_compatibility_shim": installed_compat,
                },
                indent=args.indent,
                sort_keys=True,
            )
        )
        return 0

    report = inspect_asset_bundle(
        repo_root=args.repo_root,
        array_id=args.array_id,
        hrtf_id=args.hrtf_id,
        producer_session_id=args.producer_session_id,
        run_config_ref=args.run_config_ref,
    )
    print(json.dumps(report.to_dict(), indent=args.indent, sort_keys=True))
    if args.command == "smoke" and not report.ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_cli())
