from __future__ import annotations

from dataclasses import dataclass
import hashlib
import itertools
import sys
from pathlib import Path
from typing import Any

import numpy as np
import scipy.signal as signal
import soundfile

from .asset_environment import ARRAY2BINAURAL_ROOT, REPO_ROOT
from .compat import install_scipy_sph_harm_compatibility


COMPUTE_SAMPLE_RATE_HZ = 48000
ARRAY_SOURCE_SAMPLE_RATE_HZ = 32000
NFFT = 1536
EXPORT_FREQUENCY_BINS = 513
ARRAY_DELAY_SAMPLES_32K = 22
ARRAY_DELAY_SAMPLES_48K = 33
HRTF_ORDER = 5
ARRAY_ORDER = 25
OPTIMIZATION_GRID_N_DESIGN = 35
FREQUENCY_CUT_HZ = 2000.0
DIAGONAL_LOADING_FACTOR = 0.001
SAVED_ALIGNED_YPR_SOURCE_AXIS_SEMANTICS = "[microphone, ear, frequency]"
CANONICAL_COEFFICIENT_AXIS_SEMANTICS = "[frequency, microphone, ear]"


@dataclass(frozen=True)
class SavedAlignedYprReference:
    yaw_deg: int
    path: Path
    sha256: str
    source_shape: tuple[int, ...]
    canonical_shape: tuple[int, ...]
    source_axis_semantics: str
    canonical_axis_semantics: str
    coefficients: np.ndarray


@dataclass(frozen=True)
class EmaglsBuildResult:
    coefficients: np.ndarray
    least_squares_coefficients: np.ndarray
    yaw_deg: float
    pitch_deg: float
    roll_deg: float
    source: str
    sample_rate_hz: int
    nfft: int
    export_frequency_bins: int
    frequency_cut_hz: float
    array_delay_samples: int
    hrtf_delay_samples: int
    metadata: dict[str, Any]


def saved_aligned_ypr_reference_path(repo_root: Path | str, yaw_deg: int) -> Path:
    return (
        Path(repo_root).resolve()
        / "07_References"
        / "Open_Source_Baselines"
        / "Array2Binaural"
        / "compute_emagls_filters"
        / f"emagls_32kHz_dft_aligned_ypr_{yaw_deg}_0_0.npy"
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonicalize_saved_aligned_ypr_emagls(coefficients: np.ndarray) -> tuple[np.ndarray, str, str]:
    array = np.asarray(coefficients)
    if array.ndim != 3:
        raise ValueError(f"Expected rank-3 eMagLS coefficients, received shape {array.shape}.")
    if array.shape == (5, 2, EXPORT_FREQUENCY_BINS):
        return (
            np.transpose(array, (2, 0, 1)).astype(np.complex64, copy=False),
            SAVED_ALIGNED_YPR_SOURCE_AXIS_SEMANTICS,
            CANONICAL_COEFFICIENT_AXIS_SEMANTICS,
        )
    if array.shape == (EXPORT_FREQUENCY_BINS, 5, 2):
        return (
            array.astype(np.complex64, copy=False),
            CANONICAL_COEFFICIENT_AXIS_SEMANTICS,
            CANONICAL_COEFFICIENT_AXIS_SEMANTICS,
        )
    raise ValueError(
        "Could not canonicalize eMagLS coefficients. Expected saved "
        "[microphone=5, ear=2, frequency=513] or canonical "
        f"[frequency=513, microphone=5, ear=2], received {array.shape}."
    )


def load_saved_aligned_ypr_emagls_reference_details(
    repo_root: Path | str = REPO_ROOT,
    yaw_deg: int = 0,
) -> SavedAlignedYprReference:
    path = saved_aligned_ypr_reference_path(repo_root, yaw_deg)
    source = np.load(path)
    canonical, source_axes, canonical_axes = canonicalize_saved_aligned_ypr_emagls(source)
    if not np.isfinite(canonical).all():
        raise ValueError(f"Saved aligned-ypr eMagLS coefficients contain non-finite values: {path}")
    return SavedAlignedYprReference(
        yaw_deg=int(yaw_deg),
        path=path,
        sha256=sha256_file(path),
        source_shape=tuple(int(v) for v in source.shape),
        canonical_shape=tuple(int(v) for v in canonical.shape),
        source_axis_semantics=source_axes,
        canonical_axis_semantics=canonical_axes,
        coefficients=canonical,
    )


def load_saved_aligned_ypr_emagls_reference(
    repo_root: Path | str = REPO_ROOT,
    yaw_deg: int = 0,
) -> np.ndarray:
    """Load the opaque Array2Binaural aligned-ypr runtime filter as [frequency, microphone, ear]."""

    return load_saved_aligned_ypr_emagls_reference_details(repo_root, yaw_deg).coefficients


def _array2binaural_root(repo_root: Path | str) -> Path:
    return Path(repo_root).resolve() / ARRAY2BINAURAL_ROOT.relative_to(REPO_ROOT)


def _load_array2binaural_rotation_matrix(
    root: Path,
    order: int,
    yaw: float,
    pitch: float,
    roll: float,
) -> np.ndarray:
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from ambisonics import calculate_rotation_matrix

    return np.asarray(
        calculate_rotation_matrix(
            order,
            np.asarray([yaw], dtype=np.float64),
            np.asarray([pitch], dtype=np.float64),
            np.asarray([roll], dtype=np.float64),
        )[0],
        dtype=np.float64,
    )


def _right_ear_sign_convention(channel_count: int) -> np.ndarray:
    nm = np.arange(channel_count, dtype=np.int64)
    n = np.floor(np.sqrt(nm))
    m = nm - n**2 - n
    mult = np.ones(channel_count, dtype=np.float64)
    mult[m < 0] = -1.0
    return mult


def build_visible_raw_array2binaural_emagls_coefficients(
    repo_root: Path | str = REPO_ROOT,
    yaw_deg: float = 0.0,
    pitch_deg: float = 0.0,
    roll_deg: float = 0.0,
) -> EmaglsBuildResult:
    """Port the visible Array2Binaural 48 kHz/1536 raw eMagLS path.

    This intentionally returns the raw `filters_32kHz_dft.npy` semantics from the visible
    script, not the opaque saved `emagls_32kHz_dft_aligned_ypr_*` artifact.
    """

    install_scipy_sph_harm_compatibility()
    import spaudiopy

    root = _array2binaural_root(repo_root)
    hrir, fs_hrirs = soundfile.read(str(root / "ku100_magls_sh_hrir" / "irsOrd5.wav"))
    hrir = signal.resample_poly(hrir, COMPUTE_SAMPLE_RATE_HZ, fs_hrirs, axis=0) * (
        fs_hrirs / COMPUTE_SAMPLE_RATE_HZ
    )
    hrtf_delay_samples = int(np.argmax(np.abs(hrir[:, 0])))
    right = hrir * _right_ear_sign_convention(hrir.shape[1])[None, :]
    left = hrir

    fvec = np.arange(NFFT // 2 + 1, dtype=np.float64) / NFFT * COMPUTE_SAMPLE_RATE_HZ
    hrtf_delay_phase = np.exp(
        1j * 2 * np.pi * fvec * hrtf_delay_samples / COMPUTE_SAMPLE_RATE_HZ
    )[:, None]
    dl_sh5 = np.fft.rfft(left, NFFT, axis=0) * hrtf_delay_phase
    dr_sh5 = np.fft.rfft(right, NFFT, axis=0) * hrtf_delay_phase

    ir_sh = np.asarray(np.load(root / "Easycom_array_32000Hz_o25_22samps_delay.npy"), dtype=np.float64)
    ir_sh = (ARRAY_SOURCE_SAMPLE_RATE_HZ / COMPUTE_SAMPLE_RATE_HZ) * signal.resample_poly(
        ir_sh,
        COMPUTE_SAMPLE_RATE_HZ,
        ARRAY_SOURCE_SAMPLE_RATE_HZ,
        axis=0,
    )

    optim_grid = np.asarray(spaudiopy.grids.load_n_design(OPTIMIZATION_GRID_N_DESIGN), dtype=np.float64)
    azi, polar, _ = spaudiopy.utils.cart2sph(
        optim_grid[:, 0],
        optim_grid[:, 1],
        optim_grid[:, 2],
    )
    optim_sh5 = np.asarray(spaudiopy.sph.sh_matrix(HRTF_ORDER, azi, polar, "real"), dtype=np.float64)
    optim_sh25 = np.asarray(spaudiopy.sph.sh_matrix(ARRAY_ORDER, azi, polar, "real"), dtype=np.float64)

    optim_irs = np.einsum("dk,tkm->tdm", optim_sh25, ir_sh)
    steering = np.fft.rfft(optim_irs, NFFT, axis=0)
    steering *= np.exp(
        1j * 2 * np.pi * fvec * ARRAY_DELAY_SAMPLES_48K / COMPUTE_SAMPLE_RATE_HZ
    )[:, None, None]

    diff_cov = np.einsum("fdm,fdn->fmn", np.conj(steering), steering)
    eigvals = np.linalg.eigvalsh(diff_cov)
    regularized_cov = diff_cov + DIAGONAL_LOADING_FACTOR * eigvals[:, -1][:, None, None] * np.eye(
        diff_cov.shape[-1],
        dtype=np.complex128,
    )[None, :, :]
    reg_inv_y = np.linalg.inv(regularized_cov) @ np.conj(np.transpose(steering, (0, 2, 1)))

    dl0 = np.einsum("dm,fm->fd", optim_sh5, dl_sh5)
    dr0 = np.einsum("dm,fm->fd", optim_sh5, dr_sh5)
    unrotated_target = np.stack([dl0, dr0], axis=-1)
    target_cov = np.mean(
        unrotated_target[..., None] * np.conj(unrotated_target[..., None, :]),
        axis=1,
    )

    rotmat_o5 = _load_array2binaural_rotation_matrix(
        root,
        HRTF_ORDER,
        np.deg2rad(yaw_deg),
        np.deg2rad(pitch_deg),
        np.deg2rad(roll_deg),
    )
    rotated_sh5 = (rotmat_o5 @ optim_sh5.T).T
    target_left = np.einsum("dm,fm->fd", rotated_sh5, dl_sh5)
    target_right = np.einsum("dm,fm->fd", rotated_sh5, dr_sh5)
    target = np.stack([target_left, target_right], axis=-1)

    c_ls = np.zeros((fvec.shape[0], steering.shape[-1], 2), dtype=np.complex128)
    c_magls = np.zeros_like(c_ls)
    for k, freq_hz in enumerate(fvec):
        c_ls[k] = reg_inv_y[k] @ target[k]
        if freq_hz > FREQUENCY_CUT_HZ and k > 0:
            previous_response = steering[k] @ c_magls[k - 1]
            phase = np.angle(previous_response)
            desired = np.abs(target[k]) * np.exp(1j * phase)
            c_magls[k] = reg_inv_y[k] @ desired
        else:
            c_magls[k] = c_ls[k]
        if freq_hz > ARRAY_SOURCE_SAMPLE_RATE_HZ / 2:
            break

    estimated_response = np.einsum("fdm,fme->fde", steering, c_magls)
    estimated_cov = np.mean(
        estimated_response[..., None] * np.conj(estimated_response[..., None, :]),
        axis=1,
    ) + 1e-20 * np.eye(2, dtype=np.complex128)[None, :, :]
    equalization = np.sqrt(
        np.abs(
            np.stack(
                [
                    target_cov[:, 0, 0] / (estimated_cov[:, 0, 0] + 1e-20),
                    target_cov[:, 1, 1] / (estimated_cov[:, 1, 1] + 1e-20),
                ],
                axis=-1,
            )
        )
    )
    c_magls = c_magls * equalization[:, None, :]

    return EmaglsBuildResult(
        coefficients=c_magls[:EXPORT_FREQUENCY_BINS].astype(np.complex64),
        least_squares_coefficients=c_ls[:EXPORT_FREQUENCY_BINS].astype(np.complex64),
        yaw_deg=float(yaw_deg),
        pitch_deg=float(pitch_deg),
        roll_deg=float(roll_deg),
        source="visible_array2binaural_raw_48k_1536",
        sample_rate_hz=COMPUTE_SAMPLE_RATE_HZ,
        nfft=NFFT,
        export_frequency_bins=EXPORT_FREQUENCY_BINS,
        frequency_cut_hz=FREQUENCY_CUT_HZ,
        array_delay_samples=ARRAY_DELAY_SAMPLES_48K,
        hrtf_delay_samples=hrtf_delay_samples,
        metadata={
            "array_source_sample_rate_hz": ARRAY_SOURCE_SAMPLE_RATE_HZ,
            "array_delay_samples_32k": ARRAY_DELAY_SAMPLES_32K,
            "optimization_grid_n_design": OPTIMIZATION_GRID_N_DESIGN,
            "optimization_direction_count": int(optim_grid.shape[0]),
            "coefficient_axis_semantics": CANONICAL_COEFFICIENT_AXIS_SEMANTICS,
        },
    )


def coefficient_difference_metrics(
    coefficients: np.ndarray,
    reference: np.ndarray,
    *,
    sample_rate_hz: int = ARRAY_SOURCE_SAMPLE_RATE_HZ,
) -> dict[str, Any]:
    project = np.asarray(coefficients)
    target = np.asarray(reference)
    if project.shape != target.shape:
        raise ValueError(f"Coefficient shape mismatch: {project.shape} vs {target.shape}.")
    residual = project - target
    abs_residual = np.abs(residual)
    reference_energy = float(np.mean(np.abs(target) ** 2))
    safe_reference_energy = max(reference_energy, np.finfo(np.float64).tiny)
    bin_hz = sample_rate_hz / ((project.shape[0] - 1) * 2.0)
    per_frequency = np.mean(abs_residual, axis=(1, 2))
    worst_indices = np.argsort(per_frequency)[-min(8, per_frequency.shape[0]) :][::-1]
    return {
        "max_abs": float(np.max(abs_residual)),
        "mean_abs": float(np.mean(abs_residual)),
        "rmse": float(np.sqrt(np.mean(abs_residual**2))),
        "nmse": float(np.mean(abs_residual**2) / safe_reference_energy),
        "reference_energy": reference_energy,
        "coefficient_energy": float(np.mean(np.abs(project) ** 2)),
        "worst_frequency_bins": [
            {
                "frequency_bin": int(index),
                "frequency_hz": float(index * bin_hz),
                "mean_abs": float(per_frequency[index]),
                "max_abs": float(np.max(abs_residual[index])),
            }
            for index in worst_indices
        ],
    }


def compare_emagls_to_saved_reference(
    result: EmaglsBuildResult,
    saved_reference: np.ndarray,
) -> dict[str, Any]:
    metrics = coefficient_difference_metrics(
        result.coefficients,
        saved_reference,
        sample_rate_hz=ARRAY_SOURCE_SAMPLE_RATE_HZ,
    )
    metrics["candidate_source"] = result.source
    metrics["saved_reference_semantics"] = "opaque_array2binaural_aligned_ypr_runtime_artifact"
    return metrics


def banded_coefficient_metrics(
    coefficients: np.ndarray,
    reference: np.ndarray,
    *,
    sample_rate_hz: int = ARRAY_SOURCE_SAMPLE_RATE_HZ,
) -> dict[str, Any]:
    project = np.asarray(coefficients)
    target = np.asarray(reference)
    if project.shape != target.shape:
        raise ValueError(f"Coefficient shape mismatch: {project.shape} vs {target.shape}.")
    freq_count = project.shape[0]
    freqs = np.arange(freq_count, dtype=np.float64) * sample_rate_hz / ((freq_count - 1) * 2.0)
    bands = {
        "ls_band_le_2khz": freqs <= FREQUENCY_CUT_HZ,
        "magls_band_gt_2khz": freqs > FREQUENCY_CUT_HZ,
        "audible_export_band_le_16khz": freqs <= ARRAY_SOURCE_SAMPLE_RATE_HZ / 2,
    }
    payload: dict[str, Any] = {}
    for name, mask in bands.items():
        if not np.any(mask):
            continue
        residual = project[mask] - target[mask]
        abs_residual = np.abs(residual)
        reference_energy = float(np.mean(np.abs(target[mask]) ** 2))
        safe_reference_energy = max(reference_energy, np.finfo(np.float64).tiny)
        per_frequency = np.mean(abs_residual, axis=(1, 2))
        band_indices = np.flatnonzero(mask)
        worst_local = np.argsort(per_frequency)[-min(8, per_frequency.shape[0]) :][::-1]
        payload[name] = {
            "max_abs": float(np.max(abs_residual)),
            "mean_abs": float(np.mean(abs_residual)),
            "rmse": float(np.sqrt(np.mean(abs_residual**2))),
            "nmse": float(np.mean(abs_residual**2) / safe_reference_energy),
            "reference_energy": reference_energy,
            "coefficient_energy": float(np.mean(np.abs(project[mask]) ** 2)),
            "frequency_hz_min": float(freqs[band_indices[0]]),
            "frequency_hz_max": float(freqs[band_indices[-1]]),
            "worst_frequency_bins": [
                {
                    "frequency_bin": int(band_indices[local_index]),
                    "frequency_hz": float(freqs[band_indices[local_index]]),
                    "mean_abs": float(per_frequency[local_index]),
                    "max_abs": float(np.max(abs_residual[local_index])),
                }
                for local_index in worst_local
            ],
        }
    return payload


def scalar_fit_nmse(candidate: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    x = np.asarray(candidate).reshape(-1)
    y = np.asarray(reference).reshape(-1)
    denom = np.vdot(x, x)
    if abs(denom) <= np.finfo(np.float64).tiny:
        scalar = 0.0 + 0.0j
    else:
        scalar = np.vdot(x, y) / denom
    residual = scalar * x - y
    reference_energy = max(float(np.mean(np.abs(y) ** 2)), np.finfo(np.float64).tiny)
    return {
        "scalar_re": float(np.real(scalar)),
        "scalar_im": float(np.imag(scalar)),
        "nmse": float(np.mean(np.abs(residual) ** 2) / reference_energy),
        "max_abs": float(np.max(np.abs(residual))),
        "mean_abs": float(np.mean(np.abs(residual))),
    }


def mismatch_probe_metrics(coefficients: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    project = np.asarray(coefficients)
    target = np.asarray(reference)
    probes: dict[str, Any] = {
        "direct_scalar_fit": scalar_fit_nmse(project, target),
        "conjugated_scalar_fit": scalar_fit_nmse(np.conj(project), target),
        "ear_swap_scalar_fit": scalar_fit_nmse(project[:, :, ::-1], target),
    }
    best_permutation: dict[str, Any] | None = None
    for permutation in itertools.permutations(range(project.shape[1])):
        metrics = scalar_fit_nmse(project[:, permutation, :], target)
        candidate = {"microphone_permutation": list(permutation), **metrics}
        if best_permutation is None or candidate["nmse"] < best_permutation["nmse"]:
            best_permutation = candidate
    probes["best_microphone_permutation_scalar_fit"] = best_permutation
    return probes
