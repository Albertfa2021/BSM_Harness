from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np

from .asset_environment import (
    DEFAULT_ARRAY_ID,
    DEFAULT_HRTF_ID,
    DEFAULT_INTERFACE_VERSION,
    DEFAULT_SCHEMA_VERSION,
    REPO_ROOT,
)
from .front_end_bundle import (
    FrontEndBundle,
    resolve_front_end_bundle,
)


DEFAULT_PRODUCER_TASK_ID = "TASK-0004"
DEFAULT_PRODUCER_SESSION_ID = "SESSION-P2-0005"
DEFAULT_RUN_CONFIG_REF = "phase02/default_baseline_renderer"
BASELINE_NAME_LS = "BSM-LS"
BASELINE_NAME_MAGLS = "BSM-MagLS"


@dataclass(frozen=True)
class BaselineRenderMetrics:
    nmse_to_target: float
    max_abs_error: float
    mean_abs_error: float
    response_energy: float
    target_energy: float

    def to_dict(self) -> dict[str, float]:
        return {
            "nmse_to_target": self.nmse_to_target,
            "max_abs_error": self.max_abs_error,
            "mean_abs_error": self.mean_abs_error,
            "response_energy": self.response_energy,
            "target_energy": self.target_energy,
        }


@dataclass(frozen=True)
class BaselineRenderResult:
    schema_version: str
    interface_version: str
    producer_task_id: str
    producer_session_id: str
    run_config_ref: str
    baseline_name: str
    coefficient_field_name: str
    coefficients: np.ndarray
    response: np.ndarray
    target_response: np.ndarray
    metrics: BaselineRenderMetrics

    def to_summary(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "interface_version": self.interface_version,
            "producer_task_id": self.producer_task_id,
            "producer_session_id": self.producer_session_id,
            "run_config_ref": self.run_config_ref,
            "baseline_name": self.baseline_name,
            "coefficient_field_name": self.coefficient_field_name,
            "coefficient_shape": list(self.coefficients.shape),
            "response_shape": list(self.response.shape),
            "target_shape": list(self.target_response.shape),
            "finite": {
                "coefficients": bool(np.isfinite(self.coefficients).all()),
                "response": bool(np.isfinite(self.response).all()),
                "target_response": bool(np.isfinite(self.target_response).all()),
            },
            "metrics": self.metrics.to_dict(),
        }


def _canonicalize_baseline_name(baseline_name: str) -> tuple[str, str]:
    normalized = baseline_name.strip().lower().replace("_", "").replace("-", "")
    if normalized in {"ls", "bsmls", "cls"}:
        return BASELINE_NAME_LS, "c_ls"
    if normalized in {"magls", "bsmmagls", "cmagls"}:
        return BASELINE_NAME_MAGLS, "c_magls"
    raise ValueError(
        "Unknown baseline_name. Expected one of: "
        "'BSM-LS', 'ls', 'c_ls', 'BSM-MagLS', 'magls', 'c_magls'."
    )


def select_baseline_coefficients(
    front_end_bundle: FrontEndBundle,
    baseline_name: str,
) -> tuple[str, str, np.ndarray]:
    canonical_name, coefficient_field_name = _canonicalize_baseline_name(baseline_name)
    coefficients = getattr(front_end_bundle, coefficient_field_name)
    return canonical_name, coefficient_field_name, coefficients


def render_coefficients(
    front_end_bundle: FrontEndBundle,
    coefficients: np.ndarray,
) -> np.ndarray:
    coefficient_array = np.asarray(coefficients)
    expected_shape = front_end_bundle.c_ls.shape
    if coefficient_array.shape != expected_shape:
        raise ValueError(
            "Coefficient shape mismatch: "
            f"expected {expected_shape}, received {coefficient_array.shape}."
        )
    if not np.isfinite(coefficient_array).all():
        raise ValueError("Coefficient array contains non-finite values.")
    response = np.einsum("dfm,fme->dfe", front_end_bundle.V, coefficient_array)
    expected_response_shape = front_end_bundle.h.shape
    if response.shape != expected_response_shape:
        raise RuntimeError(
            "Rendered response shape mismatch: "
            f"expected {expected_response_shape}, received {response.shape}."
        )
    if not np.isfinite(response).all():
        raise RuntimeError("Rendered response contains non-finite values.")
    return response.astype(np.complex64)


def _compute_baseline_metrics(
    response: np.ndarray,
    target_response: np.ndarray,
) -> BaselineRenderMetrics:
    residual = response - target_response
    residual_energy = float(np.mean(np.abs(residual) ** 2))
    target_energy = float(np.mean(np.abs(target_response) ** 2))
    safe_target_energy = max(target_energy, np.finfo(np.float32).tiny)
    return BaselineRenderMetrics(
        nmse_to_target=residual_energy / safe_target_energy,
        max_abs_error=float(np.max(np.abs(residual))),
        mean_abs_error=float(np.mean(np.abs(residual))),
        response_energy=float(np.mean(np.abs(response) ** 2)),
        target_energy=target_energy,
    )


def build_baseline_render(
    front_end_bundle: FrontEndBundle,
    *,
    baseline_name: str,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
) -> BaselineRenderResult:
    canonical_name, coefficient_field_name, coefficients = select_baseline_coefficients(
        front_end_bundle,
        baseline_name,
    )
    response = render_coefficients(front_end_bundle, coefficients)
    target_response = np.asarray(front_end_bundle.h)
    metrics = _compute_baseline_metrics(response, target_response)
    return BaselineRenderResult(
        schema_version=DEFAULT_SCHEMA_VERSION,
        interface_version=DEFAULT_INTERFACE_VERSION,
        producer_task_id=DEFAULT_PRODUCER_TASK_ID,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
        baseline_name=canonical_name,
        coefficient_field_name=coefficient_field_name,
        coefficients=np.asarray(coefficients),
        response=response,
        target_response=target_response,
        metrics=metrics,
    )


def inspect_baseline_renderer(
    repo_root: Path | str = REPO_ROOT,
    *,
    array_id: str = DEFAULT_ARRAY_ID,
    hrtf_id: str = DEFAULT_HRTF_ID,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
    baseline_name: str,
) -> BaselineRenderResult:
    front_end_bundle = resolve_front_end_bundle(
        repo_root=repo_root,
        array_id=array_id,
        hrtf_id=hrtf_id,
    )
    return build_baseline_render(
        front_end_bundle,
        baseline_name=baseline_name,
        producer_session_id=producer_session_id,
        run_config_ref=run_config_ref,
    )


def smoke_baseline_renderer(
    repo_root: Path | str = REPO_ROOT,
    *,
    array_id: str = DEFAULT_ARRAY_ID,
    hrtf_id: str = DEFAULT_HRTF_ID,
    producer_session_id: str = DEFAULT_PRODUCER_SESSION_ID,
    run_config_ref: str = DEFAULT_RUN_CONFIG_REF,
) -> dict[str, object]:
    front_end_bundle = resolve_front_end_bundle(
        repo_root=repo_root,
        array_id=array_id,
        hrtf_id=hrtf_id,
    )
    baseline_results = [
        build_baseline_render(
            front_end_bundle,
            baseline_name=baseline_name,
            producer_session_id=producer_session_id,
            run_config_ref=run_config_ref,
        )
        for baseline_name in (BASELINE_NAME_LS, BASELINE_NAME_MAGLS)
    ]
    return {
        "ok": True,
        "bundle_summary": front_end_bundle.to_summary(),
        "baseline_results": [result.to_summary() for result in baseline_results],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 02 shared baseline renderer.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--repo-root", default=str(REPO_ROOT))
    report_parser.add_argument("--array-id", default=DEFAULT_ARRAY_ID)
    report_parser.add_argument("--hrtf-id", default=DEFAULT_HRTF_ID)
    report_parser.add_argument("--producer-session-id", default=DEFAULT_PRODUCER_SESSION_ID)
    report_parser.add_argument("--run-config-ref", default=DEFAULT_RUN_CONFIG_REF)
    report_parser.add_argument("--baseline-name", default=BASELINE_NAME_MAGLS)
    report_parser.add_argument("--indent", type=int, default=2)

    smoke_parser = subparsers.add_parser("smoke")
    smoke_parser.add_argument("--repo-root", default=str(REPO_ROOT))
    smoke_parser.add_argument("--array-id", default=DEFAULT_ARRAY_ID)
    smoke_parser.add_argument("--hrtf-id", default=DEFAULT_HRTF_ID)
    smoke_parser.add_argument("--producer-session-id", default=DEFAULT_PRODUCER_SESSION_ID)
    smoke_parser.add_argument("--run-config-ref", default=DEFAULT_RUN_CONFIG_REF)
    smoke_parser.add_argument("--indent", type=int, default=2)

    return parser


def _run_cli() -> int:
    args = _build_parser().parse_args()
    if args.command == "report":
        result = inspect_baseline_renderer(
            repo_root=args.repo_root,
            array_id=args.array_id,
            hrtf_id=args.hrtf_id,
            producer_session_id=args.producer_session_id,
            run_config_ref=args.run_config_ref,
            baseline_name=args.baseline_name,
        )
        print(json.dumps(result.to_summary(), indent=args.indent, sort_keys=True))
        return 0

    report = smoke_baseline_renderer(
        repo_root=args.repo_root,
        array_id=args.array_id,
        hrtf_id=args.hrtf_id,
        producer_session_id=args.producer_session_id,
        run_config_ref=args.run_config_ref,
    )
    print(json.dumps(report, indent=args.indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_cli())
