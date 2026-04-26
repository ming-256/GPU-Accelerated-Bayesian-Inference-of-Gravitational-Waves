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

## Prior bounds — the only material differences

These are the prior choices that differ from LVK. **The first one is the prime suspect for the q-posterior discrepancy.**

| Item | Our config | LVK | Difference |
|---|---|---|---|
| **GW170817 m₁, m₂ hard bounds** | **[0.5, 7.7] M_⊙** | **[0.87, 1.74] M_⊙ (low-spin)** | **3.2× wider lower bound, 4.4× wider upper** |
| GW170817 M_c (det) | [1.184, 2.168] M_⊙ | ~[1.18, 1.21] M_⊙ (data-driven) | wider upper bound |
| GW150914 m₁, m₂ hard bounds | [1, 100] M_⊙ | ~[5, 100] M_⊙ | 5× wider lower bound |
| GW150914 M_c (det) | [10, 80] M_⊙ | ~[28, 32] M_⊙ (data-driven) | wider |

### Why this matters for the q posterior

For uniform-in-(m₁, m₂) prior with a fixed M_c, the induced q distribution depends sensitively on the (m₁, m₂) bounds. With wide bounds, the M_c ≈ 1.198 iso-curve sweeps through a larger region of (m₁, m₂) space, including configurations with m₂ as low as 0.5 M_⊙ paired with m₁ ≈ 2.7 M_⊙ (q ≈ 0.18). LVK's tight bounds [0.87, 1.74] forbid most of this, concentrating the prior near q = 1.

This is the correct explanation for the corner-plot observation that our q posterior peaks at q ≈ 0.85 while LVK peaks at q → 1, *despite* using the same Jacobian and the same data.

## Diagnostic strategy

The first run that should be done is **IMRPhenomD_NRTidalv2 with LVK-matched mass bounds** (`m_comp_lo=0.87, m_comp_hi=1.74`, χ_z range unchanged). If this run's q posterior matches LVK's q posterior, the gap is fully explained by the mass bounds and waveform variations are second-order. Only then do we add the IMRPhenomXAS_NRTidalv3 and IMRPhenomPv2 runs at LVK-matched bounds to compare-and-contrast.

Implementation: see `CODE_CHANGES_NEEDED.md` §7 (patch P-MASSBOUNDS).
