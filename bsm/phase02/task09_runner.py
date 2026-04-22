from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import time
from typing import Any

import numpy as np

from .asset_environment import (
    DEFAULT_ARRAY_ID,
    DEFAULT_HRTF_ID,
    DEFAULT_INTERFACE_VERSION,
    DEFAULT_SCHEMA_VERSION,
    REPO_ROOT,
    resolve_environment_name,
)
from .baseline_renderer import BASELINE_NAME_MAGLS, render_coefficients
from .cue_bank import build_cue_bank
from .front_end_bundle import (
    FrontEndBundle,
    OrientationCoefficientEntry,
    resolve_front_end_bundle,
    select_orientation_coefficients,
)
from .residual_solver import (
    FCRMixerResidualSolver,
    ResidualSolverConfig,
    SolverInputPack,
    build_solver_input_pack,
    compose_joint_coefficients,
    compute_loss_breakdown_torch,
    render_response_torch,
)


DEFAULT_PRODUCER_TASK_ID = "TASK-0009"
DEFAULT_PRODUCER_SESSION_ID = "SESSION-P2-0011"
DEFAULT_RUN_CONFIG_REF = "phase02/task09_planned_optimization_campaign"
DEFAULT_ARTIFACT_ROOT = REPO_ROOT / "06_Assets" / "Generated_Artifacts" / "TASK-0009"
DEFAULT_POWER_MODE = "ac_no_system_sleep"
DEFAULT_SLEEP_POLICY_NOTE = "AC power connected; display sleep allowed; system sleep disabled for authoritative runs."
DEFAULT_RETAINED_CRITERION = "best_composite"
RAW_LOSS_NAMES = ("mag", "dmag", "ild", "itd", "reg")
UNWEIGHTED_LOSS = {
    "mag": 1.0,
    "dmag": 1.0,
    "ild": 1.0,
    "itd": 1.0,
    "reg": 1.0,
}


@dataclass(frozen=True)
class WeightStage:
    mag: float
    dmag: float
    ild: float
    itd: float
    reg: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)

    def as_mapping(self) -> dict[str, float]:
        return self.to_dict()


@dataclass(frozen=True)
class LossProfile:
    name: str
    warmup: WeightStage
    main: WeightStage
    final: WeightStage

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "warmup": self.warmup.to_dict(),
            "main": self.main.to_dict(),
            "final": self.final.to_dict(),
        }


LOSS_PROFILES: dict[str, LossProfile] = {
    "balanced_norm_v1": LossProfile(
        name="balanced_norm_v1",
        warmup=WeightStage(mag=0.40, dmag=0.25, ild=0.20, itd=0.10, reg=0.05),
        main=WeightStage(mag=0.30, dmag=0.20, ild=0.25, itd=0.20, reg=0.05),
        final=WeightStage(mag=0.25, dmag=0.15, ild=0.30, itd=0.25, reg=0.05),
    ),
    "spatial_norm_v1": LossProfile(
        name="spatial_norm_v1",
        warmup=WeightStage(mag=0.35, dmag=0.20, ild=0.25, itd=0.15, reg=0.05),
        main=WeightStage(mag=0.20, dmag=0.15, ild=0.35, itd=0.25, reg=0.05),
        final=WeightStage(mag=0.15, dmag=0.10, ild=0.40, itd=0.30, reg=0.05),
    ),
    "fidelity_norm_v1": LossProfile(
        name="fidelity_norm_v1",
        warmup=WeightStage(mag=0.45, dmag=0.25, ild=0.15, itd=0.10, reg=0.05),
        main=WeightStage(mag=0.40, dmag=0.25, ild=0.20, itd=0.10, reg=0.05),
        final=WeightStage(mag=0.35, dmag=0.20, ild=0.25, itd=0.15, reg=0.05),
    ),
    "paper_ild_guarded_v1": LossProfile(
        name="paper_ild_guarded_v1",
        warmup=WeightStage(mag=0.40, dmag=0.20, ild=0.30, itd=0.05, reg=0.05),
        main=WeightStage(mag=0.28, dmag=0.17, ild=0.45, itd=0.05, reg=0.05),
        final=WeightStage(mag=0.22, dmag=0.13, ild=0.55, itd=0.05, reg=0.05),
    ),
    "paper_ild_push_v1": LossProfile(
        name="paper_ild_push_v1",
        warmup=WeightStage(mag=0.35, dmag=0.20, ild=0.35, itd=0.05, reg=0.05),
        main=WeightStage(mag=0.22, dmag=0.13, ild=0.55, itd=0.05, reg=0.05),
        final=WeightStage(mag=0.15, dmag=0.10, ild=0.65, itd=0.05, reg=0.05),
    ),
    "paper_ild_push_v2": LossProfile(
        name="paper_ild_push_v2",
        warmup=WeightStage(mag=0.35, dmag=0.25, ild=0.30, itd=0.05, reg=0.05),
        main=WeightStage(mag=0.20, dmag=0.20, ild=0.50, itd=0.05, reg=0.05),
        final=WeightStage(mag=0.15, dmag=0.20, ild=0.55, itd=0.05, reg=0.05),
    ),
}


@dataclass(frozen=True)
class Task09RunConfig:
    run_id: str
    orientation_yaw_deg: int
    seed: int
    iterations: int
    learning_rate: float
    loss_profile: str
    eval_every: int
    checkpoint_every: int
    max_frequency_bins: int | None
    max_coefficients: int | None
    early_stop_patience: int
    warmup_fraction: float = 0.10
    final_fraction: float = 0.20
    normalization_ema_decay: float = 0.95
    normalization_eps: float = 1e-8
    optimizer_name: str = "Adam"
    retained_criterion: str = DEFAULT_RETAINED_CRITERION
    power_mode: str = DEFAULT_POWER_MODE
    sleep_policy_note: str = DEFAULT_SLEEP_POLICY_NOTE

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class NormalizedLossController:
    profile: LossProfile
    total_iterations: int
    warmup_fraction: float
    final_fraction: float
    ema_decay: float
    eps: float
    ema: dict[str, float]
    scales: dict[str, float] | None = None
    frozen_iteration: int | None = None

    @classmethod
    def from_config(cls, run_config: Task09RunConfig) -> "NormalizedLossController":
        return cls(
            profile=LOSS_PROFILES[run_config.loss_profile],
            total_iterations=run_config.iterations,
            warmup_fraction=run_config.warmup_fraction,
            final_fraction=run_config.final_fraction,
            ema_decay=run_config.normalization_ema_decay,
            eps=run_config.normalization_eps,
            ema={name: 0.0 for name in RAW_LOSS_NAMES},
        )

    @property
    def warmup_iterations(self) -> int:
        return max(1, int(round(self.total_iterations * self.warmup_fraction)))

    @property
    def final_start_iteration(self) -> int:
        final_span = max(1, int(round(self.total_iterations * self.final_fraction)))
        return max(self.warmup_iterations, self.total_iterations - final_span + 1)

    def stage_name(self, iteration: int) -> str:
        if iteration < self.warmup_iterations:
            return "warmup"
        if iteration >= self.final_start_iteration:
            return "final"
        return "main"

    def stage_weights(self, iteration: int) -> dict[str, float]:
        return getattr(self.profile, self.stage_name(iteration)).as_mapping()

    def state_dict(self) -> dict[str, object]:
        return {
            "profile_name": self.profile.name,
            "total_iterations": self.total_iterations,
            "warmup_fraction": self.warmup_fraction,
            "final_fraction": self.final_fraction,
            "ema_decay": self.ema_decay,
            "eps": self.eps,
            "ema": dict(self.ema),
            "scales": None if self.scales is None else dict(self.scales),
            "frozen_iteration": self.frozen_iteration,
        }

    @classmethod
    def from_state_dict(cls, state: dict[str, object]) -> "NormalizedLossController":
        controller = cls(
            profile=LOSS_PROFILES[str(state["profile_name"])],
            total_iterations=int(state["total_iterations"]),
            warmup_fraction=float(state["warmup_fraction"]),
            final_fraction=float(state["final_fraction"]),
            ema_decay=float(state["ema_decay"]),
            eps=float(state["eps"]),
            ema={name: float(value) for name, value in dict(state["ema"]).items()},
            scales=None,
            frozen_iteration=None,
        )
        scales = state.get("scales")
        if isinstance(scales, dict):
            controller.scales = {name: float(value) for name, value in scales.items()}
        frozen_iteration = state.get("frozen_iteration")
        controller.frozen_iteration = None if frozen_iteration is None else int(frozen_iteration)
        return controller

    def describe_policy(self) -> dict[str, object]:
        return {
            "profile": self.profile.to_dict(),
            "warmup_iterations": self.warmup_iterations,
            "final_start_iteration": self.final_start_iteration,
            "ema_decay": self.ema_decay,
            "eps": self.eps,
            "rule": "Warmup accumulates frozen raw-loss scales via EMA. After warmup, optimize sum(lambda_i * loss_i / scale_i).",
        }

    def _freeze_if_ready(self, iteration: int) -> None:
        if self.scales is None and iteration + 1 >= self.warmup_iterations:
            self.scales = {
                name: max(float(self.ema[name]), self.eps)
                for name in RAW_LOSS_NAMES
            }
            self.frozen_iteration = iteration

    def observe_training_losses(
        self,
        iteration: int,
        raw_losses: dict[str, Any],
        *,
        device: Any,
    ) -> tuple[Any, dict[str, object]]:
        torch = _get_torch_module()
        weights = self.stage_weights(iteration)
        if self.scales is None:
            for name in RAW_LOSS_NAMES:
                current = float(raw_losses[name])
                if self.ema[name] == 0.0:
                    self.ema[name] = current
                else:
                    self.ema[name] = self.ema_decay * self.ema[name] + (1.0 - self.ema_decay) * current
            self._freeze_if_ready(iteration)
        if self.scales is None:
            components = {
                name: weights[name] * raw_losses[name]
                for name in RAW_LOSS_NAMES
            }
            objective_type = "warmup_raw_weighted"
        else:
            components = {
                name: weights[name]
                * (
                    raw_losses[name]
                    / max(float(self.scales[name]), self.eps)
                )
                for name in RAW_LOSS_NAMES
            }
            objective_type = "normalized_weighted"
        objective = sum(components.values())
        details = {
            "stage": self.stage_name(iteration),
            "stage_weights": weights,
            "objective_type": objective_type,
            "scales": None if self.scales is None else dict(self.scales),
            "warmup_ema": dict(self.ema),
            "frozen_iteration": self.frozen_iteration,
            "objective_components": {
                name: float(component.detach().cpu().item()) if hasattr(component, "detach") else float(component)
                for name, component in components.items()
            },
        }
        return objective, details

    def composite_score(self, iteration: int, raw_losses: dict[str, float]) -> float:
        weights = self.stage_weights(iteration)
        if self.scales is None:
            return float(sum(weights[name] * float(raw_losses[name]) for name in RAW_LOSS_NAMES))
        return float(
            sum(
                weights[name] * (float(raw_losses[name]) / max(float(self.scales[name]), self.eps))
                for name in RAW_LOSS_NAMES
            )
        )


def _get_torch_module() -> Any:
    try:
        import torch  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Torch is required for TASK-0009 optimization runs.") from exc
    return torch


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


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=_json_default),
        encoding="utf-8",
    )


def _append_jsonl(path: Path, payload: dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, default=_json_default) + "\n")


def _optional_positive_int(value: str) -> int | None:
    parsed = int(value)
    return None if parsed <= 0 else parsed


def _orientation_summary(entry: OrientationCoefficientEntry) -> dict[str, object]:
    summary = entry.to_summary()
    return {
        "yaw_deg": summary["yaw_deg"],
        "pitch_deg": summary["pitch_deg"],
        "roll_deg": summary["roll_deg"],
        "c_ls_shape": summary["c_ls_shape"],
        "c_magls_shape": summary["c_magls_shape"],
        "c_ls_source": summary["c_ls_source"],
        "c_magls_source": summary["c_magls_source"],
        "coefficient_axis_semantics": summary["coefficient_axis_semantics"],
        "reference_path": summary.get("reference_path"),
        "reference_sha256": summary.get("reference_sha256"),
    }


def _select_orientation_bundle(
    front_end_bundle: FrontEndBundle,
    *,
    yaw_deg: int,
) -> tuple[FrontEndBundle, dict[str, object]]:
    entry = select_orientation_coefficients(front_end_bundle, yaw_deg=yaw_deg)
    selected = _orientation_summary(entry)
    return (
        FrontEndBundle(
            schema_version=front_end_bundle.schema_version,
            interface_version=front_end_bundle.interface_version,
            producer_task_id=front_end_bundle.producer_task_id,
            producer_session_id=front_end_bundle.producer_session_id,
            run_config_ref=front_end_bundle.run_config_ref,
            array_id=front_end_bundle.array_id,
            hrtf_id=front_end_bundle.hrtf_id,
            sample_rate_hz=front_end_bundle.sample_rate_hz,
            fft_size=front_end_bundle.fft_size,
            grid=front_end_bundle.grid,
            optimization_grid=front_end_bundle.optimization_grid,
            V=front_end_bundle.V,
            h=front_end_bundle.h,
            c_ls=entry.c_ls.astype(np.complex64, copy=True),
            c_magls=entry.c_magls.astype(np.complex64, copy=True),
            asset_bundle=front_end_bundle.asset_bundle,
            c_ls_source=entry.c_ls_source,
            c_magls_source=entry.c_magls_source,
            coefficient_axis_semantics=entry.coefficient_axis_semantics,
            emagls_compute_sample_rate_hz=front_end_bundle.emagls_compute_sample_rate_hz,
            emagls_nfft=front_end_bundle.emagls_nfft,
            emagls_reference_yaw_deg=entry.yaw_deg,
            emagls_reference_path=entry.reference_path,
            emagls_reference_sha256=entry.reference_sha256,
            orientation_coefficients=front_end_bundle.orientation_coefficients,
        ),
        selected,
    )


def _slice_front_end_bundle(
    front_end_bundle: FrontEndBundle,
    *,
    max_frequency_bins: int | None,
    max_coefficients: int | None,
) -> FrontEndBundle:
    frequency_count = front_end_bundle.c_magls.shape[0]
    coefficient_count = front_end_bundle.c_magls.shape[1]
    selected_frequency_count = frequency_count if max_frequency_bins is None else min(max_frequency_bins, frequency_count)
    selected_coefficient_count = coefficient_count if max_coefficients is None else min(max_coefficients, coefficient_count)
    if selected_frequency_count < 2:
        raise ValueError("TASK-0009 requires at least two frequency bins.")
    if ((selected_frequency_count - 1) * 2) - 1 < 32:
        raise ValueError(
            "TASK-0009 frequency selection is too short for the ITD proxy path. "
            "Select at least 18 frequency bins."
        )
    if selected_coefficient_count < 1:
        raise ValueError("TASK-0009 requires at least one coefficient.")
    orientation_coefficients = {
        yaw_deg: OrientationCoefficientEntry(
            yaw_deg=entry.yaw_deg,
            pitch_deg=entry.pitch_deg,
            roll_deg=entry.roll_deg,
            c_ls=entry.c_ls[:selected_frequency_count, :selected_coefficient_count, :].astype(np.complex64, copy=True),
            c_magls=entry.c_magls[:selected_frequency_count, :selected_coefficient_count, :].astype(np.complex64, copy=True),
            c_ls_source=entry.c_ls_source,
            c_magls_source=entry.c_magls_source,
            coefficient_axis_semantics=entry.coefficient_axis_semantics,
            reference_path=entry.reference_path,
            reference_sha256=entry.reference_sha256,
        )
        for yaw_deg, entry in front_end_bundle.orientation_coefficients.items()
    }
    return FrontEndBundle(
        schema_version=front_end_bundle.schema_version,
        interface_version=front_end_bundle.interface_version,
        producer_task_id=front_end_bundle.producer_task_id,
        producer_session_id=front_end_bundle.producer_session_id,
        run_config_ref=front_end_bundle.run_config_ref,
        array_id=front_end_bundle.array_id,
        hrtf_id=front_end_bundle.hrtf_id,
        sample_rate_hz=front_end_bundle.sample_rate_hz,
        fft_size=(selected_frequency_count - 1) * 2,
        grid=front_end_bundle.grid,
        optimization_grid=front_end_bundle.optimization_grid,
        V=front_end_bundle.V[:, :selected_frequency_count, :selected_coefficient_count],
        h=front_end_bundle.h[:, :selected_frequency_count, :],
        c_ls=front_end_bundle.c_ls[:selected_frequency_count, :selected_coefficient_count, :],
        c_magls=front_end_bundle.c_magls[:selected_frequency_count, :selected_coefficient_count, :],
        asset_bundle=front_end_bundle.asset_bundle,
        c_ls_source=front_end_bundle.c_ls_source,
        c_magls_source=front_end_bundle.c_magls_source,
        coefficient_axis_semantics=front_end_bundle.coefficient_axis_semantics,
        emagls_compute_sample_rate_hz=front_end_bundle.emagls_compute_sample_rate_hz,
        emagls_nfft=front_end_bundle.emagls_nfft,
        emagls_reference_yaw_deg=front_end_bundle.emagls_reference_yaw_deg,
        emagls_reference_path=front_end_bundle.emagls_reference_path,
        emagls_reference_sha256=front_end_bundle.emagls_reference_sha256,
        orientation_coefficients=orientation_coefficients,
    )


def _build_solver_assets(
    front_end_bundle: FrontEndBundle,
    *,
    run_config: Task09RunConfig,
    solver_config: ResidualSolverConfig,
) -> tuple[FrontEndBundle, dict[str, object], SolverInputPack]:
    selected_bundle, selected_orientation = _select_orientation_bundle(
        front_end_bundle,
        yaw_deg=run_config.orientation_yaw_deg,
    )
    run_bundle = _slice_front_end_bundle(
        selected_bundle,
        max_frequency_bins=run_config.max_frequency_bins,
        max_coefficients=run_config.max_coefficients,
    )
    run_entry = select_orientation_coefficients(run_bundle, yaw_deg=run_config.orientation_yaw_deg)
    solver_input_pack = build_solver_input_pack(
        run_bundle,
        include_front_end_energy_descriptor=solver_config.include_front_end_energy_descriptor,
        selected_orientation=_orientation_summary(run_entry),
        producer_task_id=DEFAULT_PRODUCER_TASK_ID,
        producer_session_id=DEFAULT_PRODUCER_SESSION_ID,
        run_config_ref=DEFAULT_RUN_CONFIG_REF,
    )
    return run_bundle, _orientation_summary(run_entry), solver_input_pack


def _expand_learned_coefficients(
    evaluation_bundle: FrontEndBundle,
    learned_coefficients: np.ndarray,
) -> np.ndarray:
    expanded = evaluation_bundle.c_magls.astype(np.complex64, copy=True)
    frequency_count = min(expanded.shape[0], learned_coefficients.shape[0])
    coefficient_count = min(expanded.shape[1], learned_coefficients.shape[1])
    expanded[:frequency_count, :coefficient_count, :] = learned_coefficients[:frequency_count, :coefficient_count, :]
    return expanded


def _response_metrics(target_response: np.ndarray, estimated_response: np.ndarray) -> tuple[float, float]:
    eps = np.finfo(np.float64).tiny
    magnitude_numerator = float(np.mean((np.abs(estimated_response) - np.abs(target_response)) ** 2))
    magnitude_denominator = float(max(np.mean(np.abs(target_response) ** 2), eps))
    residual = estimated_response - target_response
    nmse = float(np.mean(np.abs(residual) ** 2) / magnitude_denominator)
    return magnitude_numerator / magnitude_denominator, nmse


def _metric_summary(
    front_end_bundle: FrontEndBundle,
    response: np.ndarray,
    *,
    producer_session_id: str,
    run_config_ref: str,
) -> dict[str, float]:
    cue_result = build_cue_bank(
        front_end_bundle.h,
        response,
        sample_rate_hz=front_end_bundle.sample_rate_hz,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
    )
    normalized_magnitude_error, nmse = _response_metrics(front_end_bundle.h, response)
    return {
        "ild_error": float(cue_result.metrics.ild_error_db),
        "itd_proxy_error": float(cue_result.metrics.itd_proxy_error),
        "normalized_magnitude_error": float(normalized_magnitude_error),
        "nmse": float(nmse),
    }


def _composite_metric_from_summary(summary: dict[str, float]) -> float:
    return float(
        summary["ild_error"]
        + summary["itd_proxy_error"]
        + summary["normalized_magnitude_error"]
        + summary["nmse"]
    )


def _seed_everything(seed: int) -> None:
    torch = _get_torch_module()
    np.random.seed(seed)
    torch.manual_seed(seed)


def _grad_norm(parameters: Any) -> float | None:
    total_sq = 0.0
    found = False
    for parameter in parameters:
        if parameter.grad is None:
            continue
        grad = parameter.grad.detach()
        total_sq += float(grad.norm().cpu().item()) ** 2
        found = True
    if not found:
        return None
    return math.sqrt(total_sq)


def _checkpoint_paths(checkpoint_dir: Path) -> dict[str, Path]:
    return {
        "last": checkpoint_dir / "last.pt",
        "best_loss": checkpoint_dir / "best_loss.pt",
        "best_composite": checkpoint_dir / "best_composite.pt",
    }


def _save_checkpoint(
    path: Path,
    *,
    iteration: int,
    run_config: Task09RunConfig,
    solver_config: ResidualSolverConfig,
    solver: Any,
    optimizer: Any,
    loss_controller: NormalizedLossController,
    best_loss: float,
    best_composite: float,
    best_loss_iteration: int,
    best_composite_iteration: int,
    summary_path: Path,
    run_manifest_path: Path,
    selected_orientation: dict[str, object],
) -> None:
    torch = _get_torch_module()
    torch.save(
        {
            "iteration": iteration,
            "run_config": run_config.to_dict(),
            "solver_config": solver_config.to_dict(),
            "model_state_dict": solver.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "loss_controller": loss_controller.state_dict(),
            "best_loss": float(best_loss),
            "best_composite": float(best_composite),
            "best_loss_iteration": int(best_loss_iteration),
            "best_composite_iteration": int(best_composite_iteration),
            "summary_path": str(summary_path),
            "run_manifest_path": str(run_manifest_path),
            "selected_orientation": selected_orientation,
        },
        path,
    )


def _load_checkpoint(path: Path) -> dict[str, object]:
    torch = _get_torch_module()
    return torch.load(path, map_location="cpu", weights_only=False)


def _checkpoint_ref(path: Path, artifact_dir: Path) -> str:
    try:
        return str(path.relative_to(artifact_dir))
    except ValueError:
        return str(path)


def _initial_summary(run_manifest_path: Path) -> dict[str, object]:
    return {
        "manifest_ref": str(run_manifest_path),
        "best_checkpoint_refs": {},
        "selected_retained_criterion": DEFAULT_RETAINED_CRITERION,
        "best_iteration": None,
        "final_iteration": None,
        "stop_reason": None,
        "retained_metric_summary": None,
    }


def _update_summary(
    summary_path: Path,
    *,
    summary: dict[str, object],
) -> None:
    _write_json(summary_path, summary)


def _build_run_manifest(
    artifact_dir: Path,
    *,
    run_config: Task09RunConfig,
    solver_config: ResidualSolverConfig,
    solver_input_pack: SolverInputPack,
    selected_orientation: dict[str, object],
    front_end_bundle: FrontEndBundle,
    loss_controller: NormalizedLossController,
) -> dict[str, object]:
    return {
        "schema_version": DEFAULT_SCHEMA_VERSION,
        "interface_version": DEFAULT_INTERFACE_VERSION,
        "producer_task_id": DEFAULT_PRODUCER_TASK_ID,
        "producer_session_id": DEFAULT_PRODUCER_SESSION_ID,
        "run_config_ref": DEFAULT_RUN_CONFIG_REF,
        "run_id": run_config.run_id,
        "orientation_yaw_deg": run_config.orientation_yaw_deg,
        "selected_orientation": selected_orientation,
        "seed": run_config.seed,
        "optimizer": run_config.optimizer_name,
        "learning_rate": run_config.learning_rate,
        "loss_profile": run_config.loss_profile,
        "normalized_loss_policy": loss_controller.describe_policy(),
        "checkpoint_cadence": run_config.checkpoint_every,
        "evaluation_cadence": run_config.eval_every,
        "artifact_root": str(artifact_dir),
        "environment_name": resolve_environment_name(),
        "power_mode": run_config.power_mode,
        "sleep_policy_note": run_config.sleep_policy_note,
        "front_end_bundle_summary": front_end_bundle.to_summary(),
        "solver_input_summary": solver_input_pack.to_summary(),
        "solver_config": solver_config.to_dict(),
        "run_config": run_config.to_dict(),
    }


def _comparison_payload(
    *,
    artifact_dir: Path,
    run_config: Task09RunConfig,
    evaluation_bundle: FrontEndBundle,
    selected_orientation: dict[str, object],
    retained_checkpoint: Path,
    retained_response: np.ndarray,
) -> dict[str, object]:
    retained_metrics = _metric_summary(
        evaluation_bundle,
        retained_response,
        producer_session_id=DEFAULT_PRODUCER_SESSION_ID,
        run_config_ref=DEFAULT_RUN_CONFIG_REF,
    )
    saved_reference_coefficients = select_orientation_coefficients(
        evaluation_bundle,
        yaw_deg=run_config.orientation_yaw_deg,
    ).c_magls
    baselines = []
    for baseline_name, coefficients in (
        (BASELINE_NAME_MAGLS, evaluation_bundle.c_magls),
        ("saved_aligned_ypr_eMagLS_reference", saved_reference_coefficients),
    ):
        baseline_response = render_coefficients(evaluation_bundle, coefficients)
        metric_summary = _metric_summary(
            evaluation_bundle,
            baseline_response,
            producer_session_id=DEFAULT_PRODUCER_SESSION_ID,
            run_config_ref=DEFAULT_RUN_CONFIG_REF,
        )
        baselines.append(
            {
                "baseline_name": baseline_name,
                "metric_summary": metric_summary,
                "composite_metric": _composite_metric_from_summary(metric_summary),
                "coefficient_equal_to_front_end_magls": bool(np.allclose(coefficients, evaluation_bundle.c_magls)),
            }
        )

    retained_composite = _composite_metric_from_summary(retained_metrics)
    baseline_composites = [float(entry["composite_metric"]) for entry in baselines]
    if all(retained_composite < baseline_value for baseline_value in baseline_composites):
        verdict = "retain_learned_checkpoint"
    elif any(retained_composite < baseline_value for baseline_value in baseline_composites):
        verdict = "retain_for_followup_review"
    else:
        verdict = "baseline_not_beaten"
    return {
        "schema_version": DEFAULT_SCHEMA_VERSION,
        "interface_version": DEFAULT_INTERFACE_VERSION,
        "producer_task_id": DEFAULT_PRODUCER_TASK_ID,
        "producer_session_id": DEFAULT_PRODUCER_SESSION_ID,
        "run_config_ref": DEFAULT_RUN_CONFIG_REF,
        "retained_run_id": run_config.run_id,
        "retained_checkpoint": _checkpoint_ref(retained_checkpoint, artifact_dir),
        "selected_orientation": selected_orientation,
        "retained_metric_summary": retained_metrics,
        "retained_composite_metric": retained_composite,
        "comparison_baselines": baselines,
        "concise_retention_verdict": verdict,
    }


def _write_comparison_summary(
    artifact_dir: Path,
    *,
    run_config: Task09RunConfig,
    training_bundle: FrontEndBundle,
    evaluation_bundle: FrontEndBundle,
    solver_input_pack: SolverInputPack,
    solver_config: ResidualSolverConfig,
    checkpoint_path: Path,
    selected_orientation: dict[str, object],
) -> dict[str, object]:
    torch = _get_torch_module()
    checkpoint = _load_checkpoint(checkpoint_path)
    solver = FCRMixerResidualSolver(
        input_channels=solver_input_pack.solver_input_packed.shape[-1],
        config=solver_config,
    )
    solver.load_state_dict(checkpoint["model_state_dict"])
    solver.eval()
    solver_input_tensor = torch.as_tensor(solver_input_pack.solver_input_packed, dtype=torch.float32)
    c_magls = torch.as_tensor(training_bundle.c_magls, dtype=torch.complex64)
    with torch.no_grad():
        delta_c, alpha = solver(solver_input_tensor)
        c_joint = compose_joint_coefficients(c_magls, delta_c, alpha)
    learned_coefficients = c_joint.detach().cpu().numpy().astype(np.complex64)
    expanded_coefficients = _expand_learned_coefficients(evaluation_bundle, learned_coefficients)
    retained_response = render_coefficients(evaluation_bundle, expanded_coefficients)
    payload = _comparison_payload(
        artifact_dir=artifact_dir,
        run_config=run_config,
        evaluation_bundle=evaluation_bundle,
        selected_orientation=selected_orientation,
        retained_checkpoint=checkpoint_path,
        retained_response=retained_response,
    )
    _write_json(artifact_dir / "comparison_summary.json", payload)
    return payload


def train_task09_run(
    front_end_bundle: FrontEndBundle,
    *,
    run_config: Task09RunConfig,
    solver_config: ResidualSolverConfig,
    artifact_dir: Path | str | None = None,
    resume_from: Path | str | None = None,
) -> dict[str, object]:
    if run_config.iterations <= 0:
        raise ValueError("iterations must be positive.")
    if run_config.eval_every <= 0 or run_config.checkpoint_every <= 0:
        raise ValueError("eval_every and checkpoint_every must be positive.")
    if run_config.loss_profile not in LOSS_PROFILES:
        raise ValueError(f"Unknown loss_profile {run_config.loss_profile!r}.")

    torch = _get_torch_module()
    _seed_everything(run_config.seed)
    artifact_dir_path = Path(artifact_dir) if artifact_dir is not None else (DEFAULT_ARTIFACT_ROOT / run_config.run_id)
    artifact_dir_path.mkdir(parents=True, exist_ok=True)
    checkpoint_dir = artifact_dir_path / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_paths = _checkpoint_paths(checkpoint_dir)
    evaluation_bundle, _ = _select_orientation_bundle(
        front_end_bundle,
        yaw_deg=run_config.orientation_yaw_deg,
    )
    run_bundle, selected_orientation, solver_input_pack = _build_solver_assets(
        front_end_bundle,
        run_config=run_config,
        solver_config=solver_config,
    )
    solver = FCRMixerResidualSolver(
        input_channels=solver_input_pack.solver_input_packed.shape[-1],
        config=solver_config,
    )
    optimizer = torch.optim.Adam(solver.parameters(), lr=run_config.learning_rate)
    loss_controller = NormalizedLossController.from_config(run_config)
    solver_input_tensor = torch.as_tensor(solver_input_pack.solver_input_packed, dtype=torch.float32)
    c_magls = torch.as_tensor(run_bundle.c_magls, dtype=torch.complex64)
    run_manifest_path = artifact_dir_path / "run_manifest.json"
    loss_trace_path = artifact_dir_path / "loss_trace.jsonl"
    eval_trace_path = artifact_dir_path / "eval_trace.jsonl"
    summary_path = artifact_dir_path / "summary.json"
    comparison_path = artifact_dir_path / "comparison_summary.json"

    if resume_from is None:
        for path in (loss_trace_path, eval_trace_path, comparison_path):
            if path.exists():
                path.unlink()
        summary = _initial_summary(run_manifest_path)
        start_iteration = 0
        best_loss = float("inf")
        best_composite = float("inf")
        best_loss_iteration = -1
        best_composite_iteration = -1
    else:
        checkpoint = _load_checkpoint(Path(resume_from))
        solver.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        loss_controller = NormalizedLossController.from_state_dict(
            dict(checkpoint["loss_controller"])
        )
        if run_config.iterations != int(checkpoint["run_config"]["iterations"]):
            loss_controller.total_iterations = run_config.iterations
        start_iteration = int(checkpoint["iteration"]) + 1
        best_loss = float(checkpoint["best_loss"])
        best_composite = float(checkpoint["best_composite"])
        best_loss_iteration = int(checkpoint["best_loss_iteration"])
        best_composite_iteration = int(checkpoint["best_composite_iteration"])
        summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else _initial_summary(run_manifest_path)

    run_manifest = _build_run_manifest(
        artifact_dir_path,
        run_config=run_config,
        solver_config=solver_config,
        solver_input_pack=solver_input_pack,
        selected_orientation=selected_orientation,
        front_end_bundle=run_bundle,
        loss_controller=loss_controller,
    )
    _write_json(run_manifest_path, run_manifest)
    _update_summary(summary_path, summary=summary)

    start_time = time.perf_counter()
    stop_reason = "max_iterations_reached"
    stale_evaluations = 0
    final_iteration = start_iteration - 1

    for iteration in range(start_iteration, run_config.iterations + 1):
        final_iteration = iteration
        solver.train()
        optimizer.zero_grad(set_to_none=True)
        delta_c, alpha = solver(solver_input_tensor)
        c_joint = compose_joint_coefficients(c_magls, delta_c, alpha)
        _, breakdown = compute_loss_breakdown_torch(
            run_bundle,
            c_joint=c_joint,
            delta_c=delta_c,
            weights=type("UnitWeights", (), UNWEIGHTED_LOSS)(),  # type: ignore[misc]
        )
        raw_losses_tensor = {
            "mag": breakdown["loss_mag"],
            "dmag": breakdown["loss_dmag"],
            "ild": breakdown["loss_ild"],
            "itd": breakdown["loss_itd"],
            "reg": breakdown["loss_reg"],
        }
        raw_losses = {
            name: float(value.detach().cpu().item())
            for name, value in raw_losses_tensor.items()
        }
        objective, objective_details = loss_controller.observe_training_losses(
            iteration,
            raw_losses_tensor,
            device=solver_input_tensor.device,
        )
        grad_norm = None
        if iteration < run_config.iterations:
            objective.backward()
            grad_norm = _grad_norm(solver.parameters())
            optimizer.step()
        residual_norm = float(torch.linalg.vector_norm(torch.view_as_real(delta_c)).detach().cpu().item())
        _append_jsonl(
            loss_trace_path,
            {
                "iteration": iteration,
                "wall_time_sec": float(time.perf_counter() - start_time),
                "learning_rate": float(optimizer.param_groups[0]["lr"]),
                "alpha": float(alpha.detach().cpu().item()),
                "loss_total": float(objective.detach().cpu().item()),
                "loss_mag": raw_losses["mag"],
                "loss_dmag": raw_losses["dmag"],
                "loss_ild": raw_losses["ild"],
                "loss_itd": raw_losses["itd"],
                "loss_reg": raw_losses["reg"],
                "residual_norm": residual_norm,
                "grad_norm": grad_norm,
                "objective_details": objective_details,
            },
        )

        composite_score = loss_controller.composite_score(iteration, raw_losses)
        if float(objective.detach().cpu().item()) < best_loss:
            best_loss = float(objective.detach().cpu().item())
            best_loss_iteration = iteration
            _save_checkpoint(
                checkpoint_paths["best_loss"],
                iteration=iteration,
                run_config=run_config,
                solver_config=solver_config,
                solver=solver,
                optimizer=optimizer,
                loss_controller=loss_controller,
                best_loss=best_loss,
                best_composite=best_composite,
                best_loss_iteration=best_loss_iteration,
                best_composite_iteration=best_composite_iteration,
                summary_path=summary_path,
                run_manifest_path=run_manifest_path,
                selected_orientation=selected_orientation,
            )
        if composite_score < best_composite:
            best_composite = composite_score
            best_composite_iteration = iteration
            stale_evaluations = 0
            _save_checkpoint(
                checkpoint_paths["best_composite"],
                iteration=iteration,
                run_config=run_config,
                solver_config=solver_config,
                solver=solver,
                optimizer=optimizer,
                loss_controller=loss_controller,
                best_loss=best_loss,
                best_composite=best_composite,
                best_loss_iteration=best_loss_iteration,
                best_composite_iteration=best_composite_iteration,
                summary_path=summary_path,
                run_manifest_path=run_manifest_path,
                selected_orientation=selected_orientation,
            )

        should_save_last = (iteration % run_config.checkpoint_every == 0) or (iteration == run_config.iterations)
        if should_save_last:
            _save_checkpoint(
                checkpoint_paths["last"],
                iteration=iteration,
                run_config=run_config,
                solver_config=solver_config,
                solver=solver,
                optimizer=optimizer,
                loss_controller=loss_controller,
                best_loss=best_loss,
                best_composite=best_composite,
                best_loss_iteration=best_loss_iteration,
                best_composite_iteration=best_composite_iteration,
                summary_path=summary_path,
                run_manifest_path=run_manifest_path,
                selected_orientation=selected_orientation,
            )

        should_evaluate = (iteration % run_config.eval_every == 0) or (iteration == run_config.iterations)
        if should_evaluate:
            solver.eval()
            with torch.no_grad():
                eval_delta_c, eval_alpha = solver(solver_input_tensor)
                eval_joint = compose_joint_coefficients(c_magls, eval_delta_c, eval_alpha)
                eval_response = render_response_torch(run_bundle, eval_joint).detach().cpu().numpy().astype(np.complex64)
            metric_summary = _metric_summary(
                run_bundle,
                eval_response,
                producer_session_id=DEFAULT_PRODUCER_SESSION_ID,
                run_config_ref=DEFAULT_RUN_CONFIG_REF,
            )
            validation_score = loss_controller.composite_score(iteration, raw_losses)
            if validation_score > best_composite:
                stale_evaluations += 1
            best_checkpoint_ref = (
                _checkpoint_ref(checkpoint_paths[run_config.retained_criterion], artifact_dir_path)
                if checkpoint_paths[run_config.retained_criterion].exists()
                else None
            )
            _append_jsonl(
                eval_trace_path,
                {
                    "iteration": iteration,
                    "checkpoint_ref": best_checkpoint_ref,
                    "validation_score_composite": validation_score,
                    "ild_error": metric_summary["ild_error"],
                    "itd_proxy_error": metric_summary["itd_proxy_error"],
                    "normalized_magnitude_error": metric_summary["normalized_magnitude_error"],
                    "nmse": metric_summary["nmse"],
                    "retained_best_loss": best_loss,
                    "retained_best_composite": best_composite,
                },
            )
            summary.update(
                {
                    "best_checkpoint_refs": {
                        name: str(path)
                        for name, path in checkpoint_paths.items()
                        if path.exists()
                    },
                    "selected_retained_criterion": run_config.retained_criterion,
                    "best_iteration": best_composite_iteration if run_config.retained_criterion == "best_composite" else best_loss_iteration,
                    "final_iteration": iteration,
                    "stop_reason": stop_reason,
                    "retained_metric_summary": metric_summary,
                }
            )
            _update_summary(summary_path, summary=summary)
            if stale_evaluations >= run_config.early_stop_patience:
                stop_reason = f"early_stop_no_composite_improvement_{run_config.early_stop_patience}"
                break

    retained_checkpoint = checkpoint_paths[run_config.retained_criterion]
    comparison_summary = _write_comparison_summary(
        artifact_dir_path,
        run_config=run_config,
        training_bundle=run_bundle,
        evaluation_bundle=evaluation_bundle,
        solver_input_pack=solver_input_pack,
        solver_config=solver_config,
        checkpoint_path=retained_checkpoint,
        selected_orientation=selected_orientation,
    )
    summary.update(
        {
            "best_checkpoint_refs": {
                name: str(path)
                for name, path in checkpoint_paths.items()
                if path.exists()
            },
            "selected_retained_criterion": run_config.retained_criterion,
            "best_iteration": best_composite_iteration if run_config.retained_criterion == "best_composite" else best_loss_iteration,
            "final_iteration": final_iteration,
            "stop_reason": stop_reason,
            "retained_metric_summary": comparison_summary["retained_metric_summary"],
            "comparison_summary_ref": str(comparison_path),
        }
    )
    _update_summary(summary_path, summary=summary)
    return {
        "ok": True,
        "artifact_dir": str(artifact_dir_path),
        "run_manifest": run_manifest,
        "summary": summary,
        "comparison_summary": comparison_summary,
    }


def compare_task09_run(
    artifact_dir: Path | str,
    *,
    checkpoint_ref: str = DEFAULT_RETAINED_CRITERION,
    repo_root: Path | str = REPO_ROOT,
    array_id: str = DEFAULT_ARRAY_ID,
    hrtf_id: str = DEFAULT_HRTF_ID,
    front_end_bundle: FrontEndBundle | None = None,
) -> dict[str, object]:
    artifact_dir_path = Path(artifact_dir)
    run_manifest = json.loads((artifact_dir_path / "run_manifest.json").read_text(encoding="utf-8"))
    run_config = Task09RunConfig(**run_manifest["run_config"])
    solver_config = ResidualSolverConfig(**run_manifest["solver_config"])
    effective_bundle = front_end_bundle
    if effective_bundle is None:
        effective_bundle = resolve_front_end_bundle(
            repo_root=repo_root,
            array_id=array_id,
            hrtf_id=hrtf_id,
            producer_session_id=DEFAULT_PRODUCER_SESSION_ID,
            run_config_ref=DEFAULT_RUN_CONFIG_REF,
        )
    evaluation_bundle, _ = _select_orientation_bundle(
        effective_bundle,
        yaw_deg=run_config.orientation_yaw_deg,
    )
    run_bundle, selected_orientation, solver_input_pack = _build_solver_assets(
        effective_bundle,
        run_config=run_config,
        solver_config=solver_config,
    )
    checkpoint_path = artifact_dir_path / "checkpoints" / f"{checkpoint_ref}.pt"
    payload = _write_comparison_summary(
        artifact_dir_path,
        run_config=run_config,
        training_bundle=run_bundle,
        evaluation_bundle=evaluation_bundle,
        solver_input_pack=solver_input_pack,
        solver_config=solver_config,
        checkpoint_path=checkpoint_path,
        selected_orientation=selected_orientation,
    )
    summary_path = artifact_dir_path / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["comparison_summary_ref"] = str(artifact_dir_path / "comparison_summary.json")
        summary["retained_metric_summary"] = payload["retained_metric_summary"]
        _update_summary(summary_path, summary=summary)
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TASK-0009 planned optimization campaign runner.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train")
    train_parser.add_argument("--repo-root", default=str(REPO_ROOT))
    train_parser.add_argument("--array-id", default=DEFAULT_ARRAY_ID)
    train_parser.add_argument("--hrtf-id", default=DEFAULT_HRTF_ID)
    train_parser.add_argument("--run-id", required=True)
    train_parser.add_argument("--orientation-yaw-deg", type=int, default=90)
    train_parser.add_argument("--seed", type=int, default=3401)
    train_parser.add_argument("--iterations", type=int, default=1200)
    train_parser.add_argument("--learning-rate", type=float, default=1e-3)
    train_parser.add_argument("--loss-profile", default="balanced_norm_v1", choices=sorted(LOSS_PROFILES))
    train_parser.add_argument("--eval-every", type=int, default=100)
    train_parser.add_argument("--checkpoint-every", type=int, default=200)
    train_parser.add_argument("--max-frequency-bins", type=_optional_positive_int, default=129)
    train_parser.add_argument("--max-coefficients", type=_optional_positive_int, default=None)
    train_parser.add_argument("--early-stop-patience", type=int, default=4)
    train_parser.add_argument("--artifact-dir", default=None)
    train_parser.add_argument("--resume-from", default=None)
    train_parser.add_argument("--hidden-dim", type=int, default=24)
    train_parser.add_argument("--block-count", type=int, default=2)
    train_parser.add_argument("--rank", type=int, default=4)
    train_parser.add_argument("--alpha-init", type=float, default=0.15)
    train_parser.add_argument("--alpha-max", type=float, default=0.35)
    train_parser.add_argument("--include-front-end-energy-descriptor", action="store_true")
    train_parser.add_argument("--power-mode", default=DEFAULT_POWER_MODE)
    train_parser.add_argument("--sleep-policy-note", default=DEFAULT_SLEEP_POLICY_NOTE)
    train_parser.add_argument("--indent", type=int, default=2)

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--artifact-dir", required=True)
    compare_parser.add_argument("--checkpoint-ref", default=DEFAULT_RETAINED_CRITERION)
    compare_parser.add_argument("--repo-root", default=str(REPO_ROOT))
    compare_parser.add_argument("--array-id", default=DEFAULT_ARRAY_ID)
    compare_parser.add_argument("--hrtf-id", default=DEFAULT_HRTF_ID)
    compare_parser.add_argument("--indent", type=int, default=2)

    return parser


def _run_cli() -> int:
    args = _build_parser().parse_args()
    if args.command == "train":
        front_end_bundle = resolve_front_end_bundle(
            repo_root=args.repo_root,
            array_id=args.array_id,
            hrtf_id=args.hrtf_id,
            producer_session_id=DEFAULT_PRODUCER_SESSION_ID,
            run_config_ref=DEFAULT_RUN_CONFIG_REF,
        )
        report = train_task09_run(
            front_end_bundle,
            run_config=Task09RunConfig(
                run_id=args.run_id,
                orientation_yaw_deg=args.orientation_yaw_deg,
                seed=args.seed,
                iterations=args.iterations,
                learning_rate=args.learning_rate,
                loss_profile=args.loss_profile,
                eval_every=args.eval_every,
                checkpoint_every=args.checkpoint_every,
                max_frequency_bins=args.max_frequency_bins,
                max_coefficients=args.max_coefficients,
                early_stop_patience=args.early_stop_patience,
                power_mode=args.power_mode,
                sleep_policy_note=args.sleep_policy_note,
            ),
            solver_config=ResidualSolverConfig(
                hidden_dim=args.hidden_dim,
                block_count=args.block_count,
                rank=args.rank,
                alpha_init=args.alpha_init,
                alpha_max=args.alpha_max,
                include_front_end_energy_descriptor=args.include_front_end_energy_descriptor,
            ),
            artifact_dir=args.artifact_dir,
            resume_from=args.resume_from,
        )
        print(json.dumps(report, indent=args.indent, sort_keys=True, default=_json_default))
        return 0
    report = compare_task09_run(
        args.artifact_dir,
        checkpoint_ref=args.checkpoint_ref,
        repo_root=args.repo_root,
        array_id=args.array_id,
        hrtf_id=args.hrtf_id,
    )
    print(json.dumps(report, indent=args.indent, sort_keys=True, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_cli())
