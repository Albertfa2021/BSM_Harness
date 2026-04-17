"""Phase 02 project-side modules."""

from importlib import import_module
from typing import Any


__all__ = [
    "AssetBundle",
    "AssetValidationError",
    "AssetValidationReport",
    "ValidationIssue",
    "inspect_asset_bundle",
    "resolve_asset_bundle",
    "resolve_environment_name",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module(".asset_environment", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
