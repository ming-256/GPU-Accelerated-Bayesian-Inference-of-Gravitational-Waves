# Data and configuration equivalence with the LVK canonical analysis

Verified 2026-04-25 against `GW170817/Scripts/GW170817_heterodyned_1.py` and `GW150914/Scripts/GW150914_heterodyned.py`.

## Strain data — exact match

| Item | Our config | LVK reference | Match |
|---|---|---|:---:|
| GW170817 GPS trigger | 1187008882.43 | 1187008882.43 (Abbott 2017a) | ✓ |
| GW170817 strain files | `H/L/V-{IFO}_LOSC_CLN_4_V1-1187007040-2048.hdf5` (GWOSC cleaned, 4 kHz, 2048 s) | GWOSC cleaned strain release | ✓ |
| GW170817 segment | 128 s, 2 s post-trigger | 128 s, 2 s post-trigger | ✓ |
| GW170817 detectors | H1, L1, V1 | H1, L1, V1 | ✓ |
| GW170817 f_min / f_max / f_ref | 23.0 / 2048.0 / 20 Hz | 23 / 2048 / 20 Hz (Abbott 2017b H0) | ✓ |
| GW150914 GPS trigger | 1126259462.4 | 1126259462.4 | ✓ |
| GW150914 strain files | `H/L-{IFO}_LOSC_4_V1-1126256640-4096.hdf5` (GWOSC, 4 kHz, 4096 s) | GWOSC | ✓ |
| GW150914 segment | 8 s, 2 s post-trigger | 8 s (Abbott 2016 PRL 116 241102 §II.B) | ✓ |
| GW150914 detectors | H1, L1 | H1, L1 | ✓ |
| GW150914 f_min / f_max | 20 / 1024 Hz | 20 / 1024 Hz | ✓ |

## PSDs — exact match

| Event | PSD source | LVK reference | Match |
|---|---|---|:---:|
| GW170817 | `EventData/GWOSC/GW170817/GWTC1_GW170817_PSDs.dat` | LIGO-P1900011 BayesWave PSDs (GWTC-1) | ✓ |
| GW150914 | `gwtc2p1` PSDs from GWTC-2.1 release | LVK GWTC-2.1 PSDs | ✓ |

PSD estimation parameters when computed self: 32 s FFT length, 50% overlap, median, 1024 s of off-source data. These match bilby/kazewong defaults but are not used for the production runs (we always use the official PSD files).

## Prior structure — match

| Item | Our config | LVK | Match |
|---|---|---|:---:|
| Mass-ratio Jacobian | sample (M_c, q) with `\|M_c·(1+q)^{2/5}/q^{6/5}\|` → uniform in (m1, m2) | uniform in (m1, m2) directly | ✓ (equivalent under the change of variables) |
| GW170817 spin priors | aligned, χ_z uniform in [−0.05, 0.05] | low-spin: \|χ\| < 0.05 (bright-siren primary) | ✓ |
| GW150914 spin priors | aligned, χ_z uniform in [−1, 1] | high-spin: \|χ\| < 0.99 | ≈ (modest difference; matters for waveform but not for the q-prior question) |
| iota / dec / ra priors | sin(iota) / cos(dec) / uniform(ra) | sin / cos / uniform | ✓ |
| GW170817 Λ₁, Λ₂ priors | uniform [0, 5000] | uniform [0, 5000] | ✓ |
| H₀ prior (GW170817) | log-uniform [20, 250] km/s/Mpc | log-uniform [10, 220] (Abbott 2017b) | ≈ |
| v_p prior | uniform [−1000, 1000] km/s | uniform | ✓ |
| d_L prior (GW170817) | Beta(3,1) on [10, 75] Mpc | volumetric d_L² on [10, 75] Mpc | ≈ |

**Note on d_L prior:** Beta(3,1) on [10, 75] Mpc has density ∝ (d_L − 10)² rather than the LVK ∝ d_L². The shapes differ at the low-d_L end (Beta(3,1) → 0 at d_L = 10, LVK volumetric → finite). This is a *separate* prior issue from the q-discrepancy and may marginally suppress our high-H₀ tail relative to LVK, but it is not the cause of the q-discrepancy.

## Prior bounds — GW170817 matches LVK exactly

**CORRECTION (2026-05-18).** An earlier version of this file claimed our GW170817
component-mass prior [0.5, 7.7] M_⊙ differed from an "LVK low-spin" prior of
[0.87, 1.74] M_⊙, and named that difference as the prime suspect for the
q-posterior discrepancy. That was wrong on the facts. The actual GW170817 LVK
parameter-estimation prior is given in Abbott et al. 2019 (Properties of the
binary neutron star merger GW170817, PRX 9, 011001), Sec. III D:

> "we assume a prior PDF p(ϑ) uniform in the detector-frame masses, with the
> constraint that 0.5 M_⊙ ≤ m1_det, m2_det ≤ 7.7 M_⊙, where m1 ≥ m2, and with
> an additional constraint on the chirp mass, 1.184 M_⊙ ≤ Mc_det ≤ 2.168 M_⊙."

So our GW170817 prior reproduces the LVK PE prior **exactly**. The [0.87, 1.74]
range matches no published LVK prior; it appears to be a constructed [m, 2m]
range (1.74 = 2 × 0.87) and should not be used or cited as "LVK".

| Item | Our config | LVK GW170817 PE (Abbott+2019 PRX) | Match |
|---|---|---|:---:|
| GW170817 m₁, m₂ hard bounds | [0.5, 7.7] M_⊙ | [0.5, 7.7] M_⊙ | ✓ exact |
| GW170817 M_c (det) constraint | [1.184, 2.168] M_⊙ | [1.184, 2.168] M_⊙ | ✓ exact |
| GW150914 m₁, m₂ hard bounds | [1, 100] M_⊙ | ~[5, 100] M_⊙ (unverified) | ≈ — needs check against the GW150914 PE paper |
| GW150914 M_c (det) | [10, 80] M_⊙ | data-driven (unverified) | needs check |

### Consequence for the q posterior

The earlier "wide mass bounds concentrate/dilute the q prior" explanation is
**void**: with the GW170817 mass and chirp-mass priors identical to LVK's, the
induced q prior is identical too. If a q-posterior discrepancy with the public
GWTC-1 posterior remains, it is **not** explained by the mass bounds and must be
investigated separately (candidates: waveform family, spin prior, the d_L prior
shape noted above, or the heterodyne reference). Do not attribute it to mass
bounds without new evidence.

## Diagnostic strategy

The mass-bounds hypothesis is closed. Runs that vary `--m-comp-lo/--m-comp-hi`
away from [0.5, 7.7] (e.g. the s07/s15/s19 `*_lvkbounds*` runs at [0.87, 1.74])
are *non-LVK* narrow-prior experiments, not LVK reproductions, and should be
labelled as such. The LVK-matched GW170817 runs are those with no `--m-comp`
flags (script defaults M_COMP_LO=0.5, M_COMP_HI=7.7). The two used for the
cross-waveform headline (Section 4.3, Table 4) already exist:

- IMRPhenomXAS_NRTidalv3: `Results/test_suite/s14__gw170817__imrphenomxas_nrtidalv3__baseline__seed0000/samples.csv`
- TaylorF2: `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv`

Both use the GWTC-1 PSD and GWTC-1 heterodyne reference at n_live=5000. The
TaylorF2 component-mass range in that file spans [0.53, 2.47]/[1.37, 7.69]
M_⊙, confirming the [0.5, 7.7] prior. No new run is required.
