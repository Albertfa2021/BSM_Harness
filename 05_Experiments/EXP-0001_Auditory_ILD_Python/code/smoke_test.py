from __future__ import annotations

import math

import numpy as np

from auditory_ild import (
    compute_band_ild_db,
    design_ild_filterbank,
    erb_filter_bank,
    make_erb_filters,
)


def main() -> None:
    sample_rate_hz = 48000
    center_freqs, filter_coeffs = design_ild_filterbank(sample_rate_hz)
    print(f"center_freqs shape: {center_freqs.shape}")
    print(f"filter_coeffs shape: {filter_coeffs.shape}")

    rng = np.random.default_rng(20260417)
    wave = rng.standard_normal(1024)

    try:
        import gammatone.filters as gtf

        reference_coeffs = gtf.make_erb_filters(sample_rate_hz, center_freqs)
        coeff_max_abs_diff = float(np.max(np.abs(filter_coeffs - reference_coeffs)))
        print(f"gammatone coeff max abs diff: {coeff_max_abs_diff:.3e}")

        local_filtered = erb_filter_bank(wave, filter_coeffs)
        reference_filtered = gtf.erb_filterbank(wave, reference_coeffs)
        output_max_abs_diff = float(np.max(np.abs(local_filtered - reference_filtered)))
        print(f"gammatone output max abs diff: {output_max_abs_diff:.3e}")

        if coeff_max_abs_diff > 1e-12:
            raise SystemExit("Coefficient mismatch is larger than expected.")
        if output_max_abs_diff > 1e-10:
            raise SystemExit("Filterbank output mismatch is larger than expected.")
    except ImportError:
        print("gammatone not installed; skipped parity check.")

    left_wave = rng.standard_normal(4096)
    right_wave = 0.5 * left_wave
    ild_bands = compute_band_ild_db(left_wave, right_wave, filter_coeffs)
    expected_ild_db = 10.0 * math.log10(4.0)
    ild_error = float(np.max(np.abs(ild_bands - expected_ild_db)))
    print(f"constant-ratio ILD target: {expected_ild_db:.6f} dB")
    print(f"constant-ratio ILD max abs error: {ild_error:.3e}")

    if ild_error > 1e-9:
        raise SystemExit("ILD sanity check failed.")

    print("smoke test passed")


if __name__ == "__main__":
    main()
