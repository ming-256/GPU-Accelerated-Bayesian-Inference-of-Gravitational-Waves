# Plot review — locked-in waveform set + reproduction targets

**All plots in `Results/gwtc1_phasemarg/plots/` (PDF + 300-dpi PNG, existing `Plots/` style).**

Generators are listed only for internal traceability — they will not be cited in the final paper.

## 0. Locked decisions (2026-04-27)

- **GW150914 (validation only):** IMRPhenomXPHM, always. Like-for-like LVK GWTC-2.1 reproduction.
- **GW170817 primary set:** IMRPhenomXAS_NRTidalv3 (primary) + IMRPhenomD_NRTidalv2 (anchor) + TaylorF2 (family check). IMRPhenomPv2 dropped from main figures, retained in repo (`s07__…__imrphenompv2__baseline_lvkbounds`) for the open-source reproducibility appendix.
- **LVK reference:** plotted as the actual GWTC-1 IMRPhenomPv2_NRTidal posterior (`Results/GW170817_GWTC-1.hdf5`) mapped through this work's standard-siren model — not as an HPD band or `[62, 82]` rectangle.
- **1-D posterior style:** weighted step-histograms with sample-derived HPDs. KDEs only kept for 2-D corner contours.
- **Sky priors:** every heterodyned run is **already full-sky** (RA on [0, 2π], dec on [-π/2, π/2] with cos prior). The `_local_` suffix in CSV names refers to `--data-source local` (HDF5 from disk) — *not* a sky restriction. NGC 4993 enters only as the heterodyne reference parameters.
- **Prior-sensitivity sweep status:** IMR + TF2 complete (gwtc1_phasemarg). XAS in flight on GPU as `session_14_xas_prior_sensitivity.sh` — produces `s14__…__{baseline,flatz,vp250}` runs and a post-hoc reweighted variant. When those land the prior-sensitivity figure becomes a 3-waveform × 4-prior matrix.
- **Paper framing:** companion reproduction of Abbott+2017 (Nature 24471 / arXiv 1710.05835). Extensive test-suite results referenced inline ("we have done this, compared this, similar to that") rather than all plotted.

## 1. Scaling study (full coverage)

`scaling_study_full.{pdf,png}` — heterodyned IMR with default mass bounds (8 points: n_live = 500, 1000, 2500, 5000, 10000, 20000, 50000, 100000) + heterodyned IMR with LVK-tight mass bounds (6 points: 500–20000) + all unheterodyned points (IMR default-mass 500/1500/2500, IMR full-sky 1500, TF2 default-mass 1500, TF2 full-sky 1500). Right panel: speedup factor unhetero/hetero at matched n_live (31× at 500, 51× at 1500, 68× at 2500).

Naming note for the scaling study: "host-localised" / "default-mass" in CSV/legend = `--m-comp-{lo,hi}` defaults (0.5, 7.7 M_sun) and *full sky*. "LVK-bounds" = `--m-comp-{lo,hi} 0.87 1.74` (Abbott 2017 H0 paper) and *full sky*. The only sky-narrowed runs in the project are the *unheterodyned* ones tagged as default in their script (`--wide-prior`, ±0.05 rad of NGC 4993); the unheterodyned `_full_sky` CSVs are the full-sky cross-checks.

Driver: `Plots/build_scaling_table.py` → `Results/scaling_study/scaling_summary_full.csv`; `Plots/plot_scaling_full.py`.

## 2. GW150914 — pick a waveform

`corner_GW150914_waveform_comparison.{pdf,png}` — overlays: (i) LVK GWTC-2.1 IMRPhenomXPHM PE (downloaded from Zenodo: `EventData/GWOSC/GW150914/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_nocosmo.h5`); (ii) our IMRPhenomD heterodyned baseline (existing `Results/gwtc1_phasemarg/GW15_PhaseMarg_Heterodyned_IMRPhenomD_…`); (iii) our IMRPhenomXPHM heterodyned (s06 `Results/test_suite/s06__gw150914__imrphenomxphm__lvkbounds__seed0000/samples.csv`).

| Run                  | $\mathcal{M}_c$ med | $q$ med | $d_L$ med (Mpc) | $\iota$ med | $\ln Z$        |
|----------------------|--------------------:|--------:|----------------:|------------:|---------------:|
| LVK GWTC-2.1 (XPHM)  | 30.7                | ~0.83   | ~440            | 2.62        | n/a            |
| this work IMRPhenomD | 30.04               | 0.83    | 404.6           | 2.49        | $260.95\pm0.08$|
| this work XPHM       | 30.34               | 0.87    | 459.8           | 2.62        | $261.09\pm0.08$|

**Recommendation to discuss:** XPHM matches LVK's $d_L$ within a few Mpc, IMRPhenomD is offset by ~50 Mpc. If we want a like-for-like LVK reproduction, use XPHM. If we want to keep cost down for the validation argument, IMRPhenomD is fine — but we should explicitly say the offset is from missing precession/HOM.

Driver: `Plots/plot_GW150914_waveform_comparison.py`.

## 3. GW170817 — three-waveform set + LVK posterior

`H0_waveform_comparison.{pdf,png}` — weighted-histogram H_0 marginals (sample-derived HPDs, no KDE) for IMRPhenomXAS_NRTidalv3 + IMRPhenomD_NRTidalv2 + TaylorF2 + LVK GWTC-1 (mapped through this work's standard-siren model).

`corner_GW170817_waveform_comparison.{pdf,png}` — full $(\mathcal{M}_c, q, \chi_{\rm eff}, d_L, \iota)$ corner overlay; XAS first, then IMR, then TF2; GWTC-1 reference kept; Pv2 dropped.

H_0 summary (sample-derived HPDs — same recipe as the LVK convention):

| Waveform                  | MAP   | 68% HPD       | 95% HPD        | $P(H_0>120)$ | $\ln Z$           |
|---------------------------|------:|---------------|----------------|------------:|-------------------|
| IMRPhenomXAS_NRTidalv3    | 71.5  | [63.1, 88.5]  | [58.8, 117.6]  | 0.034       | $490.08\pm0.10$   |
| IMRPhenomD_NRTidalv2      | 71.5  | [63.2, 90.5]  | [58.2, 130.0]  | 0.070       | $489.96\pm0.10$   |
| TaylorF2                  | 68.5  | [61.2, 89.3]  | [56.7, 127.0]  | 0.065       | $486.90\pm0.10$   |
| LVK GWTC-1 (mapped)       | 67.5  | [61.6, 87.6]  | [57.1, 125.6]  | n/a         | n/a               |

The "LVK GWTC-1 (mapped)" row is the GWTC-1 IMRPhenomPv2_NRTidal d_L posterior pushed through this work's $v_{\rm obs}\sim\mathcal{N}(v_p + H_0 d_L, 72)$ likelihood with $v_p\sim\mathcal{N}(310, 150)$ — same model used by `GW170817_heterodyned_1.py`. All H_0 differences against this row are therefore d_L-distribution differences, not $v_p$-model differences.

Drivers: `Plots/plot_H0_GW170817_waveform_comparison.py`, `Plots/plot_GW170817_waveform_corner.py`.

**Discussion**:
- XAS_NRTv3 and IMRPhenomD_NRTv2 sit on top of each other in MAP (71.5) and share 68% HPD endpoints to within 2 km/s/Mpc. XAS_NRTv3 has the tighter upper tail (95% upper 117.6 vs 130.0) — modern NR-calibrated tides damping the high-H_0 modes.
- TaylorF2 sits 3 km/s/Mpc lower in MAP — small, expected for a lower-PN family — and overlaps the others within their 68% HPDs.
- The LVK posterior peak sits at MAP=67.5; this is *lower* than Abbott+2017's published 70 because the LVK d_L distribution has a long low-d_L tail and our $v_p$ prior centres at 310 km/s rather than their 215 km/s. Tail-shape comparison still passes the eye test.
- IMRPhenomPv2 (no tides) is intentionally *not* in this figure; the precession-only systematic stays in `Results/test_suite/s07__gw170817__imrphenompv2__baseline_lvkbounds/` and is referenced inline in the paper without a dedicated panel.

**Locked primary:** IMRPhenomXAS_NRTidalv3.

## 4. Synoptic H_0 forest (sample-derived HPD; LVK as a real row)

`H0_synoptic.{pdf,png}` — six-row forest, all HPDs computed directly from weighted samples (no KDE). LVK GWTC-1 is its own row using the d_L → H_0 mapping from §3 — **no shaded reference band**. Planck and SH0ES bands kept (population-level priors, not GW170817 measurements).

Rows (top → bottom):

| Row | MAP | 68% HPD | 95% HPD |
|---|---:|---|---|
| IMRPhenomXAS_NRTidalv3 (siren, primary)    | 71.5 | [63.1, 88.5] | [58.8, 117.6] |
| IMRPhenomD_NRTidalv2 (siren, anchor)        | 71.5 | [63.2, 90.5] | [58.2, 130.0] |
| TaylorF2 (siren)                             | 68.5 | [61.2, 89.3] | [56.7, 127.0] |
| IMRPhenomXAS_NRTidalv3 (GW-only)             | 69.5 | [64.4, 91.1] | [62.0, 147.2] |
| IMRPhenomD_NRTidalv2 (GW-only)               | 70.5 | [64.0, 91.2] | [61.5, 147.1] |
| LVK GWTC-1 (Abbott+2017, mapped)             | 67.5 | [61.6, 87.6] | [57.1, 125.6] |

Driver: `Plots/plot_H0_synoptic.py`.

## 5. Prior-sensitivity (the central science finding)

`H0_prior_sensitivity.{pdf,png}` — four prior variants for the primary waveform overlaid as weighted histograms (no KDE), with LVK GWTC-1 plotted as a real curve (not a shaded band). The script auto-selects:

- **Primary (locked):** IMRPhenomXAS_NRTidalv3, four variants from `s14__…__{baseline,flatz,reweighted_flatz,vp250}__seed0000`. **Available once `session_14_xas_prior_sensitivity.sh` finishes on the GPU.**
- **Fallback (used until s14 lands):** IMRPhenomD_NRTidalv2 host-loc suite from `gwtc1_phasemarg/`, identical four variants. The values below are from this fallback and will be replaced once XAS s14 CSVs arrive.

Tail-probability summary (direct sample-weighted, not KDE):

| Variant                          | MAP  | 68% HPD       | $P(H_0>120)$ | $P(H_0>150)$ | $\ln Z$           |
|----------------------------------|-----:|---------------|------------:|------------:|-------------------|
| Baseline ($\pi(d_L)\propto d_L^2$)| 71.6 | [62.5, 91.4]  | 0.076       | 0.016       | $486.67\pm0.09$   |
| Flat-in-$z$ direct                | 75.2 | [61.5, 118.0] | 0.281       | 0.147       | $486.49\pm0.10$   |
| Flat-in-$z$ reweighted            | 74.1 | [63.1, 107.8] | 0.195       | 0.056       | (post-hoc)        |
| $\sigma_{v_p}=250\,\rm km\,s^{-1}$| 72.3 | [61.2, 91.5]  | 0.067       | 0.012       | $485.96\pm0.08$   |

The reweighted estimator captures roughly $(0.195-0.076)/(0.281-0.076) \approx 58$ per cent of the prior-induced shift in $P(H_0>120)$; the residual 42 per cent is the missing Mode-B mass.

Evidence ratios are essentially flat across baseline / flatZ / vp250 ($\Delta \ln Z \lesssim 0.7$) — the data does not prefer any one $d_L$ prior, so the $H_0$ shift is a *prior* effect, not a data-driven update. This is the central science finding.

Driver: `Plots/plot_H0_prior_sensitivity.py`.

## 6. The $d_L$–$\iota$ bimodality (mechanism behind the prior-sensitivity result)

`bimodality.{pdf,png}` — joint $(d_L,\iota)$ posterior under the unrestricted flat-in-$z$ run, with the prior-restricted Mode-A and Mode-B contours overlaid; right panel shows the per-mode $H_0$ marginal.

| Variant        | $d_L$ range (Mpc) | MAP $H_0$ | 68% HPD       | $P(H_0>120)$ | $\ln Z$        |
|----------------|------------------:|----------:|---------------|------------:|----------------|
| Mode A         | [30, 75]          | 74.4      | [66.4, 88.6]  | $\sim 10^{-7}$ | $486.80\pm0.10$|
| Mode B         | [10, 30]          | 110.8     | [98.6, 152.1] | 0.638       | $486.95\pm0.09$|
| Combined       | [10, 75]          | 75.2      | [61.5, 118.0] | 0.281       | $486.48\pm0.09$|

$\ln \mathcal{B}_{\rm B/A} = (\ln Z_{\rm B}-\ln Z_{\rm A}) + \ln(20/45) = +0.15 - 0.81 = -0.66$ (Mode B mildly disfavoured).

Driver: `Plots/plot_bimodality.py`.

## 7. Existing figures kept as-is

Still useful and in matching style:
- `corner_combined_waveforms.{pdf,png}` (IMR vs TF2 baseline + GWTC-1)
- `corner_IMRPhenomD_hetero_vs_unhetero.{pdf,png}`
- `corner_TaylorF2_hetero_vs_unhetero.{pdf,png}`
- `dL_reweight_comparison_IMRPhenomD_NRTidalv2.{pdf,png}`
- `H0_baseline_IMRPhenomD.{pdf,png}` (single-baseline KDE)

## 8. Action items remaining (post-decision)

All waveform-choice questions are now resolved (see §0). Remaining work:

1. **s14 IMRPhenomXAS_NRTidalv3 prior-sensitivity sweep.** In flight on the GPU box (`mnras_paper/test_suite/session_plans/session_14_xas_prior_sensitivity.sh`, 3 runs × ~15 min). Post-hoc reweighted variant produced locally via `Plots/reweight_dL_to_flat_z.py`. When the four CSVs land at `Results/test_suite/s14__gw170817__imrphenomxas_nrtidalv3__*`, `build_full_summary.py` and `plot_H0_prior_sensitivity.py` pick them up automatically — no manual wiring needed.
2. **Regenerate `mnras_paper/figures/output/` in `Plots/_plot_utils.py` style.** Existing v1 set has the wrong style + stale data. Plan: write a v2 set under `mnras_paper/figures/v2/` so we can A/B before retiring v1.
3. **`paper_knowledge_base/data_manifest.csv`** (optional but recommended for the reproducibility framing) — single source of truth mapping `(figure, panel, dataset, samples_file, sha256, n_samples, log_Z)` so a stale CSV cannot sneak into a figure.
4. **Manuscript hygiene pass.** Drop all `Source: …` and `Plots/…` mentions from `mnras_paper/main.tex`; preserve provenance in `paper_knowledge_base/result_link_index.md` and `Results/scaling_study/scaling_summary_full.csv` and (planned) `data_manifest.csv`.

## 9. Data provenance (for cross-checking)

Authoritative numbers in this document trace to:

- **H_0 / d_L summary stats** (MAP, HPD, tail probs): `Results/gwtc1_phasemarg/summary_stats_full.csv` — generated by `Plots/build_full_summary.py`. Histogram-MAP and sample-derived HPDs are computed in `Plots/_plot_utils.py` (`map_from_hist`, `compute_hpd_samples`) and used by the updated 1-D plot scripts; the legacy KDE-grid HPDs (`compute_hpd` on a 4000-point grid) are still used by `build_full_summary.py` itself for back-compat with older REVIEW versions, with $\le 1$ km/s/Mpc differences vs the new sample-HPDs.
- **Scaling study** (n_live, dead points, log Z, wall-clock): `Results/scaling_study/scaling_summary_full.csv` — generated by `Plots/build_scaling_table.py`.
- **log Z and N_eff** (default-mass heterodyned suite + GW150914 IMRPhenomD): `Results/gwtc1_phasemarg/evidence_table.csv` (from `Plots/compute_evidence_table.py`).
- **log Z** (s06 GW150914 XPHM, s07 LVK-bounds 4-waveform suite, s10 bimodality, s14 XAS sensitivity): grep `"Log Evidence"` in `Results/test_suite/<run>/sampler.log`.
- **LVK GW170817 reference posterior** (used as a real curve, never as a band): GWTC-1 `IMRPhenomPv2NRT_lowSpin_posterior` from `Results/GW170817_GWTC-1.hdf5`, mapped to H_0 via `derive_lvk_h0_samples` in `Plots/_plot_utils.py` using the same standard-siren constants as `GW170817_heterodyned_1.py` (v_obs=3327, sigma_v=72, v_p~N(310, 150) km/s).
- **LVK GW150914 reference posterior**: GWTC-2.1 `C01:IMRPhenomXPHM/posterior_samples` from `EventData/GWOSC/GW150914/IGWN-GWTC2p1-v2-...h5`.
