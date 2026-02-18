# GW170817 Analysis Context

## Event
- **GW170817**: First binary neutron star (BNS) merger detected (2017-08-17)
- **GPS time**: 1187008882.43 (1842.43 s from local GWOSC file start at 1187007040)
- **Host galaxy**: NGC 4993 (heliocentric recession velocity 3327 km/s)
- **Detectors**: LIGO Hanford (H1), LIGO Livingston (L1), Virgo (V1)

## Data
- **Local GWOSC files**: GWTC-1 cleaned strain (glitch removed), 4096 Hz sampling, 2048 s duration
  - `H-H1_LOSC_CLN_4_V1-1187007040-2048.hdf5` (and L1, V1 equivalents)
  - Data spans [1187007040, 1187009088] GPS
- **Analysis segment**: 128 s, 2 s post-trigger → [1187008756.43, 1187008884.43]
- **PSD segment**: 1024 s, 16 s pad before analysis → [1187007716.43, 1187008740.43]
- All segments fit within the 2048 s local files

## Waveform Models
- **IMRPhenomD_NRTidalv2**: Aligned-spin inspiral-merger-ringdown model with NR-calibrated tidal corrections. fmax = 2048 Hz (has signal content through merger/post-merger).
- **TaylorF2**: Post-Newtonian inspiral-only model. Has hard ISCO cutoff built into ripple (~1570–1630 Hz for GW170817 masses); fmax = 1792 Hz is used in kazewong-data scripts as a performance optimisation (bins above ISCO are zero). For GWOSC-data scripts fmax = 2048 Hz is fine since the waveform auto-zeros above ISCO.
- The aligned-spin (non-precessing) assumption makes analytic phase marginalization strictly valid
- Tidal deformabilities (Lambda_1, Lambda_2) capture neutron star equation-of-state effects
- Implementation: `ripple` library via `jimgw.single_event.waveform.RippleIMRPhenomD_NRTidalv2`

## PSD Sources
All sources store **power spectral density** $S_n(f)$ in units of 1/Hz (strain²/Hz). Verified at multiple frequencies — no ASD/PSD confusion.
- **self**: Welch-estimated from off-source data via gwpy `.psd()`. 32 s Tukey-windowed segments, 50% overlap, median averaging over 1024 s. Interpolated from df=1/32 Hz to df=1/128 Hz (analysis grid).
- **bilby**: Text files from `EventData/GWOSC/GW170817/Bilby/`. Values identical to GWTC-1 BayesWave PSDs.
- **gwtc1**: Official BayesWave PSDs from `GWTC1_GW170817_PSDs.dat` (LIGO-P1900011). Header confirms units: "PSD (1/Hz)".
- **kazewong**: Pre-processed PSDs from `EventData/GWOSC/GW170817/kazewong/`. Same order of magnitude as GWTC-1, independently estimated.
- All external PSDs are linearly interpolated to the analysis frequency grid. This is standard practice (PSD varies smoothly).

## Likelihood
- **Heterodyned (relative binning)**: Pre-computes summary coefficients A0, A1, B0, B1 at ~501 frequency bins instead of evaluating at ~10^5 frequencies. ~500x speedup. Reference: Zackay et al. (arXiv:1806.08792)
- **Phase marginalization**: Analytically marginalizes over coalescence phase (phase_c) by replacing real match-filter SNR with log I_0(|<d|h>|), where I_0 is the modified Bessel function of order 0. Reduces dimensionality by 1.
- **Standard siren**: Joint H_0 inference using peculiar velocity model from Abbott et al. 2017 (arXiv:1710.05832)

## Reference Parameters
- Loaded from `Results/GW170817_GWTC-1.hdf5` (IMRPhenomPv2NRT_lowSpin_posterior dataset)
- Median of GWTC-1 posteriors used as reference state for heterodyning
- The optimizer (`flowMC.AdamOptimization`) is broken; file-based loading is the workaround

## Parameter Space (14 dimensions)

| Parameter  | Prior         | Range              | Physics                                    |
|------------|---------------|--------------------|--------------------------------------------|
| M_c        | Uniform       | [1.184, 2.168]     | Chirp mass (solar masses)                  |
| q          | Uniform       | [0.125, 1.0]       | Mass ratio m2/m1                           |
| s1_z       | Uniform       | [-0.05, 0.05]      | Primary aligned spin                       |
| s2_z       | Uniform       | [-0.05, 0.05]      | Secondary aligned spin                     |
| iota       | Sin           | [0, pi]            | Inclination angle                          |
| d_L        | Beta(3,1)     | [1, 75] Mpc        | Luminosity distance (volume-weighted)      |
| t_c        | Uniform       | [-0.1, 0.1] s      | Coalescence time offset                    |
| psi        | Uniform       | [0, pi]            | Polarization angle (periodic, wraps on pi) |
| ra         | Uniform       | [0, 2pi]           | Right ascension (full sky)                 |
| dec        | Cosine        | [-pi/2, pi/2]      | Declination (full sky, cosine prior)       |
| Lambda_1   | Uniform       | [0, 5000]          | Primary tidal deformability                |
| Lambda_2   | Uniform       | [0, 5000]          | Secondary tidal deformability              |
| H_0        | Log-uniform   | [20, 140] km/s/Mpc | Hubble constant                            |
| v_p        | Uniform       | [-1000, 1000] km/s | Peculiar velocity                          |

**Note**: phase_c is NOT sampled -- it is analytically marginalized.

## Sampler
- **Blackjax nested slice sampling** (`blackjax.ns.adaptive.nss`)
- 5000 live points, 50% deletion rate
- Custom `stepper_fn` with periodic wrapping for psi (period pi) and ra (period 2pi)

## Key Files
- `Scripts/GW170817_heterodyned_1.py` -- main analysis script (GWOSC data, heterodyned)
- `Scripts/GW170817_unheterodyned_1.py` -- reference full-likelihood script (GWOSC data)
- `Scripts/GW170817_heterodyned_kazewong.py` -- heterodyned with kazewong pre-processed data
- `Scripts/GW170817_unheterodyned_kazewong.py` -- full-likelihood with kazewong data
- `Scripts/GW170817_bilby.py` -- bilby/dynesty comparison script
- `Scripts/BatchRun.py` -- batch runner for all data/PSD/waveform combinations
- `Results/GW170817_GWTC-1.hdf5` -- GWTC-1 posterior samples for reference parameters

## Performance Architecture
- **No dicts in JIT hot path**: All parameter access uses static integer indices (`I_MC=0`, `I_Q=1`, etc.)
- **Stacked detector arrays**: Heterodyning coefficients A0/A1/B0/B1 and reference waveforms stored as `(n_det, n_bins)` JAX arrays, enabling vectorized computation over detectors
- **Vectorized prior**: All 14 prior types computed in parallel via `jnp.where` selection on static `PRIOR_TYPE` array -- no Python loops or list comprehensions
- **jimgw API boundary**: Dict creation for `waveform()` and `detector.fd_response()` is a trace-time operation; after JIT compilation the XLA graph contains only array ops
- **Inlined likelihood**: Phase-marginalized heterodyned computation written directly in array ops rather than importing jimgw's dict-based function

## Library Dependencies
- `jimgw` (installed): Detector response (`fd_response`), waveform models (`RippleIMRPhenomD_NRTidalv2`)
- `ripple` / `ripplegw`: JAX-based gravitational waveform generation
- `blackjax`: JAX-based nested sampling
- `anesthetic`: Nested sampling post-processing
