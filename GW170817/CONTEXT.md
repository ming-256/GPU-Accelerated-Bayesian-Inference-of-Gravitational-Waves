# GW170817 Analysis Context

## Event
- **GW170817**: First binary neutron star (BNS) merger detected (2017-08-17)
- **GPS time**: 1187008882.43
- **Host galaxy**: NGC 4993 (heliocentric recession velocity 3327 km/s)
- **Detectors**: LIGO Hanford (H1), LIGO Livingston (L1), Virgo (V1)

## Waveform Model
- **IMRPhenomD_NRTidalv2**: Aligned-spin inspiral-merger-ringdown model with NR-calibrated tidal corrections
- The aligned-spin (non-precessing) assumption makes analytic phase marginalization strictly valid
- Tidal deformabilities (Lambda_1, Lambda_2) capture neutron star equation-of-state effects
- Implementation: `ripple` library via `jimgw.single_event.waveform.RippleIMRPhenomD_NRTidalv2`

## Likelihood
- **Heterodyned (relative binning)**: Pre-computes summary coefficients A0, A1, B0, B1 at ~100 frequency bins instead of evaluating at ~10^5 frequencies. ~100x speedup. Reference: Zackay et al. (arXiv:1806.08792)
- **Phase marginalization**: Analytically marginalizes over coalescence phase (phase_c) by replacing real match-filter SNR with log I_0(|<d|h>|), where I_0 is the modified Bessel function of order 0. Reduces dimensionality by 1.
- **Standard siren**: Joint H_0 inference using peculiar velocity model from Abbott et al. 2017 (arXiv:1710.05832)

## Reference Parameters
- Loaded from `GW170817_GWTC-1.hdf5` (IMRPhenomPv2NRT_lowSpin_posterior dataset)
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
| d_L        | Beta(3,1)     | [10, 75] Mpc       | Luminosity distance (volume-weighted)      |
| t_c        | Uniform       | [-0.1, 0.1] s      | Coalescence time offset                    |
| psi        | Uniform       | [0, pi]            | Polarization angle (periodic, wraps on pi) |
| ra         | Uniform       | [3.44, 3.45] rad   | Right ascension (narrow EM-informed prior) |
| dec        | Uniform       | [-0.41, -0.40] rad | Declination (narrow EM-informed prior)     |
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
- `Scripts/refactored_script_heterodyned.py` -- main analysis script
- `Scripts/GW170817_GWTC-1.hdf5` -- GWTC-1 posterior samples for reference parameters
- `Scripts/Final_UniformMass_Final.csv` -- previous run results (column name reference)

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
