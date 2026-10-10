"""
Circular decomposition (rotating-vector Fourier analysis) for SPP trajectories.

Any closed 2-D trajectory ``w(t) = x(t) + i·y(t)`` can be written as a sum of
complex rotating vectors (phasors):

    w(t) = Σ_k c_k · e^{ i·ω_k·t }

where ``c_k = r_k · e^{ i·φ_k }``.  ``|c_k| = r_k`` is the circle radius and the
sign of ``ω_k`` is the rotation direction:

    * ``ω_k > 0`` → counter-clockwise (anti-clockwise)
    * ``ω_k < 0`` → clockwise

The forward DFT of a periodic signal gives exactly this decomposition.  For a
length-L period with fundamental angular frequency ``ω₁ = 2π·f`` sampled at
``t_n = n·dt`` the coefficient at angular frequency ``ω_k`` is

    c_k = (1/L) · Σ_n w_n · e^{ -i·ω_k·t_n }

so that the reconstruction ``w(t) = Σ_k c_k e^{ i·ω_k t }`` is exact (up to the
Nyquist limit).  Because the trajectory is real-valued in each component we fold
the negative-frequency pair so that every listed component is a *counter-
clockwise* phasor, carrying an explicit ``direction`` flag.

Trajectory order (matches the SPP matlab/Rogers convention used elsewhere in the
program): component 0 = strain γ, 1 = strain rate γ̇, 2 = stress σ.
"""

from typing import Dict, List, Any
import numpy as np


# Human readable names for the physical components.
COMPONENT_NAMES = {
    0: ("Strain", "γ"),
    1: ("Strain Rate", "γ̇"),
    2: ("Stress", "σ"),
}

TWO_PI = 2.0 * np.pi


def decompose_trajectory(x: np.ndarray, y: np.ndarray, omega1: float,
                         n_harmonics: int = 15, harmonic_steps: int = 1,
                         min_radius_ratio: float = 1e-6) -> Dict[str, Any]:
    """
    Decompose a closed 2-D trajectory into rotating circular components.

    Args:
        x, y: 1-D arrays of the two components (e.g. G′ₜ and G″ₜ), one period.
        omega1: fundamental angular frequency ω₁ = 2πf (rad/s).
        n_harmonics: highest harmonic number to keep.
        harmonic_steps: keep every ``harmonic_steps``-th harmonic (1 = all odd
            and even; 2 = odd only, matching the SPP stress convention).
        min_radius_ratio: drop components whose radius is below this fraction of
            the largest radius (removes FFT round-off noise).

    Returns:
        dict with:
            'components': list of dicts (n, omega, direction, radius, phase_deg,
                          cx, cy, real, imag)
            'k_max': number of DFT coefficients (Nyquist), when defined
            'mean': complex mean (DC component)
            'omega1': fundamental angular frequency
            'reconstruction': (x_rec, y_rec)
            'residual': relative RMS residual of the reconstruction
    """
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    L = min(len(x), len(y))
    x = x[:L]
    y = y[:L]

    w = x + 1j * y
    mean = complex(np.mean(w))
    w0 = w - mean

    c = np.fft.fft(w0) / L                      # c[k] ↔ ω_k = k·ω₁
    N = c.shape[0]
    neg = (N - 1) // 2                          # max negative index (excl. nyquist)
    max_k = min(int(n_harmonics), abs(neg))
    step = max(1, int(harmonic_steps))

    n = np.arange(L)
    theta = TWO_PI * n / L                      # ω₁·t_n
    components: List[Dict[str, Any]] = []
    x_rec = np.full(L, mean.real)
    y_rec = np.full(L, mean.imag)

    for k in range(1, max_k + 1, step):
        ck = c[k]
        cmk = c[N - k] if k <= neg else 0.0 + 0.0j

        # Positive frequency (counter-clockwise) pair contribution.
        if abs(ck) > 0:
            mag = abs(ck)
            phase = np.angle(ck)
            ang = k * theta + phase
            x_rec += mag * np.cos(ang)
            y_rec += mag * np.sin(ang)
            components.append({
                'n': k,
                'omega': k * omega1,
                'direction': 'ccw',
                'direction_code': 1,
                'radius': mag,
                'phase_deg': np.degrees(phase),
                'real': ck.real,
                'imag': ck.imag,
                'cx': ck.real,
                'cy': ck.imag,
            })

        # Negative frequency (clockwise) pair contribution.
        if abs(cmk) > 0:
            mag = abs(cmk)
            phase = np.angle(cmk)
            ang = -k * theta + phase
            x_rec += mag * np.cos(ang)
            y_rec += mag * np.sin(ang)
            components.append({
                'n': k,
                'omega': -k * omega1,
                'direction': 'cw',
                'direction_code': -1,
                'radius': mag,
                'phase_deg': np.degrees(phase),
                'real': cmk.real,
                'imag': cmk.imag,
                'cx': cmk.real,
                'cy': cmk.imag,
            })

    rms = float(np.sqrt(np.mean(w0.real ** 2 + w0.imag ** 2)))
    res = float(np.sqrt(np.mean((x - x_rec) ** 2 + (y - y_rec) ** 2)))
    residual = res / rms if rms > 0 else 0.0

    # Discard components that are pure FFT round-off noise.
    if components:
        max_r = max(c['radius'] for c in components)
        if max_r > 0:
            components = [c for c in components
                          if c['radius'] >= min_radius_ratio * max_r]

    return {
        'components': components,
        'k_max': max_k,
        'nyquist_k': neg,
        'mean': mean,
        'omega1': omega1,
        'reconstruction': (x_rec, y_rec),
        'residual': residual,
    }


def components_to_rows(components: List[Dict[str, Any]]) -> List[List[float]]:
    """Flatten components into tabular rows for display / export."""
    rows = []
    for comp in components:
        rows.append([
            comp['n'],
            comp['omega'],
            1 if comp['direction'] == 'ccw' else -1,
            comp['radius'],
            comp['phase_deg'],
            comp['real'],
            comp['imag'],
        ])
    return rows