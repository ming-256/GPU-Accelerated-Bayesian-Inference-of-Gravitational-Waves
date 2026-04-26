# Result Inventory for MNRAS Draft

Date prepared: 2026-04-22

## LFS Hydration

`git lfs pull` completed successfully. The posterior CSVs and HDF5 reference files are real hydrated data files, not LFS pointer placeholders.

Key hydrated files:

| File | Size | Role |
|---|---:|---|
| `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv` | 65 MB | Primary GW170817 baseline H0 run |
| `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_flatZ.csv` | 66 MB | Direct flat-in-z prior run |
| `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv` | 59 MB | Reweighted flat-in-z comparison |
| `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_vp250.csv` | 65 MB | Peculiar-velocity uncertainty variant |
| `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv` | 66 MB | TaylorF2 waveform cross-check |
| `Results/gwtc1_phasemarg/summary_stats.csv` | 8.6 KB | Current parameter summaries |
| `Results/gwtc1_phasemarg/evidence_table.csv` | 1.6 KB | Current evidence summaries |
| `Results/scaling_study/scaling_summary.csv` | 869 B | n_live scaling summary |

## Source-of-Truth Tables

Use repository-generated tables for manuscript numbers:

- `Results/gwtc1_phasemarg/summary_stats.csv`
- `Results/gwtc1_phasemarg/evidence_table.csv`
- `Results/gwtc1_phasemarg/waveform_systematics.csv`
- `Results/scaling_study/scaling_summary.csv`
- `paper_knowledge_base/a100_run_data.md`

The thesis PDF is useful for narrative and method structure, but its L4 hardware results are superseded by the A100 repository outputs.

## Primary H0 Numbers: IMRPhenomD_NRTidalv2

From `summary_stats.csv` and a read-only weighted diagnostic using `/opt/miniconda3/envs/jax/bin/python`.

| Run | MAP | Median | 68% quantile interval | 68% KDE HPD | Notes |
|---|---:|---:|---:|---:|---|
| Baseline | 71.5 | 79.1 | [68.2, 103.5] | [62.7, 91.1] | Volumetric distance prior, sigma_vp=150 km/s |
| Flat-in-z direct | 75.4 | 93.6 | [72.4, 146.9] | [61.9, 117.5] | Direct nested-sampling run |
| Flat-in-z reweighted | 74.2 | 88.9 | [71.3, 126.2] | [63.4, 107.6] | Reweighted baseline samples |
| sigma_vp=250 | 72.4 | 78.6 | [67.0, 101.9] | [61.3, 91.3] | Peculiar-velocity sensitivity |

Weighted posterior tail diagnostics:

| Run | P(H0 > 100) | P(H0 > 120) | P(H0 > 150) | P(dL < 30 Mpc) |
|---|---:|---:|---:|---:|
| Baseline | 0.186 | 0.076 | 0.016 | 0.179 |
| Flat-in-z direct | 0.431 | 0.281 | 0.147 | 0.428 |
| Flat-in-z reweighted | 0.362 | 0.195 | 0.056 | 0.357 |
| sigma_vp=250 | 0.175 | 0.067 | 0.012 | 0.163 |

Wasserstein distances in H0:

| Comparison | W1 (km/s/Mpc) |
|---|---:|
| Baseline to flat-in-z direct | 20.82 |
| Baseline to flat-in-z reweighted | 11.24 |
| Baseline to sigma_vp=250 | 1.24 |
| Flat-in-z direct to reweighted | 9.58 |

Evidence values:

| Run | log Z |
|---|---:|
| Baseline | 486.67 +/- 0.09 |
| Flat-in-z direct | 486.49 +/- 0.09 |
| sigma_vp=250 | 485.96 +/- 0.09 |

## Runtime and Scaling

Primary A100 headline, from `paper_knowledge_base/a100_run_data.md`:

| Analysis | Waveform | Sampling | Total |
|---|---|---:|---:|
| GW170817 H0 baseline | IMRPhenomD_NRTidalv2 | 12 min 52 s | 14 min 45 s |
| GW170817 H0 baseline | TaylorF2 | 2 min 41 s | 3 min 55 s |
| GW150914 validation | IMRPhenomD | 2 min 52 s | 4 min 8 s |
| Six-run prior-sensitivity suite | Both GW170817 waveforms | - | 57 min |

Scaling study:

| n_live | Dead points | log Z | sigma(log Z) | Sampling (s) | Total (s) |
|---:|---:|---:|---:|---:|---:|
| 500 | 19650 | 486.73 | 0.30 | 158.1 | 234.9 |
| 1000 | 39900 | 486.04 | 0.21 | 225.9 | 304.0 |
| 2500 | 99750 | 486.32 | 0.13 | 457.6 | 549.8 |
| 5000 | 198000 | 486.66 | 0.10 | 761.0 | 872.1 |
| 10000 | 402000 | 485.92 | 0.07 | 1478.4 | 1659.0 |
| 20000 | 690000 | 485.95 | 0.05 | 1694.5 | 2034.6 |
| 50000 | 1725000 | 486.22 | 0.03 | 4812.3 | 6279.9 |
| 100000 | 3450000 | 486.29 | 0.02 | 9149.5 | 14392.5 |

Open check: confirm why the 20000 live-point row has fewer dead points than strict linear scaling would suggest before using it as a central scaling claim.

## Figure Shortlist

Candidate main-text figures:

1. `Results/gwtc1_phasemarg/plots/H0_baseline_IMRPhenomD.pdf`
   Baseline GW170817 H0 posterior with Planck/SH0ES bands.
2. `Results/gwtc1_phasemarg/plots/H0_IMRPhenomD_reweighted.pdf`
   Primary prior-sensitivity comparison: baseline, direct flat-in-z, reweighted flat-in-z, sigma_vp=250.
3. `Results/gwtc1_phasemarg/plots/dL_reweight_comparison_IMRPhenomD_NRTidalv2.pdf`
   Distance-posterior explanation of reweighting limitations.
4. `Results/gwtc1_phasemarg/plots/corner_combined_waveforms.pdf`
   GW170817 PE comparison across waveform choices and GWTC reference.
5. `Results/gwtc1_phasemarg/plots/corner_IMRPhenomD_hetero_vs_unhetero.pdf`
   Heterodyned versus unheterodyned consistency.
6. `Results/gwtc1_phasemarg/plots/scaling_study.pdf`
   A100 runtime scaling with live points.

Candidate appendix figures:

- `Results/gwtc1_phasemarg/plots/corner_GW150914.pdf`
- `Results/gwtc1_phasemarg/plots/H0_TaylorF2_reweighted.pdf`
- `Results/gwtc1_phasemarg/plots/corner_reweighted_vs_sampled_flatZ_IMRPhenomD.pdf`
- `Results/gwtc1_phasemarg/plots/prior_functions_IMRPhenomD_NRTidalv2.pdf`
- `Results/gwtc1_phasemarg/plots/gpu_vs_cpu_projection.pdf`

## Open Items Before Submission

- Verify current Planck/SH0ES reference values and use the most appropriate citations for the final comparison bands.
- Fill in the pBilby/CSD3 like-for-like baseline once available.
- Regenerate `prior_sensitivity_full.json` separately for IMRPhenomD_NRTidalv2 and TaylorF2, or avoid relying on the JSON until the waveform metadata is unambiguous.
- Confirm whether H0 constraints should be reported as KDE HPD intervals or weighted quantile intervals; the draft currently states both where relevant.
- Verify all BibTeX records, arXiv IDs, DOIs, and journal metadata.
