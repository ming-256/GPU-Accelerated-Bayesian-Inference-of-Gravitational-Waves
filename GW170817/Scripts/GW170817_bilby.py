"""
Bilby Nested Sampling for GW170817
====================================

Runs Bayesian inference on GW170817 using bilby + dynesty, with options for:
  - Full likelihood (unheterodyned)
  - Relative binning (heterodyned)
  - Phase marginalization

Priors are matched to the JAX heterodyned script (GW170817_heterodyned_1.py).
Data is fetched from GWOSC (version 2, glitch-free L1).

Usage:
  python GW170817_bilby.py --mode full
  python GW170817_bilby.py --mode heterodyned
  python GW170817_bilby.py --mode full --phase-marginalization
  python GW170817_bilby.py --mode heterodyned --phase-marginalization

For parallel bilby (MPI):
  mpirun -n <NPROCS> parallel_bilby_analysis outdir/GW170817_bilby_<mode>_data_dump.pickle
"""

import os
import argparse
import time
import numpy as np

import bilby
from bilby.gw.detector import InterferometerList
from bilby.gw.source import lal_binary_neutron_star
from bilby.gw.waveform_generator import WaveformGenerator
from bilby.gw.likelihood import (
    GravitationalWaveTransient,
    RelativeBinningGravitationalWaveTransient,
)

# ============================================================================
# 0. COMMAND-LINE ARGUMENTS
# ============================================================================
parser = argparse.ArgumentParser(description='Bilby nested sampling for GW170817')
parser.add_argument('--mode', choices=['full', 'heterodyned'], default='full',
                    help='Likelihood: "full" (standard) or "heterodyned" (relative binning)')
parser.add_argument('--waveform', choices=['IMRPhenomD_NRTidalv2', 'TaylorF2'],
                    default='IMRPhenomD_NRTidalv2', help='Waveform approximant')
parser.add_argument('--phase-marginalization', action='store_true',
                    help='Enable analytic phase marginalization')
parser.add_argument('--nlive', type=int, default=1000,
                    help='Number of live points for dynesty')
parser.add_argument('--nact', type=int, default=10,
                    help='Number of autocorrelation times for dynesty')
parser.add_argument('--seed', type=int, default=42,
                    help='Random seed for reproducibility')
parser.add_argument('--parallel', action='store_true',
                    help='Use parallel_bilby data generation (for MPI runs)')
args = parser.parse_args()

# ============================================================================
# 1. EVENT CONFIGURATION (matched to JAX script)
# ============================================================================
trigger_time = 1187008882.43
fmin = 23.0
fmax = 2048.0
duration = 128
post_trigger_duration = 2
roll_off = 0.4
psd_duration = 1024
psd_pad = 16

# Label for output (consistent with JAX script naming: PhaseMarg / NoMarg prefix)
marg_tag = 'PhaseMarg' if args.phase_marginalization else 'NoMarg'
label = f'{marg_tag}_Bilby_{args.mode}_{args.waveform}'
outdir = os.path.join('Results', label)
os.makedirs(outdir, exist_ok=True)

bilby.core.utils.setup_logger(outdir=outdir, label=label, log_level='INFO')
logger = bilby.core.utils.logger

logger.info(f'Mode: {args.mode}')
logger.info(f'Waveform: {args.waveform}')
logger.info(f'Phase marginalization: {args.phase_marginalization}')
logger.info(f'N_live: {args.nlive}')

# ============================================================================
# 2. DATA LOADING (GWOSC fetch, version 2 — matches JAX "fetch" source)
# ============================================================================
t_start = time.time()

# Analysis segment
start_time = trigger_time - (duration - post_trigger_duration)

# PSD segment: immediately before analysis, with padding
psd_start_time = start_time - psd_pad - psd_duration
psd_end_time = start_time - psd_pad

ifo_names = ['H1', 'L1', 'V1']
ifos = InterferometerList([])

for ifo_name in ifo_names:
    t_det = time.time()
    logger.info(f'Loading {ifo_name} data from GWOSC (version 2)...')

    ifo = bilby.gw.detector.get_empty_interferometer(ifo_name)

    # Fetch strain data (version=2 avoids L1 glitch in v1/v3)
    from gwpy.timeseries import TimeSeries
    strain_gwpy = TimeSeries.fetch_open_data(
        ifo_name, start_time, start_time + duration, version=2
    )

    # Set strain data on interferometer
    ifo.strain_data.set_from_gwpy_timeseries(strain_gwpy)

    # Fetch PSD data and estimate PSD using Welch method
    psd_gwpy = TimeSeries.fetch_open_data(
        ifo_name, psd_start_time, psd_end_time, version=2
    )

    # PSD: 32s Tukey-windowed segments, 50% overlap, median averaging (matching bilby/kazewong)
    psd_fftlength = 32  # seconds per FFT segment
    psd_alpha = 2 * roll_off / psd_fftlength
    psd_asd = psd_gwpy.psd(
        fftlength=psd_fftlength, overlap=psd_fftlength / 2,
        window=('tukey', psd_alpha), method='median',
    )

    ifo.power_spectral_density = bilby.gw.detector.PowerSpectralDensity(
        frequency_array=np.array(psd_asd.frequencies.value),
        psd_array=np.array(psd_asd.value),
    )

    ifo.minimum_frequency = fmin
    ifo.maximum_frequency = fmax

    ifos.append(ifo)
    logger.info(f'  {ifo_name} loaded in {time.time() - t_det:.1f}s')

t_data = time.time() - t_start
logger.info(f'Total data loading time: {t_data:.1f}s')

# ============================================================================
# 3. WAVEFORM GENERATOR
# ============================================================================
waveform_arguments = dict(
    waveform_approximant=args.waveform,
    reference_frequency=20.0,
    minimum_frequency=fmin,
)

waveform_generator = WaveformGenerator(
    duration=duration,
    sampling_frequency=ifos[0].strain_data.sampling_frequency,
    frequency_domain_source_model=lal_binary_neutron_star,
    parameter_conversions=bilby.gw.conversion.convert_to_lal_binary_neutron_star_parameters,
    waveform_arguments=waveform_arguments,
)

# ============================================================================
# 4. PRIORS (matched to JAX script)
# ============================================================================
prior_file = os.path.join(os.path.dirname(__file__), 'GW170817_bilby.prior')
priors = bilby.gw.prior.PriorDict(prior_file)

# ============================================================================
# 5. LIKELIHOOD
# ============================================================================
t_like_start = time.time()

likelihood_kwargs = dict(
    interferometers=ifos,
    waveform_generator=waveform_generator,
    phase_marginalization=args.phase_marginalization,
    priors=priors,
    time_marginalization=False,
    distance_marginalization=False,
    jitter_time=False,
)

if args.mode == 'heterodyned':
    logger.info('Setting up relative binning likelihood...')
    # Fiducial parameters from GWTC-1 median (same as JAX reference params)
    import h5py
    gwtc1_path = 'Results/GW170817_GWTC-1.hdf5'
    with h5py.File(gwtc1_path, 'r') as f:
        data = f['IMRPhenomPv2NRT_lowSpin_posterior'][:]

    m1_det = np.median(data['m1_detector_frame_Msun'])
    m2_det = np.median(data['m2_detector_frame_Msun'])
    M = m1_det + m2_det
    eta_val = m1_det * m2_det / M**2
    Mc_det = M * eta_val**(3.0 / 5)
    q_val = m2_det / m1_det

    s1_z = np.median(data['spin1'] * np.cos(np.arccos(data['costilt1'])))
    s2_z = np.median(data['spin2'] * np.cos(np.arccos(data['costilt2'])))

    fiducial_parameters = dict(
        chirp_mass=float(Mc_det),
        mass_ratio=float(q_val),
        chi_1=float(s1_z),
        chi_2=float(s2_z),
        luminosity_distance=float(np.median(data['luminosity_distance_Mpc'])),
        theta_jn=float(np.median(np.arccos(data['costheta_jn']))),
        ra=float(np.median(data['right_ascension'])),
        dec=float(np.median(data['declination'])),
        geocent_time=float(trigger_time),
        psi=0.0,
        phase=0.0,
        lambda_1=float(np.median(data['lambda1'])),
        lambda_2=float(np.median(data['lambda2'])),
    )

    logger.info(f'Fiducial: Mc={fiducial_parameters["chirp_mass"]:.4f}, '
                f'q={fiducial_parameters["mass_ratio"]:.4f}, '
                f'd_L={fiducial_parameters["luminosity_distance"]:.1f}')

    likelihood = RelativeBinningGravitationalWaveTransient(
        **likelihood_kwargs,
        fiducial_parameters=fiducial_parameters,
        epsilon=0.5,
    )
else:
    logger.info('Setting up full (unheterodyned) likelihood...')
    likelihood = GravitationalWaveTransient(**likelihood_kwargs)

t_like = time.time() - t_like_start
logger.info(f'Likelihood setup time: {t_like:.1f}s')

# ============================================================================
# 6. PARALLEL BILBY DATA GENERATION (optional)
# ============================================================================
if args.parallel:
    logger.info('Generating parallel_bilby data dump...')
    import pickle
    data_dump = dict(
        interferometers=ifos,
        waveform_generator=waveform_generator,
        likelihood=likelihood,
        priors=priors,
        args=vars(args),
    )
    dump_path = os.path.join(outdir, f'{label}_data_dump.pickle')
    with open(dump_path, 'wb') as f:
        pickle.dump(data_dump, f)
    logger.info(f'Data dump saved to {dump_path}')
    logger.info('Run with: mpirun -n <NPROCS> parallel_bilby_analysis '
                f'{dump_path} --nlive {args.nlive}')
    import sys
    sys.exit(0)

# ============================================================================
# 7. SAMPLING (dynesty)
# ============================================================================
logger.info('Starting dynesty nested sampling...')
t_sample_start = time.time()

result = bilby.run_sampler(
    likelihood=likelihood,
    priors=priors,
    sampler='dynesty',
    nlive=args.nlive,
    nact=args.nact,
    resume=True,
    outdir=outdir,
    label=label,
    seed=args.seed,
    conversion_function=bilby.gw.conversion.generate_all_bns_parameters,
    plot=True,
    check_point_delta_t=600,
    print_method='interval-60',
)

t_sample = time.time() - t_sample_start
t_total = time.time() - t_start

logger.info(f'Sampling completed in {t_sample:.1f}s ({t_sample/3600:.2f}h)')
logger.info(f'Total runtime: {t_total:.1f}s ({t_total/3600:.2f}h)')

# ============================================================================
# 8. SAVE RESULTS IN JAX-COMPATIBLE FORMAT
# ============================================================================
# Save a CSV matching the JAX output format for the plotter
posteriors = result.posterior
csv_path = os.path.join('Results', f'{marg_tag}_Bilby_{args.mode}_{args.waveform}.csv')

# Map bilby parameter names to JAX names
param_map = {
    'chirp_mass': 'M_c',
    'mass_ratio': 'q',
    'chi_1': 's1_z',
    'chi_2': 's2_z',
    'theta_jn': 'iota',
    'luminosity_distance': 'd_L',
    'geocent_time': 't_c',
    'psi': 'psi',
    'ra': 'ra',
    'dec': 'dec',
    'lambda_1': 'lambda_1',
    'lambda_2': 'lambda_2',
}

import pandas as pd
csv_data = {}
for bilby_name, jax_name in param_map.items():
    if bilby_name in posteriors.columns:
        values = posteriors[bilby_name].values
        # Convert geocent_time to offset from trigger
        if bilby_name == 'geocent_time':
            values = values - trigger_time
        csv_data[jax_name] = values

df = pd.DataFrame(csv_data)
df.to_csv(csv_path, index=False)
logger.info(f'Posteriors saved to {csv_path}')

# Print timing summary
print(f'\n{"="*60}')
print(f'TIMING SUMMARY: {label}')
print(f'{"="*60}')
print(f'  Data loading:     {t_data:>8.1f}s')
print(f'  Likelihood setup: {t_like:>8.1f}s')
print(f'  Sampling:         {t_sample:>8.1f}s ({t_sample/3600:.2f}h)')
print(f'  Total:            {t_total:>8.1f}s ({t_total/3600:.2f}h)')
print(f'{"="*60}')
