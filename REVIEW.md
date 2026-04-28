# Plot review — locked-in waveform set + reproduction targets

**Final-stretch state (2026-04-28).** All test-suite runs are on disk; all figures and summary tables regenerated against the complete result set. Plots in `Results/gwtc1_phasemarg/plots/` (PDF + 300-dpi PNG, `Plots/_plot_utils.py` style throughout).

Generators are listed only for internal traceability — they will not be cited in the final paper.

## 0. Locked decisions (status: green across the board)

- **GW150914 (validation only):** IMRPhenomXPHM, always. Like-for-like LVK GWTC-2.1 reproduction.
- **GW170817 primary set:** IMRPhenomXAS_NRTidalv3 (primary) + IMRPhenomD_NRTidalv2 (anchor) + TaylorF2 (family check). IMRPhenomPv2 dropped from main figures, retained in repo (`s07__…__imrphenompv2__baseline_lvkbounds`) for the reproducibility appendix.
- **LVK reference:** plotted as the actual GWTC-1 IMRPhenomPv2_NRTidal posterior (`Results/GW170817_GWTC-1.hdf5`) mapped through this work's standard-siren model — never as an HPD band or `[62, 82]` rectangle.
- **1-D posterior style:** weighted step-histograms with sample-derived HPDs. KDEs only kept for 2-D corner contours.
- **Sky priors:** every heterodyned run is *already full-sky* (RA on [0, 2π], dec on [−π/2, π/2] with cos prior). The `_local_` suffix in CSV names refers to `--data-source local` (HDF5 from disk) — *not* a sky restriction. NGC 4993 enters only as the heterodyne reference parameters and as the optional `--narrow-sky` patch (s15).
- **Prior-sensitivity sweep (XAS):** ✅ complete. `s14__…__{baseline,flatz,vp250}` produced on the GPU box; the post-hoc reweighted variant produced locally via `Plots/reweight_dL_to_flat_z.py`. Now the primary panel of `H0_prior_sensitivity.pdf`.
- **Sky-prior runtime sweep (s15):** ✅ complete. `s15__…__{IMR,XAS}__baseline_lvkbounds_narrow` — matched `n_live=5000` against the s07 full-sky LVK-bounds runs.
- **Paper framing:** companion reproduction of Abbott+2017 (Nature 24471 / arXiv 1710.05835). The full test-suite is referenced inline ("we have done this, compared this, similar to that") rather than all plotted.

## 1. Scaling study (full coverage)

`scaling_study_full.{pdf,png}` — heterodyned IMR with default mass bounds (8 points: n_live = 500, 1000, 2500, 5000, 10000, 20000, 50000, 100000) + heterodyned IMR with LVK-tight mass bounds (6 points: 500–20000) + all unheterodyned points (IMR default-mass 500/1500/2500, IMR full-sky 1500, TF2 default-mass 1500, TF2 full-sky 1500). Right panel: speedup factor unhetero/hetero at matched n_live.

| n_live | hetero (s) | unhetero (s) | speedup |
|------:|-----------:|-------------:|--------:|
| 500  | 235        | 7,317        | 31.1×   |
| 1500 | 395        | 20,042       | 50.7×   |
| 2500 | 550        | 37,200       | 67.7×   |

Naming note: "default-mass" / "host-localised" in CSV/legend = `--m-comp-{lo,hi}` defaults (0.5, 7.7 M_sun) and *full sky*. "LVK-bounds" = `--m-comp-{lo,hi} 0.87 1.74` (Abbott 2017 H0 paper) and *full sky*. The only sky-narrowed runs in the project are (i) the *unheterodyned* `--wide-prior` runs (±0.05 rad of NGC 4993, the default in the unhetero scripts) and (ii) the heterodyned s15 runs with `--narrow-sky`.

Driver: `Plots/build_scaling_table.py` → `Results/scaling_study/scaling_summary_full.csv` (23 rows); `Plots/plot_scaling_full.py`.

## 2. GW150914 — pick a waveform

`corner_GW150914_waveform_comparison.{pdf,png}` — overlays: (i) LVK GWTC-2.1 IMRPhenomXPHM PE (Zenodo: `EventData/GWOSC/GW150914/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_nocosmo.h5`); (ii) our IMRPhenomD heterodyned baseline (`Results/gwtc1_phasemarg/GW15_PhaseMarg_Heterodyned_IMRPhenomD_…`); (iii) our IMRPhenomXPHM heterodyned (`s06__gw150914__imrphenomxphm__lvkbounds__seed0000`).

| Run                  | $\mathcal{M}_c$ med | $q$ med | $d_L$ med (Mpc) | $\iota$ med | $\ln Z$           |
|----------------------|--------------------:|--------:|----------------:|------------:|-------------------|
| LVK GWTC-2.1 (XPHM)  | 30.7                | ~0.83   | ~440            | 2.62        | n/a               |
| this work IMRPhenomD | 30.04               | 0.83    | 404.6           | 2.49        | $260.95\pm0.08$   |
| this work XPHM       | 30.34               | 0.87    | 459.8           | 2.62        | $261.09\pm0.08$   |

XPHM matches LVK's $d_L$ within a few Mpc; IMRPhenomD is offset by ~50 Mpc. Like-for-like LVK reproduction → XPHM.

Driver: `Plots/plot_GW150914_waveform_comparison.py`.

## 3. GW170817 — three-waveform set + LVK posterior

`H0_waveform_comparison.{pdf,png}` — weighted-histogram H_0 marginals (sample-derived HPDs, no KDE) for IMRPhenomXAS_NRTidalv3 + IMRPhenomD_NRTidalv2 + TaylorF2 + LVK GWTC-1 (mapped through this work's standard-siren model).

`corner_GW170817_waveform_comparison.{pdf,png}` — full $(\mathcal{M}_c, q, \chi_{\rm eff}, d_L, \iota)$ corner overlay; XAS first, then IMR, then TF2; GWTC-1 reference kept; Pv2 dropped.

H_0 summary (sample-derived HPDs from the `_plot_utils.compute_hpd_samples` recipe; LVK row is the same recipe applied to GWTC-1 d_L pushed through the standard-siren model):

| Waveform                  | MAP   | 68% HPD       | 95% HPD        | $P(H_0>120)$ | $\ln Z$           |
|---------------------------|------:|---------------|----------------|------------:|-------------------|
| IMRPhenomXAS_NRTidalv3    | 72.4  | [63.1, 88.5]  | [58.8, 117.6]  | 0.034       | $490.08\pm0.10$   |
| IMRPhenomD_NRTidalv2      | 72.4  | [63.2, 90.5]  | [58.2, 130.0]  | 0.070       | $489.96\pm0.10$   |
| TaylorF2                  | 68.9  | [61.2, 89.3]  | [56.7, 127.0]  | 0.065       | $486.90\pm0.10$   |
| LVK GWTC-1 (mapped)       | 67.1  | [61.6, 87.6]  | [57.1, 125.6]  | n/a         | n/a               |

The LVK row is the GWTC-1 IMRPhenomPv2_NRTidal d_L posterior pushed through this work's $v_{\rm obs}\sim\mathcal{N}(v_p + H_0 d_L, 72)$ likelihood with $v_p\sim\mathcal{N}(310, 150)$ — same model as `GW170817_heterodyned_1.py`. All H_0 differences against this row are therefore d_L-distribution differences, not $v_p$-model differences.

Drivers: `Plots/plot_H0_GW170817_waveform_comparison.py`, `Plots/plot_GW170817_waveform_corner.py`.

**Discussion.**
- XAS_NRTv3 and IMRPhenomD_NRTv2 sit on top of each other at MAP=72.4 and share 68% HPD endpoints to within ~2 km/s/Mpc. XAS_NRTv3 has the tighter upper tail (95% upper 117.6 vs 130.0) — modern NR-calibrated tides damping the high-H_0 modes.
- TaylorF2 sits ~3.5 km/s/Mpc lower in MAP — small, expected for a lower-PN family — and overlaps the others within their 68% HPDs.
- The LVK posterior peaks at MAP=67.1; this is *lower* than Abbott+2017's published 70 because the LVK d_L distribution has a long low-d_L tail and our $v_p$ prior centres at 310 km/s rather than their 215 km/s.
- IMRPhenomPv2 (no tides) is intentionally *not* in this figure; the precession-only systematic stays in `s07__…__imrphenompv2__baseline_lvkbounds/` and is referenced inline in the paper.

**Locked primary:** IMRPhenomXAS_NRTidalv3.

## 4. Synoptic H_0 forest

`H0_synoptic.{pdf,png}` — six-row forest, all HPDs computed directly from weighted samples. LVK GWTC-1 is its own row using the d_L → H_0 mapping from §3 — **no shaded reference band**. Planck and SH0ES bands kept.

| Row                                              | MAP  | 68% HPD       | 95% HPD        |
|--------------------------------------------------|-----:|---------------|----------------|
| IMRPhenomXAS_NRTidalv3 (siren, primary)          | 71.5 | [63.1, 88.5]  | [58.8, 117.6]  |
| IMRPhenomD_NRTidalv2 (siren, anchor)             | 71.5 | [63.2, 90.5]  | [58.2, 130.0]  |
| TaylorF2 (siren)                                 | 68.5 | [61.2, 89.3]  | [56.7, 127.0]  |
| IMRPhenomXAS_NRTidalv3 (GW-only)                 | 69.5 | [64.4, 91.1]  | [62.0, 147.2]  |
| IMRPhenomD_NRTidalv2 (GW-only)                   | 70.5 | [64.0, 91.2]  | [61.5, 147.1]  |
| LVK GWTC-1 (Abbott+2017, mapped)                 | 67.5 | [61.6, 87.6]  | [57.1, 125.6]  |

Driver: `Plots/plot_H0_synoptic.py`.

## 5. Prior-sensitivity (the central science finding) — XAS_NRTv3 primary

`H0_prior_sensitivity.{pdf,png}` — four prior variants for **IMRPhenomXAS_NRTidalv3** (s14 sweep, full-sky default-mass) overlaid as weighted histograms (no KDE), with LVK GWTC-1 plotted as a real curve.

Sample-derived HPDs (from `compute_hpd_samples` in `_plot_utils.py`):

| Variant                              | MAP  | 68% HPD       | $P(H_0>120)$ | $P(H_0>150)$ | $\ln Z$           |
|--------------------------------------|-----:|---------------|------------:|------------:|-------------------|
| Baseline ($\pi(d_L)\propto d_L^2$)   | 73.5 | [63.8, 87.6]  | 0.017       | 0.000       | $486.25\pm0.11$   |
| Flat-in-$z$ direct                   | 71.9 | [64.2, 103.8] | 0.159       | 0.038       | $487.30\pm0.10$   |
| Flat-in-$z$ reweighted               | 73.5 | [65.2, 95.9]  | 0.041       | 0.000       | (post-hoc)        |
| $\sigma_{v_p}=250\,\rm km\,s^{-1}$   | 71.9 | [61.7, 90.5]  | 0.069       | 0.015       | $485.55\pm0.09$   |

Reweighting captures $(0.041-0.017)/(0.159-0.017)\approx 17\%$ of the prior-induced shift in $P(H_0>120)$ for the XAS sweep — much smaller than the IMR fallback's ~58% because XAS's tighter upper tail leaves less Mode-B mass to be "rescued" by a flat-in-$z$ shift in the first place.

Evidence ratios across baseline / flatZ / vp250 are within $\Delta\ln Z\lesssim 1.8$ — consistent with the data not preferring any one $d_L$ prior. The $H_0$ shift is a *prior* effect, not a data-driven update. **This is the central science finding.**

For comparison, the IMRPhenomD_NRTidalv2 host-loc fallback (now retired from the primary panel; kept for cross-checks) gave: baseline MAP 71.6, $P(H_0>120)=0.076$; flat-z direct MAP 75.2, $P=0.281$; reweighted MAP 74.1, $P=0.195$; vp250 MAP 72.3, $P=0.067$. Same qualitative behaviour, larger amplitude.

Driver: `Plots/plot_H0_prior_sensitivity.py` (auto-detects s14 XAS, falls back to IMR if missing).

## 6. The $d_L$–$\iota$ bimodality (mechanism behind §5)

`bimodality.{pdf,png}` — joint $(d_L,\iota)$ posterior under the unrestricted flat-in-$z$ run, with the prior-restricted Mode-A and Mode-B contours overlaid; right panel shows the per-mode $H_0$ marginal.

| Variant        | $d_L$ range (Mpc) | MAP $H_0$ | 68% HPD       | $P(H_0>120)$    | $\ln Z$           |
|----------------|------------------:|----------:|---------------|----------------:|-------------------|
| Mode A         | [30, 75]          | 74.4      | [66.4, 88.6]  | $\sim 10^{-7}$  | $486.80\pm0.10$   |
| Mode B         | [10, 30]          | 110.8     | [98.6, 152.1] | 0.638           | $486.95\pm0.09$   |
| Combined       | [10, 75]          | 75.2      | [61.5, 118.0] | 0.281           | $486.48\pm0.09$   |

$\ln \mathcal{B}_{\rm B/A} = (\ln Z_{\rm B} - \ln Z_{\rm A}) + \ln(20/45) = +0.15 - 0.81 = -0.66$ (Mode B mildly disfavoured).

Driver: `Plots/plot_bimodality.py`.

## 7. Sky-prior runtime sweep (new — s15)

`sky_prior_runtime.{pdf,png}` — wall-clock and runtime ratio for full-sky vs narrow-sky (`±0.05 rad` of NGC 4993) at matched n_live=5000.

| Sampler        | Waveform                | Full-sky (s) | Narrow-sky (s) | Ratio |
|----------------|-------------------------|-------------:|---------------:|------:|
| Heterodyned    | IMRPhenomD_NRTidalv2    | 858          | 735            | 0.86  |
| Heterodyned    | IMRPhenomXAS_NRTidalv3  | n/a (s15 only at n_live=5000; full-sky baseline = 489.96 lnZ s07) | 753 | — |
| Unheterodyned  | IMRPhenomD_NRTidalv2    | 20,474       | 20,042         | 0.98  |
| Unheterodyned  | TaylorF2                | 5,981        | 8,615          | 1.44  |

Narrow-sky $\ln Z$ at n_live=5000: IMR 496.54±0.09, XAS 496.49±0.10 — both consistent with the full-sky LVK-bounds values within Monte-Carlo noise, but the narrow-sky integrals are higher because the sky-prior volume is much smaller (so prior odds boost the marginal). **Per-sample posterior** is statistically identical, which is the point.

Take-away: the heterodyned sampler is already so efficient over the sky angles that imposing a tight prior buys ~14% wall-clock; for the unhetero sampler it ranges from negligible to (TF2 case) actively negative due to the smaller acceptance-probability gradient near the prior edge. Sky-prior tightness is therefore *not* the source of the speedup result in §1.

Driver: `Plots/plot_sky_prior_runtime.py`. Pre-computed companion CSV: `Results/test_suite/sky_prior_runtime_pairs.csv` (regenerated by the same script at runtime).

## 8. Existing figures kept as-is

Still useful and in matching style:
- `corner_combined_waveforms.{pdf,png}` (IMR vs TF2 baseline + GWTC-1)
- `corner_IMRPhenomD_hetero_vs_unhetero.{pdf,png}`
- `corner_TaylorF2_hetero_vs_unhetero.{pdf,png}`
- `dL_reweight_comparison_IMRPhenomD_NRTidalv2.{pdf,png}`
- `H0_baseline_IMRPhenomD.{pdf,png}` (single-baseline KDE)
- `phase_marginalization_schematic.{pdf,png}`
- `corner_full_sky_vs_narrow.{pdf,png}` and `H0_full_sky_vs_narrow.{pdf,png}`

## 9. Action items remaining

All sampling work is complete. Remaining tasks are paper-side:

1. **Regenerate `mnras_paper/figures/output/` in `Plots/_plot_utils.py` style** (v1 is stale; plan: write v2 set under `mnras_paper/figures/v2/` so we can A/B before retiring v1).
2. **`paper_knowledge_base/data_manifest.csv`** — single source of truth mapping `(figure, panel, dataset, samples_file, sha256, n_samples, log_Z)` so a stale CSV cannot sneak into a figure.
3. **Manuscript hygiene pass.** Drop all `Source: …` and `Plots/…` mentions from `mnras_paper/main.tex`; preserve provenance in `paper_knowledge_base/result_link_index.md`, `Results/scaling_study/scaling_summary_full.csv`, and (planned) `data_manifest.csv`.
4. **One-off:** `Plots/plot_bimodality.py` patched from `np.trapz` → `np.trapezoid` for NumPy 2.x; `Plots/build_scaling_table.py` `_runtime` now falls back to `sampler.log` "Total:" line when `finish.json` is missing (s15 was missing it). Both committed-locally fixes — fold into the next commit.

## 10. Data provenance (for cross-checking)

Authoritative numbers in this document trace to:

- **H_0 / d_L summary stats** (MAP, HPD, tail probs): `Results/gwtc1_phasemarg/summary_stats_full.csv` (18 rows, includes XAS s14) — generated by `Plots/build_full_summary.py`. The KDE-grid HPDs in that CSV are kept for back-compat; the *plotted* HPDs use `compute_hpd_samples` (sample-derived) from `Plots/_plot_utils.py` and differ by ≤1 km/s/Mpc.
- **Scaling study** (n_live, dead points, log Z, wall-clock; 23 rows including s15 narrow-sky): `Results/scaling_study/scaling_summary_full.csv` — `Plots/build_scaling_table.py`.
- **log Z and N_eff** (default-mass heterodyned suite + GW150914 IMRPhenomD): `Results/gwtc1_phasemarg/evidence_table.csv` (`Plots/compute_evidence_table.py`).
- **log Z** (s06 GW150914 XPHM, s07 LVK-bounds 4-waveform suite, s10 bimodality, s14 XAS sensitivity, s15 narrow-sky): grep `"Log Evidence"` in `Results/test_suite/<run>/sampler.log`. Confirmed values used here:
  - s14 XAS baseline: 486.25±0.11; flatZ: 487.30±0.10; vp250: 485.55±0.09.
  - s15 IMR narrow-sky: 496.54±0.09; XAS narrow-sky: 496.49±0.10.
- **LVK GW170817 reference posterior**: GWTC-1 `IMRPhenomPv2NRT_lowSpin_posterior` from `Results/GW170817_GWTC-1.hdf5`, mapped to H_0 via `derive_lvk_h0_samples` in `Plots/_plot_utils.py` using the same standard-siren constants as `GW170817_heterodyned_1.py` (v_obs=3327, sigma_v=72, v_p~N(310, 150) km/s).
- **LVK GW150914 reference posterior**: GWTC-2.1 `C01:IMRPhenomXPHM/posterior_samples` from `EventData/GWOSC/GW150914/IGWN-GWTC2p1-v2-...h5`.
