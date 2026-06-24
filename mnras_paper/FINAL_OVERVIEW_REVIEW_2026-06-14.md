# Final pre-submission overview — MNRAS draft

**Paper:** *Rapid Hubble constant inference from GW170817 using GPU-accelerated nested sampling: prior sensitivity and the limits of post-hoc reweighting*
**Authors:** Yang, Prathaban, Yallup & Handley (2026)
**Reviewed file:** `mnras_paper/main.tex` (compiled `main.pdf`, 11 pp., 7 figures, 4 tables), last edited 2026-05-24 (commit `dae2605`).
**Review date:** 2026-06-14
**Scope:** image confirmation (visual), full numerical audit against source CSVs/`sampler.log`s, internal/abstract↔body↔table consistency, live literature & citation check.

---

## 0. Bottom line

**The headline science is sound and reproducible.** Every `\input` table regenerates **byte-identical** from `Plots/build_paper_tables.py`; every derived quantity I re-derived from the canonical chains matches (capture fractions 16.7 %/58.0 %, Mode-B weights 0.325/0.428, k̂ = 0.683, ln 𝓑 = −0.66/+0.10, speedups 31.2×/50.7×/67.7×). The abstract numbers all trace to Table 2, and the `lnZ` values match the sampler logs exactly. The LaTeX compiles with **no undefined references or citations** and the bibliography has no orphans.

What remains is **polish, figure/caption integrity, two citation fixes, and one internal-number inconsistency** — all cheap — plus a set of **scientific residuals you have already consciously deferred** (the M1/M2/M4/M7 items), of which the selection-term framing (M1) is the most likely referee pushback. Nothing I found undermines the central result; the issues below are about making the manuscript clean enough that a referee can't pick at it.

Recommended classification if I were the referee: **minor-to-moderate revision**, contingent on closing the figure/caption items and deciding how far to go on M1.

---

## 1. Must-fix before submission

### 1.1 Internal `n_eff` contradiction (same page) — **trivial fix**
§4.1 reports the reweighted-IMRX effective sample size **twice with different values**:
- L236 (bias-vs-variance ¶): "draws at the reweighted `n_eff = 27,539`"
- L238 (ESS-diagnostic ¶): "the reweighted uniform-in-`d_L` estimator has `n_eff = 27,317`"

Both are individually reproducible, but they are the **same physical quantity** computed two ways: **27,317** = Kish ESS of the saved `reweighted_flatz/samples.csv` `weight` column (this is what `build_paper_tables.py` and `paper_diagnostics.csv` use, and what the "lower than the baseline" coverage argument rests on); **27,539** = an on-the-fly reweight inside `analyze_psis_khat.py` over the unfiltered baseline draw. **27,317 is the canonical value.** Harmonise L236 → 27,317 (the bootstrap CI [0.037, 0.042] is unaffected by the 0.8 % draw-size change). Baseline 30,695 and direct 37,022 are internally consistent and exact.

### 1.2 Figure 3 carries an internal referee code in its plot title — **must regenerate**
The suptitle of `bimodality_imr_vs_imrx.pdf` is literally **"M4 cross-check: (d_L, ι) bimodality across the NRTidalv2 → NRTidalv3 calibration."** "M4 cross-check:" is an internal referee-response label (`compare_bimodality_waveforms.py` suptitle). Drop it.

### 1.3 Figures contradict the stated 1-D methodology — **most important figure issue**
§2.6 (L162) states, as a deliberate scientific choice: *"We do not use kernel-density estimates for one-dimensional summaries because the GW170817 posterior tails carry the prior-sensitivity signal … and KDE smoothing distorts the tails."* The figure captions echo this ("weighted step-histograms"; Fig 5 caption even says "(no KDE smoothing)"). **But the actual generators use `scipy.stats.gaussian_kde(bw_method='silverman')` for the 1-D H₀ marginals:**
- Fig 2 — `Plots/plot_H0_prior_sensitivity.py` L43
- Fig 4(b) — `Plots/plot_bimodality.py` L96
- Fig 5 — `Plots/plot_H0_GW170817_waveform_comparison.py` → `plot_h0_kde`

Your own QC checklist (`final_critical_analysis.md:524`) marks "Figures use weighted step-histograms (not KDEs) for 1-D ✅" — but the conversion was never actually done. Because the figures the reader uses to judge the prior-sensitivity **tails** are KDE-smoothed (the exact smoothing §2.6 says distorts those tails), this is an integrity inconsistency a referee can seize on. **The table numbers are unaffected** (they come from weighted samples, no KDE), so only the rendering needs reconciling. Two options:
- **(A, preferred)** regenerate Figs 2/4b/5 as weighted step-histograms — consistent with §2.6 and the captions, and with the paper's own argument; or
- **(B, fast)** change §2.6 + the three captions to admit KDE is used for the 1-D *plots* (tables remain KDE-free), and add one sentence on why Silverman KDE doesn't distort the displayed tails.

### 1.4 Captions describe figure elements that are not drawn — **fix captions or figures**
- **Fig 2** caption (L221): "The published Abbott+2017 H₀ = 70₋₈⁺¹² band is shown in panel (a) as a vertical reference." → the generator passes `lvk_band=False` for **both** panels (L117/L120); no Abbott band/line is drawn and there is no legend entry.
- **Fig 5** caption (L298–299): "Vertical markers are 68 and 95 per cent HPD bounds …" and "the published Abbott+2017 … band is shown as a vertical reference." → generated with `hpd_lines=False, lvk_band=False`; **neither** is drawn.

Either re-enable them in the generators (note: `lvk_band=True` currently draws a single line at H₀=70, not a 62–82 *band* — add an `axvspan` if you want a literal band) **or** delete the claims from the captions. Planck/SH0ES bands *are* drawn correctly in both.

### 1.5 Citation error: Hu & Veitch 2025 mischaracterised — **factual**
L371: "for the Einstein Telescope and Cosmic Explorer era, \citet{HuVeitch2025} project a compact-binary detection rate that brings the bright-siren sub-population to ∼10–100 events per year." The cited paper's own title (in your `.bib`) is *"Costs of Bayesian Parameter Estimation in Third-Generation Gravitational Wave Detectors: an Assessment of Current Acceleration Methods"* (arXiv:2412.02651) — a **compute-cost / acceleration** paper, **not** a bright-siren rate forecast. Re-attribute the ∼10–100/yr figure to a proper source (Chen, Fishbach & Holz 2018 — already in your bib — or Maggiore et al. 2020 ET science case / Branchesi et al. 2023) and keep Hu & Veitch 2025 for the GPU-acceleration motivation, where it belongs.

---

## 2. Should-fix

### 2.1 Missing must-cite: Ashton 2025
**Ashton, G. 2025, "Reconstructing and resampling: a guide to utilising posterior samples from gravitational wave observations," arXiv:2510.11197 (RASTI, under review).** A general guide to reweighting/resampling GW (Bilby) posteriors that explicitly uses Pareto-smoothing/efficiency diagnostics — the **closest methodological neighbour** to your reweighting-validity framing. It does **not** scoop you (not H₀/standard-siren-specific, no direct-vs-reweighted comparison), but a referee will expect it. Cite near the reweighting discussion (L102, alongside `Speagle2020Dynesty`/`Vehtari2024PSIS`). Optional companion: Dax et al. 2023 (neural importance sampling, PRL 130, 171403), which establishes sample-efficiency as the GW reweighting-failure diagnostic.

### 2.2 Name Abbott's reweighted variant precisely: "flat-in-redshift," not "uniform-in-`d_L`"
Abbott et al. (2017) Extended Data Table 1's reweighted alternative (the 71₋₉⁺²³ value you reproduce) is **flat-in-redshift**, not literally uniform-in-`d_L`. You already justify the ≈1 % equivalence at z ≲ 0.02 in §2.4 — good — but L100 ("switching to a uniform-in-`d_L` prior, implemented by reweighting") and L234 ("consistent with the uniform-in-`d_L` posterior reported by Abbott2017") attribute the *uniform-in-`d_L`* label to Abbott. Tighten to "flat-in-redshift (≈ uniform-in-`d_L` at this z; see §2.4)" so an LVK referee can't call it a mischaracterisation of the primary source. (The mechanism claim — that Abbott did this by post-hoc reweighting — is verbatim-confirmed and accurate.)

### 2.3 Hand-typed numbers sit outside the "single source of truth"
Three blocks of numbers are typed directly into `main.tex` rather than regenerated by `build_paper_tables.py`:
- **Table 4 (`tab:waveform-h0`)** — IMRX row = `s14` baseline (reproduces exactly); **TF row** = `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_…_baseline.csv` (lnZ 486.90 from `Results/logs/…baseline_TaylorF2.log`), which is **not in the table-builder's mapping**.
- The **31.2×/50.7×/67.7× speedups** (§5.2) and the **scaling figure** numbers.

The TF row's **95 % HPD upper bounds are mildly stale** (sample-noise in the long upper tail, from an earlier rerun of the same config): IMRX 95 % claimed [59.4, **111.3**] vs current CSV [59.3, **112.4**]; TF claimed [56.9, **125.6**] vs [56.7, **127.0**]. MAP, 68 % HPD, P(H₀>120), and lnZ all match. The same [59.4,111.3]/125.6 values appear in the §4.3 body (L294). **Recommend** regenerating these from the canonical CSVs (ideally fold the waveform table + speedups into `build_paper_tables.py`) so the data release reproduces every printed number.

---

## 3. Nice-to-have / repo hygiene (mostly for the data release)

- **Speedup 50.7× is interpolated, not measured.** There is no heterodyned `n_live=1500` run; the 50.7× comes from log-space interpolation of the heterodyned curve (1000→2500) in `plot_scaling_full.py`. The 31.2× and 67.7× are exact matched-`n_live` ratios. The Fig 7 caption presents all three as "matched … at n_live = 500/1500/2500." Add a half-clause that the 1500 heterodyned point is interpolated.
- **Orphan `table4_cross_waveform.tex`.** Regenerated by `build_paper_tables.py` (from the `s07 lvkbounds` runs, lnZ ≈ 490) but **not** `\input` by the paper, and its numbers differ from the hand-typed `tab:waveform-h0`. Either remove it from the builder or reconcile, so the repo doesn't ship two different "cross-waveform" tables.
- **Unused `figures/output/fig01–fig10`.** A complete alternative figure set (`mnras_paper/figures/plot_all.py`) that the paper does **not** use (the paper pulls 6 figures from `Results/gwtc1_phasemarg/plots/` + 1 from `figures/`). Harmless, but prune or clearly mark it so the data release isn't ambiguous about which figures are canonical.
- **"LVK-matched prior" terminology.** Internally consistent in the paper (= the [0.5, 7.7] M⊙ + chirp [1.184, 2.168], full-sky, volumetric `d_L²` baseline, which **matches** the `s14` run config and §2.4) — but the code's internal `lvkbounds` label means something *different* ([0.87, 1.74] M⊙, the `s07` runs). One clarifying half-sentence in §2.4 ("the source-parameter priors we term *LVK-matched* are the [0.5,7.7] M⊙ + chirp-constraint set of the LVK GW170817 PE") would prevent a reader (or a re-analyst reading the run names) from conflating the two.

---

## 4. Scientific residuals (advisory — you have consciously deferred these)

These are tracked in `DEFERRED_RUNS.md`; the 2026-05-24 rewrite **inoculated** them in-text and deferred the confirmatory runs. My read on referee risk:

- **M1 — selection term `1/N_s(H₀)` (highest risk).** You legitimately drop `N_s(H₀)` by defining variant (i) as a *fixed density on observable `d_L`* (uniform-in-`d_L`), for which `N_s` is H₀-independent — and you verify this in the §2.4 footnote. The residual: your comparison to Abbott's **flat-in-redshift** result (which *does* carry an H₀-dependent `N_s`) leans on the ≈1 % equivalence, and you do **not** show a true flat-in-z + `N_s(H₀)` direct run. A careful (LVK) referee may ask whether the 0.159 tail survives a genuine z-prior with the selection term included. **One** such run would close it decisively; absent that, lean on the §2.4 footnote and the uniform-in-`d_L` reframing and make the flat-in-z-vs-uniform-in-`d_L` distinction explicit wherever you invoke Abbott (ties to §2.2 above).
- **M2 — two-seed lnZ scatter (1.04 gap vs nominal ±0.1).** Honestly disclosed in §4.2 ("within-run statistical error, not a run-to-run reproducibility bound"), falling back to the sign-only `|ln 𝓑|<1` claim. Reasonable; a 5–8-seed ensemble would upgrade it from sign-only to distributional.
- **M4 — bimodality shown on IMR (NRTidalv2), attributed to IMRX.** Bridged by Fig 3 (both waveforms show the two-peak structure) + caveats. The deferred IMRX mode-isolated runs would make it direct rather than proxy.
- **M7 — no `n_mcmc` convergence sweep for the 14-d problem.** Runs use 112 = 8·n_dim (paper §2.1 correct; the `DEFERRED_RUNS.md` "70" was stale). Disclosed as follow-up. Since the headline is a tail probability and under-stepped slice sampling biases tails first, a referee may still ask; the GW150914 validation at 160 steps partly covers the "not sampler-limited" argument.

---

## 5. Figure-by-figure confirmation

All 7 figures the paper compiles resolve to real files (verified via `main.fls`) and render correctly in `main.pdf`. The `fig01–fig10` set in `figures/output/` is **not** used.

| # | File (resolved) | Shows what caption claims? | Notes |
|---|---|---|---|
| 1 | `corner_GW150914_waveform_comparison.pdf` | ✓ | LVK vs XPHM overlap clean; component-mass prior note accurate |
| 2 | `H0_prior_sensitivity.pdf` | ⚠ | direct>reweighted high-tail visible ✓; **Abbott band claimed but not drawn (§1.4)**; **KDE not step (§1.3)** |
| 3 | `bimodality_imr_vs_imrx.pdf` | ⚠ | weights 0.428/0.325 match text ✓; **"M4 cross-check:" in title (§1.2)** |
| 4 | `bimodality.pdf` | ⚠ | joint (d_L,ι) + d_L=30 boundary drawn ✓; **right panel KDE not step (§1.3)** |
| 5 | `H0_waveform_comparison.pdf` | ⚠ | IMRX/TF + Planck/SH0ES ✓; **HPD markers + Abbott band claimed but not drawn (§1.4)**; **KDE not step (§1.3)** |
| 6 | `corner_GW170817_waveform_comparison.pdf` | ✓ | GWTC-1/IMRX/TF overlay clean and professional |
| 7 | `scaling_study_full.pdf` | ✓ | 31×/51×/68× annotated; nlive=20k bend noted; **51× is interpolated (§3)** |

---

## 6. Verified clean (high confidence)

- **Tables 1/4/5/6 reproduce byte-identical** from `build_paper_tables.py`.
- **Abstract ↔ body ↔ Table 2 consistent:** 0.017→0.159, median 77.6→87.6, MAP 70.5, reweighted 0.041 (16.7 %), ΔlnZ decision-pair 1.05, max-spread 1.75 ≲ 1.8; ∼13 min runtime.
- **§2.4 mass prior ([0.5,7.7] M⊙ + chirp [1.184,2.168]) matches the actual `s14` run config** and §III D of Abbott 2019b; the old internal "M3" mass-prior concern is genuinely resolved.
- **Eq. 2 (joint H₀ likelihood) matches Abbott 2017 Eqs 5–6 exactly**; host inputs (v_r=3327±72, ⟨v_p⟩=310±150) match.
- **k̂ = 0.683** reproduces via `analyze_psis_khat.py` and an arviz cross-check; **Bayes factors, capture fractions, Mode-B weights, n_eff(baseline/direct), speedups, scaling gradient 0.60** all reproduce.
- **Reference values exact:** Planck 67.4±0.5, SH0ES 73.04±1.04, Abbott 70₋₈⁺¹², Palmese 2024 75.5₋₅.₄⁺⁵·³, Hotokezaka 70.3₋₅.₀⁺⁵·³.
- **LaTeX:** no undefined refs/citations, no overfull/underfull warnings, no orphan bib entries.
- **Core result is novel and not scooped** (2023–2026 literature swept).

---

## 7. Changes applied to the working tree (2026-06-14)

Recompiled clean each time (latexmk exit 0, no undefined refs/citations; `main.pdf` now 12 pp.). No GW/sampler runs — only the CPU table-builders on existing CSVs.

**Text / citation (§1, §2):**
- §4.1 reweighted `n_eff` 27,539 → **27,317**.
- Abbott variant renamed **flat-in-redshift** (≈ uniform-in-`d_L`) in intro + §4.1.
- §6.3 Hu & Veitch rate claim re-attributed to **Branchesi 2023** (ET); Hu & Veitch kept for PE-cost.
- Added **Ashton 2025** (arXiv:2510.11197) reweighting cite + **Branchesi 2023** to `references.bib` (both as `@misc`/`@article`, render correctly).

**Figures (captions/methods reconciled to the actual KDE rendering; tables stay KDE-free):**
- §2.6 rewritten: 1-D *summaries* (MAP/HPD/tail) are weighted-sample, no KDE; 1-D *curves* in Figs 2/4/5 are Silverman KDE for display only.
- Fig 2/4/5/6 captions: "step-histogram" → "kernel-density estimate"; removed the un-drawn Abbott-band (Figs 2, 5) and HPD-marker (Fig 5) claims.
- **Fig 3 regenerated** without the "M4 cross-check:" title (weights 0.428/0.325 reproduce; rest identical).

**Reproducibility cleanup:**
- `tab:waveform-h0` now `\input{../Results/gwtc1_phasemarg/tableW_waveform.tex}`, generated by new **`Plots/build_waveform_table.py`** from the released CSVs (IMRX = s14 baseline; TF = `gwtc1_phasemarg` TaylorF2 baseline, lnZ 486.90±0.10 from the documented log). Corrected the stale 95 % HPD upper bounds in the table **and** §4.3 body: IMRX 95 % `[59.4,111.3]→[59.3,112.4]`; TF 68 % `[61.4,89.3]→[61.2,89.3]`, 95 % `[56.9,125.6]→[56.7,127.0]`.
- §5.2 speedups: disclosed that the `n_live=1500` heterodyned point is log–log interpolated (500/2500 are direct); noted provenance = `Plots/plot_scaling_full.py`; Fig 7 caption flagged likewise.
- Removed the superseded `table4_cross_waveform.tex` (deleted file + dropped from `build_paper_tables.py`); verified Tables 1/5/6 still regenerate **byte-identical**.
- Marked the unused `figures/output/fig01–fig10` set non-canonical via `figures/output/README.txt`.

**Not done (need either a run or your call):** the M1 flat-in-z + N_s(H₀) confirmatory run (no compute), and pushing any of this to the public `ming-256/GW170817-bright-siren-H0` repo (left to you).
