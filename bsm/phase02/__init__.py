"""Phase 02 project-side modules."""

from importlib import import_module
from typing import Any


__all__ = [
    "AssetBundle",
    "AssetValidationError",
    "AssetValidationReport",
    "BaselineRenderMetrics",
    "BaselineRenderResult",
    "CueBankMetrics",
    "CueBankResult",
    "DirectionGrid",
    "FCRMixerResidualSolver",
    "FrontEndBundle",
    "FrontEndValidationError",
    "FrontEndValidationReport",
    "LossTraceEntry",
    "LossWeights",
    "OptimizationExport",
    "OrientationCoefficientEntry",
    "ResidualSolverConfig",
    "SolverInputPack",
    "ValidationIssue",
    "build_baseline_render",
    "build_cue_bank",
    "build_front_end_bundle",
    "build_solver_input_pack",
    "build_saved_aligned_ypr_orientation_bank",
    "build_visible_raw_array2binaural_emagls_coefficients",
    "canonicalize_reference_coefficients",
    "compose_joint_coefficients",
    "coefficient_difference_metrics",
    "compute_ild_loss_torch",
    "compute_itd_loss_torch",
    "compute_loss_breakdown_torch",
    "inspect_baseline_renderer",
    "inspect_asset_bundle",
    "inspect_cue_bank",
    "inspect_front_end_bundle",
    "load_evaluation_grid",
    "load_optimization_grid",
    "load_saved_aligned_ypr_emagls_reference",
    "render_coefficients",
    "render_response_torch",
    "resolve_asset_bundle",
    "select_baseline_coefficients",
    "resolve_environment_name",
    "resolve_front_end_bundle",
    "run_audit",
    "run_short_optimization",
    "train_task09_run",
    "compare_task09_run",
    "select_orientation_coefficients",
    "smoke_cue_bank",
    "smoke_baseline_renderer",
    "smoke_residual_solver",
    "write_listening_audio_artifacts",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        asset_module_names = {
            "AssetBundle",
            "AssetValidationError",
            "AssetValidationReport",
            "ValidationIssue",
            "inspect_asset_bundle",
            "resolve_asset_bundle",
            "resolve_environment_name",
        }
        baseline_module_names = {
            "BaselineRenderMetrics",
            "BaselineRenderResult",
            "build_baseline_render",
            "inspect_baseline_renderer",
            "render_coefficients",
            "select_baseline_coefficients",
            "smoke_baseline_renderer",
        }
        cue_module_names = {
            "CueBankMetrics",
            "CueBankResult",
            "build_cue_bank",
            "compute_ild_loss_torch",
            "compute_itd_loss_torch",
            "inspect_cue_bank",
            "smoke_cue_bank",
        }
        residual_solver_module_names = {
            "FCRMixerResidualSolver",
            "LossTraceEntry",
            "LossWeights",
            "OptimizationExport",
            "ResidualSolverConfig",
            "SolverInputPack",
            "build_solver_input_pack",
            "compose_joint_coefficients",
            "compute_loss_breakdown_torch",
            "render_response_torch",
            "run_short_optimization",
            "smoke_residual_solver",
        }
        task09_module_names = {
            "train_task09_run",
            "compare_task09_run",
        }
        correctness_validation_module_names = {
            "canonicalize_reference_coefficients",
            "coefficient_difference_metrics",
            "run_audit",
            "write_listening_audio_artifacts",
        }
        array2binaural_emagls_module_names = {
            "build_visible_raw_array2binaural_emagls_coefficients",
            "load_saved_aligned_ypr_emagls_reference",
        }
        if name in asset_module_names:
            module = import_module(".asset_environment", __name__)
            return getattr(module, name)
        if name in baseline_module_names:
            module = import_module(".baseline_renderer", __name__)
            return getattr(module, name)
        if name in cue_module_names:
            module = import_module(".cue_bank", __name__)
            return getattr(module, name)
        if name in residual_solver_module_names:
            module = import_module(".residual_solver", __name__)
            return getattr(module, name)
        if name in task09_module_names:
            module = import_module(".task09_runner", __name__)
            return getattr(module, name)
        if name in correctness_validation_module_names:
            module = import_module(".correctness_validation", __name__)
            return getattr(module, name)
        if name in array2binaural_emagls_module_names:
            module = import_module(".array2binaural_emagls", __name__)
            return getattr(module, name)
        module = import_module(".front_end_bundle", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
