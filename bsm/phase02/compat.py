from __future__ import annotations

from importlib import import_module


def install_scipy_sph_harm_compatibility() -> bool:
    scipy_special = import_module("scipy.special")
    if hasattr(scipy_special, "sph_harm"):
        return False
    if not hasattr(scipy_special, "sph_harm_y"):
        return False

    def _compat_sph_harm(m: int, n: int, theta, phi, *args, **kwargs):
        return scipy_special.sph_harm_y(n, m, theta, phi, *args, **kwargs)

    scipy_special.sph_harm = _compat_sph_harm
    return True
