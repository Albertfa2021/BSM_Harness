from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import numpy as np
import scipy.signal as signal
import soundfile

from .asset_environment import (
    DEFAULT_ARRAY_ID,
    DEFAULT_HRTF_ID,
    DEFAULT_INTERFACE_VERSION,
    DEFAULT_SCHEMA_VERSION,
    REPO_ROOT,
    inspect_asset_bundle,
)
from .array2binaural_emagls import (
    banded_coefficient_metrics,
    build_visible_raw_array2binaural_emagls_coefficients,
    canonicalize_saved_aligned_ypr_emagls,
    compare_emagls_to_saved_reference,
    load_saved_aligned_ypr_emagls_reference_details,
    mismatch_probe_metrics,
    saved_aligned_ypr_reference_path,
    sha256_file,
)
from .baseline_renderer import render_coefficients
from .cue_bank import build_cue_bank
from .front_end_bundle import (
    DEFAULT_FFT_SIZE,
    DEFAULT_SAMPLE_RATE_HZ,
    FrontEndBundle,
    resolve_front_end_bundle,
    select_orientation_coefficients,
)
from .residual_solver import build_solver_input_pack, render_response_torch


DEFAULT_PRODUCER_TASK_ID = "TASK-0007"
DEFAULT_PRODUCER_SESSION_ID = "SESSION-P2-0008"
DEFAULT_RUN_CONFIG_REF = "phase02/pre_training_correctness_validation"
DEFAULT_ARTIFACT_ROOT = REPO_ROOT / "06_Assets" / "Generated_Artifacts" / "TASK-0007"
REFERENCE_YAWS_DEG = (0, 90)
COEFFICIENT_PARITY_MAX_ABS_TOLERANCE = 5e-4
COEFFICIENT_PARITY_NMSE_TOLERANCE = 1e-6
RENDERER_PARITY_MAX_ABS_TOLERANCE = 2e-5


@dataclass(frozen=True)
class ReferenceCoefficients:
    yaw_deg: int
    path: Path
    source_shape: tuple[int, ...]
    canonical_shape: tuple[int, ...]
    source_axis_semantics: str
    canonical_axis_semantics: str
    coefficients: np.ndarray


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable.")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=_json_default),
        encoding="utf-8",
    )


def _timestamped_artifact_dir(root: Path = DEFAULT_ARTIFACT_ROOT) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return root / timestamp


def _reference_coefficients_path(repo_root: Path, yaw_deg: int) -> Path:
    return saved_aligned_ypr_reference_path(repo_root, yaw_deg)


def canonicalize_reference_coefficients(
    coefficients: np.ndarray,
) -> tuple[np.ndarray, str, str]:
    """Return eMagLS coefficients as [frequency, microphone, ear]."""

    return canonicalize_saved_aligned_ypr_emagls(coefficients)


def load_reference_coefficients(repo_root: Path | str, yaw_deg: int) -> ReferenceCoefficients:
    saved_reference = load_saved_aligned_ypr_emagls_reference_details(repo_root, yaw_deg)
    return ReferenceCoefficients(
        yaw_deg=saved_reference.yaw_deg,
        path=saved_reference.path,
        source_shape=saved_reference.source_shape,
        canonical_shape=saved_reference.canonical_shape,
        source_axis_semantics=saved_reference.source_axis_semantics,
        canonical_axis_semantics=saved_reference.canonical_axis_semantics,
        coefficients=saved_reference.coefficients,
    )


def _sha256(path: Path) -> str:
    return sha256_file(path)


def _array_file_summary(path: Path) -> dict[str, Any]:
    array = np.load(path)
    return {
        "path": str(path),
        "shape": list(array.shape),
        "dtype": str(array.dtype),
        "finite": bool(np.isfinite(array).all()),
        "file_size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def coefficient_difference_metrics(
    project_coefficients: np.ndarray,
    reference_coefficients: np.ndarray,
    *,
    sample_rate_hz: int = DEFAULT_SAMPLE_RATE_HZ,
) -> dict[str, Any]:
    project = np.asarray(project_coefficients)
    reference = np.asarray(reference_coefficients)
    if project.shape != reference.shape:
        raise ValueError(f"Coefficient shape mismatch: {project.shape} vs {reference.shape}.")
    residual = project - reference
    abs_residual = np.abs(residual)
    reference_energy = float(np.mean(np.abs(reference) ** 2))
    safe_reference_energy = max(reference_energy, np.finfo(np.float64).tiny)
    per_frequency = np.mean(abs_residual, axis=(1, 2))
    worst_count = min(8, per_frequency.shape[0])
    worst_indices = np.argsort(per_frequency)[-worst_count:][::-1]
    bin_hz = sample_rate_hz / ((project.shape[0] - 1) * 2.0)
    return {
        "max_abs": float(np.max(abs_residual)),
        "mean_abs": float(np.mean(abs_residual)),
        "rmse": float(np.sqrt(np.mean(abs_residual**2))),
        "nmse": float(np.mean(abs_residual**2) / safe_reference_energy),
        "reference_energy": reference_energy,
        "project_energy": float(np.mean(np.abs(project) ** 2)),
        "by_ear": [
            {
                "ear_index": int(ear_index),
                "max_abs": float(np.max(abs_residual[:, :, ear_index])),
                "mean_abs": float(np.mean(abs_residual[:, :, ear_index])),
                "rmse": float(np.sqrt(np.mean(abs_residual[:, :, ear_index] ** 2))),
                "nmse": float(
                    np.mean(abs_residual[:, :, ear_index] ** 2)
                    / max(float(np.mean(np.abs(reference[:, :, ear_index]) ** 2)), np.finfo(np.float64).tiny)
                ),
            }
            for ear_index in range(project.shape[-1])
        ],
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


def _response_metrics(
    response: np.ndarray,
    target_response: np.ndarray,
) -> dict[str, float]:
    residual = np.asarray(response) - np.asarray(target_response)
    target_energy = float(np.mean(np.abs(target_response) ** 2))
    safe_target_energy = max(target_energy, np.finfo(np.float64).tiny)
    return {
        "max_abs_error": float(np.max(np.abs(residual))),
        "mean_abs_error": float(np.mean(np.abs(residual))),
        "nmse": float(np.mean(np.abs(residual) ** 2) / safe_target_energy),
        "normalized_magnitude_error": float(
            np.mean((np.abs(response) - np.abs(target_response)) ** 2) / safe_target_energy
        ),
    }


def _worst_direction_records(
    front_end_bundle: FrontEndBundle,
    response: np.ndarray,
    *,
    count: int = 8,
) -> list[dict[str, Any]]:
    residual = np.abs(np.asarray(response) - np.asarray(front_end_bundle.h))
    per_direction = np.mean(residual, axis=(1, 2))
    worst_indices = np.argsort(per_direction)[-min(count, per_direction.shape[0]) :][::-1]
    return [
        {
            "direction_index": int(index),
            "azimuth_deg": float(front_end_bundle.grid.azimuth_deg[index]),
            "elevation_deg": float(front_end_bundle.grid.elevation_deg[index]),
            "mean_abs": float(per_direction[index]),
            "max_abs": float(np.max(residual[index])),
        }
        for index in worst_indices
    ]


def _renderer_parity(
    front_end_bundle: FrontEndBundle,
    coefficients: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    numpy_response = render_coefficients(front_end_bundle, coefficients)
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Torch is required for renderer parity validation.") from exc
    coefficient_tensor = torch.as_tensor(coefficients, dtype=torch.complex64)
    torch_response = render_response_torch(front_end_bundle, coefficient_tensor).detach().cpu().numpy()
    diff = numpy_response - torch_response
    return numpy_response, {
        "max_abs": float(np.max(np.abs(diff))),
        "mean_abs": float(np.mean(np.abs(diff))),
        "nmse": float(
            np.mean(np.abs(diff) ** 2)
            / max(float(np.mean(np.abs(numpy_response) ** 2)), np.finfo(np.float64).tiny)
        ),
        "numpy_response_shape": list(numpy_response.shape),
        "torch_response_shape": list(torch_response.shape),
        "finite": {
            "numpy_response": bool(np.isfinite(numpy_response).all()),
            "torch_response": bool(np.isfinite(torch_response).all()),
        },
    }


def _render_validation(
    front_end_bundle: FrontEndBundle,
    reference_coefficients: dict[int, ReferenceCoefficients],
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    candidates: dict[str, np.ndarray] = {
        "c_ls": front_end_bundle.c_ls,
        "project_bsm_magls": front_end_bundle.c_magls,
    }
    for yaw_deg, entry in sorted(front_end_bundle.orientation_coefficients.items()):
        candidates[f"project_bsm_magls_yaw_{yaw_deg}"] = entry.c_magls
    for yaw_deg, reference in reference_coefficients.items():
        candidates[f"array2binaural_emagls_reference_yaw_{yaw_deg}"] = reference.coefficients

    response_by_name: dict[str, np.ndarray] = {}
    candidate_metrics: dict[str, Any] = {}
    for name, coefficients in candidates.items():
        response, renderer_metrics = _renderer_parity(front_end_bundle, coefficients)
        response_by_name[name] = response
        candidate_metrics[name] = {
            "coefficient_shape": list(coefficients.shape),
            "response_shape": list(response.shape),
            "finite": {
                "coefficients": bool(np.isfinite(coefficients).all()),
                "response": bool(np.isfinite(response).all()),
            },
            "renderer_numpy_torch": renderer_metrics,
            "target_comparison": _response_metrics(response, front_end_bundle.h),
            "worst_directions": _worst_direction_records(front_end_bundle, response),
        }

    ok = all(
        metrics["renderer_numpy_torch"]["max_abs"] <= RENDERER_PARITY_MAX_ABS_TOLERANCE
        and metrics["finite"]["response"]
        for metrics in candidate_metrics.values()
    )
    return {
        "ok": bool(ok),
        "renderer_parity_max_abs_tolerance": RENDERER_PARITY_MAX_ABS_TOLERANCE,
        "target_shape": list(front_end_bundle.h.shape),
        "candidates": candidate_metrics,
    }, response_by_name


def _cue_validation(
    front_end_bundle: FrontEndBundle,
    response_by_name: dict[str, np.ndarray],
) -> dict[str, Any]:
    candidates = {
        name: response
        for name, response in response_by_name.items()
        if name != "c_ls"
    }
    summaries: dict[str, Any] = {}
    for name, response in candidates.items():
        result = build_cue_bank(
            front_end_bundle.h,
            response,
            sample_rate_hz=front_end_bundle.sample_rate_hz,
            producer_session_id=DEFAULT_PRODUCER_SESSION_ID,
            run_config_ref=DEFAULT_RUN_CONFIG_REF,
        )
        summaries[name] = result.to_summary()
    finite = all(
        all(candidate["finite"].values())
        and np.isfinite(list(candidate["metrics"].values())).all()
        for candidate in summaries.values()
    )
    return {
        "ok": bool(finite),
        "reference_definitions": {
            "ild": "ERB-band AuditoryToolbox Python replication",
            "itd": "GCC-PHAT proxy window aligned to ITD-loss paper semantics",
        },
        "candidates": summaries,
    }


def _select_direction_index(front_end_bundle: FrontEndBundle, azimuth_deg: float) -> int:
    azimuths = np.asarray(front_end_bundle.grid.azimuth_deg, dtype=np.float64)
    wrapped = np.abs(((azimuths - azimuth_deg + 180.0) % 360.0) - 180.0)
    return int(np.argmin(wrapped))


def _test_signal(sample_rate_hz: int, duration_seconds: float = 0.75) -> np.ndarray:
    sample_count = int(round(sample_rate_hz * duration_seconds))
    time = np.arange(sample_count, dtype=np.float64) / sample_rate_hz
    chirp = signal.chirp(time, f0=160.0, f1=7000.0, t1=duration_seconds, method="logarithmic")
    envelope = signal.windows.tukey(sample_count, 0.18)
    return (0.35 * chirp * envelope).astype(np.float64)


def _response_direction_to_audio(
    response: np.ndarray,
    direction_index: int,
    *,
    sample_rate_hz: int,
) -> tuple[np.ndarray, bool]:
    impulse = np.fft.irfft(response[direction_index], n=(response.shape[1] - 1) * 2, axis=0)
    dry = _test_signal(sample_rate_hz)
    stereo = np.stack(
        [
            signal.fftconvolve(dry, impulse[:, 0], mode="full"),
            signal.fftconvolve(dry, impulse[:, 1], mode="full"),
        ],
        axis=-1,
    )
    stereo = np.asarray(stereo, dtype=np.float64)
    if not np.isfinite(stereo).all():
        raise RuntimeError("Generated listening audio contains non-finite samples.")
    peak = float(np.max(np.abs(stereo)))
    normalized = False
    if peak > 0.95:
        stereo = stereo * (0.95 / peak)
        normalized = True
    return stereo.astype(np.float32), normalized


def write_listening_audio_artifacts(
    artifact_dir: Path | str,
    front_end_bundle: FrontEndBundle,
    response_by_name: dict[str, np.ndarray],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    artifact_path = Path(artifact_dir)
    audio_dir = artifact_path / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    cases = [
        ("frontal", 0.0, "project_bsm_magls_yaw_0", "array2binaural_emagls_reference_yaw_0"),
        ("lateral_left", 90.0, "project_bsm_magls_yaw_0", "array2binaural_emagls_reference_yaw_0"),
        ("lateral_right", -90.0, "project_bsm_magls_yaw_0", "array2binaural_emagls_reference_yaw_0"),
        ("rear", 180.0, "project_bsm_magls_yaw_0", "array2binaural_emagls_reference_yaw_0"),
        ("rotation_90", 0.0, "project_bsm_magls_yaw_90", "array2binaural_emagls_reference_yaw_90"),
    ]
    manifest_entries: list[dict[str, Any]] = []
    for case_name, azimuth_deg, project_name, reference_name in cases:
        direction_index = _select_direction_index(front_end_bundle, azimuth_deg)
        project_response = response_by_name.get(project_name, response_by_name["project_bsm_magls"])
        case_sources = [
            ("target", "target", front_end_bundle.h),
            ("project_bsm_magls", project_name, project_response),
        ]
        if reference_name in response_by_name:
            case_sources.append(
                ("array2binaural_emagls_reference", reference_name, response_by_name[reference_name])
            )
        for label, source_response, response in case_sources:
            audio, normalized = _response_direction_to_audio(
                response,
                direction_index,
                sample_rate_hz=front_end_bundle.sample_rate_hz,
            )
            peak = float(np.max(np.abs(audio)))
            file_name = f"{case_name}__{label}.wav"
            path = audio_dir / file_name
            soundfile.write(str(path), audio, front_end_bundle.sample_rate_hz)
            manifest_entries.append(
                {
                    "file_path": str(path),
                    "label": label,
                    "case": case_name,
                    "source_response": source_response,
                    "direction_index": direction_index,
                    "azimuth_deg": float(front_end_bundle.grid.azimuth_deg[direction_index]),
                    "elevation_deg": float(front_end_bundle.grid.elevation_deg[direction_index]),
                    "sample_rate_hz": front_end_bundle.sample_rate_hz,
                    "duration_seconds": float(audio.shape[0] / front_end_bundle.sample_rate_hz),
                    "channels": int(audio.shape[1]),
                    "peak_amplitude": peak,
                    "finite": bool(np.isfinite(audio).all()),
                    "normalized_to_prevent_clipping": normalized,
                    "non_clipping": bool(peak <= 1.0),
                }
            )
    manifest = {
        "ok": bool(
            manifest_entries
            and all(entry["channels"] == 2 and entry["finite"] and entry["non_clipping"] for entry in manifest_entries)
        ),
        "entries": manifest_entries,
    }
    return manifest, manifest_entries


def _write_listening_notes(path: Path, artifact_dir: Path, manifest_entries: list[dict[str, Any]]) -> None:
    lines = [
        "# TASK-0007 Listening Notes",
        "",
        f"Artifact directory: `{artifact_dir}`",
        "Listener: pending human headphone review",
        f"Date: {datetime.now(timezone.utc).date().isoformat()}",
        "Playback device: pending human headphone review",
        "",
        "| Case | File | Channel Swap | Direction Plausible | Coloration | ITD Stability | Level Balance | Clipping/Artifacts | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in manifest_entries:
        lines.append(
            "| {case} | `{file}` | pending human check | pending human check | "
            "pending human check | pending human check | pending human check | "
            "machine peak {peak:.6f}; finite stereo WAV; no sample clipping | "
            "{label} generated from {source}; automated run cannot provide perceptual judgement |".format(
                case=entry["case"],
                file=Path(entry["file_path"]).name,
                peak=entry["peak_amplitude"],
                label=entry["label"],
                source=entry["source_response"],
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _solver_readiness(front_end_bundle: FrontEndBundle) -> dict[str, Any]:
    pack = build_solver_input_pack(
        front_end_bundle,
        producer_session_id=DEFAULT_PRODUCER_SESSION_ID,
        run_config_ref=DEFAULT_RUN_CONFIG_REF,
    )
    summary = pack.to_summary()
    required_fields = {
        "baseline_name",
        "ild_error",
        "itd_proxy_error",
        "normalized_magnitude_error",
        "nmse",
        "selected_iteration",
        "loss_trace",
    }
    return {
        "ok": bool(all(summary["finite"].values())),
        "solver_input_summary": summary,
        "short_run_smoke_command": (
            "conda run -n bsm_harness_py311 python -m bsm.phase02.residual_solver "
            "smoke --iterations 4 --max-frequency-bins 65 --max-coefficients 96 "
            "--hidden-dim 24 --block-count 2 --rank 4 --indent 2"
        ),
        "task0006_style_required_fields": sorted(required_fields),
        "note": "The session protocol runs the residual solver smoke as a separate recorded command.",
    }


def run_audit(
    *,
    repo_root: Path | str = REPO_ROOT,
    artifact_dir: Path | str | None = None,
    skip_audio: bool = False,
    reference_rotation_yaw_deg: int = 0,
) -> dict[str, Any]:
    repo_root_path = Path(repo_root).resolve()
    output_dir = Path(artifact_dir) if artifact_dir is not None else _timestamped_artifact_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    asset_report = inspect_asset_bundle(repo_root_path)
    front_end_bundle = resolve_front_end_bundle(
        repo_root_path,
        producer_session_id=DEFAULT_PRODUCER_SESSION_ID,
        run_config_ref=DEFAULT_RUN_CONFIG_REF,
    )
    reference_coefficients = {
        yaw_deg: load_reference_coefficients(repo_root_path, yaw_deg)
        for yaw_deg in REFERENCE_YAWS_DEG
    }

    reference_files = {
        f"yaw_{yaw_deg}": _array_file_summary(reference.path)
        for yaw_deg, reference in reference_coefficients.items()
    }
    gate_asset = {
        "ok": bool(
            asset_report.ok
            and all(file_summary["finite"] for file_summary in reference_files.values())
            and front_end_bundle.sample_rate_hz == DEFAULT_SAMPLE_RATE_HZ
            and front_end_bundle.fft_size == DEFAULT_FFT_SIZE
        ),
        "asset_report": asset_report.to_dict(),
        "sample_rate_hz": front_end_bundle.sample_rate_hz,
        "fft_size": front_end_bundle.fft_size,
        "reference_files": reference_files,
        "front_end_summary": front_end_bundle.to_summary(),
    }

    selected_reference = reference_coefficients[reference_rotation_yaw_deg]
    parity_metrics = {
        "ok": False,
        "reference_rotation_yaw_deg": reference_rotation_yaw_deg,
        "reference_path": str(selected_reference.path),
        "source_shape": list(selected_reference.source_shape),
        "source_axis_semantics": selected_reference.source_axis_semantics,
        "canonical_shape": list(selected_reference.canonical_shape),
        "canonical_axis_semantics": selected_reference.canonical_axis_semantics,
        "project_shape": list(front_end_bundle.c_magls.shape),
        "orientation_bank_yaws_deg": sorted(int(yaw) for yaw in front_end_bundle.orientation_coefficients),
        "max_abs_tolerance": COEFFICIENT_PARITY_MAX_ABS_TOLERANCE,
        "nmse_tolerance": COEFFICIENT_PARITY_NMSE_TOLERANCE,
        "comparisons": {},
    }
    for yaw_deg, reference in reference_coefficients.items():
        orientation_entry = select_orientation_coefficients(front_end_bundle, yaw_deg=yaw_deg)
        comparison = coefficient_difference_metrics(
            orientation_entry.c_magls,
            reference.coefficients,
            sample_rate_hz=front_end_bundle.sample_rate_hz,
        )
        comparison["passes_direct_parity"] = bool(
            comparison["max_abs"] <= COEFFICIENT_PARITY_MAX_ABS_TOLERANCE
            and comparison["nmse"] <= COEFFICIENT_PARITY_NMSE_TOLERANCE
        )
        comparison["reference_path"] = str(reference.path)
        comparison["source_shape"] = list(reference.source_shape)
        comparison["canonical_shape"] = list(reference.canonical_shape)
        comparison["project_orientation_yaw_deg"] = int(orientation_entry.yaw_deg)
        comparison["project_orientation_source"] = orientation_entry.c_magls_source
        comparison["project_reference_path"] = orientation_entry.reference_path
        parity_metrics["comparisons"][f"yaw_{yaw_deg}"] = comparison
    selected_comparison = parity_metrics["comparisons"][f"yaw_{reference_rotation_yaw_deg}"]
    parity_metrics["ok"] = bool(selected_comparison["passes_direct_parity"])
    yaw90_comparison = parity_metrics["comparisons"].get("yaw_90")
    parity_metrics["selected_authority"] = {
        "option": "A",
        "name": "saved_array2binaural_aligned_ypr_runtime_artifact",
        "reason": (
            "The checked-in aligned-ypr files are the Array2Binaural evaluation/runtime "
            "filters consumed by the reference renderer; their exact generation script is absent."
        ),
    }
    parity_metrics["rotation_generalization"] = {
        "supported_in_front_end_bundle": True,
        "static_reference_yaw_deg": int(front_end_bundle.emagls_reference_yaw_deg or 0),
        "yaw_90_direct_parity_with_selected_bank_entry": (
            None if yaw90_comparison is None else bool(yaw90_comparison["passes_direct_parity"])
        ),
        "selection_policy": "exact_yaw_lookup_in_orientation_coefficient_bank",
        "note": (
            "The default c_magls remains yaw 0 for backward compatibility, while rotation-specific "
            "validation and listening use the selected orientation-bank entry."
        ),
    }
    if not parity_metrics["ok"]:
        parity_metrics["blocker"] = (
            "Project BSM-MagLS coefficients do not pass direct parity against the saved "
            "Array2Binaural eMagLS reference after explicit [frequency, microphone, ear] "
            "canonicalization. Training remains blocked until the mismatch is repaired or "
            "accepted with a narrowed cause."
        )

    render_metrics, response_by_name = _render_validation(front_end_bundle, reference_coefficients)
    cue_metrics = _cue_validation(front_end_bundle, response_by_name)
    solver_metrics = _solver_readiness(front_end_bundle)

    if skip_audio:
        audio_manifest = {
            "ok": False,
            "entries": [],
            "blocker": "Audio generation was skipped; human listening artifacts are required.",
        }
        manifest_entries: list[dict[str, Any]] = []
    else:
        audio_manifest, manifest_entries = write_listening_audio_artifacts(
            output_dir,
            front_end_bundle,
            response_by_name,
        )
    listening_notes_path = output_dir / "listening_notes.md"
    _write_listening_notes(listening_notes_path, output_dir, manifest_entries)

    blockers: list[dict[str, str]] = []
    if not gate_asset["ok"]:
        blockers.append({"gate": "environment_and_assets", "message": "Asset/environment invariant gate failed."})
    if not parity_metrics["ok"]:
        blockers.append({"gate": "coefficient_parity", "message": str(parity_metrics["blocker"])})
    if not render_metrics["ok"]:
        blockers.append({"gate": "renderer_parity", "message": "Numpy and torch renderer parity failed."})
    if not cue_metrics["ok"]:
        blockers.append({"gate": "cue_bank", "message": "Cue-bank metrics contain non-finite values."})
    if not solver_metrics["ok"]:
        blockers.append({"gate": "solver_readiness", "message": "Solver input/export readiness failed."})
    if not audio_manifest["ok"]:
        blockers.append({"gate": "listening_audio", "message": "Listening WAV generation failed or was skipped."})
    blockers.append(
        {
            "gate": "human_listening",
            "message": (
                "Generated listening notes still require a human headphone pass for channel swap, "
                "direction, coloration, ITD stability, level balance, and artifacts."
            ),
        }
    )

    gate_status = [
        {"name": "environment_and_assets", "ok": gate_asset["ok"]},
        {"name": "coefficient_parity", "ok": parity_metrics["ok"]},
        {"name": "renderer_parity", "ok": render_metrics["ok"]},
        {"name": "cue_bank", "ok": cue_metrics["ok"]},
        {"name": "solver_export_readiness", "ok": solver_metrics["ok"]},
        {"name": "listening_audio", "ok": audio_manifest["ok"]},
        {"name": "human_listening", "ok": False},
    ]

    artifact_refs = {
        "validation_summary": str(output_dir / "validation_summary.json"),
        "parity_metrics": str(output_dir / "parity_metrics.json"),
        "render_metrics": str(output_dir / "render_metrics.json"),
        "cue_metrics": str(output_dir / "cue_metrics.json"),
        "audio_manifest": str(output_dir / "audio_manifest.json"),
        "listening_notes": str(listening_notes_path),
        "audio_dir": str(output_dir / "audio"),
    }
    validation_summary = {
        "ok": False,
        "schema_version": DEFAULT_SCHEMA_VERSION,
        "interface_version": DEFAULT_INTERFACE_VERSION,
        "producer_task_id": DEFAULT_PRODUCER_TASK_ID,
        "producer_session_id": DEFAULT_PRODUCER_SESSION_ID,
        "run_config_ref": DEFAULT_RUN_CONFIG_REF,
        "artifact_dir": str(output_dir),
        "artifact_refs": artifact_refs,
        "gate_status": gate_status,
        "blockers": blockers,
        "training_allowed": False,
    }
    validation_summary["ok"] = bool(not blockers)
    validation_summary["training_allowed"] = bool(validation_summary["ok"])

    _write_json(output_dir / "parity_metrics.json", parity_metrics)
    _write_json(output_dir / "render_metrics.json", render_metrics)
    _write_json(output_dir / "cue_metrics.json", cue_metrics)
    _write_json(output_dir / "audio_manifest.json", audio_manifest)
    _write_json(output_dir / "validation_summary.json", validation_summary)
    return validation_summary


def diagnose_emagls(
    *,
    repo_root: Path | str = REPO_ROOT,
    yaw_deg: int = 0,
    include_visible_raw: bool = False,
) -> dict[str, Any]:
    repo_root_path = Path(repo_root).resolve()
    front_end_bundle = resolve_front_end_bundle(
        repo_root_path,
        producer_session_id=DEFAULT_PRODUCER_SESSION_ID,
        run_config_ref=DEFAULT_RUN_CONFIG_REF,
    )
    saved_reference = load_saved_aligned_ypr_emagls_reference_details(repo_root_path, yaw_deg)
    orientation_entry = select_orientation_coefficients(front_end_bundle, yaw_deg=yaw_deg)
    project_vs_saved = coefficient_difference_metrics(
        orientation_entry.c_magls,
        saved_reference.coefficients,
        sample_rate_hz=front_end_bundle.sample_rate_hz,
    )
    diagnostics: dict[str, Any] = {
        "yaw_deg": int(yaw_deg),
        "selected_authority": "saved_array2binaural_aligned_ypr_runtime_artifact",
        "coefficient_contract_conclusion": (
            "The prior failure was a coefficient-contract mismatch: project raw-like 32 kHz "
            "eMagLS and saved Array2Binaural aligned-ypr filters are distinct coefficient "
            "objects. The current front-end keeps yaw 0 as the default and exposes yaw-specific "
            "saved aligned-ypr filters through an orientation coefficient bank."
        ),
        "saved_reference": {
            "path": str(saved_reference.path),
            "sha256": saved_reference.sha256,
            "source_shape": list(saved_reference.source_shape),
            "source_axis_semantics": saved_reference.source_axis_semantics,
            "canonical_shape": list(saved_reference.canonical_shape),
            "canonical_axis_semantics": saved_reference.canonical_axis_semantics,
            "mean_energy": float(np.mean(np.abs(saved_reference.coefficients) ** 2)),
        },
        "front_end": {
            "summary": front_end_bundle.to_summary(),
            "selected_orientation": orientation_entry.to_summary(),
            "c_ls_mean_energy": float(np.mean(np.abs(front_end_bundle.c_ls) ** 2)),
            "c_magls_mean_energy": float(np.mean(np.abs(front_end_bundle.c_magls) ** 2)),
            "selected_c_magls_mean_energy": float(np.mean(np.abs(orientation_entry.c_magls) ** 2)),
            "c_magls_minus_c_ls_mean_energy": float(
                np.mean(np.abs(front_end_bundle.c_magls - front_end_bundle.c_ls) ** 2)
            ),
        },
        "project_c_magls_vs_saved_reference": project_vs_saved,
        "banded_project_c_magls_vs_saved_reference": banded_coefficient_metrics(
            orientation_entry.c_magls,
            saved_reference.coefficients,
            sample_rate_hz=front_end_bundle.sample_rate_hz,
        ),
        "mismatch_probes": mismatch_probe_metrics(
            orientation_entry.c_magls,
            saved_reference.coefficients,
        ),
        "visible_raw_array2binaural": {
            "included": bool(include_visible_raw),
            "note": (
                "Use --include-visible-raw to build the visible 48 kHz/1536 raw Array2Binaural "
                "path. That path is intentionally distinguished from the opaque saved "
                "aligned-ypr runtime artifact."
            ),
        },
    }
    if include_visible_raw:
        raw_result = build_visible_raw_array2binaural_emagls_coefficients(repo_root_path, yaw_deg=yaw_deg)
        raw_metrics = compare_emagls_to_saved_reference(raw_result, saved_reference.coefficients)
        diagnostics["visible_raw_array2binaural"] = {
            "included": True,
            "source": raw_result.source,
            "coefficient_shape": list(raw_result.coefficients.shape),
            "sample_rate_hz": raw_result.sample_rate_hz,
            "nfft": raw_result.nfft,
            "export_frequency_bins": raw_result.export_frequency_bins,
            "frequency_cut_hz": raw_result.frequency_cut_hz,
            "array_delay_samples": raw_result.array_delay_samples,
            "hrtf_delay_samples": raw_result.hrtf_delay_samples,
            "mean_energy": float(np.mean(np.abs(raw_result.coefficients) ** 2)),
            "raw_vs_saved_reference": raw_metrics,
            "raw_vs_selected_orientation_c_magls": coefficient_difference_metrics(
                raw_result.coefficients,
                orientation_entry.c_magls,
                sample_rate_hz=front_end_bundle.sample_rate_hz,
            ),
        }
    return diagnostics


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TASK-0007 pre-training correctness validation harness.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("--repo-root", default=str(REPO_ROOT))
    audit_parser.add_argument("--artifact-dir", default=None)
    audit_parser.add_argument("--skip-audio", action="store_true")
    audit_parser.add_argument("--reference-rotation-yaw-deg", type=int, default=0)
    audit_parser.add_argument("--indent", type=int, default=2)

    diagnose_parser = subparsers.add_parser("diagnose-emagls")
    diagnose_parser.add_argument("--repo-root", default=str(REPO_ROOT))
    diagnose_parser.add_argument("--yaw-deg", type=int, default=0)
    diagnose_parser.add_argument("--include-visible-raw", action="store_true")
    diagnose_parser.add_argument("--indent", type=int, default=2)
    return parser


def _run_cli() -> int:
    args = _build_parser().parse_args()
    if args.command == "audit":
        summary = run_audit(
            repo_root=args.repo_root,
            artifact_dir=args.artifact_dir,
            skip_audio=args.skip_audio,
            reference_rotation_yaw_deg=args.reference_rotation_yaw_deg,
        )
        print(json.dumps(summary, indent=args.indent, sort_keys=True, default=_json_default))
        return 0 if summary["ok"] else 1
    if args.command == "diagnose-emagls":
        diagnostics = diagnose_emagls(
            repo_root=args.repo_root,
            yaw_deg=args.yaw_deg,
            include_visible_raw=args.include_visible_raw,
        )
        print(json.dumps(diagnostics, indent=args.indent, sort_keys=True, default=_json_default))
        return 0
    raise RuntimeError(f"Unsupported command: {args.command}")  # pragma: no cover


if __name__ == "__main__":
    raise SystemExit(_run_cli())
