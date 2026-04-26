# Test Suite Manifest

Canonical list of every run, its expected output files, and the analysis script that consumes it. Read this file to answer: *does run X exist yet, where should its CSV be, and what happens after it finishes?*

All output paths are relative to the repository root.

---

## Session 01 — TaylorF2 heterodyned scaling

| Run ID | n_live | n_delete | n_bins | Expected CSV | Consumed by |
|---|---:|---:|---:|---|---|
| `s01__gw170817__taylorf2__nlive00500__seed0000` | 500 | 250 | 501 | `Results/test_suite/s01__gw170817__taylorf2__nlive00500__seed0000/samples.csv` | `analysis/analyze_tf2_scaling.py` |
| `s01__gw170817__taylorf2__nlive01000__seed0000` | 1000 | 500 | 501 | `Results/test_suite/s01__gw170817__taylorf2__nlive01000__seed0000/samples.csv` | same |
| `s01__gw170817__taylorf2__nlive02500__seed0000` | 2500 | 1250 | 501 | `Results/test_suite/s01__gw170817__taylorf2__nlive02500__seed0000/samples.csv` | same |
| `s01__gw170817__taylorf2__nlive05000__seed0000` | 5000 | 2500 | 501 | `Results/test_suite/s01__gw170817__taylorf2__nlive05000__seed0000/samples.csv` | same |
| `s01__gw170817__taylorf2__nlive10000__seed0000` | 10000 | 5000 | 501 | `Results/test_suite/s01__gw170817__taylorf2__nlive10000__seed0000/samples.csv` | same |
| `s01__gw170817__taylorf2__nlive20000__seed0000` | 20000 | 10000 | 501 | `Results/test_suite/s01__gw170817__taylorf2__nlive20000__seed0000/samples.csv` | same |

Derived output: `Results/test_suite/scaling_tf2_summary.csv` (one row per run, produced by the analysis script).

## Session 02 — DROPPED (2026-04-25)

Repeat-run variance was dropped per the project lead's decision; the paper does not need a per-run sigma on `P(H0 > 120)` for the prior-sensitivity claim.

## Session 03 — Unheterodyned TaylorF2 scaling

TaylorF2 full-likelihood (259 201 bins) at three live-point counts.

| Run ID | n_live | Expected CSV |
|---|---:|---|
| `s03__gw170817__taylorf2__unheterodyned__nlive00500__seed0000` | 500 | `Results/test_suite/s03__.../samples.csv` |
| `s03__gw170817__taylorf2__unheterodyned__nlive01500__seed0000` | 1500 | same |
| `s03__gw170817__taylorf2__unheterodyned__nlive02500__seed0000` | 2500 | same |

Consumed by: `analysis/analyze_unhet_scaling.py`.

## Session 04 — Unheterodyned IMRPhenomD_NRTidalv2 at n_live = 2500 — **DONE**

Completed externally on 2026-04-22. Symlinked into the test-suite tree from `Results/scaling_study/PhaseMarg_Unheterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_nlive2500.csv`. Headline numbers from the run log:

- $\ln Z = 490.51 \pm 0.14$
- Total wall-clock: 37 200 s (~10.3 h)
- Sampling time: 36 366 s
- JIT compilation: 803 s

| Run ID | n_live | Expected CSV |
|---|---:|---|
| `s04__gw170817__imrphenomd_nrtidalv2__unheterodyned__nlive02500__seed0000` | 2500 | `Results/test_suite/s04__.../samples.csv` (symlink) |

Consumed by: `analysis/analyze_unhet_scaling.py` (jointly with Session 03 and Session 05 outputs).

## Session 05 — Unheterodyned IMRPhenomD_NRTidalv2 at n_live = 500

| Run ID | n_live | Expected CSV |
|---|---:|---|
| `s05__gw170817__imrphenomd_nrtidalv2__unheterodyned__nlive00500__seed0000` | 500 | `Results/test_suite/s05__.../samples.csv` |

Plus three short heterodyned supplements (fit in remaining time):

| Run ID | Config | Expected CSV |
|---|---|---|
| `s05__gw170817__imrphenomd_nrtidalv2__baseline__n_dim_reduced__seed0000` | Cross-check: baseline with ref-params=optimize | `Results/test_suite/s05__.../samples.csv` |
| `s05__gw170817__taylorf2__baseline__psd_kazewong__seed0000` | PSD-source sensitivity: kazewong PSDs | same |
| `s05__gw170817__taylorf2__baseline__psd_bilby__seed0000` | PSD-source sensitivity: bilby PSDs | same |

## Session 06 — GW150914 with IMRPhenomXPHM

Requires **patch P-WAV-GW150914** (`CODE_CHANGES_NEEDED.md`, §1).

XPHM is LVK's GWTC-2.1+ production waveform for GW150914 (precession + higher modes). See `WAVEFORM_RECOMMENDATION.md` for the rationale.

| Run ID | Waveform | Expected CSV |
|---|---|---|
| `s06__gw150914__imrphenomxphm__nlive05000__seed0000` | IMRPhenomXPHM | `Results/test_suite/s06__.../samples.csv` |

Consumed by: `analysis/analyze_precessing_gw150914.py`.
Key output: `Results/test_suite/gw150914_waveform_comparison.csv` with d_L / M_c / q / iota summaries against the GWTC-2.1 reference.

## Session 07 — GW170817 with IMRPhenomXAS_NRTidalv3 (primary upgrade) and IMRPhenomPv2 (precession systematic)

Requires **patch P-WAV-GW170817** (`CODE_CHANGES_NEEDED.md`, §2).

Ripple does not provide a precessing tidal waveform. The strategy is therefore tides+aligned-spin as primary, plus precession-without-tides as systematic. See `WAVEFORM_RECOMMENDATION.md` for the rationale.

| Run ID | Waveform | Variant | Notes | Expected CSV |
|---|---|---|---|---|
| `s07__gw170817__imrphenomxas_nrtidalv3__baseline__seed0000` | IMRPhenomXAS_NRTidalv3 | baseline | Primary upgrade (better tides + base) | `Results/test_suite/s07__.../samples.csv` |
| `s07__gw170817__imrphenomxas_nrtidalv3__flatz__seed0000` | same | flatZ direct | | same |
| `s07__gw170817__imrphenomxas_nrtidalv3__vp250__seed0000` | same | σ_vp = 250 km/s | | same |
| `s07__gw170817__imrphenompv2__baseline__seed0000` | IMRPhenomPv2 | baseline_precession_only | BBH; brackets precession effect on H0 (no tides) | same |
| `s07__gw170817__imrphenompv2__flatz__seed0000` | IMRPhenomPv2 | flatZ_precession_only | | same |

Consumed by: `analysis/analyze_precessing_gw170817.py`.

## Session 08 — num_delete sweep

Requires **patch P-NDELETE** (`CODE_CHANGES_NEEDED.md`, §3).

All runs: IMR baseline, n_live = 5000.

| Run ID | num_delete / n_live | num_delete | Expected CSV |
|---|---:|---:|---|
| `s08__gw170817__imrphenomd_nrtidalv2__baseline__ndelete00500__seed0000` | 0.10 | 500 | `Results/test_suite/s08__.../samples.csv` |
| `s08__gw170817__imrphenomd_nrtidalv2__baseline__ndelete01250__seed0000` | 0.25 | 1250 | same |
| `s08__gw170817__imrphenomd_nrtidalv2__baseline__ndelete02500__seed0000` | 0.50 | 2500 | same |
| `s08__gw170817__imrphenomd_nrtidalv2__baseline__ndelete03750__seed0000` | 0.75 | 3750 | same |

Consumed by: `analysis/analyze_num_delete_sweep.py`.

## Session 09 — Heterodyne-bin sweep

Requires **patch P-NBINS** (`CODE_CHANGES_NEEDED.md`, §4).

All runs: IMR baseline, n_live = 5000, num_delete = 2500.

| Run ID | n_bins | Expected CSV |
|---|---:|---|
| `s09__gw170817__imrphenomd_nrtidalv2__baseline__nbins00251__seed0000` | 251 | `Results/test_suite/s09__.../samples.csv` |
| `s09__gw170817__imrphenomd_nrtidalv2__baseline__nbins00501__seed0000` | 501 (reference) | same |
| `s09__gw170817__imrphenomd_nrtidalv2__baseline__nbins01001__seed0000` | 1001 | same |

Consumed by: `analysis/analyze_het_bins_sweep.py`.

## Session 10 — d_L–ι bimodality characterisation

Requires **patch P-MODEB** (`CODE_CHANGES_NEEDED.md`, §5).

All runs: IMR, flat-in-z, n_live = 5000.

| Run ID | d_L bounds (Mpc) | Ref params | Purpose | Expected CSV |
|---|---|---|---|---|
| `s10__gw170817__imrphenomd_nrtidalv2__flatz__dL10-30__refGWTC1__seed0000` | [10, 30] | GWTC-1 (Mode A) | Mode-B local evidence | `Results/test_suite/s10__.../samples.csv` |
| `s10__gw170817__imrphenomd_nrtidalv2__flatz__dL30-75__refGWTC1__seed0000` | [30, 75] | GWTC-1 (Mode A) | Mode-A local evidence | same |
| `s10__gw170817__imrphenomd_nrtidalv2__flatz__dL10-75__refModeB__seed0000` | [10, 75] | Mode-B anchored (d_L = 20 Mpc, ι = 2.0) | Heterodyne reference bias test | same |

Consumed by: `analysis/analyze_bimodality.py`.
Key output: Mode-B Bayes factor $\ln Z_{\rm B} - \ln Z_{\rm A}$ (accounting for prior-volume normalisation).

## Session 11 — n_live = 20 000 anomaly diagnostic

Requires **patch P-TERM** (`CODE_CHANGES_NEEDED.md`, §6).

| Run ID | Stopping tol | Expected CSV |
|---|---|---|
| `s11__gw170817__imrphenomd_nrtidalv2__baseline__nlive20000__tol1e-4__seed0000` | fractional dlogZ < 1e-4 (tighter) | `Results/test_suite/s11__.../samples.csv` |

Consumed by: `analysis/analyze_scaling_20k_anomaly.py`.

## Session H — Prior-only q diagnostic

Requires **patch P-PRIOR** (`CODE_CHANGES_NEEDED.md`, §7) OR a standalone script.

Standalone option: `scripts/prior_only_q_diagnostic.py` (CPU, <1 minute) generates the nested-sampler prior in `q` by sampling from the code's prior transform with the likelihood set to zero, and overlays the LVK-equivalent bilby mass prior analytically.

| Run ID | Expected CSV |
|---|---|
| `sH__gw170817__prior_only_q__seed0000` | `Results/test_suite/sH__.../prior_samples.csv` + `prior_comparison.csv` |

Consumed by: `analysis/analyze_q_prior.py`.

---

## Aggregate outputs

After all sessions:
- `mnras_paper/test_suite/RESULTS_SUMMARY.md` — produced by `analysis/compile_test_suite_report.py`, aggregates every per-session analysis into a single manuscript-ready summary.
- Manuscript edits flagged by per-analysis scripts via their stdout.

## File-integrity check

Every `samples.csv` under `Results/test_suite/` must have a sibling `config.json` whose fields match the run_id. The session scripts enforce this on success. `analysis/verify_manifest.py` walks the tree and reports missing, orphaned, or mismatched files.
