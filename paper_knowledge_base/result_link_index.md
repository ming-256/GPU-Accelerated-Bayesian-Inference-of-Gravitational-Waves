# Result Link Index

Prepared: 2026-04-22

Purpose: connect result CSVs, generated graphs/tables, and the scripts that created or consumed them. Paths are relative to the repository root.

## One-Command Plot/Table Regeneration

| Task | Script |
|---|---|
| Regenerate the standard figure/table set | [`Plots/run_all_plots.sh`](../Plots/run_all_plots.sh) |
| Shared plotting/data-loading helpers | [`Plots/_plot_utils.py`](../Plots/_plot_utils.py) |

Run from repository root:

```bash
bash Plots/run_all_plots.sh
```

Outputs go to:

- Figures: [`Results/gwtc1_phasemarg/plots/`](../Results/gwtc1_phasemarg/plots/)
- Summary tables: [`Results/gwtc1_phasemarg/`](../Results/gwtc1_phasemarg/)

Note: `Plots/run_all_plots.sh` runs `compute_prior_sensitivity.py` twice, first for `IMRPhenomD_NRTidalv2` and then for `TaylorF2`. The files `prior_sensitivity.csv`, `prior_sensitivity_full.json`, and `prior_sensitivity_pdfs.csv` are overwritten by the second run unless copied or renamed.

## Sampling Result CSV Provenance

| Result file | Created by | Batch/log source | Primary use |
|---|---|---|---|
| [`Results/gwtc1_phasemarg/GW15_PhaseMarg_Heterodyned_IMRPhenomD_local_psd-gwtc2p1_ref-gwtc1.csv`](../Results/gwtc1_phasemarg/GW15_PhaseMarg_Heterodyned_IMRPhenomD_local_psd-gwtc2p1_ref-gwtc1.csv) | [`GW150914/Scripts/GW150914_heterodyned.py`](../GW150914/Scripts/GW150914_heterodyned.py) | [`Results/logs/GW150914_heterodyned_IMRPhenomD.log`](../Results/logs/GW150914_heterodyned_IMRPhenomD.log) | GW150914 validation |
| [`Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv) | [`GW170817/Scripts/GW170817_heterodyned_1.py`](../GW170817/Scripts/GW170817_heterodyned_1.py) | [`GW170817/Scripts/run_all_heterodyned.sh`](../GW170817/Scripts/run_all_heterodyned.sh), [`GW170817/Scripts/BatchRun.py`](../GW170817/Scripts/BatchRun.py), `Results/logs/*baseline_IMRPhenomD_NRTidalv2.log` | Primary GW170817 H0 run |
| [`Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_flatZ.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_flatZ.csv) | [`GW170817/Scripts/GW170817_heterodyned_2.py`](../GW170817/Scripts/GW170817_heterodyned_2.py) | [`GW170817/Scripts/run_all_heterodyned.sh`](../GW170817/Scripts/run_all_heterodyned.sh), [`GW170817/Scripts/BatchRun.py`](../GW170817/Scripts/BatchRun.py), `Results/logs/*flatZ_IMRPhenomD_NRTidalv2.log` | Direct flat-in-z prior run |
| [`Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_vp250.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_vp250.csv) | [`GW170817/Scripts/GW170817_heterodyned_3.py`](../GW170817/Scripts/GW170817_heterodyned_3.py) | [`GW170817/Scripts/run_all_heterodyned.sh`](../GW170817/Scripts/run_all_heterodyned.sh), [`GW170817/Scripts/BatchRun.py`](../GW170817/Scripts/BatchRun.py), `Results/logs/*vp250_IMRPhenomD_NRTidalv2.log` | Peculiar-velocity uncertainty sensitivity |
| [`Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv) | [`Plots/reweight_dL_to_flat_z.py`](../Plots/reweight_dL_to_flat_z.py) | [`Results/logs/reweight_dL_to_flat_z.log`](../Results/logs/reweight_dL_to_flat_z.log) | Post-hoc flat-in-z reweighting comparison |
| [`Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv) | [`GW170817/Scripts/GW170817_heterodyned_1.py`](../GW170817/Scripts/GW170817_heterodyned_1.py) with `--waveform TaylorF2` | `Results/logs/*baseline_TaylorF2.log` | TaylorF2 baseline cross-check |
| [`Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_flatZ.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_flatZ.csv) | [`GW170817/Scripts/GW170817_heterodyned_2.py`](../GW170817/Scripts/GW170817_heterodyned_2.py) with `--waveform TaylorF2` | `Results/logs/*flatZ_TaylorF2.log` | TaylorF2 direct flat-in-z cross-check |
| [`Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_vp250.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_vp250.csv) | [`GW170817/Scripts/GW170817_heterodyned_3.py`](../GW170817/Scripts/GW170817_heterodyned_3.py) with `--waveform TaylorF2` | `Results/logs/*vp250_TaylorF2.log` | TaylorF2 peculiar-velocity sensitivity |
| [`Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv) | [`Plots/reweight_dL_to_flat_z.py`](../Plots/reweight_dL_to_flat_z.py) | [`Results/logs/reweight_dL_to_flat_z.log`](../Results/logs/reweight_dL_to_flat_z.log) | TaylorF2 post-hoc flat-in-z comparison |
| [`Results/gwtc1_phasemarg/PhaseMarg_Unheterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Unheterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1.csv) | [`GW170817/Scripts/GW170817_unheterodyned_1.py`](../GW170817/Scripts/GW170817_unheterodyned_1.py) | [`GW170817/Scripts/run_unheterodyned.sh`](../GW170817/Scripts/run_unheterodyned.sh), [`Results/logs/unheterodyned_IMRPhenomD_NRTidalv2_host_localised.log`](../Results/logs/unheterodyned_IMRPhenomD_NRTidalv2_host_localised.log) | Heterodyned-vs-full-likelihood validation |
| [`Results/gwtc1_phasemarg/PhaseMarg_Unheterodyned_TaylorF2_local_psd-gwtc1.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Unheterodyned_TaylorF2_local_psd-gwtc1.csv) | [`GW170817/Scripts/GW170817_unheterodyned_1.py`](../GW170817/Scripts/GW170817_unheterodyned_1.py) with `--waveform TaylorF2` | [`GW170817/Scripts/run_unheterodyned.sh`](../GW170817/Scripts/run_unheterodyned.sh), [`Results/logs/unheterodyned_TaylorF2_host_localised.log`](../Results/logs/unheterodyned_TaylorF2_host_localised.log) | TaylorF2 full-likelihood validation |
| [`Results/gwtc1_phasemarg/PhaseMarg_Unheterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_full_sky.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Unheterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_full_sky.csv) | [`GW170817/Scripts/GW170817_unheterodyned_1.py`](../GW170817/Scripts/GW170817_unheterodyned_1.py) with `--label-suffix "_full_sky"` | [`Results/logs/unheterodyned_IMRPhenomD_NRTidalv2_full_sky.log`](../Results/logs/unheterodyned_IMRPhenomD_NRTidalv2_full_sky.log) | Sky-prior validation |
| [`Results/gwtc1_phasemarg/PhaseMarg_Unheterodyned_TaylorF2_local_psd-gwtc1_full_sky.csv`](../Results/gwtc1_phasemarg/PhaseMarg_Unheterodyned_TaylorF2_local_psd-gwtc1_full_sky.csv) | [`GW170817/Scripts/GW170817_unheterodyned_1.py`](../GW170817/Scripts/GW170817_unheterodyned_1.py) with `--waveform TaylorF2 --label-suffix "_full_sky"` | [`Results/logs/unheterodyned_TaylorF2_full_sky.log`](../Results/logs/unheterodyned_TaylorF2_full_sky.log) | TaylorF2 sky-prior validation |
| [`Results/scaling_study/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv`](../Results/scaling_study/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv) | [`GW170817/Scripts/GW170817_heterodyned_1.py`](../GW170817/Scripts/GW170817_heterodyned_1.py) with `--n-live` | [`GW170817/Scripts/run_scaling_study.sh`](../GW170817/Scripts/run_scaling_study.sh), [`GW170817/Scripts/run_scaling_extended.sh`](../GW170817/Scripts/run_scaling_extended.sh), [`Results/scaling_study/logs/`](../Results/scaling_study/logs/) | Large scaling-study posterior; latest run overwrites this filename |

## Derived Tables

| Derived output | Script | Inputs | Used for |
|---|---|---|---|
| [`Results/gwtc1_phasemarg/evidence_table.csv`](../Results/gwtc1_phasemarg/evidence_table.csv) | [`Plots/compute_evidence_table.py`](../Plots/compute_evidence_table.py) | All CSVs in `Results/gwtc1_phasemarg/` | Evidence, `N_dead`, `N_eff` summary |
| [`Results/gwtc1_phasemarg/summary_stats.csv`](../Results/gwtc1_phasemarg/summary_stats.csv) | [`Plots/compute_summary_stats.py`](../Plots/compute_summary_stats.py) | All CSVs in `Results/gwtc1_phasemarg/` | MAP, median, 68/95 per cent intervals |
| [`Results/gwtc1_phasemarg/waveform_systematics.csv`](../Results/gwtc1_phasemarg/waveform_systematics.csv) | [`Plots/compute_waveform_systematics.py`](../Plots/compute_waveform_systematics.py) | IMRPhenomD/TaylorF2 baseline, flatZ, vp250 CSV pairs | Waveform posterior-distance metrics |
| [`Results/gwtc1_phasemarg/prior_sensitivity.csv`](../Results/gwtc1_phasemarg/prior_sensitivity.csv) | [`Plots/compute_prior_sensitivity.py`](../Plots/compute_prior_sensitivity.py) | Baseline, flatZ, vp250, reweighted flatZ for selected waveform | Prior-sensitivity divergences |
| [`Results/gwtc1_phasemarg/prior_sensitivity_full.json`](../Results/gwtc1_phasemarg/prior_sensitivity_full.json) | [`Plots/compute_prior_sensitivity.py`](../Plots/compute_prior_sensitivity.py) | Same as above | Structured prior-sensitivity results |
| [`Results/gwtc1_phasemarg/prior_sensitivity_pdfs.csv`](../Results/gwtc1_phasemarg/prior_sensitivity_pdfs.csv) | [`Plots/compute_prior_sensitivity.py`](../Plots/compute_prior_sensitivity.py) | Same as above | KDE grid for prior-sensitivity plots |
| [`Results/scaling_study/scaling_summary.csv`](../Results/scaling_study/scaling_summary.csv) | [`GW170817/Scripts/run_scaling_study.sh`](../GW170817/Scripts/run_scaling_study.sh), appended/combined with extended results | Scaling logs in [`Results/scaling_study/logs/`](../Results/scaling_study/logs/) | Runtime scaling plot |
| [`Results/scaling_study/scaling_summary_extended.csv`](../Results/scaling_study/scaling_summary_extended.csv) | [`GW170817/Scripts/run_scaling_extended.sh`](../GW170817/Scripts/run_scaling_extended.sh) | Extended scaling logs | High-live-point runtime checks |

## Figure and Graph Lineage

All listed figures are emitted as both PDF and PNG unless otherwise noted.

### Paper Core Candidates

| Graph | Script | Direct inputs |
|---|---|---|
| [`H0_baseline_IMRPhenomD.pdf`](../Results/gwtc1_phasemarg/plots/H0_baseline_IMRPhenomD.pdf) | [`Plots/plot_H0_baseline_IMRPhenomD.py`](../Plots/plot_H0_baseline_IMRPhenomD.py) | IMR baseline heterodyned CSV |
| [`H0_IMRPhenomD_variants.pdf`](../Results/gwtc1_phasemarg/plots/H0_IMRPhenomD_variants.pdf) | [`Plots/plot_H0_IMRPhenomD_variants.py`](../Plots/plot_H0_IMRPhenomD_variants.py) | IMR baseline, direct flatZ, vp250 CSVs |
| [`H0_IMRPhenomD_reweighted.pdf`](../Results/gwtc1_phasemarg/plots/H0_IMRPhenomD_reweighted.pdf) | [`Plots/plot_H0_IMRPhenomD_reweighted.py`](../Plots/plot_H0_IMRPhenomD_reweighted.py) | IMR baseline, reweighted flatZ, vp250 CSVs |
| [`H0_TaylorF2_variants.pdf`](../Results/gwtc1_phasemarg/plots/H0_TaylorF2_variants.pdf) | [`Plots/plot_H0_TaylorF2_variants.py`](../Plots/plot_H0_TaylorF2_variants.py) | TaylorF2 baseline, direct flatZ, vp250 CSVs |
| [`H0_TaylorF2_reweighted.pdf`](../Results/gwtc1_phasemarg/plots/H0_TaylorF2_reweighted.pdf) | [`Plots/plot_H0_TaylorF2_reweighted.py`](../Plots/plot_H0_TaylorF2_reweighted.py) | TaylorF2 baseline, reweighted flatZ, vp250 CSVs |
| [`H0_reweight_comparison.pdf`](../Results/gwtc1_phasemarg/plots/H0_reweight_comparison.pdf) | [`Plots/plot_H0_reweight_comparison.py`](../Plots/plot_H0_reweight_comparison.py) | IMR direct flatZ and reweighted flatZ CSVs |
| [`H0_reweighted_vs_sampled_flatZ.pdf`](../Results/gwtc1_phasemarg/plots/H0_reweighted_vs_sampled_flatZ.pdf) | [`Plots/plot_corner_reweighted_vs_sampled_flatZ.py`](../Plots/plot_corner_reweighted_vs_sampled_flatZ.py) | Direct and reweighted flatZ CSVs for both waveforms |
| [`dL_posterior.pdf`](../Results/gwtc1_phasemarg/plots/dL_posterior.pdf) | [`Plots/plot_dL_posterior.py`](../Plots/plot_dL_posterior.py) | IMR/TaylorF2 baseline and flatZ CSVs |
| [`dL_reweight_comparison_IMRPhenomD_NRTidalv2.pdf`](../Results/gwtc1_phasemarg/plots/dL_reweight_comparison_IMRPhenomD_NRTidalv2.pdf) | [`Plots/compute_prior_sensitivity.py`](../Plots/compute_prior_sensitivity.py) with `WAVEFORM=IMRPhenomD_NRTidalv2` | IMR baseline, direct flatZ, reweighted flatZ |
| [`corner_combined_waveforms.pdf`](../Results/gwtc1_phasemarg/plots/corner_combined_waveforms.pdf) | [`Plots/plot_corner_combined_waveforms.py`](../Plots/plot_corner_combined_waveforms.py) | IMR baseline, TaylorF2 baseline, GWTC-1 HDF5 |
| [`corner_IMRPhenomD_hetero_vs_unhetero.pdf`](../Results/gwtc1_phasemarg/plots/corner_IMRPhenomD_hetero_vs_unhetero.pdf) | [`Plots/plot_corner_IMRPhenomD_hetero_vs_unhetero.py`](../Plots/plot_corner_IMRPhenomD_hetero_vs_unhetero.py) | IMR heterodyned baseline, IMR unheterodyned, GWTC-1 HDF5 |
| [`corner_TaylorF2_hetero_vs_unhetero.pdf`](../Results/gwtc1_phasemarg/plots/corner_TaylorF2_hetero_vs_unhetero.pdf) | [`Plots/plot_corner_TaylorF2_hetero_vs_unhetero.py`](../Plots/plot_corner_TaylorF2_hetero_vs_unhetero.py) | TaylorF2 heterodyned baseline, TaylorF2 unheterodyned, GWTC-1 HDF5 |
| [`corner_GW150914.pdf`](../Results/gwtc1_phasemarg/plots/corner_GW150914.pdf) | [`Plots/plot_GW150914.py`](../Plots/plot_GW150914.py) | GW150914 CSV, GWTC-2.1 HDF5 |
| [`scaling_study.pdf`](../Results/gwtc1_phasemarg/plots/scaling_study.pdf) | [`Plots/plot_scaling_study.py`](../Plots/plot_scaling_study.py) | `Results/scaling_study/scaling_summary.csv` plus hardcoded L4/Bilby references |
| [`gpu_vs_cpu_projection.pdf`](../Results/gwtc1_phasemarg/plots/gpu_vs_cpu_projection.pdf) | [`Plots/plot_scaling_study.py`](../Plots/plot_scaling_study.py) | Hardcoded projection in plotting script |

### Additional Diagnostic Figures

| Graph | Script | Direct inputs |
|---|---|---|
| [`H0_baseline_TaylorF2.pdf`](../Results/gwtc1_phasemarg/plots/H0_baseline_TaylorF2.pdf) | [`Plots/plot_H0_baseline_TaylorF2.py`](../Plots/plot_H0_baseline_TaylorF2.py) | TaylorF2 baseline CSV |
| [`H0_summary_all_methods.pdf`](../Results/gwtc1_phasemarg/plots/H0_summary_all_methods.pdf) | [`Plots/plot_H0_summary.py`](../Plots/plot_H0_summary.py) | IMR baseline, unheterodyned, narrow-H0, flatZ, reweighted, vp250 CSVs |
| [`H0_unheterodyned_vs_gwtc.pdf`](../Results/gwtc1_phasemarg/plots/H0_unheterodyned_vs_gwtc.pdf) | [`Plots/plot_unheterodyned_vs_gwtc.py`](../Plots/plot_unheterodyned_vs_gwtc.py) | IMR/TaylorF2 unheterodyned CSVs, GWTC-1 HDF5 |
| [`H0_prior_comparison.pdf`](../Results/gwtc1_phasemarg/plots/H0_prior_comparison.pdf) | [`Plots/plot_h0_prior_comparison.py`](../Plots/plot_h0_prior_comparison.py) | Unheterodyned standard and small-H0-prior CSVs |
| [`H0_prior_vs_posterior.pdf`](../Results/gwtc1_phasemarg/plots/H0_prior_vs_posterior.pdf) | [`Plots/plot_prior_vs_posterior_H0.py`](../Plots/plot_prior_vs_posterior_H0.py) | IMR/TaylorF2 baseline CSVs |
| [`H0_full_sky_vs_narrow.pdf`](../Results/gwtc1_phasemarg/plots/H0_full_sky_vs_narrow.pdf) | [`Plots/plot_full_sky_vs_narrow.py`](../Plots/plot_full_sky_vs_narrow.py) | Full-sky and narrow-sky unheterodyned CSVs |
| [`corner_full_sky_vs_narrow.pdf`](../Results/gwtc1_phasemarg/plots/corner_full_sky_vs_narrow.pdf) | [`Plots/plot_full_sky_vs_narrow.py`](../Plots/plot_full_sky_vs_narrow.py) | Full-sky and narrow-sky unheterodyned CSVs, GWTC-1 HDF5 |
| [`corner_sky_localization.pdf`](../Results/gwtc1_phasemarg/plots/corner_sky_localization.pdf) | [`Plots/plot_full_sky_vs_narrow.py`](../Plots/plot_full_sky_vs_narrow.py) | Full-sky and narrow-sky unheterodyned CSVs |
| [`corner_reweighted_vs_sampled_flatZ_IMRPhenomD.pdf`](../Results/gwtc1_phasemarg/plots/corner_reweighted_vs_sampled_flatZ_IMRPhenomD.pdf) | [`Plots/plot_corner_reweighted_vs_sampled_flatZ.py`](../Plots/plot_corner_reweighted_vs_sampled_flatZ.py) | IMR direct and reweighted flatZ CSVs |
| [`corner_reweighted_vs_sampled_flatZ_TaylorF2.pdf`](../Results/gwtc1_phasemarg/plots/corner_reweighted_vs_sampled_flatZ_TaylorF2.pdf) | [`Plots/plot_corner_reweighted_vs_sampled_flatZ.py`](../Plots/plot_corner_reweighted_vs_sampled_flatZ.py) | TaylorF2 direct and reweighted flatZ CSVs |
| [`corner_h0_prior_IMRPhenomD.pdf`](../Results/gwtc1_phasemarg/plots/corner_h0_prior_IMRPhenomD.pdf) | [`Plots/plot_h0_prior_comparison.py`](../Plots/plot_h0_prior_comparison.py) | IMR unheterodyned standard and small-H0-prior CSVs |
| [`corner_h0_prior_TaylorF2.pdf`](../Results/gwtc1_phasemarg/plots/corner_h0_prior_TaylorF2.pdf) | [`Plots/plot_h0_prior_comparison.py`](../Plots/plot_h0_prior_comparison.py) | TaylorF2 unheterodyned standard and small-H0-prior CSVs |
| [`corner_speedup_hetero_vs_unhetero.pdf`](../Results/gwtc1_phasemarg/plots/corner_speedup_hetero_vs_unhetero.pdf) | [`Plots/plot_speedup_comparison.py`](../Plots/plot_speedup_comparison.py) | IMR heterodyned baseline and unheterodyned CSVs |
| [`ess_comparison_hetero_vs_unhetero.pdf`](../Results/gwtc1_phasemarg/plots/ess_comparison_hetero_vs_unhetero.pdf) | [`Plots/plot_speedup_comparison.py`](../Plots/plot_speedup_comparison.py) | IMR heterodyned baseline and unheterodyned CSVs |
| [`phase_marginalization_schematic.pdf`](../Results/gwtc1_phasemarg/plots/phase_marginalization_schematic.pdf) | [`Plots/plot_phase_marginalization_schematic.py`](../Plots/plot_phase_marginalization_schematic.py) | IMR heterodyned baseline and IMR unheterodyned CSVs |
| [`prior_sensitivity_H0_IMRPhenomD_NRTidalv2.pdf`](../Results/gwtc1_phasemarg/plots/prior_sensitivity_H0_IMRPhenomD_NRTidalv2.pdf) | [`Plots/compute_prior_sensitivity.py`](../Plots/compute_prior_sensitivity.py) with `WAVEFORM=IMRPhenomD_NRTidalv2` | IMR baseline, flatZ, vp250, reweighted flatZ CSVs |
| [`prior_sensitivity_H0_TaylorF2.pdf`](../Results/gwtc1_phasemarg/plots/prior_sensitivity_H0_TaylorF2.pdf) | [`Plots/compute_prior_sensitivity.py`](../Plots/compute_prior_sensitivity.py) with `WAVEFORM=TaylorF2` | TaylorF2 baseline, flatZ, vp250, reweighted flatZ CSVs |
| [`prior_sensitivity_annotated_IMRPhenomD_NRTidalv2.pdf`](../Results/gwtc1_phasemarg/plots/prior_sensitivity_annotated_IMRPhenomD_NRTidalv2.pdf) | [`Plots/compute_prior_sensitivity.py`](../Plots/compute_prior_sensitivity.py) with `WAVEFORM=IMRPhenomD_NRTidalv2` | IMR prior-sensitivity CSVs |
| [`prior_sensitivity_annotated_TaylorF2.pdf`](../Results/gwtc1_phasemarg/plots/prior_sensitivity_annotated_TaylorF2.pdf) | [`Plots/compute_prior_sensitivity.py`](../Plots/compute_prior_sensitivity.py) with `WAVEFORM=TaylorF2` | TaylorF2 prior-sensitivity CSVs |
| [`prior_functions_IMRPhenomD_NRTidalv2.pdf`](../Results/gwtc1_phasemarg/plots/prior_functions_IMRPhenomD_NRTidalv2.pdf) | [`Plots/compute_prior_sensitivity.py`](../Plots/compute_prior_sensitivity.py) with `WAVEFORM=IMRPhenomD_NRTidalv2` | Analytic prior functions |
| [`prior_functions_TaylorF2.pdf`](../Results/gwtc1_phasemarg/plots/prior_functions_TaylorF2.pdf) | [`Plots/compute_prior_sensitivity.py`](../Plots/compute_prior_sensitivity.py) with `WAVEFORM=TaylorF2` | Analytic prior functions |

## Reference Data Files

| Reference data | Used by |
|---|---|
| [`Results/GW170817_GWTC-1.hdf5`](../Results/GW170817_GWTC-1.hdf5) | [`Plots/_plot_utils.py`](../Plots/_plot_utils.py), GW170817 corner comparisons |
| [`GW170817/Scripts/GW170817_GWTC-1.hdf5`](../GW170817/Scripts/GW170817_GWTC-1.hdf5) | Legacy/script-local copy of GWTC-1 posterior data |
| `EventData/GWOSC/GW170817/*.hdf5` | GW170817 sampling scripts |
| `EventData/GWOSC/GW150914/*.hdf5` | GW150914 sampling script |

## Known Caveats

- `Results/scaling_study/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv` is overwritten by each scaling run because the sampler output label does not include `n_live`. Use `Results/scaling_study/scaling_summary.csv` and the logs for per-`n_live` timing provenance.
- `prior_sensitivity.csv`, `prior_sensitivity_full.json`, and `prior_sensitivity_pdfs.csv` are overwritten when `compute_prior_sensitivity.py` is run for a different waveform. Save waveform-specific copies before relying on these tables for manuscript numbers.
- Some old scripts write to `Plots/Results/` instead of `Results/gwtc1_phasemarg/plots/`; prefer the scripts listed in `Plots/run_all_plots.sh` for the current paper figures.
