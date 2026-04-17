"""Auditory ERB-band ILD helpers translated from Matlab AuditoryToolbox.

This module mirrors the ERB spacing and filter cascade used by:

- ERBSpace.m
- MakeERBFilters.m
- ERBFilterBank.m

from `07_References/Open_Source_Baselines/ILD computer method/AuditoryToolbox/`.
"""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from scipy import signal

EAR_Q = 9.26449
MIN_BW = 24.7
ERB_ORDER = 1.0
DEFAULT_EPS = np.finfo(np.float64).eps


def _as_1d_float_array(values: Iterable[float] | np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim == 0:
        return array.reshape(1)
    if array.ndim == 1:
        return array
    if array.ndim == 2 and 1 in array.shape:
        return array.reshape(-1)
    raise ValueError("Expected a one-dimensional array or scalar input.")


def _as_audio_vector(wave: Iterable[float] | np.ndarray) -> np.ndarray:
    array = np.asarray(wave, dtype=np.float64)
    if array.ndim == 1:
        return array
    if array.ndim == 2 and 1 in array.shape:
        return array.reshape(-1)
    raise ValueError("Expected a mono waveform.")


def erb_space(
    low_freq: float = 100.0,
    high_freq: float = 44100.0 / 4.0,
    num_bands: int = 100,
) -> np.ndarray:
    """Return Matlab-style ERB-spaced center frequencies.

    The order matches AuditoryToolbox: high to low. Sort externally if an
    ascending list is required.
    """

    if num_bands <= 0:
        raise ValueError("num_bands must be positive.")
    if low_freq <= 0 or high_freq <= 0:
        raise ValueError("Frequencies must be positive.")

    idx = np.arange(1, num_bands + 1, dtype=np.float64)
    offset = EAR_Q * MIN_BW
    exponent = idx * (-math.log(high_freq + offset) + math.log(low_freq + offset)) / num_bands
    return -offset + np.exp(exponent) * (high_freq + offset)


def make_erb_filters(
    sample_rate_hz: float,
    num_channels_or_center_freqs: int | Iterable[float] | np.ndarray,
    low_freq_hz: float | None = None,
    width: float = 1.0,
) -> np.ndarray:
    """Return the 10-column ERB filter coefficient matrix used by AuditoryToolbox."""

    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive.")
    if width <= 0:
        raise ValueError("width must be positive.")

    if np.isscalar(num_channels_or_center_freqs):
        num_channels = int(num_channels_or_center_freqs)
        if num_channels <= 0:
            raise ValueError("num_channels must be positive.")
        if low_freq_hz is None:
            raise ValueError("low_freq_hz is required when using a channel count.")
        center_freqs = erb_space(low_freq_hz, sample_rate_hz / 2.0, num_channels)
    else:
        center_freqs = _as_1d_float_array(num_channels_or_center_freqs)

    t = 1.0 / sample_rate_hz
    erb = width * ((center_freqs / EAR_Q) ** ERB_ORDER + MIN_BW ** ERB_ORDER) ** (1.0 / ERB_ORDER)
    bandwidth = 1.019 * 2.0 * np.pi * erb

    arg = 2.0 * center_freqs * np.pi * t
    exp_bt = np.exp(bandwidth * t)
    a0 = np.full_like(center_freqs, t)
    a2 = np.zeros_like(center_freqs)
    b0 = np.ones_like(center_freqs)
    b1 = -2.0 * np.cos(arg) / exp_bt
    b2 = np.exp(-2.0 * bandwidth * t)

    rt_pos = np.sqrt(3.0 + 2.0 ** 1.5)
    rt_neg = np.sqrt(3.0 - 2.0 ** 1.5)
    common = -t * np.exp(-(bandwidth * t))
    k11 = np.cos(arg) + rt_pos * np.sin(arg)
    k12 = np.cos(arg) - rt_pos * np.sin(arg)
    k13 = np.cos(arg) + rt_neg * np.sin(arg)
    k14 = np.cos(arg) - rt_neg * np.sin(arg)

    a11 = common * k11
    a12 = common * k12
    a13 = common * k13
    a14 = common * k14

    vec = np.exp(4j * center_freqs * np.pi * t)
    gain = np.abs(
        (
            -2.0 * vec * t
            + 2.0
            * np.exp(-(bandwidth * t) + 2j * center_freqs * np.pi * t)
            * t
            * (np.cos(arg) - np.sqrt(3.0 - 2.0 ** 1.5) * np.sin(arg))
        )
        * (
            -2.0 * vec * t
            + 2.0
            * np.exp(-(bandwidth * t) + 2j * center_freqs * np.pi * t)
            * t
            * (np.cos(arg) + np.sqrt(3.0 - 2.0 ** 1.5) * np.sin(arg))
        )
        * (
            -2.0 * vec * t
            + 2.0
            * np.exp(-(bandwidth * t) + 2j * center_freqs * np.pi * t)
            * t
            * (np.cos(arg) - np.sqrt(3.0 + 2.0 ** 1.5) * np.sin(arg))
        )
        * (
            -2.0 * vec * t
            + 2.0
            * np.exp(-(bandwidth * t) + 2j * center_freqs * np.pi * t)
            * t
            * (np.cos(arg) + np.sqrt(3.0 + 2.0 ** 1.5) * np.sin(arg))
        )
        / (
            -2.0 / np.exp(2.0 * bandwidth * t)
            - 2.0 * vec
            + 2.0 * (1.0 + vec) / exp_bt
        )
        ** 4
    )

    return np.column_stack([a0, a11, a12, a13, a14, a2, b0, b1, b2, gain])


def erb_filter_bank(wave: Iterable[float] | np.ndarray, filter_coeffs: np.ndarray) -> np.ndarray:
    """Apply the 4-stage ERB filter cascade and return one row per band."""

    x = _as_audio_vector(wave)
    coeffs = np.asarray(filter_coeffs, dtype=np.float64)
    if coeffs.ndim != 2 or coeffs.shape[1] != 10:
        raise ValueError("filter_coeffs must have shape (num_bands, 10).")

    a0 = coeffs[:, 0]
    a11 = coeffs[:, 1]
    a12 = coeffs[:, 2]
    a13 = coeffs[:, 3]
    a14 = coeffs[:, 4]
    a2 = coeffs[:, 5]
    b0 = coeffs[:, 6]
    b1 = coeffs[:, 7]
    b2 = coeffs[:, 8]
    gain = coeffs[:, 9]

    output = np.zeros((coeffs.shape[0], x.shape[0]), dtype=np.float64)
    for channel in range(coeffs.shape[0]):
        y1 = signal.lfilter([a0[channel] / gain[channel], a11[channel] / gain[channel], a2[channel]], [b0[channel], b1[channel], b2[channel]], x)
        y2 = signal.lfilter([a0[channel], a12[channel], a2[channel]], [b0[channel], b1[channel], b2[channel]], y1)
        y3 = signal.lfilter([a0[channel], a13[channel], a2[channel]], [b0[channel], b1[channel], b2[channel]], y2)
        y4 = signal.lfilter([a0[channel], a14[channel], a2[channel]], [b0[channel], b1[channel], b2[channel]], y3)
        output[channel, :] = y4
    return output


def band_energies(wave: Iterable[float] | np.ndarray, filter_coeffs: np.ndarray) -> np.ndarray:
    """Return ERB-band energies for a mono waveform."""

    filtered = erb_filter_bank(wave, filter_coeffs)
    return np.sum(np.abs(filtered) ** 2, axis=1)


def compute_band_ild_db(
    left_wave: Iterable[float] | np.ndarray,
    right_wave: Iterable[float] | np.ndarray,
    filter_coeffs: np.ndarray,
    eps: float = DEFAULT_EPS,
) -> np.ndarray:
    """Return per-band ILD in dB using the Matlab reference power-ratio definition."""

    left_power = band_energies(left_wave, filter_coeffs)
    right_power = band_energies(right_wave, filter_coeffs)
    return 10.0 * np.log10((left_power + eps) / (right_power + eps))


def compute_mean_ild_db(
    left_wave: Iterable[float] | np.ndarray,
    right_wave: Iterable[float] | np.ndarray,
    filter_coeffs: np.ndarray,
    eps: float = DEFAULT_EPS,
) -> float:
    """Return the average ILD across ERB bands."""

    return float(np.mean(compute_band_ild_db(left_wave, right_wave, filter_coeffs, eps=eps)))


def compute_mean_ild_error_db(
    ref_left_wave: Iterable[float] | np.ndarray,
    ref_right_wave: Iterable[float] | np.ndarray,
    est_left_wave: Iterable[float] | np.ndarray,
    est_right_wave: Iterable[float] | np.ndarray,
    filter_coeffs: np.ndarray,
    eps: float = DEFAULT_EPS,
) -> float:
    """Return the mean absolute ERB-band ILD error in dB."""

    reference = compute_band_ild_db(ref_left_wave, ref_right_wave, filter_coeffs, eps=eps)
    estimate = compute_band_ild_db(est_left_wave, est_right_wave, filter_coeffs, eps=eps)
    return float(np.mean(np.abs(estimate - reference)))


def design_ild_filterbank(
    sample_rate_hz: float,
    num_bands: int = 29,
    low_freq_hz: float = 50.0,
    high_freq_hz: float = 6000.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Return ascending ERB center frequencies and filter coefficients for ILD analysis."""

    center_freqs = np.sort(erb_space(low_freq_hz, high_freq_hz, num_bands))
    return center_freqs, make_erb_filters(sample_rate_hz, center_freqs)
