from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import numpy as np

from .asset_environment import (
    DEFAULT_ARRAY_ID,
    DEFAULT_HRTF_ID,
    DEFAULT_INTERFACE_VERSION,
    DEFAULT_SCHEMA_VERSION,
    REPO_ROOT,
)
from .baseline_renderer import BASELINE_NAME_MAGLS
from .cue_bank import build_cue_bank, compute_ild_loss_torch, compute_itd_loss_torch
from .front_end_bundle import (
    FrontEndBundle,
    OrientationCoefficientEntry,
    resolve_front_end_bundle,
    select_orientation_coefficients,
)


DEFAULT_PRODUCER_TASK_ID = "TASK-0006"
DEFAULT_PRODUCER_SESSION_ID = "SESSION-P2-0007"
DEFAULT_RUN_CONFIG_REF = "phase02/default_residual_solver_short_run"
DEFAULT_ARTIFACT_ROOT = REPO_ROOT / "06_Assets" / "Generated_Artifacts" / "TASK-0006"
TASK08_PRODUCER_TASK_ID = "TASK-0008"
TASK08_PRODUCER_SESSION_ID = "TASK-0008_MACHINE_ACCEPTANCE"
TASK08_RUN_CONFIG_REF = "phase02/orientation_training_path_smoke"
TASK08_ARTIFACT_ROOT = REPO_ROOT / "06_Assets" / "Generated_Artifacts" / "TASK-0008"
DEFAULT_ALPHA_MAX = 0.35
DEFAULT_ALPHA_INIT = 0.15


@dataclass(frozen=True)
class SolverInputPack:
    schema_version: str
    interface_version: str
    producer_task_id: str
    producer_session_id: str
    run_config_ref: str
    c_ls: np.ndarray
    c_magls: np.ndarray
    c_magls_minus_c_ls: np.ndarray
    normalized_frequency_index: np.ndarray
    normalized_coefficient_index: np.ndarray
    solver_input_packed: np.ndarray
    channel_names: tuple[str, ...]
    front_end_energy_descriptor: np.ndarray | None = None
    selected_orientation: dict[str, object] | None = None

    def to_summary(self) -> dict[str, object]:
        summary: dict[str, object] = {
            "schema_version": self.schema_version,
            "interface_version": self.interface_version,
            "producer_task_id": self.producer_task_id,
            "producer_session_id": self.producer_session_id,
            "run_config_ref": self.run_config_ref,
            "c_ls_shape": list(self.c_ls.shape),
            "c_magls_shape": list(self.c_magls.shape),
            "c_magls_minus_c_ls_shape": list(self.c_magls_minus_c_ls.shape),
            "normalized_frequency_index_shape": list(self.normalized_frequency_index.shape),
            "normalized_coefficient_index_shape": list(self.normalized_coefficient_index.shape),
            "solver_input_packed_shape": list(self.solver_input_packed.shape),
            "channel_names": list(self.channel_names),
            "selected_orientation": self.selected_orientation,
            "finite": {
                "c_ls": bool(np.isfinite(self.c_ls).all()),
                "c_magls": bool(np.isfinite(self.c_magls).all()),
                "c_magls_minus_c_ls": bool(np.isfinite(self.c_magls_minus_c_ls).all()),
                "normalized_frequency_index": bool(np.isfinite(self.normalized_frequency_index).all()),
                "normalized_coefficient_index": bool(np.isfinite(self.normalized_coefficient_index).all()),
                "solver_input_packed": bool(np.isfinite(self.solver_input_packed).all()),
            },
        }
        if self.front_end_energy_descriptor is not None:
            summary["front_end_energy_descriptor_shape"] = list(
                self.front_end_energy_descriptor.shape
            )
            summary["finite"]["front_end_energy_descriptor"] = bool(
                np.isfinite(self.front_end_energy_descriptor).all()
            )
        return summary


@dataclass(frozen=True)
class ResidualSolverConfig:
    hidden_dim: int = 96
    block_count: int = 6
    rank: int = 8
    alpha_init: float = DEFAULT_ALPHA_INIT
    alpha_max: float = DEFAULT_ALPHA_MAX
    include_front_end_energy_descriptor: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LossWeights:
    mag: float = 1.0
    dmag: float = 0.25
    ild: float = 0.02
    itd: float = 0.05
    reg: float = 0.01

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class LossTraceEntry:
    iteration: int
    loss_total: float
    loss_mag: float
    loss_dmag: float
    loss_ild: float
    loss_itd: float
    loss_reg: float
    residual_norm: float
    alpha: float

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


@dataclass(frozen=True)
class OptimizationExport:
    schema_version: str
    interface_version: str
    producer_task_id: str
    producer_session_id: str
    run_config_ref: str
    baseline_name: str
    ild_error: float
    itd_proxy_error: float
    normalized_magnitude_error: float
    nmse: float
    initial_loss_total: float
    final_loss_total: float
    selected_iteration: int
    loss_reduced: bool
    loss_trace_path: str
    artifact_refs: dict[str, str]
    solver_input_summary: dict[str, object]
    solver_config: dict[str, object]
    loss_weights: dict[str, float]
    selected_orientation: dict[str, object] | None = None
    orientation_bank_yaws_deg: list[int] | None = None
    task09_ready: bool = False
    blocking_issues: list[str] | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _get_torch_module() -> Any:
    try:
        import torch  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Torch is required for TASK-0006 residual solver runs.") from exc
    return torch


def _complex_numpy_to_channels(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values)
    if array.ndim != 3 or array.shape[-1] != 2:
        raise ValueError("Expected complex coefficients with shape [frequency, coefficient, ear=2].")
    return np.stack(
        [
            np.real(array[:, :, 0]),
            np.imag(array[:, :, 0]),
            np.real(array[:, :, 1]),
            np.imag(array[:, :, 1]),
        ],
        axis=-1,
    ).astype(np.float32)


def _channels_to_complex_torch(channels: Any) -> Any:
    torch = _get_torch_module()
    left = torch.complex(channels[..., 0], channels[..., 1])
    right = torch.complex(channels[..., 2], channels[..., 3])
    return torch.stack([left, right], dim=-1)


def _require_coefficient_contract(c_ls: np.ndarray, c_magls: np.ndarray) -> None:
    if c_ls.shape != c_magls.shape:
        raise ValueError(
            f"c_ls and c_magls must share shape; received {c_ls.shape} and {c_magls.shape}."
        )
    if c_ls.ndim != 3 or c_ls.shape[-1] != 2:
        raise ValueError("Expected coefficient tensors with shape [frequency, coefficient, ear=2].")
    if not np.isfinite(c_ls).all() or not np.isfinite(c_magls).all():
        raise ValueError("Solver coefficient inputs contain non-finite values.")


def _normalized_frequency_descriptor(
    frequency_count: int,
    *,
    sample_rate_hz: int,
) -> np.ndarray:
    if frequency_count <= 1:
        return np.zeros((frequency_count, 1), dtype=np.float32)
    frequency_hz = np.arange(frequency_count, dtype=np.float64) / ((frequency_count - 1) * 2.0)
    frequency_hz *= sample_rate_hz
    max_descriptor = np.log1p(sample_rate_hz / 2.0)
    return (np.log1p(frequency_hz) / max_descriptor).astype(np.float32)[:, None]


def _normalized_coefficient_descriptor(coefficient_count: int) -> np.ndarray:
    if coefficient_count <= 1:
        return np.zeros((1, coefficient_count), dtype=np.float32)
    return np.linspace(0.0, 1.0, coefficient_count, dtype=np.float32)[None, :]


def _front_end_energy_descriptor(front_end_bundle: FrontEndBundle) -> np.ndarray:
    energy = np.mean(np.abs(front_end_bundle.V) ** 2, axis=(0, 2))
    energy = np.log1p(energy)
    denom = float(np.max(energy))
    if denom <= 0.0:
        return np.zeros((energy.shape[0], 1), dtype=np.float32)
    return (energy / denom).astype(np.float32)[:, None]


def build_solver_input_pack(
    front_end_bundle: FrontEndBundle,
    *,
    include_front_end_energy_descriptor: bool = False,
    selected_orientation: dict[str, object] | None = None,
    producer_task_id: str = DEFAULT_PRODUCER_TASK_ID,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
) -> SolverInputPack:
    c_ls = np.asarray(front_end_bundle.c_ls)
    c_magls = np.asarray(front_end_bundle.c_magls)
    _require_coefficient_contract(c_ls, c_magls)

    c_delta_init = c_magls - c_ls
    frequency_count, coefficient_count, _ = c_magls.shape
    normalized_frequency = _normalized_frequency_descriptor(
        frequency_count,
        sample_rate_hz=front_end_bundle.sample_rate_hz,
    )
    normalized_coefficient = _normalized_coefficient_descriptor(coefficient_count)
    frequency_plane = np.broadcast_to(normalized_frequency[:, None, :], (frequency_count, coefficient_count, 1))
    coefficient_plane = np.broadcast_to(
        normalized_coefficient.reshape(1, coefficient_count, 1),
        (frequency_count, coefficient_count, 1),
    )

    channel_blocks = [
        _complex_numpy_to_channels(c_ls),
        _complex_numpy_to_channels(c_magls),
        _complex_numpy_to_channels(c_delta_init),
        frequency_plane.astype(np.float32),
        coefficient_plane.astype(np.float32),
    ]
    channel_names = [
        "c_ls_left_re",
        "c_ls_left_im",
        "c_ls_right_re",
        "c_ls_right_im",
        "c_magls_left_re",
        "c_magls_left_im",
        "c_magls_right_re",
        "c_magls_right_im",
        "c_magls_minus_c_ls_left_re",
        "c_magls_minus_c_ls_left_im",
        "c_magls_minus_c_ls_right_re",
        "c_magls_minus_c_ls_right_im",
        "normalized_frequency_index",
        "normalized_coefficient_index",
    ]

    energy_descriptor = None
    if include_front_end_energy_descriptor:
        energy_descriptor = _front_end_energy_descriptor(front_end_bundle)
        energy_plane = np.broadcast_to(energy_descriptor[:, None, :], (frequency_count, coefficient_count, 1))
        channel_blocks.append(energy_plane.astype(np.float32))
        channel_names.append("front_end_energy_descriptor")

    solver_input_packed = np.concatenate(channel_blocks, axis=-1).astype(np.float32)
    return SolverInputPack(
        schema_version=DEFAULT_SCHEMA_VERSION,
        interface_version=DEFAULT_INTERFACE_VERSION,
        producer_task_id=producer_task_id,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
        c_ls=c_ls.astype(np.complex64),
        c_magls=c_magls.astype(np.complex64),
        c_magls_minus_c_ls=c_delta_init.astype(np.complex64),
        normalized_frequency_index=normalized_frequency,
        normalized_coefficient_index=normalized_coefficient,
        solver_input_packed=solver_input_packed,
        channel_names=tuple(channel_names),
        front_end_energy_descriptor=energy_descriptor,
        selected_orientation=selected_orientation,
    )


class FCRMixerBlock(_get_torch_module().nn.Module):  # type: ignore[misc]
    def __init__(self, hidden_dim: int, dilation: int) -> None:
        torch = _get_torch_module()
        super().__init__()
        self.norm_coeff = torch.nn.LayerNorm(hidden_dim)
        self.coefficient_mixer = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim, hidden_dim * 2),
            torch.nn.GELU(),
            torch.nn.Linear(hidden_dim * 2, hidden_dim),
        )
        self.norm_freq = torch.nn.LayerNorm(hidden_dim)
        self.frequency_mixer = torch.nn.Conv1d(
            hidden_dim,
            hidden_dim,
            kernel_size=3,
            padding=dilation,
            dilation=dilation,
            groups=1,
        )
        self.norm_gate = torch.nn.LayerNorm(hidden_dim)
        self.binaural_gate = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.Sigmoid(),
        )

    def forward(self, hidden: Any) -> Any:
        torch = _get_torch_module()
        hidden = hidden + self.coefficient_mixer(self.norm_coeff(hidden))
        frequency_input = self.norm_freq(hidden).permute(1, 2, 0)
        frequency_delta = self.frequency_mixer(frequency_input).permute(2, 0, 1)
        hidden = hidden + frequency_delta
        gate = self.binaural_gate(self.norm_gate(hidden))
        return hidden + gate * torch.tanh(hidden)


class FCRMixerResidualSolver(_get_torch_module().nn.Module):  # type: ignore[misc]
    def __init__(self, input_channels: int, config: ResidualSolverConfig = ResidualSolverConfig()) -> None:
        torch = _get_torch_module()
        super().__init__()
        if input_channels <= 0:
            raise ValueError("input_channels must be positive.")
        if config.hidden_dim <= 0 or config.block_count <= 0 or config.rank <= 0:
            raise ValueError("hidden_dim, block_count, and rank must be positive.")
        if not 0.0 <= config.alpha_init <= config.alpha_max:
            raise ValueError("alpha_init must be inside [0, alpha_max].")
        self.config = config
        self.lift = torch.nn.Linear(input_channels, config.hidden_dim)
        self.blocks = torch.nn.ModuleList(
            [
                FCRMixerBlock(config.hidden_dim, dilation=2 ** (block_index % 3))
                for block_index in range(config.block_count)
            ]
        )
        self.local_head = torch.nn.Sequential(
            torch.nn.LayerNorm(config.hidden_dim),
            torch.nn.Linear(config.hidden_dim, 64),
            torch.nn.GELU(),
            torch.nn.Linear(64, 4),
        )
        self.frequency_head = torch.nn.Sequential(
            torch.nn.LayerNorm(config.hidden_dim),
            torch.nn.Linear(config.hidden_dim, config.rank * 4),
        )
        self.coefficient_head = torch.nn.Sequential(
            torch.nn.LayerNorm(config.hidden_dim),
            torch.nn.Linear(config.hidden_dim, config.rank),
        )
        self.blend_gate = torch.nn.Parameter(torch.tensor(0.0, dtype=torch.float32))
        alpha_ratio = np.clip(config.alpha_init / config.alpha_max, 1e-6, 1.0 - 1e-6)
        self.alpha_logit = torch.nn.Parameter(
            torch.tensor(np.log(alpha_ratio / (1.0 - alpha_ratio)), dtype=torch.float32)
        )

        with torch.no_grad():
            final_local = self.local_head[-1]
            final_local.weight.mul_(0.05)
            final_local.bias.zero_()
            self.frequency_head[-1].weight.mul_(0.05)
            self.frequency_head[-1].bias.zero_()
            self.coefficient_head[-1].weight.mul_(0.05)
            self.coefficient_head[-1].bias.zero_()

    def alpha(self) -> Any:
        torch = _get_torch_module()
        return self.config.alpha_max * torch.sigmoid(self.alpha_logit)

    def forward(self, solver_input_packed: Any) -> tuple[Any, Any]:
        torch = _get_torch_module()
        if solver_input_packed.ndim != 3:
            raise ValueError("Expected solver_input_packed with shape [frequency, coefficient, channel].")
        hidden = self.lift(solver_input_packed)
        for block in self.blocks:
            hidden = block(hidden)
        delta_local = self.local_head(hidden)
        frequency_summary = torch.mean(hidden, dim=1)
        coefficient_summary = torch.mean(hidden, dim=0)
        u = self.frequency_head(frequency_summary).reshape(
            hidden.shape[0],
            self.config.rank,
            4,
        )
        v = self.coefficient_head(coefficient_summary)
        delta_global = torch.einsum("frc,mr->fmc", u, v)
        gate = torch.sigmoid(self.blend_gate)
        delta_channels = gate * delta_local + (1.0 - gate) * delta_global
        delta_c = _channels_to_complex_torch(delta_channels)
        return delta_c, self.alpha()


def compose_joint_coefficients(c_magls: Any, delta_c: Any, alpha: Any) -> Any:
    if c_magls.shape != delta_c.shape:
        raise ValueError(f"delta_c shape {delta_c.shape} must match c_magls shape {c_magls.shape}.")
    return c_magls + alpha * delta_c


def render_response_torch(front_end_bundle: FrontEndBundle, coefficients: Any) -> Any:
    torch = _get_torch_module()
    expected_shape = front_end_bundle.c_magls.shape
    if tuple(coefficients.shape) != tuple(expected_shape):
        raise ValueError(
            f"Coefficient shape mismatch: expected {expected_shape}, received {tuple(coefficients.shape)}."
        )
    V = torch.as_tensor(front_end_bundle.V, dtype=torch.complex64, device=coefficients.device)
    return torch.einsum("dfm,fme->dfe", V, coefficients)


def _normalized_magnitude_mse(response: Any, target_response: Any, eps: float = 1e-12) -> Any:
    torch = _get_torch_module()
    numerator = torch.mean((torch.abs(response) - torch.abs(target_response)) ** 2)
    denominator = torch.clamp(torch.mean(torch.abs(target_response) ** 2), min=eps)
    return numerator / denominator


def _normalized_magnitude_derivative_mse(response: Any, target_response: Any, eps: float = 1e-12) -> Any:
    torch = _get_torch_module()
    response_diff = torch.diff(torch.abs(response), dim=1)
    target_diff = torch.diff(torch.abs(target_response), dim=1)
    numerator = torch.mean((response_diff - target_diff) ** 2)
    denominator = torch.clamp(torch.mean(target_diff**2), min=eps)
    return numerator / denominator


def _regularization_loss(delta_c: Any) -> Any:
    torch = _get_torch_module()
    residual_penalty = torch.mean(torch.abs(delta_c) ** 2)
    if delta_c.shape[0] <= 1:
        smoothness_penalty = torch.zeros((), dtype=residual_penalty.dtype, device=residual_penalty.device)
    else:
        smoothness_penalty = torch.mean(torch.abs(torch.diff(delta_c, dim=0)) ** 2)
    return residual_penalty + smoothness_penalty


def compute_loss_breakdown_torch(
    front_end_bundle: FrontEndBundle,
    *,
    c_joint: Any,
    delta_c: Any,
    weights: LossWeights,
) -> tuple[Any, dict[str, Any]]:
    torch = _get_torch_module()
    response_joint = render_response_torch(front_end_bundle, c_joint)
    target_response = torch.as_tensor(front_end_bundle.h, dtype=torch.complex64, device=response_joint.device)

    loss_mag = _normalized_magnitude_mse(response_joint, target_response)
    loss_dmag = _normalized_magnitude_derivative_mse(response_joint, target_response)
    loss_ild, ild_diagnostics = compute_ild_loss_torch(
        target_response,
        response_joint,
        sample_rate_hz=front_end_bundle.sample_rate_hz,
    )
    loss_itd, itd_diagnostics = compute_itd_loss_torch(
        target_response,
        response_joint,
        sample_rate_hz=front_end_bundle.sample_rate_hz,
    )
    loss_reg = _regularization_loss(delta_c)
    loss_total = (
        weights.mag * loss_mag
        + weights.dmag * loss_dmag
        + weights.ild * loss_ild
        + weights.itd * loss_itd
        + weights.reg * loss_reg
    )
    return loss_total, {
        "loss_total": loss_total,
        "loss_mag": loss_mag,
        "loss_dmag": loss_dmag,
        "loss_ild": loss_ild,
        "loss_itd": loss_itd,
        "loss_reg": loss_reg,
        "response_joint": response_joint,
        "ild_diagnostics": ild_diagnostics,
        "itd_diagnostics": itd_diagnostics,
    }


def _to_float(value: Any) -> float:
    if hasattr(value, "detach"):
        return float(value.detach().cpu().item())
    return float(value)


def _trace_entry_from_breakdown(
    iteration: int,
    breakdown: dict[str, Any],
    *,
    delta_c: Any,
    alpha: Any,
) -> LossTraceEntry:
    torch = _get_torch_module()
    residual_norm = torch.linalg.vector_norm(torch.view_as_real(delta_c)).detach().cpu().item()
    return LossTraceEntry(
        iteration=iteration,
        loss_total=_to_float(breakdown["loss_total"]),
        loss_mag=_to_float(breakdown["loss_mag"]),
        loss_dmag=_to_float(breakdown["loss_dmag"]),
        loss_ild=_to_float(breakdown["loss_ild"]),
        loss_itd=_to_float(breakdown["loss_itd"]),
        loss_reg=_to_float(breakdown["loss_reg"]),
        residual_norm=float(residual_norm),
        alpha=_to_float(alpha),
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
        raise ValueError("Short-run optimization requires at least two frequency bins.")
    if selected_coefficient_count < 1:
        raise ValueError("Short-run optimization requires at least one coefficient.")
    orientation_coefficients = {
        yaw_deg: OrientationCoefficientEntry(
            yaw_deg=entry.yaw_deg,
            pitch_deg=entry.pitch_deg,
            roll_deg=entry.roll_deg,
            c_ls=entry.c_ls[:selected_frequency_count, :selected_coefficient_count, :],
            c_magls=entry.c_magls[:selected_frequency_count, :selected_coefficient_count, :],
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


def _response_metrics(
    target_response: np.ndarray,
    estimated_response: np.ndarray,
) -> tuple[float, float]:
    eps = np.finfo(np.float64).tiny
    magnitude_numerator = float(np.mean((np.abs(estimated_response) - np.abs(target_response)) ** 2))
    magnitude_denominator = float(max(np.mean(np.abs(target_response) ** 2), eps))
    residual = estimated_response - target_response
    nmse = float(np.mean(np.abs(residual) ** 2) / magnitude_denominator)
    return magnitude_numerator / magnitude_denominator, nmse


def _orientation_entry_summary(entry: OrientationCoefficientEntry) -> dict[str, object]:
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


def _with_selected_orientation_coefficients(
    front_end_bundle: FrontEndBundle,
    *,
    yaw_deg: int,
) -> tuple[FrontEndBundle, dict[str, object]]:
    entry = select_orientation_coefficients(front_end_bundle, yaw_deg=yaw_deg)
    selected_summary = _orientation_entry_summary(entry)
    return (
        replace(
            front_end_bundle,
            c_ls=entry.c_ls.astype(np.complex64, copy=True),
            c_magls=entry.c_magls.astype(np.complex64, copy=True),
            c_ls_source=entry.c_ls_source,
            c_magls_source=entry.c_magls_source,
            coefficient_axis_semantics=entry.coefficient_axis_semantics,
            emagls_reference_yaw_deg=entry.yaw_deg,
            emagls_reference_path=entry.reference_path,
            emagls_reference_sha256=entry.reference_sha256,
        ),
        selected_summary,
    )


def write_evaluation_export(
    *,
    artifact_dir: Path,
    front_end_bundle: FrontEndBundle,
    solver_input_pack: SolverInputPack,
    solver_config: ResidualSolverConfig,
    loss_weights: LossWeights,
    loss_trace: list[LossTraceEntry],
    joint_response: np.ndarray,
    baseline_name: str = BASELINE_NAME_MAGLS,
    selected_orientation: dict[str, object] | None = None,
    producer_task_id: str = DEFAULT_PRODUCER_TASK_ID,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
) -> OptimizationExport:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    loss_trace_path = artifact_dir / "loss_trace.jsonl"
    summary_path = artifact_dir / "summary.json"
    orientation_training_path = artifact_dir / "orientation_training_path.json"

    with loss_trace_path.open("w", encoding="utf-8") as handle:
        for entry in loss_trace:
            handle.write(json.dumps(entry.to_dict(), sort_keys=True) + "\n")

    cue_result = build_cue_bank(
        front_end_bundle.h,
        joint_response,
        sample_rate_hz=front_end_bundle.sample_rate_hz,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
    )
    normalized_magnitude_error, nmse = _response_metrics(front_end_bundle.h, joint_response)
    initial_loss_total = loss_trace[0].loss_total
    selected_entry = min(loss_trace, key=lambda entry: entry.loss_total)
    final_loss_total = selected_entry.loss_total
    artifact_refs = {
        "summary": str(summary_path),
        "loss_trace": str(loss_trace_path),
    }
    if selected_orientation is not None:
        artifact_refs["orientation_training_path"] = str(orientation_training_path)
    export = OptimizationExport(
        schema_version=DEFAULT_SCHEMA_VERSION,
        interface_version=DEFAULT_INTERFACE_VERSION,
        producer_task_id=producer_task_id,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
        baseline_name=baseline_name,
        ild_error=cue_result.metrics.ild_error_db,
        itd_proxy_error=cue_result.metrics.itd_proxy_error,
        normalized_magnitude_error=normalized_magnitude_error,
        nmse=nmse,
        initial_loss_total=initial_loss_total,
        final_loss_total=final_loss_total,
        selected_iteration=selected_entry.iteration,
        loss_reduced=final_loss_total < initial_loss_total,
        loss_trace_path=str(loss_trace_path),
        artifact_refs=artifact_refs,
        solver_input_summary=solver_input_pack.to_summary(),
        solver_config=solver_config.to_dict(),
        loss_weights=loss_weights.to_dict(),
        selected_orientation=selected_orientation,
        orientation_bank_yaws_deg=sorted(int(yaw) for yaw in front_end_bundle.orientation_coefficients),
        task09_ready=selected_orientation is not None,
        blocking_issues=[] if selected_orientation is not None else None,
    )
    summary_path.write_text(
        json.dumps(export.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    if selected_orientation is not None:
        orientation_training_path.write_text(
            json.dumps(
                {
                    "schema_version": DEFAULT_SCHEMA_VERSION,
                    "interface_version": DEFAULT_INTERFACE_VERSION,
                    "producer_task_id": producer_task_id,
                    "producer_session_id": producer_session_id,
                    "run_config_ref": run_config_ref,
                    "selected_orientation": selected_orientation,
                    "orientation_bank_yaws_deg": export.orientation_bank_yaws_deg,
                    "solver_input_summary": export.solver_input_summary,
                    "solver_config": export.solver_config,
                    "loss_weights": export.loss_weights,
                    "metric_summary": {
                        "ild_error": export.ild_error,
                        "itd_proxy_error": export.itd_proxy_error,
                        "normalized_magnitude_error": export.normalized_magnitude_error,
                        "nmse": export.nmse,
                    },
                    "loss_trace_path": export.loss_trace_path,
                    "summary_path": str(summary_path),
                    "task09_ready": export.task09_ready,
                    "blocking_issues": export.blocking_issues,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
    return export


def run_short_optimization(
    front_end_bundle: FrontEndBundle,
    *,
    iterations: int = 8,
    learning_rate: float = 1e-2,
    solver_config: ResidualSolverConfig = ResidualSolverConfig(hidden_dim=24, block_count=2, rank=4),
    loss_weights: LossWeights = LossWeights(),
    artifact_dir: Path | str | None = None,
    max_frequency_bins: int | None = 65,
    max_coefficients: int | None = 96,
    baseline_name: str = BASELINE_NAME_MAGLS,
    orientation_yaw_deg: int | None = None,
    producer_task_id: str = DEFAULT_PRODUCER_TASK_ID,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
) -> OptimizationExport:
    if iterations <= 0:
        raise ValueError("iterations must be positive.")
    torch = _get_torch_module()
    selected_orientation = None
    if orientation_yaw_deg is not None:
        front_end_bundle, selected_orientation = _with_selected_orientation_coefficients(
            front_end_bundle,
            yaw_deg=orientation_yaw_deg,
        )
    run_bundle = _slice_front_end_bundle(
        front_end_bundle,
        max_frequency_bins=max_frequency_bins,
        max_coefficients=max_coefficients,
    )
    if orientation_yaw_deg is not None:
        selected_orientation = _orientation_entry_summary(
            select_orientation_coefficients(run_bundle, yaw_deg=orientation_yaw_deg)
        )
    solver_input_pack = build_solver_input_pack(
        run_bundle,
        include_front_end_energy_descriptor=solver_config.include_front_end_energy_descriptor,
        selected_orientation=selected_orientation,
        producer_task_id=producer_task_id,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
    )
    solver_input_tensor = torch.as_tensor(solver_input_pack.solver_input_packed, dtype=torch.float32)
    c_magls = torch.as_tensor(run_bundle.c_magls, dtype=torch.complex64)
    solver = FCRMixerResidualSolver(
        input_channels=solver_input_pack.solver_input_packed.shape[-1],
        config=solver_config,
    )
    optimizer = torch.optim.Adam(solver.parameters(), lr=learning_rate)

    loss_trace: list[LossTraceEntry] = []
    best_response = None
    best_loss_total: float | None = None
    for iteration in range(iterations + 1):
        optimizer.zero_grad(set_to_none=True)
        delta_c, alpha = solver(solver_input_tensor)
        c_joint = compose_joint_coefficients(c_magls, delta_c, alpha)
        loss_total, breakdown = compute_loss_breakdown_torch(
            run_bundle,
            c_joint=c_joint,
            delta_c=delta_c,
            weights=loss_weights,
        )
        loss_trace.append(
            _trace_entry_from_breakdown(
                iteration,
                breakdown,
                delta_c=delta_c,
                alpha=alpha,
            )
        )
        current_response = breakdown["response_joint"].detach().cpu().numpy().astype(np.complex64)
        current_loss_total = loss_trace[-1].loss_total
        if best_loss_total is None or current_loss_total < best_loss_total:
            best_loss_total = current_loss_total
            best_response = current_response
        if iteration < iterations:
            loss_total.backward()
            optimizer.step()

    if best_response is None:
        raise RuntimeError("Optimization did not produce a final response.")
    if artifact_dir is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        artifact_root = TASK08_ARTIFACT_ROOT if producer_task_id == TASK08_PRODUCER_TASK_ID else DEFAULT_ARTIFACT_ROOT
        artifact_dir = artifact_root / timestamp
    return write_evaluation_export(
        artifact_dir=Path(artifact_dir),
        front_end_bundle=run_bundle,
        solver_input_pack=solver_input_pack,
        solver_config=solver_config,
        loss_weights=loss_weights,
        loss_trace=loss_trace,
        joint_response=best_response,
        baseline_name=baseline_name,
        selected_orientation=selected_orientation,
        producer_task_id=producer_task_id,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
    )


def smoke_residual_solver(
    repo_root: Path | str = REPO_ROOT,
    *,
    array_id: str = DEFAULT_ARRAY_ID,
    hrtf_id: str = DEFAULT_HRTF_ID,
    iterations: int = 4,
    learning_rate: float = 1e-2,
    hidden_dim: int = 24,
    block_count: int = 2,
    rank: int = 4,
    max_frequency_bins: int | None = 65,
    max_coefficients: int | None = 96,
    orientation_yaw_deg: int | None = None,
    artifact_dir: Path | str | None = None,
    producer_task_id: str | None = None,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
) -> dict[str, object]:
    effective_producer_task_id = (
        producer_task_id
        if producer_task_id is not None
        else (TASK08_PRODUCER_TASK_ID if orientation_yaw_deg is not None else DEFAULT_PRODUCER_TASK_ID)
    )
    effective_run_config_ref = (
        TASK08_RUN_CONFIG_REF
        if orientation_yaw_deg is not None and run_config_ref == DEFAULT_RUN_CONFIG_REF
        else run_config_ref
    )
    effective_producer_session_id = (
        TASK08_PRODUCER_SESSION_ID
        if orientation_yaw_deg is not None and producer_session_id == DEFAULT_PRODUCER_SESSION_ID
        else producer_session_id
    )
    front_end_bundle = resolve_front_end_bundle(
        repo_root=repo_root,
        array_id=array_id,
        hrtf_id=hrtf_id,
        producer_session_id=effective_producer_session_id,
        run_config_ref=effective_run_config_ref,
    )
    export = run_short_optimization(
        front_end_bundle,
        iterations=iterations,
        learning_rate=learning_rate,
        solver_config=ResidualSolverConfig(
            hidden_dim=hidden_dim,
            block_count=block_count,
            rank=rank,
        ),
        artifact_dir=artifact_dir,
        max_frequency_bins=max_frequency_bins,
        max_coefficients=max_coefficients,
        orientation_yaw_deg=orientation_yaw_deg,
        producer_task_id=effective_producer_task_id,
        producer_session_id=effective_producer_session_id,
        run_config_ref=effective_run_config_ref,
    )
    summary = export.to_dict()
    finite_metrics = all(
        np.isfinite(value)
        for value in (
            export.initial_loss_total,
            export.final_loss_total,
            export.ild_error,
            export.itd_proxy_error,
            export.normalized_magnitude_error,
            export.nmse,
        )
    )
    artifacts_exist = all(Path(path).exists() for path in export.artifact_refs.values())
    return {
        "ok": bool(finite_metrics and artifacts_exist),
        "success_criteria": {
            "finite_metrics": bool(finite_metrics),
            "artifacts_exist": bool(artifacts_exist),
            "loss_reduction_required": False,
            "loss_reduced": bool(export.loss_reduced),
            "orientation_yaw_deg": orientation_yaw_deg,
            "task09_ready": bool(export.task09_ready),
            "note": (
                "Smoke validates the finite solver/export path. Short-run loss reduction is "
                "reported but is not required because the current coefficient authority sets "
                "c_ls equal to c_magls when no saved aligned-ypr LS reference exists."
            ),
        },
        "summary": summary,
    }


def _optional_positive_int(value: str) -> int | None:
    parsed = int(value)
    return None if parsed <= 0 else parsed


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 02 residual solver, loss loop, and export path.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    smoke_parser = subparsers.add_parser("smoke")
    smoke_parser.add_argument("--repo-root", default=str(REPO_ROOT))
    smoke_parser.add_argument("--array-id", default=DEFAULT_ARRAY_ID)
    smoke_parser.add_argument("--hrtf-id", default=DEFAULT_HRTF_ID)
    smoke_parser.add_argument("--iterations", type=int, default=4)
    smoke_parser.add_argument("--learning-rate", type=float, default=1e-2)
    smoke_parser.add_argument("--hidden-dim", type=int, default=24)
    smoke_parser.add_argument("--block-count", type=int, default=2)
    smoke_parser.add_argument("--rank", type=int, default=4)
    smoke_parser.add_argument("--max-frequency-bins", type=_optional_positive_int, default=65)
    smoke_parser.add_argument("--max-coefficients", type=_optional_positive_int, default=96)
    smoke_parser.add_argument("--orientation-yaw-deg", type=int, default=None)
    smoke_parser.add_argument("--artifact-dir", default=None)
    smoke_parser.add_argument("--producer-task-id", default=None)
    smoke_parser.add_argument("--producer-session-id", default=DEFAULT_PRODUCER_SESSION_ID)
    smoke_parser.add_argument("--run-config-ref", default=DEFAULT_RUN_CONFIG_REF)
    smoke_parser.add_argument("--indent", type=int, default=2)

    return parser


def _run_cli() -> int:
    args = _build_parser().parse_args()
    report = smoke_residual_solver(
        repo_root=args.repo_root,
        array_id=args.array_id,
        hrtf_id=args.hrtf_id,
        iterations=args.iterations,
        learning_rate=args.learning_rate,
        hidden_dim=args.hidden_dim,
        block_count=args.block_count,
        rank=args.rank,
        max_frequency_bins=args.max_frequency_bins,
        max_coefficients=args.max_coefficients,
        orientation_yaw_deg=args.orientation_yaw_deg,
        artifact_dir=args.artifact_dir,
        producer_task_id=args.producer_task_id,
        producer_session_id=args.producer_session_id,
        run_config_ref=args.run_config_ref,
    )
    print(json.dumps(report, indent=args.indent, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(_run_cli())
