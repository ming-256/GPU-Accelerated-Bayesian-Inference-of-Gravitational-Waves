"""
Bilby analysis for GW150914 — BBH (IMRPhenomD)
================================================

Uses relative binning (heterodyned likelihood) + phase marginalization,
matching the JAX heterodyned script (GW150914_heterodyned.py).

Sampler: PyPolyChord (PolyChord nested sampling) with MPI.

Usage (two-step HPC workflow):
  # Step 1 — data generation (login node, needs internet):
  python run_GW150914.py --gen-only

  # Step 2 — sampling (compute nodes, MPI):
  mpirun -n $NPROCS python run_GW150914.py --from-pickle <pickle_path>

  # Or single-step (needs internet + compute):
  python run_GW150914.py
"""

import os
import sys
import time
import pickle
import argparse
import numpy as np

import bilby
from bilby.gw.detector import InterferometerList
from bilby.gw.source import lal_binary_black_hole
from bilby.gw.waveform_generator import WaveformGenerator
from bilby.gw.likelihood import RelativeBinningGravitationalWaveTransient

# ============================================================================
# CLI
# ============================================================================
parser = argparse.ArgumentParser(
    description='Bilby GW150914 analysis — BBH (IMRPhenomD)')
parser.add_argument('--nlive', type=int, default=2000)
parser.add_argument('--num-repeats', type=int, default=40)
parser.add_argument('--outdir', default=None,
                    help='Output directory (default: ../results/GW150914_IMRPhenomD)')
parser.add_argument('--gen-only', action='store_true',
                    help='Generate data pickle and exit (run on login node)')
parser.add_argument('--from-pickle', default=None,
                    help='Load data from pickle (run on compute node)')
parser.add_argument('--seed', type=int, default=42)
args = parser.parse_args()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
label = 'GW150914_IMRPhenomD'
if args.outdir is None:
    args.outdir = os.path.join(SCRIPT_DIR, '..', 'results', label)
os.makedirs(args.outdir, exist_ok=True)

bilby.core.utils.setup_logger(outdir=args.outdir, label=label, log_level='INFO')
logger = bilby.core.utils.logger

# ============================================================================
# Event configuration (matched to JAX GW150914_heterodyned.py)
# ============================================================================
TRIGGER_TIME = 1126259462.4
FMIN = 20.0
FMAX = 1024.0
DURATION = 8
POST_TRIGGER = 2
ROLL_OFF = 0.4

# GWTC-2p1 median fiducial parameters for relative binning
FIDUCIAL = dict(
    chirp_mass=30.435750,
    mass_ratio=0.845449,
    chi_1=-0.033522,
    chi_2=-0.046909,
    luminosity_distance=463.03,
    theta_jn=2.627067,
    ra=1.787653,
    dec=-1.220306,
    geocent_time=TRIGGER_TIME,
    psi=1.465940,
    phase=0.0,
)


# ============================================================================
# Data loading
# ============================================================================
def load_data():
    """Fetch GW150914 strain data from GWOSC and estimate PSDs."""
    from gwpy.timeseries import TimeSeries

    start_time = TRIGGER_TIME - (DURATION - POST_TRIGGER)
    psd_start = start_time - 16 - 1024
    psd_end = start_time - 16

    ifos = InterferometerList([])
    for ifo_name in ['H1', 'L1']:
        logger.info(f'Loading {ifo_name} from GWOSC...')
        t0 = time.time()

        ifo = bilby.gw.detector.get_empty_interferometer(ifo_name)

        # Strain data
        strain = TimeSeries.fetch_open_data(
            ifo_name, start_time, start_time + DURATION)
        ifo.strain_data.set_from_gwpy_timeseries(strain)

        # PSD via Welch (32 s Tukey segments, 50% overlap, median averaging)
        psd_data = TimeSeries.fetch_open_data(
            ifo_name, psd_start, psd_end)
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
        dump = dict(ifos=ifos)
        with open(PICKLE_PATH, 'wb') as f:
            pickle.dump(dump, f)
        logger.info(f'Data pickle saved to {PICKLE_PATH}')
        logger.info('Run sampling with:')
        logger.info(f'  mpirun -n $NPROCS python {__file__} '
                     f'--from-pickle {PICKLE_PATH}')
        sys.exit(0)

# ============================================================================
# Waveform generator
# ============================================================================
wfg = WaveformGenerator(
    duration=DURATION,
    sampling_frequency=ifos[0].strain_data.sampling_frequency,
    frequency_domain_source_model=lal_binary_black_hole,
    parameter_conversions=bilby.gw.conversion.convert_to_lal_binary_black_hole_parameters,
    waveform_arguments=dict(
        waveform_approximant='IMRPhenomD',
        reference_frequency=20.0,
        minimum_frequency=FMIN,
    ),
)

# ============================================================================
# Priors
# ============================================================================
prior_file = os.path.join(SCRIPT_DIR, 'GW150914_IMRPhenomD.prior')
priors = bilby.gw.prior.PriorDict(prior_file)

# ============================================================================
# Likelihood: relative binning + phase marginalization
# ============================================================================
logger.info('Setting up relative binning likelihood...')
t_like0 = time.time()

likelihood = RelativeBinningGravitationalWaveTransient(
    interferometers=ifos,
    waveform_generator=wfg,
    priors=priors,
    phase_marginalization=True,
    time_marginalization=False,
    distance_marginalization=False,
    jitter_time=False,
    fiducial_parameters=FIDUCIAL,
    epsilon=0.5,
)

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
    priors=priors,
    sampler='pypolychord',
    nlive=args.nlive,
    num_repeats=args.num_repeats,
    nprior=-1,
    resume=True,
    outdir=args.outdir,
    label=label,
    seed=args.seed,
    conversion_function=bilby.gw.conversion.generate_all_bbh_parameters,
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
    f'Waveform: IMRPhenomD',
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
