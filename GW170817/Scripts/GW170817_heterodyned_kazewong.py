"""
Heterodyned Nested Sampling for GW170817 (Kazewong/Bilby data)
================================================================

Same inference pipeline as GW170817_heterodyned_1.py but uses pre-processed
bilby data from EventData/kazewong/ instead of fetching from GWOSC.

With --phase-marginalization:
  14D parameter space, phase_c analytically marginalized via log I_0(|<d|h>|)
Without --phase-marginalization:
  15D parameter space, phase_c sampled as uniform [0, 2pi]

Usage:
  python GW170817_heterodyned_kazewong.py [--waveform {IMRPhenomD_NRTidalv2,TaylorF2}]
                                           [--phase-marginalization]
"""

# ============================================================================
# 1. IMPORTS & JAX CONFIGURATION
# ============================================================================
import os
os.environ['XLA_PYTHON_CLIENT_PREALLOCATE'] = 'false'

import argparse
import jax
jax.config.update('jax_enable_x64', True)

import jax.numpy as jnp
import jax.scipy.stats as stats
import numpy as np
import blackjax
import h5py
import time
import tqdm
from astropy.time import Time
from scipy.interpolate import interp1d
from anesthetic import NestedSamples
from blackjax.ns.utils import finalise

from jimgw.core.single_event.detector import get_H1, get_L1, get_V1
from jimgw.core.single_event.waveform import RippleIMRPhenomD_NRTidalv2, RippleTaylorF2
from jimgw.core.single_event.data import Data, PowerSpectrum

# ============================================================================
# 0. COMMAND-LINE ARGUMENTS
# ============================================================================
parser = argparse.ArgumentParser(description='Heterodyned nested sampling for GW170817 (kazewong data)')
parser.add_argument('--waveform', choices=['IMRPhenomD_NRTidalv2', 'TaylorF2'],
                    default='IMRPhenomD_NRTidalv2', help='Waveform approximant')
parser.add_argument('--psd-source', choices=['kazewong', 'bilby', 'gwtc1'],
                    default='kazewong',
                    help='PSD source: "kazewong" (pre-processed), "bilby" (Bilby PSDs), '
                         '"gwtc1" (official BayesWave PSDs from LIGO-P1900011)')
parser.add_argument('--phase-marginalization', action='store_true',
                    help='Enable analytic phase marginalization (removes phase_c from sampling)')
args = parser.parse_args()
waveform_tag = args.waveform
psd_source = args.psd_source
phase_marg = args.phase_marginalization

# Numerically stable log I_0 for phase marginalization
from jax.scipy.special import i0e

@jax.jit
def log_i0(x):
    return jnp.log(i0e(x)) + x


# ============================================================================
# 2. PARAMETER CONFIGURATION
# ============================================================================
PARAM_NAMES = [
    "M_c", "q", "s1_z", "s2_z", "iota", "d_L", "t_c",
    "psi", "ra", "dec", "lambda_1", "lambda_2", "H_0", "v_p",
]
PARAM_LABELS = [
    r"$M_c$", r"$q$", r"$s_{1z}$", r"$s_{2z}$", r"$\iota$", r"$d_L$", r"$t_c$",
    r"$\psi$", r"$\alpha$", r"$\delta$", r"$\Lambda_1$", r"$\Lambda_2$", r"$H_0$", r"$v_p$",
]

I_MC, I_Q, I_S1Z, I_S2Z, I_IOTA, I_DL, I_TC = 0, 1, 2, 3, 4, 5, 6
I_PSI, I_RA, I_DEC, I_L1, I_L2, I_H0, I_VP = 7, 8, 9, 10, 11, 12, 13

_PRIOR_LO_BASE = [
    1.184, 0.125, -0.05, -0.05,             # M_c, q, s1_z, s2_z
    0.0, 1.0, -0.1,                          # iota, d_L, t_c
    0.0, 0.0, -jnp.pi / 2,                   # psi, ra, dec
    0.0, 0.0, 20.0, -1000.0,                # lambda_1, lambda_2, H_0, v_p
]
_PRIOR_HI_BASE = [
    2.168, 1.00, 0.05, 0.05,                # M_c, q, s1_z, s2_z
    jnp.pi, 75.0, 0.1,                       # iota, d_L, t_c
    jnp.pi, 2 * jnp.pi, jnp.pi / 2,         # psi, ra, dec
    5000.0, 5000.0, 140.0, 1000.0,          # lambda_1, lambda_2, H_0, v_p
]
_PRIOR_TYPE_BASE = [0, 0, 0, 0, 1, 3, 0, 0, 0, 2, 0, 0, 4, 0]

if not phase_marg:
    PARAM_NAMES.append("phase_c")
    PARAM_LABELS.append(r"$\phi_c$")
    I_PHASEC = 14
    _PRIOR_LO_BASE.append(0.0)
    _PRIOR_HI_BASE.append(float(2 * jnp.pi))
    _PRIOR_TYPE_BASE.append(0)

NUM_DIMS = len(PARAM_NAMES)

PRIOR_LO = jnp.array(_PRIOR_LO_BASE)
PRIOR_HI = jnp.array(_PRIOR_HI_BASE)

M_COMP_LO = 0.5
M_COMP_HI = 7.7

PRIOR_TYPE = jnp.array(_PRIOR_TYPE_BASE)

_PRIOR_RANGE = PRIOR_HI - PRIOR_LO
_PRIOR_LOG_RANGE = jnp.log(_PRIOR_RANGE)
_PRIOR_LOG_LOG_RATIO = jnp.log(jnp.log(PRIOR_HI / PRIOR_LO))
_BETA_LN = jax.scipy.special.betaln(3.0, 1.0)


# ============================================================================
# 3. VECTORIZED LOG-PRIOR
# ============================================================================

@jax.jit
def logprior_fn(x):
    in_bounds = (x >= PRIOR_LO) & (x <= PRIOR_HI)

    lp_uniform = jnp.where(in_bounds, -_PRIOR_LOG_RANGE, -jnp.inf)
    lp_sin = jnp.where(in_bounds, jnp.log(jnp.abs(jnp.sin(x)) + 1e-300) - jnp.log(2.0), -jnp.inf)
    lp_cos = jnp.where(in_bounds, jnp.log(jnp.abs(jnp.cos(x)) + 1e-300) - jnp.log(2.0), -jnp.inf)
    u = (x - PRIOR_LO) / _PRIOR_RANGE
    lp_beta = jnp.where(in_bounds, 2.0 * jnp.log(jnp.abs(u) + 1e-300) - _PRIOR_LOG_RANGE - _BETA_LN, -jnp.inf)
    lp_log = jnp.where(in_bounds, -_PRIOR_LOG_LOG_RATIO - jnp.log(jnp.abs(x) + 1e-300), -jnp.inf)

    lp = jnp.where(PRIOR_TYPE == 0, lp_uniform,
         jnp.where(PRIOR_TYPE == 1, lp_sin,
         jnp.where(PRIOR_TYPE == 2, lp_cos,
         jnp.where(PRIOR_TYPE == 3, lp_beta,
                    lp_log))))

    total = jnp.sum(lp)

    q = x[I_Q]
    eta = q / (1 + q) ** 2
    M_total = x[I_MC] / eta ** 0.6
    m1 = M_total / (1 + q)
    m2 = q * m1
    mass_ok = (m1 >= M_COMP_LO) & (m1 <= M_COMP_HI) & (m2 >= M_COMP_LO) & (m2 <= M_COMP_HI)
    total = jnp.where(mass_ok, total, -jnp.inf)

    # Jacobian |∂(m1,m2)/∂(M_c,q)| = M_c * (1+q)^(2/5) / q^(6/5)
    # Converts uniform-in-(M_c,q) to uniform-in-(m1,m2), as assumed in
    # Abbott et al., PhysRevX 9, 011001, Sec. II.D (z=0.0099 for NGC 4993)
    log_jacobian = jnp.log(x[I_MC]) - 1.2 * jnp.log(x[I_Q]) + 0.4 * jnp.log(1.0 + x[I_Q])
    total = total + log_jacobian

    return total


# ============================================================================
# 4. EVENT CONFIGURATION & DATA LOADING (kazewong/bilby pre-processed)
# ============================================================================

gps = 1187008882.43
fmin = 23.0
fmax = 2048.0
duration = 128
post_trigger_duration = 2

marg_tag = 'PhaseMarg' if phase_marg else 'NoMarg'
label = f'Results/{marg_tag}_Heterodyned_Kazewong_{waveform_tag}_psd-{psd_source}'

KAZEWONG_DIR = 'EventData/GWOSC/GW170817/kazewong'
KAZEWONG_PREFIX = 'GW170817-IMRD_data0_1187008882-43_generation_data_dump.pickle'
GWOSC_DIR = 'EventData/GWOSC/GW170817'


def load_external_psd(psd_src, ifo_name, target_freqs):
    """Load PSD from an external file and interpolate to target frequency grid.

    Sources:
      - 'bilby':   Bilby PSD files from EventData/GWOSC/GW170817/Bilby/
      - 'gwtc1':   Official BayesWave PSDs from GWTC1_GW170817_PSDs.dat (LIGO-P1900011)
      - 'kazewong': Kazewong PSD files from EventData/GWOSC/GW170817/kazewong/
    """
    if psd_src == 'bilby':
        psd_file = os.path.join(GWOSC_DIR, 'Bilby', f'{ifo_name.lower()}_psd.txt')
        psd_data = np.loadtxt(psd_file)
        freqs_psd, psd_vals = psd_data[:, 0], psd_data[:, 1]
    elif psd_src == 'gwtc1':
        psd_data = np.loadtxt(os.path.join(GWOSC_DIR, 'GWTC1_GW170817_PSDs.dat'))
        freqs_psd = psd_data[:, 0]
        col_map = {'H1': 1, 'L1': 2, 'V1': 3}
        psd_vals = psd_data[:, col_map[ifo_name]]
    elif psd_src == 'kazewong':
        psd_file = os.path.join(KAZEWONG_DIR, f'{KAZEWONG_PREFIX}_{ifo_name}_psd.txt')
        psd_data = np.loadtxt(psd_file)
        freqs_psd, psd_vals = psd_data[:, 0], psd_data[:, 1]
    else:
        raise ValueError(f"Unknown PSD source: {psd_src}")
    # Replace inf with large sentinel before interpolation to avoid
    # scipy RuntimeWarning from inf arithmetic (inf-finite=inf, inf*0=NaN).
    # After interpolation, restore inf where the result exceeds the sentinel threshold.
    _PSD_INF_SENTINEL = 1e300
    inf_mask_src = ~np.isfinite(psd_vals)
    psd_vals_safe = np.where(inf_mask_src, _PSD_INF_SENTINEL, psd_vals)
    psd_interp = interp1d(freqs_psd, psd_vals_safe, kind='linear',
                          fill_value=_PSD_INF_SENTINEL, bounds_error=False)
    psd_values = psd_interp(np.array(target_freqs))
    # Restore inf where interpolation touched sentinel-affected regions
    psd_values = np.where(psd_values >= _PSD_INF_SENTINEL * 0.5, np.inf, psd_values)
    return PowerSpectrum(
        values=jnp.array(psd_values),
        frequencies=jnp.array(target_freqs),
        name=ifo_name,
    )


t0 = time.time()

detectors = [get_H1(), get_L1(), get_V1()]
N_DET = len(detectors)

for ifo in detectors:
    t_det = time.time()

    # Load pre-processed frequency-domain strain: (freq, re, im)
    strain_file = os.path.join(KAZEWONG_DIR, f'{KAZEWONG_PREFIX}_{ifo.name}_fd_strain.txt')
    strain_data_raw = np.loadtxt(strain_file)
    freqs_strain = strain_data_raw[:, 0]
    fd_strain = strain_data_raw[:, 1] + 1j * strain_data_raw[:, 2]

    # Construct Data object from frequency-domain arrays
    data_obj = Data.from_fd(
        fd_strain=jnp.array(fd_strain),
        frequencies=jnp.array(freqs_strain),
        epoch=gps - (duration - post_trigger_duration),
        name=ifo.name,
    )
    ifo.set_data(data_obj)

    # Load PSD based on selected source
    psd_obj = load_external_psd(psd_source, ifo.name, freqs_strain)
    ifo.set_psd(psd_obj)

    # Set frequency bounds for the analysis band
    ifo.set_frequency_bounds(fmin, fmax)
    print(f"  {ifo.name}: loaded kazewong data + {psd_source} PSD, {len(ifo.sliced_frequencies)} freq bins, total={time.time()-t_det:.1f}s")

t_data = time.time() - t0
print(f"[TIMING] Data loading: {t_data:.1f}s")

H1, L1, V1 = detectors

if waveform_tag == 'TaylorF2':
    waveform = RippleTaylorF2(f_ref=20.0, use_lambda_tildes=False)
else:
    waveform = RippleIMRPhenomD_NRTidalv2(f_ref=20.0, use_lambda_tildes=False, no_taper=False)
print(f"Waveform: {waveform_tag}")

frequencies = H1.sliced_frequencies
epoch = duration - post_trigger_duration
gmst = Time(gps, format="gps").sidereal_time("apparent", "greenwich").rad


# ============================================================================
# 5. REFERENCE PARAMETERS (from GWTC-1 posteriors)
# ============================================================================

def load_reference_params(hdf5_path, dataset='IMRPhenomPv2NRT_lowSpin_posterior'):
    with h5py.File(hdf5_path, 'r') as f:
        data = f[dataset][:]

    m1 = np.median(data['m1_detector_frame_Msun'])
    m2 = np.median(data['m2_detector_frame_Msun'])
    M = m1 + m2
    eta_val = m1 * m2 / M**2
    Mc = M * eta_val**(3.0 / 5)
    q_val = m2 / m1

    s1_z = np.median(data['spin1'] * data['costilt1'])
    s2_z = np.median(data['spin2'] * data['costilt2'])

    ref = {
        'M_c': float(Mc), 'q': float(q_val), 'eta': float(eta_val),
        's1_z': float(s1_z), 's2_z': float(s2_z),
        'd_L': float(np.median(data['luminosity_distance_Mpc'])),
        'iota': float(np.median(np.arccos(data['costheta_jn']))),
        'ra': float(np.median(data['right_ascension'])),
        'dec': float(np.median(data['declination'])),
        'lambda_1': float(np.median(data['lambda1'])),
        'lambda_2': float(np.median(data['lambda2'])),
        't_c': 0.0, 'phase_c': 0.0, 'psi': 0.0,
        'trigger_time': float(gps),
        'gmst': float(gmst),
    }
    if np.isclose(ref['eta'], 0.25):
        ref['eta'] = 0.249995
    return ref

t_ref0 = time.time()
ref_params = load_reference_params('Results/GW170817_GWTC-1.hdf5')
t_ref = time.time() - t_ref0
print(f"Reference: M_c={ref_params['M_c']:.4f}, q={ref_params['q']:.4f}, d_L={ref_params['d_L']:.1f}")
print(f"[TIMING] Reference params: {t_ref:.1f}s")


# ============================================================================
# 6. HETERODYNING SETUP (501 bins, matching kazewong reference)
# ============================================================================

N_BINS = 501

def max_phase_diff(f, f_low, f_high, chi=1.0):
    gamma = np.arange(-5, 6, 1) / 3.0
    f_2d = np.repeat(f[:, None], len(gamma), axis=1)
    f_star = np.repeat(f_low, len(gamma))
    f_star[gamma >= 0] = f_high
    return 2 * np.pi * chi * np.sum((f_2d / f_star) ** gamma * np.sign(gamma), axis=1)

def make_binning_scheme(freqs, n_bins, chi=1):
    phase_diff_array = max_phase_diff(freqs, freqs[0], freqs[-1], chi=chi)
    bin_f = interp1d(phase_diff_array, freqs)
    f_bins = np.array([bin_f(i) for i in np.linspace(
        phase_diff_array[0], phase_diff_array[-1], n_bins + 1)])
    f_bins_center = (f_bins[:-1] + f_bins[1:]) / 2
    return jnp.array(f_bins), jnp.array(f_bins_center)

def compute_coefficients(data, h_ref, psd, freqs, f_bins, f_bins_center):
    """Pre-compute heterodyning coefficients A0, A1, B0, B1 per bin.

    Uses np.searchsorted for O(n_bins * log n_freq) bin assignment instead
    of O(n_bins * n_freq) boolean masking. The bin boundaries are identical:
    searchsorted(side='left') gives the first index >= edge, matching the
    original (freqs >= f_bins[i]) & (freqs < f_bins[i+1]) condition.
    """
    df = freqs[1] - freqs[0]
    freqs_np = np.array(freqs)
    psd_np = np.array(psd)
    data_prod = np.array(data * h_ref.conj())
    self_prod = np.array(h_ref * h_ref.conj())

    # Binary-search bin edges: bin i spans [f_bins[i], f_bins[i+1])
    edges = np.array(f_bins)
    bin_start = np.searchsorted(freqs_np, edges[:-1], side='left')
    bin_end = np.searchsorted(freqs_np, edges[1:], side='left')
    centers_np = np.array(f_bins_center)

    n_bins = len(f_bins_center)
    A0 = np.empty(n_bins, dtype=complex)
    A1 = np.empty(n_bins, dtype=complex)
    B0 = np.empty(n_bins, dtype=complex)
    B1 = np.empty(n_bins, dtype=complex)
    for i in range(n_bins):
        s = slice(bin_start[i], bin_end[i])
        d_over_psd = data_prod[s] / psd_np[s]
        h_over_psd = self_prod[s] / psd_np[s]
        freq_diff = freqs_np[s] - centers_np[i]
        A0[i] = 4 * np.sum(d_over_psd) * df
        A1[i] = 4 * np.sum(d_over_psd * freq_diff) * df
        B0[i] = 4 * np.sum(h_over_psd) * df
        B1[i] = 4 * np.sum(h_over_psd * freq_diff) * df
    return jnp.array(A0), jnp.array(A1), jnp.array(B0), jnp.array(B1)


def setup_heterodyne(ref_params, detectors, waveform, frequencies, epoch, n_bins):
    params = {k: float(v) for k, v in ref_params.items()}
    if jnp.isclose(params.get('eta', 0.25), 0.25):
        params['eta'] = 0.249995

    print(f"Setting up heterodyning with {n_bins} bins...")
    h_sky = waveform(frequencies, params)

    freq_grid, freq_grid_center = make_binning_scheme(np.array(frequencies), n_bins)
    freq_grid_low = freq_grid[:-1]

    h_amp = jnp.sum(jnp.array([jnp.abs(h_sky[k]) for k in h_sky]), axis=0)
    f_valid = frequencies[jnp.where(h_amp > 0)[0]]
    f_max_val, f_min_val = jnp.max(f_valid), jnp.min(f_valid)

    mask_center = jnp.where((freq_grid_center <= f_max_val) & (freq_grid_center >= f_min_val))[0]
    freq_grid_center = freq_grid_center[mask_center]
    freq_grid_low = freq_grid_low[mask_center]

    start_idx = mask_center[0]
    end_idx = mask_center[-1] + 2
    freq_grid = freq_grid[start_idx:end_idx]

    h_sky_low = waveform(freq_grid_low, params)
    h_sky_center = waveform(freq_grid_center, params)

    A0_list, A1_list, B0_list, B1_list = [], [], [], []
    ref_low_list, ref_center_list = [], []

    for det in detectors:
        waveform_ref = det.fd_response(frequencies, h_sky, params)
        ref_low_list.append(det.fd_response(freq_grid_low, h_sky_low, params))
        ref_center_list.append(det.fd_response(freq_grid_center, h_sky_center, params))

        A0, A1, B0, B1 = compute_coefficients(
            det.sliced_fd_data, waveform_ref, det.sliced_psd, frequencies, freq_grid, freq_grid_center)
        A0_list.append(A0)
        A1_list.append(A1)
        B0_list.append(B0)
        B1_list.append(B1)

    hetero = {
        'freq_grid_low': freq_grid_low,
        'freq_grid_center': freq_grid_center,
        'A0': jnp.stack(A0_list),
        'A1': jnp.stack(A1_list),
        'B0': jnp.stack(B0_list),
        'B1': jnp.stack(B1_list),
        'ref_low': jnp.stack(ref_low_list),
        'ref_center': jnp.stack(ref_center_list),
    }
    print(f"Heterodyning setup complete. Bin shape: {hetero['A0'].shape}")
    return hetero

t_het0 = time.time()
hetero = setup_heterodyne(ref_params, detectors, waveform, frequencies, epoch, N_BINS)
t_het = time.time() - t_het0
print(f"[TIMING] Heterodyning setup: {t_het:.1f}s")

FREQ_LOW = hetero['freq_grid_low']
FREQ_CENTER = hetero['freq_grid_center']
A0 = hetero['A0']
A1 = hetero['A1']
B0 = hetero['B0']
B1 = hetero['B1']
REF_LOW = hetero['ref_low']
REF_CENTER = hetero['ref_center']


# ============================================================================
# 7. HETERODYNED LIKELIHOOD (phase-marginalized or standard)
# ============================================================================

@jax.jit
def loglikelihood_fn(x):
    params = {
        'M_c': x[I_MC], 'q': x[I_Q], 's1_z': x[I_S1Z], 's2_z': x[I_S2Z],
        'iota': x[I_IOTA], 'd_L': x[I_DL], 't_c': x[I_TC],
        'psi': x[I_PSI], 'ra': x[I_RA], 'dec': x[I_DEC],
        'lambda_1': x[I_L1], 'lambda_2': x[I_L2],
        'eta': x[I_Q] / (1 + x[I_Q]) ** 2,
        'phase_c': 0.0 if phase_marg else x[I_PHASEC],
        'trigger_time': gps,
        'gmst': gmst,
    }

    h_sky_low = waveform(FREQ_LOW, params)
    h_sky_center = waveform(FREQ_CENTER, params)

    det_resp_low = jnp.stack([
        det.fd_response(FREQ_LOW, h_sky_low, params)
        for det in detectors
    ])
    det_resp_center = jnp.stack([
        det.fd_response(FREQ_CENTER, h_sky_center, params)
        for det in detectors
    ])

    r0 = det_resp_center / REF_CENTER
    r1 = (det_resp_low / REF_LOW - r0) / (FREQ_LOW - FREQ_CENTER)

    complex_match = jnp.sum(A0 * r0.conj() + A1 * r1.conj())
    optimal_SNR = jnp.sum(
        B0 * jnp.abs(r0) ** 2 + 2 * B1 * (r0 * r1.conj()).real
    )

    if phase_marg:
        ll_gw = -optimal_SNR.real / 2 + log_i0(jnp.absolute(complex_match))
    else:
        ll_gw = (complex_match - optimal_SNR / 2).real

    # Standard siren velocity terms (Abbott et al. 2017)
    ll_vr = stats.norm.logpdf(3327.0, x[I_VP] + x[I_H0] * x[I_DL], 72.0)
    ll_vp = stats.norm.logpdf(310.0, x[I_VP], 150.0)

    return ll_gw + ll_vr + ll_vp


# ============================================================================
# 8. NESTED SAMPLING SETUP
# ============================================================================

num_live = 5000
num_delete = int(num_live * 0.5)
num_mcmc_steps = int(NUM_DIMS * 8)

@jax.jit
def stepper_fn(x, d, t):
    y = x + t * d
    y = y.at[I_PSI].set(jnp.mod(y[I_PSI], jnp.pi))
    y = y.at[I_RA].set(jnp.mod(y[I_RA], 2 * jnp.pi))
    if not phase_marg:
        y = y.at[I_PHASEC].set(jnp.mod(y[I_PHASEC], 2 * jnp.pi))
    return y, True

nested_sampler = blackjax.nss(
    logprior_fn=logprior_fn,
    loglikelihood_fn=loglikelihood_fn,
    num_delete=num_delete,
    num_inner_steps=num_mcmc_steps,
    stepper_fn=stepper_fn,
)


# ============================================================================
# 9. PRIOR SAMPLING & INITIALIZATION
# ============================================================================

def sample_from_prior(key, n):
    collected = []
    remaining = n
    while remaining > 0:
        key, subkey = jax.random.split(key)
        n_try = remaining * 4
        keys = jax.random.split(subkey, NUM_DIMS)
        batch = jnp.zeros((n_try, NUM_DIMS))

        for i in range(NUM_DIMS):
            lo, hi = float(PRIOR_LO[i]), float(PRIOR_HI[i])
            ptype = int(PRIOR_TYPE[i])
            if ptype == 0:
                col = jax.random.uniform(keys[i], (n_try,), minval=lo, maxval=hi)
            elif ptype == 1:
                col = jnp.arccos(1 - 2 * jax.random.uniform(keys[i], (n_try,)))
            elif ptype == 2:
                col = jnp.arcsin(2 * jax.random.uniform(keys[i], (n_try,)) - 1)
            elif ptype == 3:
                col = jax.random.beta(keys[i], 3.0, 1.0, (n_try,)) * (hi - lo) + lo
            elif ptype == 4:
                col = lo * (hi / lo) ** jax.random.uniform(keys[i], (n_try,))
            batch = batch.at[:, i].set(col)

        q = batch[:, I_Q]
        eta = q / (1 + q) ** 2
        M_total = batch[:, I_MC] / eta ** 0.6
        m1 = M_total / (1 + q)
        m2 = q * m1
        valid = (m1 >= M_COMP_LO) & (m1 <= M_COMP_HI) & (m2 >= M_COMP_LO) & (m2 <= M_COMP_HI)
        good = batch[valid]
        collected.append(np.array(good[:remaining]))
        remaining -= len(collected[-1])

    return jnp.array(np.concatenate(collected)[:n])

t_init0 = time.time()
rng_key = jax.random.PRNGKey(0)
rng_key, init_key = jax.random.split(rng_key)
initial_particles = sample_from_prior(init_key, num_live)

state = nested_sampler.init(initial_particles)
t_init = time.time() - t_init0
print(f"[TIMING] Prior sampling + init: {t_init:.1f}s")


# ============================================================================
# 10. RUN NESTED SAMPLING
# ============================================================================

@jax.jit
def one_step(carry, xs):
    state, k = carry
    k, subk = jax.random.split(k, 2)
    state, dead_point = nested_sampler.step(subk, state)
    return (state, k), dead_point

phase_msg = "phase_c marginalized" if phase_marg else "phase_c sampled"
print(f"Running nested sampling: {num_live} live, {NUM_DIMS}D ({phase_msg})")
print("JIT-compiling first step...")
t_jit0 = time.time()
(state, rng_key), dead_first = one_step((state, rng_key), None)
jax.block_until_ready(state)
t_jit = time.time() - t_jit0
print(f"[TIMING] JIT compilation (first step): {t_jit:.1f}s")

ns_start = time.time()
dead = [dead_first]

with tqdm.tqdm(desc="Dead points", initial=num_delete, unit=" dead points") as pbar:
    while not state.integrator.logZ_live - state.integrator.logZ < -3:
        (state, rng_key), dead_info = one_step((state, rng_key), None)
        dead.append(dead_info)
        pbar.update(num_delete)

ns_time = time.time() - ns_start


# ============================================================================
# 11. POST-PROCESSING & OUTPUT
# ============================================================================

result = finalise(state, dead, update_info=False)

samples = NestedSamples(
    np.array(result.particles.position),
    logL=np.array(result.particles.loglikelihood),
    logL_birth=np.array(result.particles.loglikelihood_birth),
    columns=PARAM_NAMES,
    labels=PARAM_LABELS,
)

logzs = samples.logZ(100)
print(f"Log Evidence: {logzs.mean():.2f} +/- {logzs.std():.2f}")

samples.to_csv(f'{label}.csv')
print(f"Saved to {label}.csv")

# Timing summary
t_total = time.time() - t0
print(f"\n{'='*50}")
print(f"TIMING SUMMARY")
print(f"{'='*50}")
print(f"  Data loading:     {t_data:7.1f}s")
print(f"  Reference params: {t_ref:7.1f}s")
print(f"  Heterodyne setup: {t_het:7.1f}s")
print(f"  Init + prior:     {t_init:7.1f}s")
print(f"  JIT compilation:  {t_jit:7.1f}s")
print(f"  Sampling:         {ns_time:7.1f}s")
print(f"  Total:            {t_total:7.1f}s")
print(f"{'='*50}")
