"""
Bilby analysis for GW170817 — BNS with standard siren (H_0, v_p)
=================================================================

Uses relative binning (heterodyned likelihood) + phase marginalization,
matching the JAX heterodyned scripts.  Adds two standard-siren log-likelihood
terms on top of the GW likelihood:

  ll_vr = N(3327 | v_p + H_0 * d_L, 72)     recession velocity of NGC 4993
  ll_vp = N(310  | v_p,              150)     peculiar velocity constraint

Sampler: PyPolyChord (PolyChord nested sampling) with MPI.

Usage (two-step HPC workflow):
  # Step 1 — data generation (login node, needs internet):
  python run_GW170817.py --waveform IMRPhenomD_NRTidalv2 --gen-only

  # Step 2 — sampling (compute nodes, MPI):
  mpirun -n $NPROCS python run_GW170817.py \\
      --waveform IMRPhenomD_NRTidalv2 --from-pickle <pickle_path>

  # Or single-step (needs internet + compute):
  python run_GW170817.py --waveform IMRPhenomD_NRTidalv2
"""

import os
import sys
import time
import pickle
import argparse
import numpy as np
from scipy import stats

import bilby
from bilby.gw.detector import InterferometerList
from bilby.gw.source import lal_binary_neutron_star
from bilby.gw.waveform_generator import WaveformGenerator
from bilby.gw.likelihood import RelativeBinningGravitationalWaveTransient

# ============================================================================
# Custom likelihood: GW + standard siren
# ============================================================================
class StandardSirenLikelihood(bilby.Likelihood):
    """Wraps a GW likelihood and adds standard-siren H_0/v_p terms.

    The total log-likelihood is:
        log L = log L_GW + log L_vr + log L_vp

    where:
        L_vr = N(v_recession | v_p + H_0 * d_L, sigma_vr)
        L_vp = N(v_p_obs     | v_p,              sigma_vp)

    Parameters not used by the GW likelihood (H_0, v_p) are filtered out
    so they are not passed to the waveform generator.
    """

    def __init__(self, gw_likelihood,
                 v_recession=3327.0, sigma_vr=72.0,
                 v_p_obs=310.0, sigma_vp=150.0):
        self._gw_likelihood = gw_likelihood
        self._gw_param_keys = set(gw_likelihood.parameters.keys())
        self.v_recession = v_recession
        self.sigma_vr = sigma_vr
        self.v_p_obs = v_p_obs
        self.sigma_vp = sigma_vp

        # Combine parameter spaces
        parameters = dict(gw_likelihood.parameters)
        parameters['H_0'] = None
        parameters['v_p'] = None
        super().__init__(parameters=parameters)

    @property
    def priors(self):
        return getattr(self._gw_likelihood, 'priors', None)

    @priors.setter
    def priors(self, value):
        self._gw_likelihood.priors = value

    def log_likelihood(self):
        # Forward only GW parameters to the inner likelihood
        for key in self._gw_param_keys:
            self._gw_likelihood.parameters[key] = self.parameters[key]

        ll_gw = self._gw_likelihood.log_likelihood()

        d_L = self.parameters['luminosity_distance']
        H_0 = self.parameters['H_0']
        v_p = self.parameters['v_p']

        # Recession velocity: v_r_model = v_p + H_0 * d_L
        ll_vr = stats.norm.logpdf(self.v_recession,
                                  loc=v_p + H_0 * d_L,
                                  scale=self.sigma_vr)
        # Peculiar velocity constraint
        ll_vp = stats.norm.logpdf(self.v_p_obs,
                                  loc=v_p,
                                  scale=self.sigma_vp)

        return ll_gw + ll_vr + ll_vp

    def noise_log_likelihood(self):
        return self._gw_likelihood.noise_log_likelihood()


# ============================================================================
# CLI
# ============================================================================
parser = argparse.ArgumentParser(
    description='Bilby GW170817 analysis — BNS + standard siren (H_0, v_p)')
parser.add_argument('--waveform', choices=['IMRPhenomD_NRTidalv2', 'TaylorF2'],
                    default='IMRPhenomD_NRTidalv2')
parser.add_argument('--nlive', type=int, default=2000)
parser.add_argument('--num-repeats', type=int, default=40)
parser.add_argument('--outdir', default=None,
                    help='Output directory (default: ../results/GW170817_<waveform>)')
parser.add_argument('--gen-only', action='store_true',
                    help='Generate data pickle and exit (run on login node)')
parser.add_argument('--from-pickle', default=None,
                    help='Load data from pickle (run on compute node)')
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if args.outdir is None:
    args.outdir = os.path.join(SCRIPT_DIR, '..', 'results',
                               f'GW170817_{args.waveform}')
os.makedirs(args.outdir, exist_ok=True)

label = f'GW170817_{args.waveform}'
bilby.core.utils.setup_logger(outdir=args.outdir, label=label, log_level='INFO')
logger = bilby.core.utils.logger

# ============================================================================
# Event configuration (matched to JAX scripts)
# ============================================================================
TRIGGER_TIME = 1187008882.43
FMIN = 23.0
FMAX = 2048.0
DURATION = 128
POST_TRIGGER = 2
ROLL_OFF = 0.4

# GWTC-1 median fiducial parameters for relative binning
FIDUCIAL = dict(
    chirp_mass=1.197555,
    mass_ratio=0.865927,
    chi_1=0.002908,
    chi_2=0.001439,
    luminosity_distance=39.96,
    theta_jn=2.559692,
    ra=3.446160,
    dec=-0.408084,
    geocent_time=TRIGGER_TIME,
    psi=0.0,
    phase=0.0,
    lambda_1=269.0,
    lambda_2=445.8,
)


# ============================================================================
# Data loading
# ============================================================================
def load_data():
    """Fetch GW170817 strain data from GWOSC and estimate PSDs."""
    from gwpy.timeseries import TimeSeries

    start_time = TRIGGER_TIME - (DURATION - POST_TRIGGER)
    psd_start = start_time - 16 - 1024   # 1024 s PSD segment, 16 s pad
    psd_end = start_time - 16

    ifos = InterferometerList([])
    for ifo_name in ['H1', 'L1', 'V1']:
        logger.info(f'Loading {ifo_name} from GWOSC (version 2)...')
        t0 = time.time()

        ifo = bilby.gw.detector.get_empty_interferometer(ifo_name)

        # Strain data
        strain = TimeSeries.fetch_open_data(
            ifo_name, start_time, start_time + DURATION, version=2)
        ifo.strain_data.set_from_gwpy_timeseries(strain)

        # PSD via Welch (32 s Tukey segments, 50% overlap, median averaging)
        psd_data = TimeSeries.fetch_open_data(
            ifo_name, psd_start, psd_end, version=2)
        psd_alpha = 2 * ROLL_OFF / 32
        psd_asd = psd_data.psd(
            fftlength=32, overlap=16,
            window=('tukey', psd_alpha), method='median')
        ifo.power_spectral_density = bilby.gw.detector.PowerSpectralDensity(
            frequency_array=np.array(psd_asd.frequencies.value),
            psd_array=np.array(psd_asd.value))

        ifo.minimum_frequency = FMIN
        ifo.maximum_frequency = FMAX
        ifos.append(ifo)
        logger.info(f'  {ifo_name} loaded in {time.time() - t0:.1f}s')

    return ifos


# ============================================================================
# Pickle I/O (two-step HPC workflow)
# ============================================================================
PICKLE_PATH = os.path.join(args.outdir, f'{label}_data_dump.pickle')

if args.from_pickle:
    logger.info(f'Loading data from {args.from_pickle}')
    with open(args.from_pickle, 'rb') as f:
        dump = pickle.load(f)
    ifos = dump['ifos']
    logger.info(f'  Loaded {len(ifos)} interferometers')
else:
    t_data0 = time.time()
    ifos = load_data()
    t_data = time.time() - t_data0
    logger.info(f'Data loading: {t_data:.1f}s')

    if args.gen_only:
        dump = dict(ifos=ifos, waveform=args.waveform)
        with open(PICKLE_PATH, 'wb') as f:
            pickle.dump(dump, f)
        logger.info(f'Data pickle saved to {PICKLE_PATH}')
        logger.info('Run sampling with:')
        logger.info(f'  mpirun -n $NPROCS python {__file__} '
                     f'--waveform {args.waveform} --from-pickle {PICKLE_PATH}')
        sys.exit(0)

# ============================================================================
# Waveform generator
# ============================================================================
wfg = WaveformGenerator(
    duration=DURATION,
    sampling_frequency=ifos[0].strain_data.sampling_frequency,
    frequency_domain_source_model=lal_binary_neutron_star,
    parameter_conversions=bilby.gw.conversion.convert_to_lal_binary_neutron_star_parameters,
    waveform_arguments=dict(
        waveform_approximant=args.waveform,
        reference_frequency=20.0,
        minimum_frequency=FMIN,
    ),
)

# ============================================================================
# Priors
# ============================================================================
prior_file = os.path.join(SCRIPT_DIR, 'GW170817.prior')
full_priors = bilby.gw.prior.PriorDict(prior_file)

# GW-only priors (exclude H_0, v_p) — passed to the GW likelihood constructor
gw_priors = bilby.gw.prior.PriorDict({
    k: v for k, v in full_priors.items()
    if k not in ('H_0', 'v_p')
})

# ============================================================================
# Likelihood: relative binning + phase marg + standard siren
# ============================================================================
logger.info('Setting up relative binning likelihood + standard siren...')
t_like0 = time.time()

gw_likelihood = RelativeBinningGravitationalWaveTransient(
    interferometers=ifos,
    waveform_generator=wfg,
    priors=gw_priors,
    phase_marginalization=True,
    time_marginalization=False,
    distance_marginalization=False,
    jitter_time=False,
    fiducial_parameters=FIDUCIAL,
    epsilon=0.5,
)

likelihood = StandardSirenLikelihood(gw_likelihood)

t_like = time.time() - t_like0
logger.info(f'Likelihood setup: {t_like:.1f}s')

# ============================================================================
# Sampling (PyPolyChord with MPI)
# ============================================================================
logger.info(f'Starting PyPolyChord: nlive={args.nlive}, '
            f'num_repeats={args.num_repeats}')
t_samp0 = time.time()

result = bilby.run_sampler(
    likelihood=likelihood,
    priors=full_priors,
    sampler='pypolychord',
    nlive=args.nlive,
    num_repeats=args.num_repeats,
    nprior=-1,
    resume=True,
    outdir=args.outdir,
    label=label,
    seed=args.seed,
    conversion_function=bilby.gw.conversion.generate_all_bns_parameters,
    plot=False,
)

t_samp = time.time() - t_samp0
t_total = time.time() - (t_data0 if not args.from_pickle else t_like0)

# ============================================================================
# Timing summary
# ============================================================================
timing_path = os.path.join(args.outdir, 'timing.txt')
timing_lines = [
    f'Run: {label}',
    f'Waveform: {args.waveform}',
    f'nlive: {args.nlive}',
    f'num_repeats: {args.num_repeats}',
    f'Likelihood setup: {t_like:.1f}s',
    f'Sampling: {t_samp:.1f}s ({t_samp/3600:.2f}h)',
    f'Total: {t_total:.1f}s ({t_total/3600:.2f}h)',
    f'Log evidence: {result.log_evidence:.2f} +/- {result.log_evidence_err:.2f}',
]
with open(timing_path, 'w') as f:
    f.write('\n'.join(timing_lines) + '\n')

print(f'\n{"="*60}')
for line in timing_lines:
    print(f'  {line}')
print(f'  Results: {args.outdir}/')
print(f'{"="*60}')
