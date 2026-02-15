"""
Phase-Marginalized Heterodyned Nested Sampling for GW170817
============================================================

Performs Bayesian inference on the binary neutron star event GW170817 using:
  - Waveform: IMRPhenomD_NRTidalv2 or TaylorF2 (selectable via --waveform)
  - Likelihood: Heterodyned (relative binning) with analytic phase marginalization
  - Sampler: Blackjax nested slice sampling with periodic boundary wrapping

Phase marginalization reduces dimensionality by 1 (removes phase_c) via the
identity: marginalizing a uniform phase_c in [0,2pi] converts the real
match-filter SNR into log I_0(|<d|h>|), where I_0 is the modified Bessel
function of order 0. This is exact for aligned-spin (non-precessing) waveforms.

The Hubble constant H_0 is jointly inferred using the peculiar velocity model
from Abbott et al. 2017 (arXiv:1710.05832), treating GW170817's host galaxy
NGC 4993 as a standard siren.

Performance notes:
  - All JIT-compiled functions use flat arrays and static indices (no dicts)
  - Detector coefficients are stacked as (n_det, n_bins) arrays
  - Heterodyned computation is vectorized over detectors (no Python loop)
  - Prior computation is fully vectorized (no list comprehension)
  - Dict creation for jimgw API calls happens at trace time (zero runtime cost)

Usage:
  python GW170817_heterodyned_1.py [--waveform {IMRPhenomD_NRTidalv2,TaylorF2}]
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
from gwpy.timeseries import TimeSeries

# ============================================================================
# 0. COMMAND-LINE ARGUMENTS
# ============================================================================
parser = argparse.ArgumentParser(description='Heterodyned nested sampling for GW170817')
parser.add_argument('--waveform', choices=['IMRPhenomD_NRTidalv2', 'TaylorF2'],
                    default='IMRPhenomD_NRTidalv2', help='Waveform approximant')
parser.add_argument('--data-source', choices=['fetch', 'local'],
                    default='fetch',
                    help='Data source: "fetch" pulls from GWOSC via gwpy (requires internet), '
                         '"local" reads HDF5 files from EventData/GWOSC/GW170817/')
parser.add_argument('--psd-source', choices=['self', 'bilby', 'gwtc1', 'kazewong'],
                    default='self',
                    help='PSD source: "self" (estimated from data via gwpy), "bilby" (Bilby PSDs), '
                         '"gwtc1" (official BayesWave PSDs from LIGO-P1900011), '
                         '"kazewong" (kazewong pre-processed PSDs)')
args = parser.parse_args()
waveform_tag = args.waveform
data_source = args.data_source
psd_source = args.psd_source

# Numerically stable log I_0 for phase marginalization:
# log(I_0(x)) = log(i0e(x)) + x, where i0e(x) = exp(-|x|) * I_0(x)
from jax.scipy.special import i0e

@jax.jit
def log_i0(x):
    return jnp.log(i0e(x)) + x


# ============================================================================
# 2. PARAMETER CONFIGURATION (static arrays, no dicts in hot path)
# ============================================================================
# 14 parameters — phase_c is analytically marginalized, not sampled.
# All configuration is expressed as static JAX arrays for JIT-friendly access.

# Parameter names (used only at boundaries: init, output, jimgw API calls)
PARAM_NAMES = [
    "M_c", "q", "s1_z", "s2_z", "iota", "d_L", "t_c",
    "psi", "ra", "dec", "lambda_1", "lambda_2", "H_0", "v_p",
]
PARAM_LABELS = [
    r"$M_c$", r"$q$", r"$s_{1z}$", r"$s_{2z}$", r"$\iota$", r"$d_L$", r"$t_c$",
    r"$\psi$", r"$\alpha$", r"$\delta$", r"$\Lambda_1$", r"$\Lambda_2$", r"$H_0$", r"$v_p$",
]
NUM_DIMS = len(PARAM_NAMES)

# Static parameter indices (compile-time constants for array access)
I_MC, I_Q, I_S1Z, I_S2Z, I_IOTA, I_DL, I_TC = 0, 1, 2, 3, 4, 5, 6
I_PSI, I_RA, I_DEC, I_L1, I_L2, I_H0, I_VP = 7, 8, 9, 10, 11, 12, 13

# Prior bounds: M_c^det range from Abbott et al., PhysRevX 9, 011001, Sec. II.D
# NGC 4993 host galaxy at z=0.0099
PRIOR_LO = jnp.array([
    1.184, 0.125, -0.05, -0.05,             # M_c, q, s1_z, s2_z
    0.0, 1.0, -0.1,                          # iota, d_L, t_c
    0.0, 0.0, -jnp.pi / 2,                   # psi, ra, dec
    0.0, 0.0, 20.0, -1000.0,                 # lambda_1, lambda_2, H_0, v_p
])
PRIOR_HI = jnp.array([
    2.168, 1.00, 0.05, 0.05,                # M_c, q, s1_z, s2_z
    jnp.pi, 75.0, 0.1,                       # iota, d_L, t_c
    jnp.pi, 2 * jnp.pi, jnp.pi / 2,         # psi, ra, dec
    5000.0, 5000.0, 140.0, 1000.0,           # lambda_1, lambda_2, H_0, v_p
])

# Component mass bounds (applied as hard cut in M_c-q space)
M_COMP_LO = 0.5   # M_sun
M_COMP_HI = 7.7   # M_sun

# Prior type encoding: 0=uniform, 1=sin(iota), 2=cos(dec), 3=beta(d_L), 4=log-uniform(H_0)
PRIOR_TYPE = jnp.array([0, 0, 0, 0, 1, 3, 0, 0, 0, 2, 0, 0, 4, 0])

# Pre-computed prior constants (avoid recomputation in JIT)
_PRIOR_RANGE = PRIOR_HI - PRIOR_LO
_PRIOR_LOG_RANGE = jnp.log(_PRIOR_RANGE)
_PRIOR_LOG_LOG_RATIO = jnp.log(jnp.log(PRIOR_HI / PRIOR_LO))
_BETA_LN = jax.scipy.special.betaln(3.0, 1.0)


# ============================================================================
# 3. VECTORIZED LOG-PRIOR (no Python loops, fully JIT-traced)
# ============================================================================

@jax.jit
def logprior_fn(x):
    """Evaluate total log-prior for a flat parameter vector.

    Computes all prior types vectorially and selects via jnp.where.
    Includes hard cut on component masses: m1, m2 in [M_COMP_LO, M_COMP_HI].
    No Python loops, list comprehensions, or dict access.
    """
    in_bounds = (x >= PRIOR_LO) & (x <= PRIOR_HI)

    # Uniform: log(1/(hi-lo)) = -log(hi-lo)
    lp_uniform = jnp.where(in_bounds, -_PRIOR_LOG_RANGE, -jnp.inf)

    # Sin prior (iota): log(sin(x)/2) on [0, pi]
    lp_sin = jnp.where(in_bounds, jnp.log(jnp.abs(jnp.sin(x)) + 1e-300) - jnp.log(2.0), -jnp.inf)

    # Cos prior (dec): log(cos(x)/2) on [-pi/2, pi/2]
    lp_cos = jnp.where(in_bounds, jnp.log(jnp.abs(jnp.cos(x)) + 1e-300) - jnp.log(2.0), -jnp.inf)

    # Beta(3,1) prior (d_L): log(3*u^2 / range) where u = (x-lo)/(hi-lo)
    u = (x - PRIOR_LO) / _PRIOR_RANGE
    lp_beta = jnp.where(in_bounds, 2.0 * jnp.log(jnp.abs(u) + 1e-300) - _PRIOR_LOG_RANGE - _BETA_LN, -jnp.inf)

    # Log-uniform (Jeffreys) prior (H_0): -log(log(hi/lo)) - log(x)
    lp_log = jnp.where(in_bounds, -_PRIOR_LOG_LOG_RATIO - jnp.log(jnp.abs(x) + 1e-300), -jnp.inf)

    # Select per-parameter prior using type index
    lp = jnp.where(PRIOR_TYPE == 0, lp_uniform,
         jnp.where(PRIOR_TYPE == 1, lp_sin,
         jnp.where(PRIOR_TYPE == 2, lp_cos,
         jnp.where(PRIOR_TYPE == 3, lp_beta,
                    lp_log))))

    total = jnp.sum(lp)

    # Component mass constraint: m1, m2 must be in [M_COMP_LO, M_COMP_HI]
    # From M_c, q: eta = q/(1+q)^2, M_total = M_c / eta^(3/5), m1 = M_total/(1+q), m2 = q*m1
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
# 4. EVENT CONFIGURATION & DETECTOR DATA
# ============================================================================

gps = 1187008882.43
fmin = 23.0
fmax = 2048.0
duration = 128
post_trigger_duration = 2
roll_off = 0.4
tukey_alpha = 2 * roll_off / duration
psd_pad = 16
psd_duration = 1024

label = f'Results/PhaseMarg_Heterodyned_{waveform_tag}_{data_source}_psd-{psd_source}'

# Analysis segment: [gps - (duration - post_trigger), gps + post_trigger]
start = gps - (duration - post_trigger_duration)
end = gps + post_trigger_duration

# PSD segment: immediately before the analysis segment
psd_start = start - psd_pad - psd_duration
psd_end = start - psd_pad

t0 = time.time()

# Local GWOSC HDF5 file mapping: ifo name -> file path
GWOSC_LOCAL_DIR = 'EventData/GWOSC/GW170817'
GWOSC_LOCAL_FILES = {
    'H1': os.path.join(GWOSC_LOCAL_DIR, 'H-H1_LOSC_CLN_4_V1-1187007040-2048.hdf5'),
    'L1': os.path.join(GWOSC_LOCAL_DIR, 'L-L1_LOSC_CLN_4_V1-1187007040-2048.hdf5'),
    'V1': os.path.join(GWOSC_LOCAL_DIR, 'V-V1_LOSC_CLN_4_V1-1187007040-2048.hdf5'),
}

def load_gwosc_local(ifo_name, gps_start, gps_end):
    """Load GWOSC strain from a local HDF5 file, slicing to [gps_start, gps_end]."""
    path = GWOSC_LOCAL_FILES[ifo_name]
    ts = TimeSeries.read(path, format='hdf5.gwosc')
    ts = ts.crop(gps_start, gps_end)
    return Data(ts.value, ts.dt.value, ts.epoch.value, ifo_name)

def load_gwosc_local_gwpy(ifo_name, gps_start, gps_end):
    """Load GWOSC strain as a gwpy TimeSeries (for PSD estimation)."""
    path = GWOSC_LOCAL_FILES[ifo_name]
    ts = TimeSeries.read(path, format='hdf5.gwosc')
    ts = ts.crop(gps_start, gps_end)
    return ts

# PSD estimation config (matching bilby/kazewong):
#   - 32s Tukey-windowed segments, 50% overlap, median averaging
PSD_FFT_LENGTH = 32  # seconds per FFT segment
PSD_OVERLAP_FRAC = 0.5
PSD_METHOD = 'median'

GWOSC_PSD_DIR = 'EventData/GWOSC/GW170817'
KAZEWONG_PSD_DIR = 'EventData/GWOSC/GW170817/kazewong'
KAZEWONG_PSD_PREFIX = 'GW170817-IMRD_data0_1187008882-43_generation_data_dump.pickle'


def load_external_psd(psd_src, ifo_name, target_freqs):
    """Load PSD from an external file and interpolate to target frequency grid.

    Sources:
      - 'bilby':   Bilby PSD files from EventData/GWOSC/GW170817/Bilby/
      - 'gwtc1':   Official BayesWave PSDs from GWTC1_GW170817_PSDs.dat (LIGO-P1900011)
      - 'kazewong': Kazewong PSD files from EventData/GWOSC/GW170817/kazewong/
    """
    if psd_src == 'bilby':
        psd_file = os.path.join(GWOSC_PSD_DIR, 'Bilby', f'{ifo_name.lower()}_psd.txt')
        psd_data = np.loadtxt(psd_file)
        freqs_psd, psd_vals = psd_data[:, 0], psd_data[:, 1]
    elif psd_src == 'gwtc1':
        psd_data = np.loadtxt(os.path.join(GWOSC_PSD_DIR, 'GWTC1_GW170817_PSDs.dat'))
        freqs_psd = psd_data[:, 0]
        col_map = {'H1': 1, 'L1': 2, 'V1': 3}
        psd_vals = psd_data[:, col_map[ifo_name]]
    elif psd_src == 'kazewong':
        psd_file = os.path.join(KAZEWONG_PSD_DIR, f'{KAZEWONG_PSD_PREFIX}_{ifo_name}_psd.txt')
        psd_data = np.loadtxt(psd_file)
        freqs_psd, psd_vals = psd_data[:, 0], psd_data[:, 1]
    else:
        raise ValueError(f"Unknown PSD source: {psd_src}")
    psd_interp = interp1d(freqs_psd, psd_vals, kind='linear',
                          fill_value='extrapolate', bounds_error=False)
    return PowerSpectrum(
        values=jnp.array(psd_interp(np.array(target_freqs))),
        frequencies=jnp.array(target_freqs),
        name=ifo_name,
    )


detectors = [get_H1(), get_L1(), get_V1()]
N_DET = len(detectors)
print(f"Data source: {data_source}, PSD source: {psd_source}")

for ifo in detectors:
    t_det = time.time()

    if data_source == 'local':
        # Load from local GWOSC HDF5 files (no internet required)
        strain_data = load_gwosc_local(ifo.name, start, end)
        if psd_source == 'self':
            psd_ts = load_gwosc_local_gwpy(ifo.name, psd_start, psd_end)
    else:
        # Fetch from GWOSC via gwpy (version=2 required for GW170817: V1/V3 have L1 glitch)
        strain_data = Data.from_gwosc(ifo.name, start, end, version=2)
        if psd_source == 'self':
            psd_ts = TimeSeries.fetch_open_data(ifo.name, psd_start, psd_end, version=2)
    t_fetch = time.time() - t_det

    strain_data.set_tukey_window(alpha=tukey_alpha)
    strain_data.fft()
    ifo.set_data(strain_data)

    # PSD loading
    t_psd0 = time.time()
    if psd_source == 'self':
        # PSD via gwpy: median-averaged, Tukey-windowed Welch (matching bilby)
        psd_alpha = 2 * roll_off / PSD_FFT_LENGTH
        psd_gwpy = psd_ts.psd(
            fftlength=PSD_FFT_LENGTH,
            overlap=PSD_FFT_LENGTH * PSD_OVERLAP_FRAC,
            window=('tukey', psd_alpha),
            method=PSD_METHOD,
        )
        # Interpolate PSD to strain frequency grid (PSD df=1/32 -> strain df=1/128)
        psd_interp_fn = interp1d(
            psd_gwpy.frequencies.value, psd_gwpy.value,
            kind='linear', fill_value=(psd_gwpy.value[0], psd_gwpy.value[-1]),
            bounds_error=False,
        )
        strain_freqs = np.array(strain_data.frequencies)
        psd_obj = PowerSpectrum(
            values=jnp.array(psd_interp_fn(strain_freqs)),
            frequencies=jnp.array(strain_freqs),
            name=ifo.name,
        )
    else:
        strain_freqs = np.array(strain_data.frequencies)
        psd_obj = load_external_psd(psd_source, ifo.name, strain_freqs)
    ifo.set_psd(psd_obj)
    t_psd = time.time() - t_psd0

    # Set frequency bounds for the analysis band
    ifo.set_frequency_bounds(fmin, fmax)
    print(f"  {ifo.name}: data={t_fetch:.1f}s, PSD({psd_source})={t_psd:.1f}s, total={time.time()-t_det:.1f}s")

t_data = time.time() - t0
print(f"[TIMING] Data loading: {t_data:.1f}s")

H1, L1, V1 = detectors

if waveform_tag == 'TaylorF2':
    waveform = RippleTaylorF2(f_ref=20.0, use_lambda_tildes=False)
else:
    waveform_tag = 'IMRPhenomD_NRTidalv2'
    waveform = RippleIMRPhenomD_NRTidalv2(f_ref=20.0, use_lambda_tildes=False, no_taper=False)
print(f"Waveform: {waveform_tag}")

frequencies = H1.sliced_frequencies
epoch = duration - post_trigger_duration
gmst = Time(gps, format="gps").sidereal_time("apparent", "greenwich").rad


# ============================================================================
# 5. REFERENCE PARAMETERS (from GWTC-1 posteriors)
# ============================================================================

def load_reference_params(hdf5_path, dataset='IMRPhenomPv2NRT_lowSpin_posterior'):
    """Load GWTC-1 posterior samples and compute median reference parameters.

    Converts detector-frame masses and spin magnitudes/tilts to the ripple
    parametrization (M_c, q, eta, s1_z, s2_z, ...).
    """
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
# 6. HETERODYNING SETUP (pre-compute stacked arrays)
# ============================================================================

N_BINS = 501

def max_phase_diff(f, f_low, f_high, chi=1.0):
    """Maximum accumulated phase across PN orders. Eq.(7) of arXiv:2302.05333."""
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
    """Pre-compute heterodyning coefficients A0, A1, B0, B1 per bin."""
    df = freqs[1] - freqs[0]
    data_prod = np.array(data * h_ref.conj())
    self_prod = np.array(h_ref * h_ref.conj())
    A0, A1, B0, B1 = [], [], [], []
    for i in range(len(f_bins) - 1):
        idx = np.where((freqs >= f_bins[i]) & (freqs < f_bins[i + 1]))[0]
        A0.append(4 * np.sum(data_prod[idx] / psd[idx]) * df)
        A1.append(4 * np.sum(data_prod[idx] / psd[idx] * (freqs[idx] - f_bins_center[i])) * df)
        B0.append(4 * np.sum(self_prod[idx] / psd[idx]) * df)
        B1.append(4 * np.sum(self_prod[idx] / psd[idx] * (freqs[idx] - f_bins_center[i])) * df)
    return jnp.array(A0), jnp.array(A1), jnp.array(B0), jnp.array(B1)


def setup_heterodyne(ref_params, detectors, waveform, frequencies, epoch, n_bins):
    """Build heterodyning reference state. Returns stacked arrays (n_det, n_bins).

    All detector-indexed quantities are stacked as (n_det, n_bins) JAX arrays
    instead of Python dicts, enabling vectorized computation in the likelihood.
    """
    params = {k: float(v) for k, v in ref_params.items()}
    if jnp.isclose(params.get('eta', 0.25), 0.25):
        params['eta'] = 0.249995

    print(f"Setting up heterodyning with {n_bins} bins...")
    h_sky = waveform(frequencies, params)

    freq_grid, freq_grid_center = make_binning_scheme(np.array(frequencies), n_bins)
    freq_grid_low = freq_grid[:-1]

    # Mask to valid waveform support.
    # Use a SINGLE mask on centers, then derive edges from it to maintain
    # the invariant: len(edges) = len(centers) + 1, with edge[i] <= center[i] < edge[i+1].
    h_amp = jnp.sum(jnp.array([jnp.abs(h_sky[k]) for k in h_sky]), axis=0)
    f_valid = frequencies[jnp.where(h_amp > 0)[0]]
    f_max_val, f_min_val = jnp.max(f_valid), jnp.min(f_valid)

    mask_center = jnp.where((freq_grid_center <= f_max_val) & (freq_grid_center >= f_min_val))[0]
    freq_grid_center = freq_grid_center[mask_center]
    freq_grid_low = freq_grid_low[mask_center]

    # Edges: need len(centers) + 1 edges that bracket the valid centers
    start_idx = mask_center[0]
    end_idx = mask_center[-1] + 2     # +1 inclusive, +1 for extra right edge
    freq_grid = freq_grid[start_idx:end_idx]

    h_sky_low = waveform(freq_grid_low, params)
    h_sky_center = waveform(freq_grid_center, params)

    # Build per-detector arrays, then stack
    # Note: fd_response handles time shifts internally (trigger_time - epoch + t_c)
    A0_list, A1_list, B0_list, B1_list = [], [], [], []
    ref_low_list, ref_center_list = [], []

    for det in detectors:
        waveform_ref = det.fd_response(frequencies, h_sky, params)
        ref_low_list.append(det.fd_response(freq_grid_low, h_sky_low, params))
        ref_center_list.append(det.fd_response(freq_grid_center, h_sky_center, params))

        A0, A1, B0, B1 = compute_coefficients(
            det.sliced_fd_data, waveform_ref, det.sliced_psd, frequencies, freq_grid, freq_grid_center)
        # No further masking needed: compute_coefficients already received the
        # masked grids, so its output contains only the valid bins.
        A0_list.append(A0)
        A1_list.append(A1)
        B0_list.append(B0)
        B1_list.append(B1)

    # Stack into (n_det, n_bins) arrays — no dicts in the hot path
    hetero = {
        'freq_grid_low': freq_grid_low,
        'freq_grid_center': freq_grid_center,
        'A0': jnp.stack(A0_list),            # (n_det, n_bins)
        'A1': jnp.stack(A1_list),
        'B0': jnp.stack(B0_list),
        'B1': jnp.stack(B1_list),
        'ref_low': jnp.stack(ref_low_list),   # (n_det, n_bins)
        'ref_center': jnp.stack(ref_center_list),
    }
    print(f"Heterodyning setup complete. Bin shape: {hetero['A0'].shape}")
    return hetero

t_het0 = time.time()
hetero = setup_heterodyne(ref_params, detectors, waveform, frequencies, epoch, N_BINS)
t_het = time.time() - t_het0
print(f"[TIMING] Heterodyning setup: {t_het:.1f}s")

# Extract as module-level constants for closure capture (static in JIT)
FREQ_LOW = hetero['freq_grid_low']
FREQ_CENTER = hetero['freq_grid_center']
A0 = hetero['A0']          # (n_det, n_bins)
A1 = hetero['A1']
B0 = hetero['B0']
B1 = hetero['B1']
REF_LOW = hetero['ref_low']      # (n_det, n_bins)
REF_CENTER = hetero['ref_center']


# ============================================================================
# 7. PHASE-MARGINALIZED HETERODYNED LIKELIHOOD (array-native)
# ============================================================================

@jax.jit
def loglikelihood_fn(x):
    """Phase-marginalized heterodyned log-likelihood + standard siren terms.

    The hot path is fully array-native:
      1. Build param dict ONCE for jimgw API calls (traced at compile time)
      2. Waveform evaluation at ~100 bin frequencies (jimgw, traced once)
      3. Detector responses stacked as (n_det, n_bins) (jimgw, traced once per det)
      4. Heterodyned computation vectorized over detectors (pure JAX arrays)
      5. Phase marginalization via log I_0(|complex <d|h>|)

    Note: dict creation for jimgw API is a trace-time operation. After JIT
    compilation, the XLA graph contains only array ops — no Python overhead.
    """
    # --- Build param dict for jimgw API (trace-time only) ---
    params = {
        'M_c': x[I_MC], 'q': x[I_Q], 's1_z': x[I_S1Z], 's2_z': x[I_S2Z],
        'iota': x[I_IOTA], 'd_L': x[I_DL], 't_c': x[I_TC],
        'psi': x[I_PSI], 'ra': x[I_RA], 'dec': x[I_DEC],
        'lambda_1': x[I_L1], 'lambda_2': x[I_L2],
        'eta': x[I_Q] / (1 + x[I_Q]) ** 2,
        'phase_c': 0.0,  # marginalized out
        'trigger_time': gps,
        'gmst': gmst,
    }

    # --- Waveform at bin frequencies (jimgw API, traced once) ---
    h_sky_low = waveform(FREQ_LOW, params)
    h_sky_center = waveform(FREQ_CENTER, params)

    # --- Detector responses: stack as (n_det, n_bins) ---
    # fd_response handles time shifts internally (trigger_time - epoch + t_c)
    det_resp_low = jnp.stack([
        det.fd_response(FREQ_LOW, h_sky_low, params)
        for det in detectors
    ])  # (n_det, n_bins)
    det_resp_center = jnp.stack([
        det.fd_response(FREQ_CENTER, h_sky_center, params)
        for det in detectors
    ])  # (n_det, n_bins)

    # --- Heterodyned computation: vectorized over detectors ---
    r0 = det_resp_center / REF_CENTER                                    # (n_det, n_bins)
    r1 = (det_resp_low / REF_LOW - r0) / (FREQ_LOW - FREQ_CENTER)       # (n_det, n_bins)

    # Complex <d|h> accumulated across detectors and bins (phase-marginalized)
    complex_d_inner_h = jnp.sum(A0 * r0.conj() + A1 * r1.conj())        # scalar

    # Optimal SNR: sum over detectors and bins
    optimal_SNR = jnp.sum(
        B0 * jnp.abs(r0) ** 2 + 2 * B1 * (r0 * r1.conj()).real
    )                                                                     # scalar

    # Phase-marginalized log-likelihood: -<h|h>/2 + log I_0(|<d|h>|)
    ll_gw = -optimal_SNR.real / 2 + log_i0(jnp.absolute(complex_d_inner_h))

    # --- Standard siren velocity terms (Abbott et al. 2017, arXiv:1710.05832) ---
    # v_r ~ N(v_p + H_0 * d_L, 72)  — Hubble flow + peculiar velocity
    # v_p ~ N(310, 150)              — host group prior
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
    """Linear step with periodic wrapping for psi (pi) and ra (2pi).

    Returns (new_position, is_accepted) as required by blackjax.nss API.
    """
    y = x + t * d
    y = y.at[I_PSI].set(jnp.mod(y[I_PSI], jnp.pi))
    y = y.at[I_RA].set(jnp.mod(y[I_RA], 2 * jnp.pi))
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
    """Draw n samples for all parameters. Returns (n, NUM_DIMS) array.

    Uses rejection sampling to enforce component mass constraint [M_COMP_LO, M_COMP_HI].
    Oversamples by 4x then filters, repeating until n valid samples are obtained.
    """
    collected = []
    remaining = n
    while remaining > 0:
        key, subkey = jax.random.split(key)
        n_try = remaining * 4  # oversample
        keys = jax.random.split(subkey, NUM_DIMS)
        batch = jnp.zeros((n_try, NUM_DIMS))

        for i in range(NUM_DIMS):
            lo, hi = float(PRIOR_LO[i]), float(PRIOR_HI[i])
            ptype = int(PRIOR_TYPE[i])
            if ptype == 0:    # uniform
                col = jax.random.uniform(keys[i], (n_try,), minval=lo, maxval=hi)
            elif ptype == 1:  # sin (iota): inverse CDF = arccos(1 - 2u)
                col = jnp.arccos(1 - 2 * jax.random.uniform(keys[i], (n_try,)))
            elif ptype == 2:  # cos (dec): inverse CDF = arcsin(2u - 1)
                col = jnp.arcsin(2 * jax.random.uniform(keys[i], (n_try,)) - 1)
            elif ptype == 3:  # beta(3,1)
                col = jax.random.beta(keys[i], 3.0, 1.0, (n_try,)) * (hi - lo) + lo
            elif ptype == 4:  # log-uniform: x = lo * (hi/lo)^u
                col = lo * (hi / lo) ** jax.random.uniform(keys[i], (n_try,))
            batch = batch.at[:, i].set(col)

        # Filter by component mass constraint
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

print(f"Running nested sampling: {num_live} live, {NUM_DIMS}D (phase_c marginalized)")
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

# Combine dead + live points via blackjax utility.
# finalise() concatenates all dead NSInfo objects with the final live particles,
# returning a single NSInfo with .particles (StateWithLogLikelihood).
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
