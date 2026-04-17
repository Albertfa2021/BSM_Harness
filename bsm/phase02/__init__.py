"""Phase 02 project-side modules."""

from importlib import import_module
from typing import Any


__all__ = [
    "AssetBundle",
    "AssetValidationError",
    "AssetValidationReport",
    "BaselineRenderMetrics",
    "BaselineRenderResult",
    "DirectionGrid",
    "FrontEndBundle",
    "FrontEndValidationError",
    "FrontEndValidationReport",
    "ValidationIssue",
    "build_baseline_render",
    "build_front_end_bundle",
    "inspect_baseline_renderer",
    "inspect_asset_bundle",
    "inspect_front_end_bundle",
    "load_evaluation_grid",
    "load_optimization_grid",
    "render_coefficients",
    "resolve_asset_bundle",
    "select_baseline_coefficients",
    "resolve_environment_name",
    "resolve_front_end_bundle",
    "smoke_baseline_renderer",
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
        if name in asset_module_names:
            module = import_module(".asset_environment", __name__)
            return getattr(module, name)
        if name in baseline_module_names:
            module = import_module(".baseline_renderer", __name__)
            return getattr(module, name)
        module = import_module(".front_end_bundle", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
