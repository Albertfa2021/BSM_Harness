from __future__ import annotations

import argparse
from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
import scipy.signal as signal

from .asset_environment import (
    DEFAULT_ARRAY_ID,
    DEFAULT_HRTF_ID,
    DEFAULT_INTERFACE_VERSION,
    DEFAULT_SCHEMA_VERSION,
    REPO_ROOT,
)
from .baseline_renderer import BASELINE_NAME_MAGLS, inspect_baseline_renderer


DEFAULT_PRODUCER_TASK_ID = "TASK-0005"
DEFAULT_PRODUCER_SESSION_ID = "SESSION-P2-0006"
DEFAULT_RUN_CONFIG_REF = "phase02/default_cue_bank"
DEFAULT_TAU_SECONDS = 0.001
DEFAULT_ILD_NUM_BANDS = 29
DEFAULT_ILD_LOW_FREQ_HZ = 50.0
DEFAULT_ILD_HIGH_FREQ_HZ = 6000.0
AUDITORY_ILD_MODULE_PATH = (
    REPO_ROOT / "05_Experiments/EXP-0001_Auditory_ILD_Python/code/auditory_ild.py"
)

_AUDITORY_ILD_MODULE: ModuleType | None = None
_TORCH_IMPORT: Any | None = None


@dataclass(frozen=True)
class CueBankMetrics:
    ild_error_db: float
    itd_proxy_error: float
    mean_ref_itd_lag_samples: float
    mean_est_itd_lag_samples: float

    def to_dict(self) -> dict[str, float]:
        return {
            "ild_error_db": self.ild_error_db,
            "itd_proxy_error": self.itd_proxy_error,
            "mean_ref_itd_lag_samples": self.mean_ref_itd_lag_samples,
            "mean_est_itd_lag_samples": self.mean_est_itd_lag_samples,
        }


@dataclass(frozen=True)
class CueBankResult:
    schema_version: str
    interface_version: str
    producer_task_id: str
    producer_session_id: str
    run_config_ref: str
    sample_rate_hz: int
    tau_seconds: float
    tau_samples: int
    itd_lowpass_cutoff_hz: float | None
    erb_center_freq_hz: np.ndarray
    ild_ref: np.ndarray
    ild_est: np.ndarray
    gcc_phat_ref: np.ndarray
    gcc_phat_est: np.ndarray
    ref_itd_lag_samples: np.ndarray
    est_itd_lag_samples: np.ndarray
    metrics: CueBankMetrics

    def to_summary(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "interface_version": self.interface_version,
            "producer_task_id": self.producer_task_id,
            "producer_session_id": self.producer_session_id,
            "run_config_ref": self.run_config_ref,
            "sample_rate_hz": self.sample_rate_hz,
            "tau_seconds": self.tau_seconds,
            "tau_samples": self.tau_samples,
            "itd_lowpass_cutoff_hz": self.itd_lowpass_cutoff_hz,
            "erb_center_freq_hz_shape": list(self.erb_center_freq_hz.shape),
            "ild_ref_shape": list(self.ild_ref.shape),
            "ild_est_shape": list(self.ild_est.shape),
            "gcc_phat_ref_shape": list(self.gcc_phat_ref.shape),
            "gcc_phat_est_shape": list(self.gcc_phat_est.shape),
            "ref_itd_lag_samples_shape": list(self.ref_itd_lag_samples.shape),
            "est_itd_lag_samples_shape": list(self.est_itd_lag_samples.shape),
            "finite": {
                "erb_center_freq_hz": bool(np.isfinite(self.erb_center_freq_hz).all()),
                "ild_ref": bool(np.isfinite(self.ild_ref).all()),
                "ild_est": bool(np.isfinite(self.ild_est).all()),
                "gcc_phat_ref": bool(np.isfinite(self.gcc_phat_ref).all()),
                "gcc_phat_est": bool(np.isfinite(self.gcc_phat_est).all()),
                "ref_itd_lag_samples": bool(np.isfinite(self.ref_itd_lag_samples).all()),
                "est_itd_lag_samples": bool(np.isfinite(self.est_itd_lag_samples).all()),
            },
            "metrics": self.metrics.to_dict(),
        }


def _load_auditory_ild_module() -> ModuleType:
    global _AUDITORY_ILD_MODULE
    if _AUDITORY_ILD_MODULE is None:
        spec = importlib.util.spec_from_file_location(
            "bsm_phase02_auditory_ild_reference",
            AUDITORY_ILD_MODULE_PATH,
        )
        if spec is None or spec.loader is None:
            raise RuntimeError(
                f"Could not load auditory ILD reference module from {AUDITORY_ILD_MODULE_PATH}."
            )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _AUDITORY_ILD_MODULE = module
    return _AUDITORY_ILD_MODULE


def _get_torch_module() -> Any:
    global _TORCH_IMPORT
    if _TORCH_IMPORT is None:
        try:
            import torch  # type: ignore
        except ImportError:
            _TORCH_IMPORT = False
        else:
            _TORCH_IMPORT = torch
    return _TORCH_IMPORT


def _require_response_shape(response: np.ndarray) -> np.ndarray:
    response_array = np.asarray(response)
    if response_array.ndim != 3 or response_array.shape[-1] != 2:
        raise ValueError(
            "Expected response with shape [direction, frequency_bin, ear=2]."
        )
    if not np.isfinite(response_array).all():
        raise ValueError("Response contains non-finite values.")
    return response_array


def _response_to_time_domain(response: np.ndarray) -> np.ndarray:
    response_array = _require_response_shape(response)
    fft_size = (response_array.shape[1] - 1) * 2
    if fft_size <= 0:
        raise ValueError("Response must include at least two frequency bins.")
    time_response = np.fft.irfft(response_array, n=fft_size, axis=1)
    if not np.isfinite(time_response).all():
        raise RuntimeError("Time-domain response contains non-finite values.")
    return np.asarray(time_response, dtype=np.float64)


def _tau_seconds_to_samples(sample_rate_hz: int, tau_seconds: float, signal_length: int) -> int:
    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive.")
    if tau_seconds < 0:
        raise ValueError("tau_seconds must be non-negative.")
    tau_samples = int(round(sample_rate_hz * tau_seconds))
    max_tau_samples = signal_length - 1
    if tau_samples > max_tau_samples:
        raise ValueError(
            f"tau_seconds={tau_seconds} resolves to {tau_samples} samples, "
            f"which exceeds the signal support {max_tau_samples}."
        )
    return tau_samples


def _maybe_apply_lowpass_filter(
    wave: np.ndarray,
    *,
    sample_rate_hz: int,
    lowpass_cutoff_hz: float | None,
) -> np.ndarray:
    if lowpass_cutoff_hz is None:
        return wave
    nyquist_hz = sample_rate_hz / 2.0
    if lowpass_cutoff_hz <= 0 or lowpass_cutoff_hz >= nyquist_hz:
        raise ValueError(
            "lowpass_cutoff_hz must be inside (0, sample_rate_hz / 2)."
        )
    sos = signal.butter(4, lowpass_cutoff_hz, btype="lowpass", fs=sample_rate_hz, output="sos")
    return signal.sosfiltfilt(sos, wave)


def _gcc_phat_window_numpy(
    left_wave: np.ndarray,
    right_wave: np.ndarray,
    *,
    tau_samples: int,
    sample_rate_hz: int,
    lowpass_cutoff_hz: float | None,
    eps: float = 1e-12,
) -> tuple[np.ndarray, int]:
    left = _maybe_apply_lowpass_filter(
        np.asarray(left_wave, dtype=np.float64),
        sample_rate_hz=sample_rate_hz,
        lowpass_cutoff_hz=lowpass_cutoff_hz,
    )
    right = _maybe_apply_lowpass_filter(
        np.asarray(right_wave, dtype=np.float64),
        sample_rate_hz=sample_rate_hz,
        lowpass_cutoff_hz=lowpass_cutoff_hz,
    )
    n_fft = left.shape[-1] * 2 - 1
    cross_spectrum = np.fft.rfft(left, n=n_fft) * np.conj(np.fft.rfft(right, n=n_fft))
    magnitude = np.maximum(np.abs(cross_spectrum), eps)
    correlation = np.fft.irfft(cross_spectrum / magnitude, n=n_fft)
    centered = np.roll(np.real(correlation), n_fft // 2)
    center_index = n_fft // 2
    window = centered[center_index - tau_samples : center_index + tau_samples + 1]
    peak_lag = int(np.argmax(window) - tau_samples)
    return np.asarray(window, dtype=np.float64), peak_lag


def _compute_ild_cues(
    reference_time_response: np.ndarray,
    estimated_time_response: np.ndarray,
    *,
    sample_rate_hz: int,
    num_bands: int,
    low_freq_hz: float,
    high_freq_hz: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    auditory_ild = _load_auditory_ild_module()
    erb_center_freq_hz, filter_coeffs = auditory_ild.design_ild_filterbank(
        sample_rate_hz,
        num_bands=num_bands,
        low_freq_hz=low_freq_hz,
        high_freq_hz=high_freq_hz,
    )
    direction_count = reference_time_response.shape[0]
    ild_ref = np.empty((erb_center_freq_hz.shape[0], direction_count), dtype=np.float64)
    ild_est = np.empty_like(ild_ref)
    for direction_index in range(direction_count):
        ild_ref[:, direction_index] = auditory_ild.compute_band_ild_db(
            reference_time_response[direction_index, :, 0],
            reference_time_response[direction_index, :, 1],
            filter_coeffs,
        )
        ild_est[:, direction_index] = auditory_ild.compute_band_ild_db(
            estimated_time_response[direction_index, :, 0],
            estimated_time_response[direction_index, :, 1],
            filter_coeffs,
        )
    return (
        np.asarray(erb_center_freq_hz, dtype=np.float64),
        ild_ref,
        ild_est,
    )


def _compute_itd_cues(
    reference_time_response: np.ndarray,
    estimated_time_response: np.ndarray,
    *,
    sample_rate_hz: int,
    tau_seconds: float,
    lowpass_cutoff_hz: float | None,
) -> tuple[int, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    tau_samples = _tau_seconds_to_samples(
        sample_rate_hz,
        tau_seconds,
        signal_length=reference_time_response.shape[1],
    )
    direction_count = reference_time_response.shape[0]
    gcc_phat_ref = np.empty((direction_count, 2 * tau_samples + 1), dtype=np.float64)
    gcc_phat_est = np.empty_like(gcc_phat_ref)
    ref_peak_lags = np.empty(direction_count, dtype=np.int64)
    est_peak_lags = np.empty(direction_count, dtype=np.int64)
    for direction_index in range(direction_count):
        ref_window, ref_peak_lag = _gcc_phat_window_numpy(
            reference_time_response[direction_index, :, 0],
            reference_time_response[direction_index, :, 1],
            tau_samples=tau_samples,
            sample_rate_hz=sample_rate_hz,
            lowpass_cutoff_hz=lowpass_cutoff_hz,
        )
        est_window, est_peak_lag = _gcc_phat_window_numpy(
            estimated_time_response[direction_index, :, 0],
            estimated_time_response[direction_index, :, 1],
            tau_samples=tau_samples,
            sample_rate_hz=sample_rate_hz,
            lowpass_cutoff_hz=lowpass_cutoff_hz,
        )
        gcc_phat_ref[direction_index] = ref_window
        gcc_phat_est[direction_index] = est_window
        ref_peak_lags[direction_index] = ref_peak_lag
        est_peak_lags[direction_index] = est_peak_lag
    return tau_samples, gcc_phat_ref, gcc_phat_est, ref_peak_lags, est_peak_lags


def build_cue_bank(
    reference_response: np.ndarray,
    estimated_response: np.ndarray,
    *,
    sample_rate_hz: int,
    tau_seconds: float = DEFAULT_TAU_SECONDS,
    itd_lowpass_cutoff_hz: float | None = None,
    ild_num_bands: int = DEFAULT_ILD_NUM_BANDS,
    ild_low_freq_hz: float = DEFAULT_ILD_LOW_FREQ_HZ,
    ild_high_freq_hz: float = DEFAULT_ILD_HIGH_FREQ_HZ,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
) -> CueBankResult:
    reference_time_response = _response_to_time_domain(reference_response)
    estimated_time_response = _response_to_time_domain(estimated_response)
    if reference_time_response.shape != estimated_time_response.shape:
        raise ValueError(
            "Reference and estimated responses must share the same shape."
        )

    erb_center_freq_hz, ild_ref, ild_est = _compute_ild_cues(
        reference_time_response,
        estimated_time_response,
        sample_rate_hz=sample_rate_hz,
        num_bands=ild_num_bands,
        low_freq_hz=ild_low_freq_hz,
        high_freq_hz=ild_high_freq_hz,
    )
    tau_samples, gcc_phat_ref, gcc_phat_est, ref_peak_lags, est_peak_lags = _compute_itd_cues(
        reference_time_response,
        estimated_time_response,
        sample_rate_hz=sample_rate_hz,
        tau_seconds=tau_seconds,
        lowpass_cutoff_hz=itd_lowpass_cutoff_hz,
    )
    metrics = CueBankMetrics(
        ild_error_db=float(np.mean(np.abs(ild_est - ild_ref))),
        itd_proxy_error=float(np.mean((gcc_phat_est - gcc_phat_ref) ** 2)),
        mean_ref_itd_lag_samples=float(np.mean(ref_peak_lags)),
        mean_est_itd_lag_samples=float(np.mean(est_peak_lags)),
    )
    return CueBankResult(
        schema_version=DEFAULT_SCHEMA_VERSION,
        interface_version=DEFAULT_INTERFACE_VERSION,
        producer_task_id=DEFAULT_PRODUCER_TASK_ID,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
        sample_rate_hz=sample_rate_hz,
        tau_seconds=tau_seconds,
        tau_samples=tau_samples,
        itd_lowpass_cutoff_hz=itd_lowpass_cutoff_hz,
        erb_center_freq_hz=erb_center_freq_hz,
        ild_ref=ild_ref,
        ild_est=ild_est,
        gcc_phat_ref=gcc_phat_ref,
        gcc_phat_est=gcc_phat_est,
        ref_itd_lag_samples=ref_peak_lags,
        est_itd_lag_samples=est_peak_lags,
        metrics=metrics,
    )


def compute_itd_loss_torch(
    reference_response: Any,
    estimated_response: Any,
    *,
    sample_rate_hz: int,
    tau_seconds: float = DEFAULT_TAU_SECONDS,
    eps: float = 1e-12,
) -> tuple[Any, dict[str, Any]]:
    torch = _get_torch_module()
    if torch is False:
        raise RuntimeError("Torch is not installed in the active environment.")
    if reference_response.ndim != 3 or estimated_response.ndim != 3:
        raise ValueError("Expected response tensors with shape [direction, frequency_bin, ear=2].")
    if reference_response.shape != estimated_response.shape:
        raise ValueError("Reference and estimated response tensors must share the same shape.")
    if reference_response.shape[-1] != 2:
        raise ValueError("Expected ear axis size 2.")

    fft_size = (reference_response.shape[1] - 1) * 2
    tau_samples = _tau_seconds_to_samples(sample_rate_hz, tau_seconds, signal_length=fft_size)

    def _to_gcc_phat_window(response_tensor: Any) -> tuple[Any, Any]:
        time_response = torch.fft.irfft(response_tensor, n=fft_size, dim=1)
        left = time_response[:, :, 0]
        right = time_response[:, :, 1]
        n_fft = left.shape[-1] * 2 - 1
        cross_spectrum = torch.fft.rfft(left, n=n_fft, dim=-1) * torch.conj(
            torch.fft.rfft(right, n=n_fft, dim=-1)
        )
        magnitude = torch.clamp(torch.abs(cross_spectrum), min=eps)
        centered = torch.roll(
            torch.fft.irfft(cross_spectrum / magnitude, n=n_fft, dim=-1),
            shifts=n_fft // 2,
            dims=-1,
        )
        center_index = n_fft // 2
        window = centered[:, center_index - tau_samples : center_index + tau_samples + 1]
        peak_lags = torch.argmax(window, dim=-1) - tau_samples
        return window, peak_lags

    gcc_phat_ref, ref_peak_lags = _to_gcc_phat_window(reference_response)
    gcc_phat_est, est_peak_lags = _to_gcc_phat_window(estimated_response)
    loss = torch.mean((gcc_phat_est - gcc_phat_ref) ** 2)
    return loss, {
        "tau_samples": tau_samples,
        "gcc_phat_ref": gcc_phat_ref,
        "gcc_phat_est": gcc_phat_est,
        "ref_peak_lags": ref_peak_lags,
        "est_peak_lags": est_peak_lags,
    }


def compute_ild_loss_torch(
    reference_response: Any,
    estimated_response: Any,
    *,
    eps: float = 1e-12,
) -> tuple[Any, dict[str, Any]]:
    """Return a differentiable broadband ILD proxy for optimization loops.

    The machine-readable evaluation path still uses the ERB-band auditory ILD
    implementation in ``build_cue_bank``. This helper exists so TASK-0006 can
    keep ILD in the autograd loss loop without duplicating cue-bank logic.
    """

    torch = _get_torch_module()
    if torch is False:
        raise RuntimeError("Torch is not installed in the active environment.")
    if reference_response.ndim != 3 or estimated_response.ndim != 3:
        raise ValueError("Expected response tensors with shape [direction, frequency_bin, ear=2].")
    if reference_response.shape != estimated_response.shape:
        raise ValueError("Reference and estimated response tensors must share the same shape.")
    if reference_response.shape[-1] != 2:
        raise ValueError("Expected ear axis size 2.")

    fft_size = (reference_response.shape[1] - 1) * 2

    def _broadband_ild_db(response_tensor: Any) -> Any:
        time_response = torch.fft.irfft(response_tensor, n=fft_size, dim=1)
        left_power = torch.mean(time_response[:, :, 0] ** 2, dim=1)
        right_power = torch.mean(time_response[:, :, 1] ** 2, dim=1)
        return 10.0 * torch.log10((left_power + eps) / (right_power + eps))

    ild_ref = _broadband_ild_db(reference_response)
    ild_est = _broadband_ild_db(estimated_response)
    loss = torch.mean((ild_est - ild_ref) ** 2)
    return loss, {
        "ild_ref_db": ild_ref,
        "ild_est_db": ild_est,
    }


def inspect_cue_bank(
    repo_root: Path | str = REPO_ROOT,
    *,
    array_id: str = DEFAULT_ARRAY_ID,
    hrtf_id: str = DEFAULT_HRTF_ID,
    baseline_name: str = BASELINE_NAME_MAGLS,
    sample_rate_hz: int = 32000,
    tau_seconds: float = DEFAULT_TAU_SECONDS,
    itd_lowpass_cutoff_hz: float | None = None,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
) -> CueBankResult:
    baseline_result = inspect_baseline_renderer(
        repo_root=repo_root,
        array_id=array_id,
        hrtf_id=hrtf_id,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
        baseline_name=baseline_name,
    )
    return build_cue_bank(
        baseline_result.target_response,
        baseline_result.response,
        sample_rate_hz=sample_rate_hz,
        tau_seconds=tau_seconds,
        itd_lowpass_cutoff_hz=itd_lowpass_cutoff_hz,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
    )


def _build_synthetic_response_examples(
    *,
    sample_rate_hz: int,
    fft_size: int = 1024,
) -> tuple[np.ndarray, np.ndarray]:
    direction_count = 2
    reference_time = np.zeros((direction_count, fft_size, 2), dtype=np.float64)
    estimated_time = np.zeros_like(reference_time)

    left_index = 80
    reference_time[0, left_index, 0] = 1.00
    reference_time[0, left_index + 3, 1] = 0.80
    reference_time[0, left_index + 18, 0] = 0.35
    reference_time[0, left_index + 21, 1] = 0.28

    estimated_time[0, left_index, 0] = 0.96
    estimated_time[0, left_index + 2, 1] = 0.82
    estimated_time[0, left_index + 18, 0] = 0.31
    estimated_time[0, left_index + 20, 1] = 0.30

    reference_time[1, left_index + 10, 0] = 0.70
    reference_time[1, left_index + 8, 1] = 1.10
    reference_time[1, left_index + 26, 0] = 0.20
    reference_time[1, left_index + 24, 1] = 0.24

    estimated_time[1, left_index + 10, 0] = 0.74
    estimated_time[1, left_index + 9, 1] = 1.02
    estimated_time[1, left_index + 26, 0] = 0.19
    estimated_time[1, left_index + 25, 1] = 0.22

    reference_response = np.fft.rfft(reference_time, n=fft_size, axis=1).astype(np.complex64)
    estimated_response = np.fft.rfft(estimated_time, n=fft_size, axis=1).astype(np.complex64)
    expected_tau_samples = int(round(sample_rate_hz * DEFAULT_TAU_SECONDS))
    if expected_tau_samples <= 0:
        raise RuntimeError("Synthetic smoke examples require a positive tau window.")
    return reference_response, estimated_response


def smoke_cue_bank(
    *,
    sample_rate_hz: int = 32000,
    tau_seconds: float = DEFAULT_TAU_SECONDS,
    itd_lowpass_cutoff_hz: float | None = None,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
) -> dict[str, object]:
    reference_response, estimated_response = _build_synthetic_response_examples(
        sample_rate_hz=sample_rate_hz
    )
    result = build_cue_bank(
        reference_response,
        estimated_response,
        sample_rate_hz=sample_rate_hz,
        tau_seconds=tau_seconds,
        itd_lowpass_cutoff_hz=itd_lowpass_cutoff_hz,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
    )
    return {
        "ok": True,
        "synthetic_direction_count": int(reference_response.shape[0]),
        "summary": result.to_summary(),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 02 cue bank and paper-aligned ITD core.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--repo-root", default=str(REPO_ROOT))
    report_parser.add_argument("--array-id", default=DEFAULT_ARRAY_ID)
    report_parser.add_argument("--hrtf-id", default=DEFAULT_HRTF_ID)
    report_parser.add_argument("--baseline-name", default=BASELINE_NAME_MAGLS)
    report_parser.add_argument("--sample-rate-hz", type=int, default=32000)
    report_parser.add_argument("--tau-seconds", type=float, default=DEFAULT_TAU_SECONDS)
    report_parser.add_argument("--itd-lowpass-cutoff-hz", type=float, default=None)
    report_parser.add_argument("--producer-session-id", default=DEFAULT_PRODUCER_SESSION_ID)
    report_parser.add_argument("--run-config-ref", default=DEFAULT_RUN_CONFIG_REF)
    report_parser.add_argument("--indent", type=int, default=2)

    smoke_parser = subparsers.add_parser("smoke")
    smoke_parser.add_argument("--sample-rate-hz", type=int, default=32000)
    smoke_parser.add_argument("--tau-seconds", type=float, default=DEFAULT_TAU_SECONDS)
    smoke_parser.add_argument("--itd-lowpass-cutoff-hz", type=float, default=None)
    smoke_parser.add_argument("--producer-session-id", default=DEFAULT_PRODUCER_SESSION_ID)
    smoke_parser.add_argument("--run-config-ref", default=DEFAULT_RUN_CONFIG_REF)
    smoke_parser.add_argument("--indent", type=int, default=2)

    return parser


def _run_cli() -> int:
    args = _build_parser().parse_args()
    if args.command == "report":
        result = inspect_cue_bank(
            repo_root=args.repo_root,
            array_id=args.array_id,
            hrtf_id=args.hrtf_id,
            baseline_name=args.baseline_name,
            sample_rate_hz=args.sample_rate_hz,
            tau_seconds=args.tau_seconds,
            itd_lowpass_cutoff_hz=args.itd_lowpass_cutoff_hz,
            producer_session_id=args.producer_session_id,
            run_config_ref=args.run_config_ref,
        )
        print(json.dumps(result.to_summary(), indent=args.indent, sort_keys=True))
        return 0

    report = smoke_cue_bank(
        sample_rate_hz=args.sample_rate_hz,
        tau_seconds=args.tau_seconds,
        itd_lowpass_cutoff_hz=args.itd_lowpass_cutoff_hz,
        producer_session_id=args.producer_session_id,
        run_config_ref=args.run_config_ref,
    )
    print(json.dumps(report, indent=args.indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_cli())
