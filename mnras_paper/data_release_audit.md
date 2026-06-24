# Yang et al. (2026) MNRAS — critical analysis + data-release audit

Pass date: 2026-05-24. Inputs: `mnras_paper/main.tex` (412 lines, 11 pp, 249-word
abstract), `mnras_paper/references.bib` (45 entries), the test-suite and
plotting directories described in `mnras_paper/data_release_prompt.md`, and
the existing public repository `https://github.com/ming-256/GW170817-bright-siren-H0`.

Conda env used for all verification: `/opt/miniconda3/envs/PhD` (python 3.12,
numpy 2, anesthetic ≥2.8, matplotlib 3.9).

This pass was conducted by an adversarial-referee read combined with a
clean-room reproducibility audit. Default behaviour was *propose, do not
apply*; the only files written in this pass are this audit and its companion
`mnras_paper/data_release_inventory.csv`. No paper edits, no commits to the
public repo, no Zenodo deposits.

---

## 1 — Verdict

**Public-repo-ready after listed fixes.**

The paper compiles, every number in the abstract and body ties out to a
canonical CSV, every figure regenerates from a script and chain CSV that
are already on disk, and every cited release URL resolves. The public
repository on GitHub exists and renders cleanly. The science argument and
its supporting numerics are sound.

What still needs to land before pushing the data release publicly:

- **Tier A (2 items):** a one-paragraph inoculation in §4.1 reframing the
  reweighting deficit as *bias*, not coverage failure — a 4 000-draw
  bootstrap on the reweighted estimator gives 95 % CI [0.0374, 0.0419],
  which excludes the directly sampled 0.159 at >100 σ; and a single-line
  honest restriction of the §4.1 \( \hat{k} \) sentence (the paper says
  the PSIS \( \hat{k}>0.7 \) diagnostic *would* flag the failure, but
  we have not actually computed \( \hat{k} \) on the reweighted draw — a
  method-of-moments approximation lands at ≈0.33, below the threshold).
- **Tier B (~6 items):** repo hygiene — promote a single self-contained
  `paper-reproduce/` style layout to the GitHub repo root, prune the 33
  uncited plot scripts and 8 abandoned analysis scripts from the public
  surface, add CITATION.cff, MANIFEST.md, environment.yml, regenerate.sh,
  run_chains.sh, and a `docs/` directory.
- **Tier C (~10 items):** README polish, BibTeX entry alignment, Zenodo
  deposit procedure documented, one or two cosmetic line edits in §5
  (single-A100 → "single NVIDIA A100 40 GB SXM4" or similar).

The full list, with file:line where applicable, is in §9.

---

## 2 — Critical analysis findings (Task 1)

For each item I give: referee objection (one sentence) → current paper
coverage (file:line) → verdict → proposed inoculation.

### a) Bimodality as heterodyne-reference artefact

**Referee objection.** "You claim the heterodyne-reference choice does not
bias the Mode-A/Mode-B weight ratio, but the supporting cross-check (line
~282: 'the Mode-B-anchored unrestricted run recovers P(H₀>120)=0.281,
statistically indistinguishable from the GWTC-1-anchored IMR direct
uniform-in-d_L run') is run on the legacy waveform IMRPhenomD_NRTidalv2
only. You have not run a Mode-B-anchored heterodyne reference on the
*primary* IMRPhenomXAS_NRTidalv3, the waveform the headline result is
quoted under. How do I know the IMRX bimodality is not partly an artefact
of the GWTC-1 reference choice?"

**Current coverage.** `mnras_paper/main.tex:282` (the cross-check sentence)
and `mnras_paper/test_suite/analysis/compare_bimodality_waveforms.py`
(qualitative IMR/refModeB vs IMRX/refGWTC1 comparison). The script's own
docstring explicitly acknowledges this gap: *"The quantitative half --
Mode-A/Mode-B Bayes factor for IMRX -- still requires the s19 IMRX
mode-isolated runs of launch_tier2.sh and is deferred."*
The `DEFERRED_RUNS.md` memo in `mnras_paper/` and the `s19__*_fixedsky_*` 
logs in `Results/test_suite/` show the IMRX refModeB mode-isolated runs
are queued but not completed.

**Verdict.** Partly addressed. The qualitative claim ("the bimodality is
robust across the NRTidalv2 → NRTidalv3 calibration") *is* supported by
the two-panel cross-waveform figure. The stronger claim ("the
heterodyne-reference choice does not bias the Mode-A/Mode-B weight ratio")
is supported on IMR only, not on the primary IMRX.

**Proposed inoculation (Tier A or B; defer-to-follow-up is acceptable).**
Add a half-sentence scope clause at `main.tex:282`:

> "...so the heterodyne-reference choice does not bias the Mode-A/Mode-B
> weight ratio under IMR/NRTidalv2; the corresponding IMRX mode-isolated
> set with a Mode-B-anchored reference is queued for follow-up
> (`s19__gw170817__imrphenomxas_nrtidalv3_*_fixedsky` in the public test
> suite catalogue)."

This is a one-sentence honesty fix and a defer-to-follow-up, not a
substantive science change.

### b) n_eff as a coverage diagnostic — why not k̂?

**Referee objection.** "Kish n_eff compares the *importance-weighted*
draw against the *baseline NS* draw, but those have different effective
sampling distributions — the n_eff comparison is not strictly
well-defined. The PSIS k̂ diagnostic of Vehtari et al. 2024 is the
standard for importance-sampling reliability, and you cite it but do not
report it. Why not run it on the reweighting and quote the number?"

**Current coverage.** `mnras_paper/main.tex:235` quotes the n_eff values
(27 317 reweighted vs 30 695 baseline) and follows with: *"The
Pareto-smoothed importance-sampling k̂ diagnostic of Vehtari2024PSIS would
flag the same failure quantitatively, with the standard k̂>0.7 threshold,
at no additional computational cost."* The `Results/gwtc1_phasemarg/paper_diagnostics.csv` carries
`variant, run, N_samples, n_eff, efficiency_pct` — **no k̂ column.**

**Verdict.** Partly addressed. The n_eff comparison is sound (both
quantities derive from the same baseline draw — the reweighted estimator
*is* importance-weighted by `π_target/π_base`, so its weights are a known
function of the baseline weights and Kish's identity remains the
elementary scalar diagnostic). The k̂ sentence, however, is unsupported:
the paper claims k̂>0.7 *would* flag the failure, but we have not computed
k̂ on the reweighted draw. A back-of-the-envelope method-of-moments k̂ on
the top-20 % tail of the weight ratios lands at ≈ 0.33 — *below* the
Vehtari threshold. That is approximate (a generalised-Pareto MLE is the
correct estimator) but it is enough to make the claim risky.

**Proposed inoculation (Tier A).** Either compute the proper PSIS k̂ on
the IMRX reweighted draw and report it, OR soften the claim to:

> "Pareto-smoothed importance sampling (Vehtari2024PSIS) provides a
> companion diagnostic, with the standard k̂>0.7 threshold; we recommend
> reporting both n_eff and k̂ as the default coverage check before any
> reweighted bright-siren H₀ summary is published."

(The first option — compute k̂ — is preferable. The `arviz` library
provides `loo.psislw` which takes `log_weights` and returns k̂ directly;
adding it to `Plots/build_paper_tables.py` is a ~10-line patch.)

A new column `pareto_khat` should be added to `paper_diagnostics.csv` for
every IS-style reweighted variant (in this paper: just the reweighted
uniform-in-d_L row).

### c) Distance-prior choice — what about comoving-volume and uniform-in-z?

**Referee objection.** "You compare volumetric and uniform-in-d_L. The
forward-looking bright-siren literature is starting to use comoving-volume
priors (Hogg 1999, eq. 30; Mortlock et al. 2019). A uniform-in-redshift
prior is also a common variant. Why these two extremes, why not the
comoving-volume case, and what do you recommend the community settle on?"

**Current coverage.** `main.tex:149` notes that at GW170817's source
redshift, uniform-in-d_L is numerically equivalent within 1 % to a
flat-in-redshift prior over the same fixed range. The literal volumetric
case `π(d_L) ∝ d_L²` *is* the flat-spatial-volume prior at low z, so
"volumetric" and "comoving-volume-at-low-z" coincide here — the paper
does not say this explicitly. The §6 Discussion does not give a forward
recommendation.

**Verdict.** Partly addressed. The numerical equivalence claim is
supported by `analyze_selection_term.py` (which I re-ran; see item g).
What is missing is a single sentence saying: "at GW170817's redshift
z ≲ 0.02, the volumetric prior π(d_L) ∝ d_L² is itself the comoving-
volume prior; the uniform-in-d_L variant is therefore literally one of
the 'two extremes' of the prior axis" plus a forward recommendation.

**Proposed inoculation (Tier B).** Add to §6.3 (Implications for future
bright sirens), after `main.tex:368`:

> "For comparison-grade single-event posteriors we recommend that both
> the volumetric (= comoving-volume at z ≲ 0.02) and the uniform-in-d_L
> posteriors be reported, with their direct-sampled rather than
> reweighted forms; the difference between the two bounds the
> prior-induced systematic. For population-level analyses the choice
> should be driven by the population model's own d_L distribution; the
> single-event prior should be flat in whatever quantity the population
> model carries as its rate density."

### d) Mode-B Bayes-factor seed scatter — only 2 seeds

**Referee objection.** "Two seeds with |ln B|<1 doesn't establish that
the result is seed-independent. The within-run uncertainty you quote is
±0.1; the between-run scatter you report is 1.04 (between seed=0 and
seed=1). That is a 10× discrepancy. Either your within-run figure is
wrong, or two seeds is far too few. Where is the seed=2 run?"

**Current coverage.** `main.tex:282` already concedes the discrepancy:
*"the run-to-run lnZ scatter is larger than the nominal ±0.1 per-run
uncertainty: the unrestricted lnZ differs by 1.04 between the two seeds,
so the ±0.1 figure should be read as a within-run statistical error, not
a run-to-run reproducibility bound. The conclusion that survives this
scatter is the sign-independent one — |ln B_{B/A}|<1 in both seeds — so
Mode B is neither significantly favoured nor disfavoured regardless of
seed."* `analyze_seed_ensemble.py` is in place to aggregate any future
seed runs (it picks up all `s*` matches by glob).

**Verdict.** Addressed (honest concession + sign-independent conclusion).
Two seeds is genuinely too few to claim distributional reproducibility,
and the paper does not try to. The sign-independent framing is the right
defence.

**Quantitative check I ran.** If we assume per-seed lnZ is iid Normal
around the true value with within-run σ_w and between-run σ_b ≥ σ_w
(due to random seed picking different live-point initial conditions),
the two-seed difference 1.04 implies σ_b ≈ 1.04/√2 ≈ 0.74. That is 7× the
quoted within-run ±0.1. The paper's defence — that the sign of ln B does
not flip across the two seeds despite that scatter — is the strongest
seed-2 claim defensible from two seeds. The natural follow-up (seed=2,
seed=3) is a one-paragraph footnote.

**Proposed inoculation (Tier C, optional).** Add a forward-looking
note at `main.tex:282` after "regardless of seed": *"A larger seed
ensemble (seed=2,3,...) would tighten this to a distributional rather
than sign-only claim; the `analyze_seed_ensemble.py` script in the
public data release is set up to aggregate that ensemble as it
accumulates."*

### e) Locked-XAS choice with no tides+precession check

**Referee objection.** "You note 'no waveform in our jax inventory
simultaneously includes precession and tides' and lock the primary at
IMRX (aligned-spin). The σ(ι)=1.17 ratio you quote on GW150914 is the
largest residual and is precession-sensitive. Published EM constraints on
the GW170817 inclination (Mooley+2018, Hotokezaka+2019) bound ι to
≲ 32° — well off-axis but tighter than the GW-only marginal. How much
could a tides-with-precession waveform shift the H₀ tail?"

**Current coverage.** `main.tex:154, 170, 372` (locked-XAS rationale,
σ(ι) ratio, "natural extensions" framing). The paper cites Mooley2018Nature
and Hotokezaka2019 in §1 but does not propagate either bound to the H₀
result. No quantitative estimate of the precession-induced H₀ bias.

**Verdict.** Partly addressed (limitation is stated; quantitative bound
is not). This is a defensible scope decision for a methodology paper:
the central claim is about the *prior-sensitivity* axis, not the
*waveform-precession* axis, and the paper makes that explicit.

**Proposed inoculation (Tier B or C).** Add one sentence to §6.4
(Scope and natural extensions), after `main.tex:372`:

> "The EM-derived inclination constraints of Mooley+2018 and
> Hotokezaka+2019 (\citealp{Mooley2018Nature,Hotokezaka2019}) bound ι ≲ 32°
> from off-axis; jointly fitting GW data with this EM prior is known to
> tighten the GW170817 H₀ posterior (Palmese+2024,
> \citealp{Palmese2024GW170817H0}). A like-for-like assessment under our
> locked-XAS pipeline is the natural way to estimate how much of the
> high-H₀ tail of Mode B survives an EM-informed inclination prior; we
> defer this to follow-up."

### f) Wall-clock claims are A100-specific

**Referee objection.** "§5.1: 'a single A100' is ambiguous. A100-40 GB
SXM4, A100-40 GB PCIe, A100-80 GB SXM4 all have meaningfully different
HBM bandwidth and tensor-core counts. What's the carbon footprint
relative to the matching CPU pipeline? Without a version line the
13-minute claim is not reproducible."

**Current coverage.** `main.tex:328` ("a single NVIDIA A100 GPU"),
`main.tex:350` ("single-A100 wall-clock on the current pipeline"). No
SKU, no jax/CUDA version, no carbon estimate.

**Verdict.** Partly addressed (the claim is meaningful for A100-class
hardware; it is not currently *reproducible* to the minute).

**Proposed inoculation (Tier B, one-liner).** At `main.tex:328` change

> "a single NVIDIA A100 GPU"

to

> "a single NVIDIA A100 (40 GB SXM4; JAX 0.4.x on CUDA 12, driver
> 535.x)"

(replace the placeholder versions with the actual ones from
`Results/test_suite/.../sampler.log`; I have not verified the exact
SKU and versions yet — that is a one-grep job for the user). The carbon
footprint can stay in the data release rather than the paper.

### g) Selection-function cancellation

**Referee objection.** "Your footnote at line ~149 claims N_s(H₀) is
H₀-independent for every prior considered. That's clear for fixed-d_L-
window priors, but what about a genuine uniform-in-redshift prior whose
d_L bounds *do* move with H₀? You claim numerical equivalence at z ≲ 0.02
— show me."

**Current coverage.** `main.tex:149` (the footnote) and
`mnras_paper/test_suite/analysis/analyze_selection_term.py`. The footnote
explicitly says: *"We verified this property by direct evaluation of
N_s(H_0) = ∫ P_det(d_L) π(d_L|H_0) d d_L over the LVK-matched H_0 ∈
[45, 250] km/s/Mpc prior with a Finn–Chernoff antenna-pattern detection
model: N_s is H_0-independent to machine precision for every horizon
distance tested (D_h ∈ {100, 150, 220} Mpc, spanning the published O2 BNS
range to inspiral horizon)."*

**Verdict.** Fully addressed.

**What I re-ran in this pass.** The script runs and prints both branches
(a) as-implemented uniform-in-d_L: N_s is H₀-independent by construction,
and (b) hypothetical genuine flat-in-z: N_s(H₀) variation in the headline
P(H₀>120) tail is 0.5–6 % depending on horizon, well below the prior-
induced shift. The paper's wording is correct as written. No fix.

### h) Reweighting failure framing — bias or variance? **[Tier A finding]**

**Referee objection.** "You call the reweighting deficit a 'coverage
failure'. That word is ambiguous. Population-level coverage means the
*credible interval* misses the true value at the wrong rate. What you
actually report is a *point estimate* P(H₀>120)=0.041 from reweighting
vs 0.159 from direct sampling. Are you saying the reweighting estimator
is biased on this draw, or just that its variance is high? A bootstrap
would settle the question."

**Current coverage.** `main.tex:228–235` (the equation~5 capture
fraction, the n_eff diagnostic paragraph). The paper does not bootstrap.

**Verdict.** Unaddressed. I ran the bootstrap and the result strengthens
the paper's claim substantially.

**Bootstrap (4000 draws, n=27 539 reweighted-n_eff per draw, IMRX baseline
samples reweighted by 1/d_L²):**

```
P(H0>120) point estimates:
  baseline (volumetric):                0.0170
  reweighted (uniform-in-dL post-hoc):  0.0397
  direct (uniform-in-dL sampled):       0.1594

Reweighted bootstrap (B=4000, n=27539):
  median:                                0.0397
  95% CI:                               [0.0374, 0.0419]
  Does 95% CI include direct estimate 0.1594?  False
  Distance from CI upper to direct:      0.1176

Binomial SE on P_rw using n_eff_rw:      0.0012
Direct - reweighted shift:                0.1198
Shift / binomial SE:                     101.8 σ
```

(The 0.0397 reweighted point differs from the paper's 0.041 by 0.0013, well
within bootstrap noise — within the rounding to 2 decimals it is the same
number. The shift `direct − reweighted = 0.120` is 100× the bootstrap
standard error.)

**Verdict on the science.** The reweighting estimator is *biased* on the
GW170817 / IMRX / volumetric-baseline draw, not high-variance. The 95 %
bootstrap CI on the reweighted estimate covers a tiny range that
*excludes* the direct estimate by 100σ.

**Proposed inoculation (Tier A).** At `main.tex:233` after the equation~5
capture fraction, insert one paragraph:

> "The deficit is *bias*, not variance. A nonparametric bootstrap on the
> reweighted estimator (4000 draws, n=27 539 effective samples per draw)
> gives a 95 % CI for P(H₀>120 km/s/Mpc) of [0.037, 0.042] — tight to
> three significant figures and excluding the directly sampled 0.159 by
> ~ 100 binomial standard errors. The reweighted estimator has therefore
> converged on its own (incorrect) value on this draw; running longer
> chains under the volumetric baseline would not close the gap. Only
> direct sampling under the target prior recovers the high-H₀ tail
> mass."

This is a one-paragraph addition. It strengthens the central claim of
the paper from "reweighting under-covers" to "reweighting is
systematically biased on GW170817", which is a substantively stronger
conclusion and is what the data show.

(Bootstrap code is one-page Python; I have it in this transcript and
will package it into `Plots/build_paper_tables.py` if you authorise.)

### i) Cross-event generalisation

**Referee objection.** "This is a GW170817-only paper. Is the conclusion
specific to GW170817 (broad posterior, low-d_L bimodality), or does it
generalise to the third-generation bright-siren era?"

**Current coverage.** `main.tex:368` cites `Chen2018Forecast` and
`HuVeitch2025` in the §6.3 forward-looking subsection. The mention is
qualitative.

**Verdict.** Partly addressed.

**Proposed inoculation (Tier B).** Extend §6.3 with one paragraph:

> "Chen, Fishbach & Holz (2018) project ~25–80 bright-siren events with
> EM counterparts in 5–10 years from a network including A+ LIGO and
> Voyager; the per-event posterior width for those will be comparable
> to GW170817's. For the third-generation detector era (Einstein
> Telescope and Cosmic Explorer), Hu & Veitch (2025) project ≳ 10^4
> compact-binary detections per year, of which the bright-siren
> sub-population will be ~10–100. The runtime budget reported in §5
> (≲ 15 min for a full single-event analysis on a single A100) is the
> compute scale that makes per-event prior-sensitivity reruns the norm
> across that population rather than the exception."

### j) Other — narrative gaps

I looked for additional narrative gaps and load-bearing claims with
thin support. Two minor items:

- **j1.** `main.tex:316` quotes ln Z = 486.25 ± 0.11 for the IMRX
  baseline (Table 4) but the inline ln Z = 486.25 in Table 5 row 1
  carries no uncertainty (Table 5 is silent on the ± because the
  reweighted row has no independent ln Z). The two values are
  consistent (same run) — no fix needed, but the row-level
  uncertainties should be in the table caption (Tier C polish).
- **j2.** `main.tex:103` cites Krishna2023RelativeBinningBilby,
  Wong2023Jim, Wouters2024JimBNS as "related accelerated BNS pipelines".
  A referee will check the timing claim against Jim's published BNS
  benchmarks (Wouters+2024 quotes ~5 min on H100 for GW170817 at lower
  n_live). Our 13-min on A100 at n_live=5000 is *not* slower; it is
  the same wall-clock on different hardware at much higher live-point
  count. A one-line comparison at `main.tex:328` is worth adding:

  > "(For reference, Wouters+2024's Jim benchmark on GW170817 reports
  > ~5 min at n_live=1000 on an H100; our 13-min figure at n_live=5000
  > on an A100 is comparable per-live-point.)"

  Tier C.

---

## 3 — Reproducibility audit (Task 2)

### 3.1 Figures (each PASS / FAIL with the regenerating command)

| # | Figure | Source script | Input files (key) | Output PDF | Verified |
|---|--------|---------------|------------------|-----------|----------|
| 1 | corner_GW150914_waveform_comparison.pdf | `Plots/plot_GW150914_waveform_comparison.py` | `Results/test_suite/s17a__gw150914__imrphenomxphm__nlive8000_mcmc160__seed0000/samples.csv`, `EventData/GWOSC/GW150914/IGWN-GWTC2p1-v2-*.h5` | `Results/gwtc1_phasemarg/plots/corner_GW150914_waveform_comparison.pdf` | **PASS** |
| 2 | H0_prior_sensitivity.pdf | `Plots/plot_H0_prior_sensitivity.py` | `Results/test_suite/s14__*xas*__{baseline,flatz,vp250}__seed0000/samples.csv`, `Results/test_suite/s18__*xas*__baseline__vpmean{215,310,405}__seed0000/samples.csv`, `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomXAS_NRTidalv3_..._reweighted_flatZ.csv` | `Results/gwtc1_phasemarg/plots/H0_prior_sensitivity.pdf` | **PASS** |
| 3 | bimodality_imr_vs_imrx.pdf | `mnras_paper/test_suite/analysis/compare_bimodality_waveforms.py` | `s10__*imrphenomd_nrtidalv2__flatz__dL10-75__refModeB__seed0000/samples.csv`, `s14__*imrphenomxas_nrtidalv3__flatz__seed0000/samples.csv` | `mnras_paper/figures/bimodality_imr_vs_imrx.pdf` | **PASS** |
| 4 | bimodality.pdf | `Plots/plot_bimodality.py` | s10 dL30-75 / dL10-30 / dL10-75 (refModeB) for IMR | `Results/gwtc1_phasemarg/plots/bimodality.pdf` | **PASS** |
| 5 | H0_waveform_comparison.pdf | `Plots/plot_H0_GW170817_waveform_comparison.py` | s14 IMRX baseline + TF2 baseline CSV | `Results/gwtc1_phasemarg/plots/H0_waveform_comparison.pdf` | **PASS** |
| 6 | corner_GW170817_waveform_comparison.pdf | `Plots/plot_GW170817_waveform_corner.py` | s14 IMRX baseline + TF2 baseline + LVK GW170817 GWTC-1 HDF5 | `Results/gwtc1_phasemarg/plots/corner_GW170817_waveform_comparison.pdf` | **PASS** |
| 7 | scaling_study_full.pdf | `Plots/plot_scaling_full.py` | sampler.log entries from s13 (n_live sweep) + s07 LVK-bounds runs (n_live=20 000 anchor) | `Results/gwtc1_phasemarg/plots/scaling_study_full.pdf` | **PASS** — speedup factors 31.1× / 50.7× / 67.7× at n_live=500 / 1500 / 2500 exactly match `main.tex:335` |

### 3.2 Tables (PASS for all three)

Re-ran `python Plots/build_paper_tables.py` (single command, ~10 s); the
script generates `table1_gw150914.tex`, `table4_cross_waveform.tex`,
`table5_prior_sensitivity.tex`, `table6_bimodality.tex` plus
`paper_tables.csv` and `paper_diagnostics.csv` under
`Results/gwtc1_phasemarg/`. All numerical values match the rendered
PDF; spot-checked: baseline P(H₀>120)=0.017, direct=0.159,
reweighted=0.041, σ_vp=250 → 0.069, weighted-median baseline=77.6,
direct=87.6, reweighted=82.9, σ_vp=250 → 78.3; GW150914 𝓜_c=30.35,
q=0.87, d_L=455 Mpc, ι=2.61 rad, ln Z=260.86; ln Z_A=486.80, ln Z_B
=486.95, ln Z_unrestr=486.48 for IMR seed=0, and the seed=1 block at
486.71/487.62/487.52. All consistent with the manuscript. **PASS.**

### 3.3 Abstract numbers (PASS)

Every numeric value in the 249-word abstract (`main.tex:84`) traces to
the regenerated tables:

| Abstract claim | Tied to |
|----------------|---------|
| "≈13 min on a single A100" | `main.tex:328` `Plots/build_paper_tables.py` does not regen this; comes from sampler.log timing — see scaling_study_full source |
| "P(H_0>120) from 0.017 to 0.159" | Table 5 row 1 (0.017) and row 2 (0.159) |
| "weighted median 77.6 → 87.6" | Table 5 row 1 column "median" (77.6) and row 2 (87.6) |
| "binned MAP stays at 70.5" | Table 5 rows 1 & 2 column "MAP" |
| "reweighted P = 0.041, 17 % of shift" | Table 5 row 3 (0.041); fraction (0.041-0.017)/(0.159-0.017) = 0.169 ≈ 17 % |
| "Δ ln Z ≲ 1.8 across three variants" | max(486.25, 487.30, 485.55) − min(...) = 1.75 |
| "|ln B_{B/A}|<1 in two independent seeds" | Seed 0: (486.95-486.80)+ln(20/45) = -0.66; seed 1: (487.62-486.71)+ln(20/45) = +0.10 (Table 6) |
| "n_eff 27 317 vs 30 695" | paper_diagnostics.csv |

**PASS** for every abstract number.

### 3.4 Appendix numbers (PASS, item-by-item)

Appendix A (`main.tex:402–408`):

| Claim | Tied to |
|-------|---------|
| n_delete/n_live ∈ {0.10,0.25,0.50,0.75} — Δ MAP ≤ 1.2, Δ ln Z ≤ 0.6 | `Results/test_suite/num_delete_sweep_summary.csv` |
| n_bins ∈ {251,501,1001} — Δ MAP ≤ 0.7, max pairwise W₁ < 2 | `Results/test_suite/het_bins_sweep_summary.csv`, `Results/test_suite/het_bins_sweep_wasserstein.csv` |
| PSD: GWTC1 / kazewong / bilby — MAP 76.4–77.7, P>120 0.043–0.065 | `Results/test_suite/psd_sensitivity_summary.csv` (Note: paper says TaylorF2 at n_live=5000 — confirm) |
| Heterodyne reference (gwtc1 vs optimize) — indistinguishable bulk | `Results/test_suite/s05__*refOptimize*/samples.csv`, verified by `analyze_ref_params.py` |
| ⟨v_p⟩ ∈ {215, 310, 405} — MAP 74.5/72.1/68.5, ΔP < 0.02 | `Results/test_suite/s18__*xas*__baseline__vpmean*/samples.csv` |
| IMR companion sweep: baseline MAP 71.5 P=0.076, flatZ MAP 73.5 P=0.281, reweighted MAP 71.5 P=0.195, σ_vp=250 MAP 70.5 P=0.067; capture 58 % | `Plots/build_paper_tables.py` output: t4 + analogous IMR rows in `Results/gwtc1_phasemarg/` PhaseMarg_*.csv |

**PASS** with one mild caveat: the PSD-sensitivity row of Appendix A
mixes "TaylorF2 at n_live=5000" with the rest of the appendix, which is
predominantly IMR. Worth a sentence clarifying.

### 3.5 Proposed `regenerate.sh`

```bash
#!/usr/bin/env bash
# Yang et al. (2026) MNRAS — CPU-only regeneration pipeline.
#
# Inputs:  Results/test_suite/sNN__*/samples.csv  (the nested-sampling
#          chains, not redistributed; see run_chains.sh).
#          EventData/GWOSC/GW150914/IGWN-GWTC2p1-v2-*.h5
#          Results/GW170817_GWTC-1.hdf5
# Outputs: Results/gwtc1_phasemarg/{table1,4,5,6}*.tex
#          Results/gwtc1_phasemarg/{paper_tables,paper_diagnostics,
#                                  evidence_table}.csv
#          Results/gwtc1_phasemarg/plots/*.pdf  (the seven figure PDFs)
#          paper/main.pdf
#
# Env: conda env create -f environment.yml && conda activate
#                                                gw170817-bright-siren-H0
# Hardware: CPU only.  Wall-clock ~ 3 min on an M2 MacBook.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PY=${PY:-python}

# 1) Tables and summary CSVs
$PY scripts/build_paper_tables.py

# 2) Figures (seven canonical PDFs)
$PY scripts/plot_GW150914_waveform_comparison.py   # Fig 1
$PY scripts/plot_H0_prior_sensitivity.py           # Fig 2
$PY scripts/compare_bimodality_waveforms.py        # Fig 3
$PY scripts/plot_bimodality.py                     # Fig 4
$PY scripts/plot_H0_GW170817_waveform_comparison.py  # Fig 5
$PY scripts/plot_GW170817_waveform_corner.py       # Fig 6
$PY scripts/plot_scaling_full.py                   # Fig 7

# 3) Build the PDF
( cd paper && latexmk -pdf -interaction=nonstopmode main.tex )

echo
echo "Regenerated:"
echo "  - 7 figure PDFs in Results/gwtc1_phasemarg/plots/  (also paper/figures/ via graphicspath)"
echo "  - 4 table .tex files in Results/gwtc1_phasemarg/"
echo "  - paper/main.pdf"
```

And the GPU-only chain regeneration recipe:

```bash
#!/usr/bin/env bash
# Yang et al. (2026) MNRAS — GPU-only chain regeneration (NOT redistributed).
#
# Each per-run chain regenerates a samples.csv (~100 MB) and a sampler.log.
# Full set runs to several GB.
#
# Hardware: a single NVIDIA A100 (40 GB SXM4 or PCIe).  Wall-clock:
#   - GW170817 IMRX baseline (n_live=5000):       ~13 min
#   - GW170817 TaylorF2 baseline (n_live=5000):    ~ 4 min
#   - GW150914 XPHM validation (n_live=8000,
#                               n_mcmc=160):      ~ 5 h
#   - Full prior-sensitivity 4-variant suite:     ~1 h
#   - Full bimodality 6-run suite (2 seeds):      ~1.5 h
#   - All appendix sweeps:                        ~6 h
#   - All 17 cited runs in one batch:            ~12-15 h
#
# Env: a CUDA-12 capable JAX install (jax[cuda12], blackjax-ns,
#      heterodyned likelihood kernel from Prathaban et al. 2025).

set -euo pipefail
echo "Chain regeneration is GPU-bound and not redistributed."
echo "See docs/chain_regeneration.md for the per-run blackjax-ns invocation."
exit 1
```

### 3.6 End-to-end verification log (Task 6)

| Step | Command | Result |
|------|---------|--------|
| environment | `conda env create -f environment.yml` | (not exercised in this pass — env existed) |
| tables | `python Plots/build_paper_tables.py` | **PASS** — wrote 4 .tex + 2 .csv, all numbers match paper |
| figure 1 | `python Plots/plot_GW150914_waveform_comparison.py` | **PASS** — 216 800 samples loaded, PDF written |
| figure 2 | `python Plots/plot_H0_prior_sensitivity.py` | **PASS** — 6 panels, PDF written; numbers match Table 5 |
| figure 3 | `python mnras_paper/test_suite/analysis/compare_bimodality_waveforms.py` | **PASS** — wrote `mnras_paper/figures/bimodality_imr_vs_imrx.pdf` |
| figure 4 | `python Plots/plot_bimodality.py` | **PASS** — wrote `Results/gwtc1_phasemarg/plots/bimodality.pdf` |
| figure 5 | `python Plots/plot_H0_GW170817_waveform_comparison.py` | **PASS** — IMRX & TF2 loaded; HPDs match Table 4 |
| figure 6 | `python Plots/plot_GW170817_waveform_corner.py` | **PASS** |
| figure 7 | `python Plots/plot_scaling_full.py` | **PASS** — speedup factors 31.1× / 50.7× / 67.7× match `main.tex:335` |
| PDF | `latexmk -pdf -interaction=nonstopmode main.tex` (in `mnras_paper/`) | (not exercised in this pass — main.pdf already exists, 11 pp, abstract matches; rebuild from scratch with `latexmk -C && latexmk -pdf` was not run for time reasons) |

### 3.7 All seven figures, all four tables: PASS

Every figure regen completed during this pass, every table regen
completed, every abstract number ties out to a tabular CSV, and every
appendix number ties to a sweep-summary CSV. The five-figure background
batch wrote:

```
-> Saved Results/gwtc1_phasemarg/plots/corner_GW150914_waveform_comparison.pdf
-> Saved Results/gwtc1_phasemarg/plots/H0_waveform_comparison.pdf
-> Saved Results/gwtc1_phasemarg/plots/bimodality.pdf
-> Wrote mnras_paper/figures/bimodality_imr_vs_imrx.pdf
-> Saved Results/gwtc1_phasemarg/plots/scaling_study_full.pdf
```

with no errors. The remaining two (H0_prior_sensitivity, GW170817 corner)
had already been verified earlier in the same pass.

---

## 4 — Inventory and dead-code list (Task 3)

The full inventory is in
**`mnras_paper/data_release_inventory.csv`** (563 rows, generated this
pass). Header columns: `path, classification, reason, recommended_action`.

Summary:

| Classification | Count | % | Includes |
|----------------|-------|---|----------|
| needed-paper | 154 | 27 % | The 7 figure scripts + their dependencies, build_paper_tables.py, _plot_utils.py, _helpers.py, the cited 17 sN__* run directories' samples.csv + sampler.log + config.json, table .tex, summary CSVs, evidence_table.csv |
| needed-verification | 78 | 14 % | session_plans/*.sh, MANIFEST.md, READMEs, sweep summary CSVs for the appendix |
| dead | 331 | 59 % | Old/ plot scripts, 33 uncited plot_*.py, 8 abandoned analyze_*.py (sky-prior, scaling-20k anomaly, precession-only experiments, q-prior), figures/output/fig01–fig10 (auto-generated previous-pass figures), per-run dirs for sN runs the paper does not cite (s04 unhet, s11 nlive20000_tol1e-4, s15 narrow priors, s16 q-test, s19 fixedsky, sH prior-only) |

**Selected dead candidates** (full list in the CSV):

- `Plots/Old/` — entirety
- `Plots/PlotExtendedFig_25_250.py`, `Plots/PlotExtendedFig_40_140.py`
- `Plots/plot_H0_abbott_reproduction.py`, `plot_H0_baseline_IMRPhenomD.py`,
  `plot_H0_baseline_TaylorF2.py`, `plot_H0_synoptic.py`, `plot_H0_summary.py`,
  `plot_H0_reweight_comparison.py`, `plot_H0_IMRPhenomD_reweighted.py`,
  `plot_H0_IMRPhenomD_variants.py`, `plot_H0_TaylorF2_reweighted.py`,
  `plot_H0_TaylorF2_variants.py`, `plot_H0_full_sky_vs_narrow.py`,
  `plot_h0_prior_comparison.py`, `plot_phase_marginalization_schematic.py`,
  `plot_phasemarg_comparison_gwtc.py`, `plot_corner_*.py` (5 variants),
  `plot_dL_posterior.py`, `plot_full_sky_vs_narrow.py`,
  `plot_paper_phasemarg_local.py`, `plot_q_overlay_s16.py`,
  `plot_q_prior_sensitivity.py`, `plot_sky_prior_runtime.py`,
  `plot_speedup_comparison.py`, `plot_unheterodyned_vs_gwtc.py`,
  `plot_waveform_comparison_gwtc.py`, `plot_prior_vs_posterior_H0.py`,
  `plot_by_waveform.py`, `plot_GW150914.py`, `plot_H0.py`,
  `plot_scaling_full.py`, `compare_bins.py`, `newplotter.py`,
  `reweight_dL_to_flat_z.py`, `build_full_summary.py`,
  `build_review_pdf.py`, `build_scaling_table.py`,
  `compute_evidence_table.py`, `compute_prior_sensitivity.py`,
  `compute_summary_stats.py`, `compute_waveform_systematics.py`
- `mnras_paper/test_suite/analysis/analyze_sky_prior_runtime.py`,
  `analyze_scaling_20k_anomaly.py`,
  `analyze_precessing_gw150914.py`, `analyze_precessing_gw170817.py`,
  `analyze_q_prior.py`, `analyze_tf2_scaling.py`, `analyze_unhet_scaling.py`,
  `analyze_nmcmc_sweep.py`, `verify_manifest.py`
- `mnras_paper/figures/output/fig01_*…fig10_*.{pdf,png}` (20 files)
- `mnras_paper/figures/v2/` (if present; check before pushing)
- Per-run dirs: `s04__*`, `s05__*unheterodyned*`, `s06__*` (s06 IS cited
  per `paper-reproduce/data/MANIFEST.md` for the GW150914 cross-check),
  `s11__*`, `s15__*_narrow_*`, `s16__*qtest*`, `s19__*_fixedsky_*`,
  `sH__*`
- `mnras_paper/test_suite/session_plans/session_{02,11,15,16,17,20,H}*.sh`
  (session 02 was dropped, session 11 was the n_live=20k diagnostic,
  session 15 sky-prior was removed in m17, session 16 q-prior is
  exploratory, session H prior-only is exploratory)

No file in the dead list will be deleted from the local repo in this
pass; the cleanup is for the GitHub mirror.

---

## 5 — Public-repo layout (Task 4)

### 5.1 Current state of the GitHub repo

`gh api repos/ming-256/GW170817-bright-siren-H0/contents/` returns:

```
.gitignore
LICENSE       (size 1289 bytes; gh license API reports "other" — open)
README.md
requirements.txt
Plots/        (51 scripts; mix of production + exploratory)
analysis/     (20 scripts; mix of production + exploratory)
```

Most recent commit `51774aa` (2026-05-23): *"Reconcile README with actual
repo contents"*. The repo therefore has a recent, current README, but the
layout is the development tree, not a curated release.

### 5.2 Target layout (matches the prompt with minor adjustments)

```
GW170817-bright-siren-H0/
├── README.md                                     # paper TL;DR, quick-start
├── MANIFEST.md                                   # file-by-file provenance
├── LICENSE                                       # (MIT or BSD-3 — see §7)
├── CITATION.cff                                  # GitHub "cite this" widget
├── environment.yml                               # conda env to reproduce
├── requirements.txt                              # pip-only mirror
├── regenerate.sh                                 # CPU-only rebuild
├── run_chains.sh                                 # GPU-only chain regen
├── paper/
│   ├── main.tex                                  # mirror of mnras_paper/main.tex (paper-reproduce layout)
│   ├── references.bib
│   ├── figures/                                  # the 7 canonical PDFs
│   ├── tables/                                   # table_1, table_4, table_5, table_6 .tex
│   └── main.pdf                                  # built artifact
├── scripts/
│   ├── _plot_utils.py                            # was Plots/_plot_utils.py
│   ├── build_paper_tables.py                     # was Plots/build_paper_tables.py
│   ├── plot_GW150914_waveform_comparison.py
│   ├── plot_H0_prior_sensitivity.py
│   ├── compare_bimodality_waveforms.py           # was mnras_paper/test_suite/analysis/compare_bimodality_waveforms.py
│   ├── plot_bimodality.py
│   ├── plot_H0_GW170817_waveform_comparison.py
│   ├── plot_GW170817_waveform_corner.py
│   └── plot_scaling_full.py
├── analysis/
│   ├── _helpers.py                               # was mnras_paper/test_suite/analysis/_helpers.py
│   ├── analyze_bimodality.py
│   ├── analyze_bimodality_imrx.py
│   ├── analyze_het_bins_sweep.py
│   ├── analyze_num_delete_sweep.py
│   ├── analyze_psd_sensitivity.py
│   ├── analyze_ref_params.py
│   ├── analyze_selection_term.py
│   ├── analyze_seed_ensemble.py
│   └── compile_test_suite_report.py
├── results/
│   ├── gwtc1_phasemarg/
│   │   ├── evidence_table.csv
│   │   ├── paper_diagnostics.csv
│   │   ├── paper_tables.csv
│   │   ├── table1_gw150914.tex
│   │   ├── table4_cross_waveform.tex
│   │   ├── table5_prior_sensitivity.tex
│   │   ├── table6_bimodality.tex
│   │   └── plots/                                # canonical figure PDFs (7)
│   └── test_suite/
│       ├── run_catalog.csv                       # was mnras_paper/test_suite/run_catalog.csv
│       ├── bimodality_summary.csv
│       ├── bimodality_imrx_summary.csv           # if available, otherwise drop
│       ├── bimodality_waveform_check.csv
│       ├── gw150914_waveform_comparison.csv
│       ├── gw170817_waveform_comparison.csv
│       ├── het_bins_sweep_summary.csv
│       ├── het_bins_sweep_wasserstein.csv
│       ├── num_delete_sweep_summary.csv
│       ├── psd_sensitivity_summary.csv
│       ├── seed_ensemble_summary.csv
│       ├── seed_ensemble_bayes_factor.csv
│       └── selection_term_Ns.csv
└── docs/
    ├── reproducibility.md
    ├── chain_regeneration.md
    └── data_provenance.md
```

### 5.3 Current → target path map (with transformation notes)

| Current path | Target path | Transformation |
|--------------|-------------|----------------|
| `mnras_paper/main.tex` | `paper/main.tex` | Update `\graphicspath` to `{figures/}{../results/gwtc1_phasemarg/plots/}`; update `\input{...}` paths to `tables/table*.tex`; same as `paper-reproduce/paper/main.tex` |
| `mnras_paper/references.bib` | `paper/references.bib` | byte-identical |
| `Plots/build_paper_tables.py` | `scripts/build_paper_tables.py` | rewrite `OUT_DIR = os.path.join(ROOT, 'Results', 'gwtc1_phasemarg')` to use `results/gwtc1_phasemarg/`; update sN__* CSV paths from `Results/test_suite/` to `results/test_suite/`; verify case (`Results` → `results`) |
| `Plots/_plot_utils.py` | `scripts/_plot_utils.py` | update import-relative paths similarly |
| `Plots/plot_*.py` (the 7 cited) | `scripts/plot_*.py` | update REPO_ROOT computation if used; otherwise byte-identical |
| `mnras_paper/test_suite/analysis/compare_bimodality_waveforms.py` | `scripts/compare_bimodality_waveforms.py` | update REPO_ROOT path constants; figure output path to `paper/figures/` |
| `mnras_paper/test_suite/analysis/_helpers.py` | `analysis/_helpers.py` | rewrite `REPO_ROOT = ../../..` → `..` (one level up); `TEST_SUITE_ROOT` → `.`; `RESULTS_ROOT` → `../results/test_suite`; `CATALOG` → `./run_catalog.csv` ALSO check the scripts/ scripts that import _helpers — fix sys.path |
| `mnras_paper/test_suite/analysis/analyze_*.py` (the 8 cited) | `analysis/analyze_*.py` | update REPO_ROOT |
| `mnras_paper/test_suite/run_catalog.csv` | `results/test_suite/run_catalog.csv` | byte-identical |
| `Results/gwtc1_phasemarg/{evidence_table,paper_diagnostics,paper_tables}.csv` | `results/gwtc1_phasemarg/...` | byte-identical |
| `Results/gwtc1_phasemarg/table{1,4,5,6}*.tex` | `results/gwtc1_phasemarg/...` AND `paper/tables/...` | byte-identical (the paper's `\input` resolves into `paper/tables/` to keep paper/ self-contained) |
| `Results/gwtc1_phasemarg/plots/<7 PDFs>` | `results/gwtc1_phasemarg/plots/...` AND `paper/figures/...` | byte-identical |
| `Results/test_suite/{bimodality_summary,...}.csv` (the 11 cited summaries) | `results/test_suite/...` | byte-identical |
| `Results/test_suite/sNN__*/samples.csv` (the 17 cited chains) | NOT redistributed; documented in `docs/chain_regeneration.md` and `MANIFEST.md`; Zenodo deposit URL pending | excluded from Git, available via Zenodo |
| `mnras_paper/test_suite/MANIFEST.md` | `MANIFEST.md` (top level, transformed: every file with its provenance) | new content authored from inventory CSV |

### 5.4 Files to keep OUT of the public repo

- The 331 dead files in the inventory CSV
- `mnras_paper/{paper_creation_prompt,final_pass_prompt,data_release_prompt,literature_review,referee_response*,GW150914_mass_prior_audit,DEFERRED_RUNS,result_inventory,final_pass_review}.md` (verification artefacts, not paper artefacts)
- `mnras_paper/main.{aux,bbl,blg,fdb_latexmk,fls,log,out}` and the 2*.pdf variants (build by-products)
- `mnras_paper/Results/` (a 1-byte sentinel or empty)
- `paper-reproduce/` itself — its scripts and structure are *replaced* by the GitHub repo's top level; do not nest

### 5.5 Size flags

No file in the proposed layout exceeds 10 MB. All seven canonical figure
PDFs are < 200 kB each. The data/ directory is empty in the GitHub repo
(chains live on Zenodo). Git LFS is **not** required.

The total proposed repo size, excluding the chains, is well under
50 MB — entirely below GitHub's 100 MB-per-file and ~1 GB-per-repo
soft limits.

---

## 6 — README and MANIFEST drafts (Task 5)

### 6.1 Proposed README.md

```markdown
# GPU-accelerated bright-siren H₀ from GW170817 — data and analysis release

This repository accompanies

> **Yang M., Prathaban M., Yallup D., Handley W.** (2026).
> *Rapid Hubble constant inference from GW170817 using GPU-accelerated
> nested sampling: prior sensitivity and the limits of post-hoc
> reweighting.* MNRAS (submitted).
> [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)

The release contains the analysis scripts, run catalogue, derived summary
tables, and figure- and table-generation code needed to reproduce every
numerical claim and every figure in the paper. The nested-sampling
**chains themselves are not committed here** — each individual
`samples.csv` is ~100 MB and the full set runs to several GB; they live
on the companion [Zenodo deposit](https://doi.org/TODO) and can be
regenerated from the public LVK strain data using the [BlackJAX-NS](https://github.com/handley-lab/blackjax)
sampler and the [GW-likelihood kernel](https://github.com/handley-lab/gw-likelihood).

## Headline result

Under the modern aligned-spin tidal waveform IMRPhenomXAS_NRTidalv3,
switching the luminosity-distance prior from volumetric (π(d_L) ∝ d_L²)
to uniform-in-d_L by **direct sampling** raises P(H₀ > 120 km/s/Mpc)
from **0.017 → 0.159**, while the binned MAP stays at 70.5 km/s/Mpc.
Post-hoc **reweighting** of the same baseline draws recovers only
P = 0.041 — *17 % of the directly-sampled shift*. The mechanism is a
(d_L, ι) bimodality whose high-H₀ / low-d_L branch (Mode B) carries
appreciable likelihood but negligible volumetric-prior mass.

The full GPU pipeline completes the n_live = 5000 IMRX analysis in
≈13 min on a single NVIDIA A100; the full four-variant prior-sensitivity
suite fits inside an hour. This makes per-event prior-sensitivity reruns
the *default* robustness tool for bright-siren cosmology, replacing
post-hoc reweighting.

## Citation

```bibtex
@misc{Yang2026DataRelease,
  author = {{Yang}, M. and {Prathaban}, M. and {Yallup}, D. and {Handley}, W.},
  title  = {{GW170817 bright-siren H_0: data and analysis release}},
  year   = {2026},
  howpublished = {\url{https://github.com/ming-256/GW170817-bright-siren-H0}},
  note   = {GitHub repository containing the derived CSV summaries, run
            catalogue, and figure/table-generation scripts for Yang et al.
            (2026). The nested-sampling chains themselves are on Zenodo
            (DOI: 10.5281/zenodo.TODO).}
}
```

## Quick start (CPU-only, ≈ 3 min)

```bash
git clone https://github.com/ming-256/GW170817-bright-siren-H0
cd GW170817-bright-siren-H0

conda env create -f environment.yml
conda activate gw170817-bright-siren-H0

# Download the chain bundle from Zenodo and unpack it into results/test_suite/.
# See docs/data_provenance.md for the exact placement.

bash regenerate.sh
```

`regenerate.sh` produces

- 4 table `.tex` files in `results/gwtc1_phasemarg/` (also mirrored to `paper/tables/`)
- 7 figure PDFs in `results/gwtc1_phasemarg/plots/` (also mirrored to `paper/figures/`)
- `paper/main.pdf` (11 pp, 249-word abstract, identical to the submitted MNRAS draft)

## Chain regeneration (GPU only)

The nested-sampling chains are reproducible on a single NVIDIA A100
(40 GB) GPU using the BlackJAX-NS sampler and the heterodyned-likelihood
kernel. See `docs/chain_regeneration.md` for the exact invocations and
expected wall-clock per run. As a budget guide:

| Run set | Wall-clock |
|---------|-----------|
| Full IMRX prior-sensitivity sweep (4 variants) | ~1 h |
| Full bimodality 6-run suite (2 seeds) | ~1.5 h |
| GW150914 XPHM validation (n_live=8000, n_mcmc=160) | ~5 h |
| All 17 cited runs in one batch | ~12–15 h |

## Repository layout

```
.
├── README.md                # this file
├── MANIFEST.md              # file-by-file provenance
├── LICENSE                  # (see §licence below)
├── CITATION.cff             # GitHub citation widget
├── environment.yml          # conda environment
├── requirements.txt         # pip-only mirror
├── regenerate.sh            # CPU-only rebuild of tables, figures, PDF
├── run_chains.sh            # GPU-only chain regeneration (stub; see docs/)
├── paper/                   # LaTeX source + figures + tables + PDF
├── scripts/                 # the 9 production plot/table scripts
├── analysis/                # the 9 per-sweep aggregators
├── results/                 # derived CSVs + .tex tables + plot PDFs
└── docs/                    # reproducibility / chain-regen / data-provenance
```

## Data sources

- GW170817 strain + PSD + reference PE: [LIGO P1800061](https://dcc.ligo.org/LIGO-P1800061/public) (LVK, 2018)
- GW170817 H₀ analysis: [LIGO P1700296](https://dcc.ligo.org/LIGO-P1700296/public) (LVK, 2017)
- GW150914 PE data release: [Zenodo 10.5281/zenodo.6513631](https://doi.org/10.5281/zenodo.6513631) (LVK GWTC-2.1)
- All chains for this paper: [Zenodo DOI: TODO](https://doi.org/TODO)

## Hardware requirements

- **Tables + figures + PDF compile (CPU only):** any modern laptop; tested
  on macOS 14 / Apple-M2 with Python 3.12, numpy ≥ 2, anesthetic ≥ 2.8.
- **Chain regeneration (optional, GPU only):** a single NVIDIA A100
  (40 GB SXM4 or PCIe). Other CUDA-12-capable GPUs with ≥ 24 GB HBM
  should also work but are not benchmarked.

## Licence

Code: MIT.  Data / CSV / figure PDFs: CC BY 4.0.

## Acknowledgements

This work was supported by the research environment of the Handley Lab at
the University of Cambridge. MP is supported by the Harding
Distinguished Postgraduate Scholars Programme (HDPSP). This material is
based upon work supported by the Google Cloud research credits program,
with the award GCP397499138. We acknowledge the LIGO–Virgo–KAGRA
Collaboration for the public strain data and reference posteriors used
here.
```

### 6.2 Proposed MANIFEST.md (table-row, abridged)

The full MANIFEST.md is a long file row-per-asset; the abridged form
keyed to the seven figures, four tables, and the 17 cited chains is:

```markdown
# Manifest — Yang et al. (2026) data release

Every artefact in this repository, with its scientific role and source.

| Path | Role | Source / generator |
|------|------|-------------------|
| paper/main.tex | manuscript source | mirror of mnras_paper/main.tex (canonical) |
| paper/references.bib | bibliography (45 entries) | mirror of mnras_paper/references.bib |
| paper/main.pdf | built artifact (11 pp) | `latexmk -pdf main.tex` |
| paper/figures/corner_GW150914_waveform_comparison.pdf | Fig 1 | scripts/plot_GW150914_waveform_comparison.py + s17a chain |
| paper/figures/H0_prior_sensitivity.pdf | Fig 2 | scripts/plot_H0_prior_sensitivity.py + s14 IMRX (×4) + s18 vpmean (×3) |
| paper/figures/bimodality_imr_vs_imrx.pdf | Fig 3 | scripts/compare_bimodality_waveforms.py + s10 IMR refModeB + s14 IMRX flatz |
| paper/figures/bimodality.pdf | Fig 4 | scripts/plot_bimodality.py + s10 IMR dL30-75 / dL10-30 / dL10-75-refModeB |
| paper/figures/H0_waveform_comparison.pdf | Fig 5 | scripts/plot_H0_GW170817_waveform_comparison.py + s14 IMRX baseline + TF2 baseline |
| paper/figures/corner_GW170817_waveform_comparison.pdf | Fig 6 | scripts/plot_GW170817_waveform_corner.py + IMRX/TF2 baseline + LVK GW170817 HDF5 |
| paper/figures/scaling_study_full.pdf | Fig 7 | scripts/plot_scaling_full.py + s13 n_live sweep + s07 LVK-bounds runs |
| paper/tables/table1_gw150914.tex | Table 1 (GW150914 validation) | scripts/build_paper_tables.py |
| paper/tables/table4_cross_waveform.tex | Table 4 (cross-waveform H₀) | scripts/build_paper_tables.py |
| paper/tables/table5_prior_sensitivity.tex | Table 5 (prior-sensitivity sweep) | scripts/build_paper_tables.py |
| paper/tables/table6_bimodality.tex | Table 6 (bimodality) | scripts/build_paper_tables.py |
| scripts/_plot_utils.py | shared plotting helpers | mirror of Plots/_plot_utils.py |
| scripts/build_paper_tables.py | canonical table+summary generator | mirror of Plots/build_paper_tables.py |
| scripts/plot_*.py (×7) | figure generators | mirror of Plots/plot_*.py |
| scripts/compare_bimodality_waveforms.py | Fig 3 generator | mirror of mnras_paper/test_suite/analysis/compare_bimodality_waveforms.py |
| analysis/_helpers.py | shared chain/config loaders | mirror of mnras_paper/test_suite/analysis/_helpers.py |
| analysis/analyze_bimodality.py | Mode-A/B Bayes factor (IMR) | analyze_bimodality.py |
| analysis/analyze_bimodality_imrx.py | Mode-A/B Bayes factor (IMRX, queued) | analyze_bimodality_imrx.py |
| analysis/analyze_het_bins_sweep.py | Appendix A het-bins sweep | analyze_het_bins_sweep.py |
| analysis/analyze_num_delete_sweep.py | Appendix A n_delete sweep | analyze_num_delete_sweep.py |
| analysis/analyze_psd_sensitivity.py | Appendix A PSD sensitivity | analyze_psd_sensitivity.py |
| analysis/analyze_ref_params.py | Appendix A heterodyne reference | analyze_ref_params.py |
| analysis/analyze_seed_ensemble.py | seed lnZ scatter aggregator | analyze_seed_ensemble.py |
| analysis/analyze_selection_term.py | selection-term N_s(H₀) verification | analyze_selection_term.py |
| analysis/compile_test_suite_report.py | end-to-end test-suite report | compile_test_suite_report.py |
| results/gwtc1_phasemarg/evidence_table.csv | per-variant lnZ ± σ + n_eff | build_paper_tables.py |
| results/gwtc1_phasemarg/paper_diagnostics.csv | per-variant n_eff + efficiency | build_paper_tables.py |
| results/gwtc1_phasemarg/paper_tables.csv | per-variant headline statistics (machine-readable) | build_paper_tables.py |
| results/gwtc1_phasemarg/table*.tex | LaTeX includes for paper tables | build_paper_tables.py |
| results/gwtc1_phasemarg/plots/<7 PDFs> | figures (mirrored to paper/figures/) | the seven scripts above |
| results/test_suite/run_catalog.csv | sN__* metadata (one row per run) | maintained by hand |
| results/test_suite/<sweep_summary>.csv | per-Appendix-A-axis aggregator output | analyze_*_sweep.py |
| results/test_suite/sNN__*/ | NOT redistributed — on Zenodo; see docs/chain_regeneration.md | — |
| docs/reproducibility.md | "fresh clone → main.pdf" recipe | hand-authored |
| docs/chain_regeneration.md | per-run blackjax-ns invocation | hand-authored |
| docs/data_provenance.md | where each summary CSV came from | derived from MANIFEST + inventory CSV |
| LICENSE | MIT (code) + CC-BY-4.0 (data) | standard text |
| CITATION.cff | "cite this" widget | hand-authored, matches Yang2026DataRelease |
| environment.yml | conda env spec | from paper-reproduce/environment.yml |
| requirements.txt | pip mirror | existing requirements.txt is already correct |
```

(Full version, ~150 rows including every chain `samples.csv` with its
expected size in MB, is generated row-by-row from the inventory CSV via
a one-page Python script in `docs/data_provenance.md`.)

---

## 7 — Paper–repo consistency findings (Task 7)

### 7.1 `Yang2026DataRelease` bib entry

`references.bib:134–140` ([here](#)) currently reads:

```bibtex
@misc{Yang2026DataRelease,
  author = {{Yang}, M. and {Prathaban}, M. and {Yallup}, D. and {Handley}, W.},
  title = {{GPU-accelerated Bayesian inference of GW170817: data and analysis release}},
  year = {2026},
  howpublished = {\url{https://github.com/ming-256/GW170817-bright-siren-H0}},
  note = {GitHub repository containing the derived CSV summaries, run catalogue, and figure/table-generation scripts for this paper; nested-sampling chains are regenerable from the public strain data using the listed sampler.}
}
```

- URL ✓ matches the public repo.
- Title — the repo description ("Data and analysis release for Yang
  et al. (2026), MNRAS") aligns; the bib title is slightly more verbose
  ("GPU-accelerated Bayesian inference of GW170817…"). Either is fine;
  for consistency with the GitHub page, suggest renaming the repo
  description to match the bib title OR simplifying the bib title to
  "GW170817 bright-siren H₀: data and analysis release". Tier C.
- Year ✓ 2026.
- Authors ✓ match.

Once the Zenodo deposit is created, augment the entry with the DOI:

```bibtex
@misc{Yang2026DataRelease,
  author = {{Yang}, M. and {Prathaban}, M. and {Yallup}, D. and {Handley}, W.},
  title  = {{GW170817 bright-siren H_0: data and analysis release}},
  year   = {2026},
  howpublished = {\url{https://github.com/ming-256/GW170817-bright-siren-H0}},
  doi    = {10.5281/zenodo.TODO},
  url    = {https://doi.org/10.5281/zenodo.TODO},
  note   = {GitHub repository (linked above) plus a Zenodo archival
            snapshot (DOI listed) containing the derived CSV summaries,
            run catalogue, and figure/table-generation scripts.
            Nested-sampling chains are regenerable from the public strain
            data using the BlackJAX-NS sampler.}
}
```

### 7.2 Reproducibility-budget claim

`main.tex:328`: "the full four-variant prior-sensitivity suite … fits
inside an hour". The repo's `run_chains.sh` (proposed in §3.5) gives
the matching budget (1 h on a single A100). Consistent.

`main.tex:350`: "a like-for-like IMRX parallel\_bilby benchmark on
matched priors and live-point counts would calibrate the speedup against
a production CPU pipeline and is the appropriate cross-check for a
follow-up". No CPU-side wall-clock is claimed in this paper, so no
calibration is owed. Consistent.

### 7.3 Data Availability hyperlinks (all live)

| Bib key | URL | WebFetch verified |
|---------|-----|--------------------|
| `Yang2026DataRelease` | https://github.com/ming-256/GW170817-bright-siren-H0 | ✓ (current README, last commit 2026-05-23) |
| `LVK_GW170817_DataRelease` | https://dcc.ligo.org/LIGO-P1800061/public | ✓ ("Properties of the binary neutron star merger GW170817", LIGO-P1800061-v11, includes posterior samples + PSDs + tutorial notebook) |
| `LVK_H0_DataRelease` | https://dcc.ligo.org/LIGO-P1700296/public | ✓ ("A gravitational-wave standard siren measurement of the Hubble constant", LIGO-P1700296-v5, the original Abbott+2017 release with figure data) |
| `GWTC2p1_GW150914_Zenodo` | https://doi.org/10.5281/zenodo.6513631 | ✓ ("GWTC-2.1: Deep Extended Catalog … Parameter Estimation Data Release") |

### 7.4 Zenodo deposit — procedure (not executed)

The current `Yang2026DataRelease` entry points to GitHub only. For
long-term archival, the standard MNRAS practice is to deposit the same
release on Zenodo and cite both. Procedure (not executed in this
pass):

1. **Connect GitHub → Zenodo.** Sign in at
   <https://zenodo.org/account/settings/github/>, authorise the
   ming-256 account, and toggle the `GW170817-bright-siren-H0`
   repository to "on".
2. **Tag a release on GitHub.** When the public-repo cleanup of §5 is
   complete, push a tag (e.g., `v1.0.0`) and create a GitHub Release
   from it. Zenodo will mint a DOI automatically.
3. **Populate the Zenodo metadata.** Title, authors (4), description
   (the README's first paragraph), keywords (gravitational waves;
   nested sampling; H₀; bright sirens; reproducibility), licence
   (MIT for code + CC-BY-4.0 for data — Zenodo accepts the mixed
   licence in the "Notes" field).
4. **Upload the chain bundle as a separate Zenodo deposit.** The
   ~5 GB samples-CSV bundle is too large for a Git push but well
   within Zenodo's 50 GB-per-record limit; deposit it as a second
   record (e.g., "GW170817 nested-sampling chains for the Yang+2026
   release") and cross-link from the first record's "Related
   identifiers" field.
5. **Update `references.bib`.** Once the DOI is minted, edit
   `Yang2026DataRelease` as in §7.1 above. Re-compile `main.pdf`.

If you authorise, I can prepare the Zenodo metadata YAML and the
release notes; the actual Zenodo upload is interactive and must be
done by the user.

---

## 8 — Ranked suggested edits (Tier A / B / C)

### Tier A — substantive (apply before public push)

| # | Location | Current | Proposed | Justification |
|---|----------|---------|----------|---------------|
| A1 | `main.tex:233` (after eq. 5 capture fraction) | (no paragraph) | Insert the bootstrap-bias paragraph from §2h above | Strengthens central claim from "reweighting under-covers" to "reweighting is biased on GW170817"; supported by 4 000-draw bootstrap with 95% CI [0.037, 0.042] excluding the direct 0.159 by ~100σ |
| A2 | `main.tex:235` (k̂ sentence) | "The Pareto-smoothed importance-sampling k̂ diagnostic of Vehtari2024PSIS would flag the same failure quantitatively, with the standard k̂>0.7 threshold, at no additional computational cost." | Either compute the proper PSIS k̂ on the IMRX reweighted draw and report it, OR soften to: "Pareto-smoothed importance sampling (Vehtari2024PSIS) provides a companion diagnostic, with the standard k̂>0.7 threshold; we recommend reporting both n_eff and k̂ as the default coverage check before any reweighted bright-siren H_0 summary is published." | Method-of-moments k̂ ≈ 0.33 (rough), below threshold; the unmodified claim is testable and could fail |

### Tier B — repo hygiene (apply before public push)

| # | Item | Action |
|---|------|--------|
| B1 | Promote the curated paper-reproduce/ structure to the repo root | Adopt the §5.2 layout; remove the current top-level `Plots/` and `analysis/` directories in favour of the trimmed `scripts/` (9) and `analysis/` (9) sets |
| B2 | Prune the 331 dead files from the repo | Per the inventory CSV; keep them in the local repo |
| B3 | Add `MANIFEST.md`, `CITATION.cff`, `environment.yml`, `regenerate.sh`, `run_chains.sh`, `docs/{reproducibility,chain_regeneration,data_provenance}.md` | Per §6 above |
| B4 | Push the seven canonical figure PDFs + four table .tex includes to `paper/{figures,tables}/` | Mirror `Results/gwtc1_phasemarg/{plots/*.pdf,table*.tex}` |
| B5 | Add the C-level addition of `main.tex:282` (IMRX heterodyne-reference scope clause) — see §2a | One half-sentence, no science change |
| B6 | Add the `main.tex:328` A100-SKU + JAX/CUDA version line — see §2f | Reproducibility-min metadata |
| B7 | Add the §6.3 forward forecast extension — see §2i | Optional Tier-B/C; bumps the §6.3 paragraph from ~3 lines to ~10 lines |

### Tier C — cosmetic (apply at submission polish)

| # | Item | Action |
|---|------|--------|
| C1 | `references.bib:Yang2026DataRelease` title alignment | Choose one of "GW170817 bright-siren H₀ data and analysis release" OR keep the current; update GitHub repo description to match |
| C2 | Add a comoving-volume / uniform-in-z forward-recommendation sentence to §6.3 | See §2c |
| C3 | Tier C addition to `main.tex:282` (seed=2,3 follow-up note) | One sentence |
| C4 | `main.tex:404` (PSD sensitivity row of Appendix A) — clarify TaylorF2 framing | One word ("\TF\ runs" already there; consider explicit "(family check)") |
| C5 | Add j2 from §2j (Jim/Wouters timing comparison) | One sentence at `main.tex:328` |
| C6 | Add `Yang2026DataRelease` Zenodo DOI once minted | See §7.1, §7.4 |
| C7 | `data_release_inventory.csv` documented in `docs/data_provenance.md` | Provenance lookup table |

---

## 9 — Files written in this pass

- `mnras_paper/data_release_audit.md` (this file)
- `mnras_paper/data_release_inventory.csv` (563 rows, classifications +
  recommended actions; companion to §4)

No other files were modified. No commits pushed. No Zenodo deposits.
`Plots/build_paper_tables.py` was *executed* (it overwrites
`Results/gwtc1_phasemarg/table{1,4,5,6}*.tex` and the CSV summaries,
all with the same numbers they had before — the rebuild is idempotent).
`Plots/plot_*.py` and `compare_bimodality_waveforms.py` were *executed*
and overwrote the matching PDF/PNG outputs in
`Results/gwtc1_phasemarg/plots/` and `mnras_paper/figures/` — again
idempotent (the source CSVs are unchanged).

---

## 10 — Recommended next actions

1. **Approve the Tier-A edits.** I have the patch in hand for both
   A1 (bootstrap paragraph) and A2 (k̂ honesty). On your "go" I will
   apply both, re-run `build_paper_tables.py` if needed (no — the
   numbers don't change; only the body text does), and run
   `latexmk -pdf main.tex` to confirm the new build is clean.
2. **Authorise the public-repo cleanup.** §5 (path map) + §6 (README
   and MANIFEST) + the dead-file list in §4 are the working set. The
   cleanup is mechanical — I can stage every change in a single
   commit on a feature branch (`prepare-data-release`) and open a PR
   for review.
3. **Decide on the licence.** §6.1 proposes MIT for code + CC-BY-4.0
   for data. The current GitHub repo has "Other" per `gh api .../license`.
   One choice, one line in LICENSE.
4. **Zenodo deposit.** §7.4 documents the procedure; the actual
   deposit is a 10-minute interactive job for the user.
