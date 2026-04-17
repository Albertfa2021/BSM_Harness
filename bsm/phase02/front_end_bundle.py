from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
import scipy.signal as signal
import soundfile

from .asset_environment import (
    DEFAULT_ARRAY_ID,
    DEFAULT_HRTF_ID,
    DEFAULT_INTERFACE_VERSION,
    DEFAULT_SCHEMA_VERSION,
    REPO_ROOT,
    AssetBundle,
    resolve_asset_bundle,
)
from .compat import install_scipy_sph_harm_compatibility


DEFAULT_PRODUCER_TASK_ID = "TASK-0003"
DEFAULT_PRODUCER_SESSION_ID = "SESSION-P2-0004"
DEFAULT_RUN_CONFIG_REF = "phase02/default_front_end_bundle"
DEFAULT_SAMPLE_RATE_HZ = 32000
DEFAULT_FFT_SIZE = 1024
DEFAULT_MAGLS_F_CUT_HZ = 2000.0
DEFAULT_OPTIMIZATION_GRID_N_DESIGN = 35
DEFAULT_EVALUATION_STEP_DEG = 5
DEFAULT_ARRAY_SH_DELAY_SAMPLES = 22
DEFAULT_HRTF_ORDER = 5
DEFAULT_ARRAY_ORDER = 25


@dataclass(frozen=True)
class DirectionGrid:
    azimuth_deg: np.ndarray
    elevation_deg: np.ndarray
    cartesian_xyz: np.ndarray | None = None

    @property
    def direction_count(self) -> int:
        return int(self.azimuth_deg.shape[0])

    def to_summary(self) -> dict[str, object]:
        summary: dict[str, object] = {
            "direction_count": self.direction_count,
            "azimuth_deg_shape": list(self.azimuth_deg.shape),
            "elevation_deg_shape": list(self.elevation_deg.shape),
        }
        if self.cartesian_xyz is not None:
            summary["cartesian_xyz_shape"] = list(self.cartesian_xyz.shape)
        return summary


@dataclass(frozen=True)
class FrontEndBundle:
    schema_version: str
    interface_version: str
    producer_task_id: str
    producer_session_id: str
    run_config_ref: str
    array_id: str
    hrtf_id: str
    sample_rate_hz: int
    fft_size: int
    grid: DirectionGrid
    optimization_grid: DirectionGrid
    V: np.ndarray
    h: np.ndarray
    c_ls: np.ndarray
    c_magls: np.ndarray
    asset_bundle: AssetBundle

    def to_summary(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "interface_version": self.interface_version,
            "producer_task_id": self.producer_task_id,
            "producer_session_id": self.producer_session_id,
            "run_config_ref": self.run_config_ref,
            "array_id": self.array_id,
            "hrtf_id": self.hrtf_id,
            "sample_rate_hz": self.sample_rate_hz,
            "fft_size": self.fft_size,
            "grid": self.grid.to_summary(),
            "optimization_grid": self.optimization_grid.to_summary(),
            "V_shape": list(self.V.shape),
            "h_shape": list(self.h.shape),
            "c_ls_shape": list(self.c_ls.shape),
            "c_magls_shape": list(self.c_magls.shape),
            "finite": {
                "V": bool(np.isfinite(self.V).all()),
                "h": bool(np.isfinite(self.h).all()),
                "c_ls": bool(np.isfinite(self.c_ls).all()),
                "c_magls": bool(np.isfinite(self.c_magls).all()),
            },
        }


@dataclass(frozen=True)
class FrontEndValidationIssue:
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class FrontEndValidationReport:
    ok: bool
    bundle: FrontEndBundle
    issues: tuple[FrontEndValidationIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "bundle": self.bundle.to_summary(),
            "issues": [issue.to_dict() for issue in self.issues],
        }


class FrontEndValidationError(RuntimeError):
    def __init__(self, report: FrontEndValidationReport):
        self.report = report
        super().__init__(self._format_message(report))

    @staticmethod
    def _format_message(report: FrontEndValidationReport) -> str:
        return "\n".join(issue.message for issue in report.issues)


def _phase_aligned_hrtf_sh(
    hrir_path: str | Path,
    *,
    sample_rate_hz: int,
    fft_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    hrir, hrir_sample_rate_hz = soundfile.read(str(hrir_path))
    hrir = signal.resample_poly(hrir, sample_rate_hz, hrir_sample_rate_hz, axis=0)
    hrir = hrir * (hrir_sample_rate_hz / sample_rate_hz)
    hrir_delay_samples = int(np.argmax(np.abs(hrir[:, 0])))
    nm = np.arange(hrir.shape[1], dtype=np.int64)
    n = np.floor(np.sqrt(nm))
    m = nm - n**2 - n
    mult = np.ones(hrir.shape[1], dtype=np.float64)
    mult[m < 0] = -1.0

    left = hrir
    right = hrir * mult[None, :]
    left_sh = np.fft.rfft(left, n=fft_size, axis=0)
    right_sh = np.fft.rfft(right, n=fft_size, axis=0)
    fvec = np.arange(fft_size // 2 + 1, dtype=np.float64) / fft_size * sample_rate_hz
    phase = np.exp(1j * 2 * np.pi * fvec * hrir_delay_samples / sample_rate_hz)[:, None]
    return left_sh * phase, right_sh * phase


def load_optimization_grid(
    *,
    n_design: int = DEFAULT_OPTIMIZATION_GRID_N_DESIGN,
) -> DirectionGrid:
    install_scipy_sph_harm_compatibility()
    import spaudiopy

    cartesian_xyz = np.asarray(spaudiopy.grids.load_n_design(n_design), dtype=np.float64)
    azimuth_rad, polar_rad, _ = spaudiopy.utils.cart2sph(
        cartesian_xyz[:, 0],
        cartesian_xyz[:, 1],
        cartesian_xyz[:, 2],
    )
    azimuth_deg = np.rad2deg(azimuth_rad)
    elevation_deg = 90.0 - np.rad2deg(polar_rad)
    return DirectionGrid(
        azimuth_deg=azimuth_deg,
        elevation_deg=elevation_deg,
        cartesian_xyz=cartesian_xyz,
    )


def load_evaluation_grid(
    *,
    step_deg: int = DEFAULT_EVALUATION_STEP_DEG,
) -> DirectionGrid:
    azimuth_deg = np.arange(-180, 180, step_deg, dtype=np.float64)
    elevation_deg = np.zeros_like(azimuth_deg)
    azimuth_rad = np.deg2rad(azimuth_deg)
    elevation_rad = np.deg2rad(elevation_deg)
    cartesian_xyz = np.stack(
        [
            np.cos(azimuth_rad) * np.cos(elevation_rad),
            np.sin(azimuth_rad) * np.cos(elevation_rad),
            np.sin(elevation_rad),
        ],
        axis=-1,
    )
    return DirectionGrid(
        azimuth_deg=azimuth_deg,
        elevation_deg=elevation_deg,
        cartesian_xyz=cartesian_xyz,
    )


def _grid_to_sh_matrix(grid: DirectionGrid, order: int) -> np.ndarray:
    install_scipy_sph_harm_compatibility()
    import spaudiopy

    azimuth_rad = np.deg2rad(grid.azimuth_deg)
    polar_rad = np.deg2rad(90.0 - grid.elevation_deg)
    return np.asarray(spaudiopy.sph.sh_matrix(order, azimuth_rad, polar_rad, "real"), dtype=np.float64)


def _phase_aligned_steering_response(
    array_sh_path: str | Path,
    grid: DirectionGrid,
    *,
    sample_rate_hz: int,
    fft_size: int,
    array_delay_samples: int,
) -> np.ndarray:
    array_sh = np.asarray(np.load(array_sh_path), dtype=np.float64)
    sh_matrix = _grid_to_sh_matrix(grid, DEFAULT_ARRAY_ORDER)
    steering_time = np.einsum("dk,tkm->dtm", sh_matrix, array_sh)
    steering_response = np.fft.rfft(steering_time, n=fft_size, axis=1)
    fvec = np.arange(fft_size // 2 + 1, dtype=np.float64) / fft_size * sample_rate_hz
    phase = np.exp(1j * 2 * np.pi * fvec * array_delay_samples / sample_rate_hz)[None, :, None]
    return steering_response * phase


def _target_response(
    grid: DirectionGrid,
    left_hrtf_sh: np.ndarray,
    right_hrtf_sh: np.ndarray,
) -> np.ndarray:
    sh_matrix = _grid_to_sh_matrix(grid, DEFAULT_HRTF_ORDER)
    left = np.einsum("dm,fm->df", sh_matrix, left_hrtf_sh)
    right = np.einsum("dm,fm->df", sh_matrix, right_hrtf_sh)
    return np.stack([left, right], axis=-1)


def _solve_least_squares_coefficients(
    steering_response: np.ndarray,
    target_response: np.ndarray,
) -> np.ndarray:
    diff_cov = np.einsum("fdm,fdn->fmn", np.conj(steering_response), steering_response)
    eigvals = np.linalg.eigvalsh(diff_cov)
    regularized_cov = diff_cov + 0.001 * eigvals[:, -1][:, None, None] * np.eye(
        diff_cov.shape[-1],
        dtype=np.complex128,
    )[None, :, :]
    reg_inv_y = np.linalg.inv(regularized_cov) @ np.conj(np.transpose(steering_response, (0, 2, 1)))

    coeffs = []
    for ear_index in range(target_response.shape[-1]):
        coeffs.append((reg_inv_y @ target_response[:, :, ear_index, None])[..., 0])
    return np.stack(coeffs, axis=-1)


def _solve_magls_coefficients(
    steering_response: np.ndarray,
    target_response: np.ndarray,
    *,
    sample_rate_hz: int,
    fft_size: int,
    frequency_cut_hz: float,
) -> np.ndarray:
    diff_cov = np.einsum("fdm,fdn->fmn", np.conj(steering_response), steering_response)
    eigvals = np.linalg.eigvalsh(diff_cov)
    regularized_cov = diff_cov + 0.001 * eigvals[:, -1][:, None, None] * np.eye(
        diff_cov.shape[-1],
        dtype=np.complex128,
    )[None, :, :]
    reg_inv_y = np.linalg.inv(regularized_cov) @ np.conj(np.transpose(steering_response, (0, 2, 1)))
    target_cov = np.mean(
        target_response[..., None] * np.conj(target_response[..., None, :]),
        axis=1,
    )

    fvec = np.arange(fft_size // 2 + 1, dtype=np.float64) / fft_size * sample_rate_hz
    c_magls = np.zeros((fvec.shape[0], steering_response.shape[-1], target_response.shape[-1]), dtype=np.complex128)
    for k, freq_hz in enumerate(fvec):
        c_ls_k = reg_inv_y[k] @ target_response[k]
        if freq_hz > frequency_cut_hz and k > 0:
            previous_response = steering_response[k] @ c_magls[k - 1]
            phase = np.angle(previous_response)
            desired = np.abs(target_response[k]) * np.exp(1j * phase)
            c_magls[k] = reg_inv_y[k] @ desired
        else:
            c_magls[k] = c_ls_k

    estimated_response = np.einsum("fdm,fme->fde", steering_response, c_magls)
    estimated_cov = np.mean(
        estimated_response[..., None] * np.conj(estimated_response[..., None, :]),
        axis=1,
    ) + 1e-20 * np.eye(target_response.shape[-1], dtype=np.complex128)[None, :, :]
    equalization = np.sqrt(
        np.abs(
            np.stack(
                [
                    target_cov[:, 0, 0] / estimated_cov[:, 0, 0],
                    target_cov[:, 1, 1] / estimated_cov[:, 1, 1],
                ],
                axis=-1,
            )
        )
    )
    return c_magls * equalization[:, None, :]


def build_front_end_bundle(
    repo_root: Path | str = REPO_ROOT,
    *,
    array_id: str = DEFAULT_ARRAY_ID,
    hrtf_id: str = DEFAULT_HRTF_ID,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
    sample_rate_hz: int = DEFAULT_SAMPLE_RATE_HZ,
    fft_size: int = DEFAULT_FFT_SIZE,
    frequency_cut_hz: float = DEFAULT_MAGLS_F_CUT_HZ,
) -> FrontEndBundle:
    asset_bundle = resolve_asset_bundle(
        repo_root=repo_root,
        array_id=array_id,
        hrtf_id=hrtf_id,
    )
    optimization_grid = load_optimization_grid()
    evaluation_grid = load_evaluation_grid()
    left_hrtf_sh, right_hrtf_sh = _phase_aligned_hrtf_sh(
        asset_bundle.hrir_path,
        sample_rate_hz=sample_rate_hz,
        fft_size=fft_size,
    )

    steering_eval = _phase_aligned_steering_response(
        asset_bundle.array_sh_path,
        evaluation_grid,
        sample_rate_hz=sample_rate_hz,
        fft_size=fft_size,
        array_delay_samples=DEFAULT_ARRAY_SH_DELAY_SAMPLES,
    )
    steering_optim = _phase_aligned_steering_response(
        asset_bundle.array_sh_path,
        optimization_grid,
        sample_rate_hz=sample_rate_hz,
        fft_size=fft_size,
        array_delay_samples=DEFAULT_ARRAY_SH_DELAY_SAMPLES,
    )
    h = _target_response(evaluation_grid, left_hrtf_sh, right_hrtf_sh).astype(np.complex64)
    target_optim = _target_response(optimization_grid, left_hrtf_sh, right_hrtf_sh)
    c_ls = _solve_least_squares_coefficients(steering_optim.transpose(1, 0, 2), target_optim.transpose(1, 0, 2))
    c_magls = _solve_magls_coefficients(
        steering_optim.transpose(1, 0, 2),
        target_optim.transpose(1, 0, 2),
        sample_rate_hz=sample_rate_hz,
        fft_size=fft_size,
        frequency_cut_hz=frequency_cut_hz,
    )

    return FrontEndBundle(
        schema_version=DEFAULT_SCHEMA_VERSION,
        interface_version=DEFAULT_INTERFACE_VERSION,
        producer_task_id=DEFAULT_PRODUCER_TASK_ID,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
        array_id=array_id,
        hrtf_id=hrtf_id,
        sample_rate_hz=sample_rate_hz,
        fft_size=fft_size,
        grid=evaluation_grid,
        optimization_grid=optimization_grid,
        V=steering_eval.astype(np.complex64),
        h=h,
        c_ls=c_ls.astype(np.complex64),
        c_magls=c_magls.astype(np.complex64),
        asset_bundle=asset_bundle,
    )


def _validate_bundle(bundle: FrontEndBundle) -> tuple[FrontEndValidationIssue, ...]:
    issues: list[FrontEndValidationIssue] = []
    expected_azimuth = np.arange(-180, 180, DEFAULT_EVALUATION_STEP_DEG, dtype=np.float64)
    if not np.array_equal(bundle.grid.azimuth_deg, expected_azimuth):
        issues.append(
            FrontEndValidationIssue(
                code="evaluation_grid_mismatch",
                message="Evaluation grid azimuths do not match the required equatorial 5-degree sweep.",
            )
        )
    if not np.array_equal(bundle.grid.elevation_deg, np.zeros_like(expected_azimuth)):
        issues.append(
            FrontEndValidationIssue(
                code="evaluation_elevation_mismatch",
                message="Evaluation grid elevations must remain on the equator.",
            )
        )
    if bundle.optimization_grid.direction_count != 632:
        issues.append(
            FrontEndValidationIssue(
                code="optimization_grid_count_mismatch",
                message=(
                    "Optimization grid must match spaudiopy.grids.load_n_design(35) direction count "
                    f"of 632; received {bundle.optimization_grid.direction_count}."
                ),
            )
        )
    if bundle.V.shape[0] != bundle.grid.direction_count:
        issues.append(
            FrontEndValidationIssue(
                code="V_direction_mismatch",
                message="V direction axis must match the evaluation grid direction count.",
            )
        )
    if bundle.h.shape[0] != bundle.grid.direction_count:
        issues.append(
            FrontEndValidationIssue(
                code="h_direction_mismatch",
                message="h direction axis must match the evaluation grid direction count.",
            )
        )
    if bundle.V.shape[1] != bundle.h.shape[1]:
        issues.append(
            FrontEndValidationIssue(
                code="frequency_mismatch",
                message="V and h must share the same frequency-bin axis.",
            )
        )
    if bundle.c_ls.shape != bundle.c_magls.shape:
        issues.append(
            FrontEndValidationIssue(
                code="coefficient_shape_mismatch",
                message="c_ls and c_magls must share the same coefficient semantics and shape.",
            )
        )
    if bundle.V.shape[1] != bundle.c_ls.shape[0]:
        issues.append(
            FrontEndValidationIssue(
                code="bundle_frequency_shape_mismatch",
                message="Bundle frequency axes must be consistent across V, h, c_ls, and c_magls.",
            )
        )
    if bundle.V.shape[2] != bundle.c_ls.shape[1]:
        issues.append(
            FrontEndValidationIssue(
                code="bundle_coefficient_shape_mismatch",
                message="Bundle coefficient axes must be consistent across V, c_ls, and c_magls.",
            )
        )
    if bundle.h.shape[2] != bundle.c_ls.shape[2]:
        issues.append(
            FrontEndValidationIssue(
                code="bundle_ear_shape_mismatch",
                message="Bundle ear axes must be consistent across h, c_ls, and c_magls.",
            )
        )
    for name, array in (("V", bundle.V), ("h", bundle.h), ("c_ls", bundle.c_ls), ("c_magls", bundle.c_magls)):
        if not np.isfinite(array).all():
            issues.append(
                FrontEndValidationIssue(
                    code=f"{name}_non_finite",
                    message=f"{name} contains non-finite values.",
                )
            )
    return tuple(issues)


def inspect_front_end_bundle(
    repo_root: Path | str = REPO_ROOT,
    *,
    array_id: str = DEFAULT_ARRAY_ID,
    hrtf_id: str = DEFAULT_HRTF_ID,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
    sample_rate_hz: int = DEFAULT_SAMPLE_RATE_HZ,
    fft_size: int = DEFAULT_FFT_SIZE,
    frequency_cut_hz: float = DEFAULT_MAGLS_F_CUT_HZ,
) -> FrontEndValidationReport:
    bundle = build_front_end_bundle(
        repo_root=repo_root,
        array_id=array_id,
        hrtf_id=hrtf_id,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
        sample_rate_hz=sample_rate_hz,
        fft_size=fft_size,
        frequency_cut_hz=frequency_cut_hz,
    )
    issues = _validate_bundle(bundle)
    return FrontEndValidationReport(
        ok=not issues,
        bundle=bundle,
        issues=issues,
    )


def resolve_front_end_bundle(
    repo_root: Path | str = REPO_ROOT,
    *,
    array_id: str = DEFAULT_ARRAY_ID,
    hrtf_id: str = DEFAULT_HRTF_ID,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
    sample_rate_hz: int = DEFAULT_SAMPLE_RATE_HZ,
    fft_size: int = DEFAULT_FFT_SIZE,
    frequency_cut_hz: float = DEFAULT_MAGLS_F_CUT_HZ,
) -> FrontEndBundle:
    report = inspect_front_end_bundle(
        repo_root=repo_root,
        array_id=array_id,
        hrtf_id=hrtf_id,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
        sample_rate_hz=sample_rate_hz,
        fft_size=fft_size,
        frequency_cut_hz=frequency_cut_hz,
    )
    if not report.ok:
        raise FrontEndValidationError(report)
    return report.bundle


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 02 direction-grid and front-end bundle builder.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command_name in ("report", "smoke"):
        subparser = subparsers.add_parser(command_name)
        subparser.add_argument("--repo-root", default=str(REPO_ROOT))
        subparser.add_argument("--array-id", default=DEFAULT_ARRAY_ID)
        subparser.add_argument("--hrtf-id", default=DEFAULT_HRTF_ID)
        subparser.add_argument("--producer-session-id", default=DEFAULT_PRODUCER_SESSION_ID)
        subparser.add_argument("--run-config-ref", default=DEFAULT_RUN_CONFIG_REF)
        subparser.add_argument("--sample-rate-hz", type=int, default=DEFAULT_SAMPLE_RATE_HZ)
        subparser.add_argument("--fft-size", type=int, default=DEFAULT_FFT_SIZE)
        subparser.add_argument("--frequency-cut-hz", type=float, default=DEFAULT_MAGLS_F_CUT_HZ)
        subparser.add_argument("--indent", type=int, default=2)

    return parser


def _run_cli() -> int:
    args = _build_parser().parse_args()
    report = inspect_front_end_bundle(
        repo_root=args.repo_root,
        array_id=args.array_id,
        hrtf_id=args.hrtf_id,
        producer_session_id=args.producer_session_id,
        run_config_ref=args.run_config_ref,
        sample_rate_hz=args.sample_rate_hz,
        fft_size=args.fft_size,
        frequency_cut_hz=args.frequency_cut_hz,
    )
    print(json.dumps(report.to_dict(), indent=args.indent, sort_keys=True))
    if args.command == "smoke" and not report.ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_cli())
