# Referee Report — MNRAS submission

**Paper:** *Rapid Hubble constant inference from GW170817 using GPU-accelerated nested
sampling: prior sensitivity and the limits of post-hoc reweighting*
**Authors:** Yang, Prathaban, Yallup & Handley
**Manuscript reviewed:** `mnras_paper/main.tex` (412 lines), with `\input` table files
`Results/gwtc1_phasemarg/table{1,5,6}_*.tex` and `references.bib`.
**Review date:** 2026-05-18
**Recommendation:** Major revision.

---

## 0. Context for whoever continues this discussion

This report was produced by acting as three simultaneous referees:
- **Referee 1** — GW methodology (nested sampling, heterodyned likelihood, waveforms).
- **Referee 2** — bright-siren cosmology (Hubble tension, importance sampling, ESS).
- **Referee 3** — MNRAS technical editor (house style, numbering, cross-refs).

Every numerical claim was traced to source files. The Abbott et al. (2017) paper was
read directly from `LIGO-P1700296.pdf` (the GW170817 H0 measurement, Nature 551, 85).
The key corroboration facts are recorded in §1 below so the discussion can continue
without re-reading the PDF.

---

## 1. Key verified facts (corroboration evidence)

### 1.1 From the table files (paper's own numbers)
`table5_prior_sensitivity.tex` (IMRX, default-mass prior set):
- Baseline `π(dL)∝dL²`: MAP 70.5, 68% HPD [63.8,87.6], P(H0>120)=0.017, P(H0>150)<1e-4, lnZ 486.25±0.11
- Flat-in-z direct: MAP 70.5, [64.2,103.8], 0.159, 0.038, lnZ 487.30±0.10
- Flat-in-z reweighted: MAP 73.5, [65.2,95.9], 0.041, 0.000, lnZ (post-hoc, none)
- σ_vp=250: MAP 73.5, [61.7,90.5], 0.069, 0.015, lnZ 485.55±0.09
- ⟨v_p⟩=215: MAP 74.5, [66.1,90.4], 0.021 ; ⟨v_p⟩=405: MAP 68.5, [61.5,87.0], 0.030

`table6_bimodality.tex`:
- seed0: Mode A [30,75] lnZ 486.80±0.10 ; Mode B [10,30] lnZ 486.95±0.09 ; Unrestricted [10,75] lnZ 486.48±0.09
- seed1: Mode A lnZ 486.71±0.09 ; Mode B lnZ 487.62±0.10 ; Unrestricted lnZ 487.52±0.09

`table4_cross_waveform.tex` (LVK-bounds prior) — NOTE this file is NOT \input by main.tex;
Table 4 in the paper is hardcoded with only the IMRX and TF rows:
- IMRX 71.5 [63.1,88.5] [58.8,117.6] P=0.034 lnZ 490.08±0.10
- IMR  71.5 [63.2,90.5] [58.2,130.0] P=0.070 lnZ 489.96±0.10
- TF   69.5 [60.2,92.0] [56.5,168.2] P=0.135 lnZ 490.35±0.09

`table1_gw150914.tex`: XPHM n_live=8000 → Mc 30.35, q 0.87, dL 455, ι 2.61, lnZ 260.86±0.06 ;
n_live=5000 → 30.34, 0.87, 460, 2.62, lnZ 261.09±0.08.

### 1.2 Arithmetic checks
- Capture fraction IMRX: (0.041−0.017)/(0.159−0.017)=0.024/0.142=**16.9% ✓** (paper: 17%)
- Capture fraction IMR: (0.195−0.076)/(0.281−0.076)=0.119/0.205=**58.0% ✓**
- ΔlnZ spread (3 variants with evidence): 487.30−485.55=**1.75 ✓** (paper: ≲1.8)
- Bayes factor seed0: (486.95−486.80)+ln(20/45)=0.15−0.81=**−0.66 ✓**
- Bayes factor seed1: (487.62−486.71)+ln(20/45)=0.91−0.81=**+0.10 ✓**
- **Volumetric mass fraction [10,30]/[10,75] for π∝dL²: (30³−10³)/(75³−10³)=26000/420875=6.2%**
  — paper says "<5%": **WRONG, should be ~6%.**
- **[10,30]/[30,75]: 26000/394875=6.6%** — paper says "below 5%": **WRONG, ~7%.**
- n_eff efficiency: 30,695/1.78e5=17.2%✓ ; 37,022/1.78e5=20.8% ≠ paper's 18.4%
  (⇒ the direct flat-in-z run had ~201k samples, not 178k; not stated).

### 1.3 From Abbott et al. 2017 (LIGO-P1700296.pdf)
- **Abbott DID use reweighting** for the flat-in-z prior: p.11, "the posterior samples
  from GW parameter estimation have to be re-weighted, since they are generated with the
  d² prior... We first 'undo' the default prior before applying the desired new prior."
  ⇒ the paper's framing on this point is ACCURATE.
- Abbott's likelihood (Eqs 5–6): `p(v_r|d,v_p,H0)=N[v_p+H0·d, σ_vr²](v_r)` and
  `p(⟨v_p⟩|v_p)=N[v_p,σ_vp²]`. The manuscript's Eq. 2 matches these EXACTLY. ✓
- **Abbott's canonical model (Eq. 7) contains a selection term `1/N_s(H0)`.** For a
  *volumetric distance* prior, p.9, "N_s(H0) is a constant and can be ignored." BUT
  p.9 + Eqs 11–12: "This would not be the case if we set a prior on the redshifts...
  since then changes in H0 would modify the range of detectable redshifts." The
  manuscript's flat-in-z variant is exactly such a z-prior; Eq. 2 has no N_s(H0) term.
- Abbott Extended Data Table 1 — flat-in-z (reweighted) result: 68.3% MAP 71.0₋₉.₀⁺²³·⁰,
  68.3% symm 81₋₁₃⁺²⁷, 90% MAP 71.0₋₁₇⁺⁴⁸ (upper edge ≈119). Abbott's "minor change"
  conclusion = "results change by less than 1σ" — refers to the bulk, not the tail.
  Abbott reported credible INTERVALS, not P(H0>120); that tail statistic is this
  paper's own choice.
- Abbott host inputs: v_r=3327±72 km/s, ⟨v_p⟩=310±150 km/s, v_H=3017±166. The
  manuscript matches these.

### 1.4 Figure files — all 6 exist
corner_GW150914_waveform_comparison.pdf, H0_prior_sensitivity.pdf, bimodality.pdf,
H0_waveform_comparison.pdf, corner_GW170817_waveform_comparison.pdf, scaling_study_full.pdf
— all present in `Results/gwtc1_phasemarg/plots/`.

---

## Part 1 — Summary Verdict

**Major revision.**

The paper makes a genuine contribution: re-running GW170817 bright-siren inference under
the target prior (rather than reweighting to it) is the right experiment, and the
demonstration that post-hoc reweighting can badly understate prior-induced tail movement
is useful for standard-siren cosmology. The (dL,ι) Mode-B mechanism is plausible. The
GPU-native heterodyned pipeline is a real capability; the heterodyned-vs-unheterodyned
check is appropriate; the authors are candid about scope (no CPU benchmark, no population
analysis). Numerical entries trace correctly to the table files in nearly all cases.

The critical concerns are about whether the headline number is clean. (1) The "direct
flat-in-z" run imposes a redshift prior but omits the H0-dependent selection term that
Abbott's own formalism (Eqs 11–12) requires for a z-prior — confounding the 0.159 vs
0.041 gap with a known missing term acting in the high-H0 tail. (2) The two-seed
bimodality "replication" is internally inconsistent at the quoted lnZ precision. (3) The
central result uses a physically implausible mass prior ([0.5,7.7] M⊙) instead of the
LVK-matched one used elsewhere in the same paper. All addressable, but all bear on the
reliability of the headline figure.

---

## Part 2 — Major Concerns

**M1 — "Direct flat-in-z" run omits the H0-dependent selection term required for a
redshift prior.** (Ref 1 & 2; Eq. 2, §2.4 variant (i), §4.1/Table 5.)
Abbott P1700296 Eqs 7–12 + p.9: with a volumetric *distance* prior N_s(H0) is constant
and ignorable, but with a prior on *redshift* it becomes H0-dependent. The manuscript's
variant (i) imposes a z-prior; Eq. 2 has no 1/N_s(H0). The neglected term acts in the
high-H0 region carrying the entire headline signal. Abbott bound it at ≲5% — but the
whole result is a few-percent tail statistic.
*Fix:* include N_s(H0) for the flat-in-z runs and show stability, OR compute it for this
configuration and prove it is flat well below the 0.142 effect.

**M2 — Two-seed bimodality "replication" is statistically inconsistent.** (Ref 1; §4.2,
Table 6, Eq. 4.) Unrestricted lnZ: 486.48±0.09 (seed0) vs 487.52±0.09 (seed1) — differ
by 1.04 (~8σ vs quoted errors). Mode B: differ by 0.67. Uncorrected lnB: 0.15±0.13 vs
0.91±0.13 — spread 0.76±0.19 (~4σ). The paper's claim this is "consistent with the ~0.1
per-run lnZ uncertainty" is false. (Related: Table 1 XPHM lnZ 260.86±0.06 vs 261.09±0.08
differ ~2σ.)
*Fix:* report honest run-to-run lnZ scatter from a seed ensemble; revise the ±0.1 claim;
re-assess whether ΔlnZ≲1.8 "not decisive" and the Mode-B Bayes factor survive.

**M3 — Central result uses a physically implausible mass prior.** (Ref 1 & 2; §2.4
l.142, §4.1, Tables 5 vs 4.) §4.1 uses "default-mass" = component masses uniform
[0.5,7.7] M⊙ (not a BNS range). §4.3 uses LVK-bounds [0.87,1.74] M⊙ "matching
Abbott2017H0." IMRX baseline P(H0>120) = 0.017 (default-mass) vs 0.034 (LVK-bounds) — a
factor of 2. The headline uses the prior set with the smallest baseline tail, maximising
the apparent factor-≈9 inflation. No direct-vs-reweighted comparison on LVK-bounds.
*Fix:* run the four-variant comparison on the LVK-bounds prior and make it the headline,
or rigorously justify the [0.5,7.7] M⊙ baseline.

**M4 — Bimodality mechanism demonstrated on IMR (NRTidalv2), not the locked primary
IMRX.** (Ref 1; §4.2 l.248–249, Table 6.) Every mode-isolated run is NRTidalv2, but the
abstract/header attribute the mechanism to IMRX and Eq. 3 is the IMRX 17%. The NRTidalv3
bridging argument is asserted, not shown.
*Fix:* run Mode-A/Mode-B decomposition for IMRX, or state plainly it is a proxy and
defend the extrapolation.

**M5 — Volumetric-prior mass fraction is numerically wrong.** (Ref 2; §4.2 l.277–279,
§5.2 l.364.) Correct values are ~6.2% and ~6.6%, not "<5%" / "below 5%" (see §1.2).
*Fix:* replace with the correct ~6%/~7% figures.

**M6 — Reweighted variant never benchmarked against Abbott's published flat-in-z
numbers.** (Ref 2; §1 l.99, §4.1.) Abbott Extended Data Table 1 flat-in-z reweighted:
68.3% MAP 71₋₉⁺²³, 90% MAP 71₋₁₇⁺⁴⁸. Abbott reported intervals, not P(H0>120). The
manuscript's reweighted 0.041 is roughly consistent with Abbott — which would strengthen
the paper — but the reconciliation is absent, and "minor change" should not be implied
to mean reweighting concealed the tail effect.
*Fix:* quote Abbott's flat-in-z numbers, show the reweighted variant reproduces them,
rephrase l.99.

**M7 — n_mcmc convergence not demonstrated for GW170817.** (Ref 1; §2.1 l.122, §5.2.)
Science runs use 5·n_dim=70 slice steps; GW150914 validation uses 160 "so the comparison
is not sampler-limited" — implying 70 may be. Convergence study varies only n_live; no
n_mcmc sweep for the 14-d problem. The headline is a tail probability; under-stepped
slice sampling biases tails first.
*Fix:* add an n_mcmc sweep (5/10/20·n_dim) on the IMRX baseline and flat-in-z runs.

---

## Part 3 — Minor Concerns

**m1** (Ref3) Abstract & §4.1 say "four nested-sampling evidences" — only three variants
have an evidence (reweighted is post-hoc). Change "four"→"three".

**m2** (Ref1/2) ΔlnZ≲1.8 mixes two prior axes; the decision-relevant pair is
baseline vs flat-in-z-direct, ΔlnZ≈1.05. "Not decisive on the Jeffreys scale" understates
— lnB≈1–1.8 is "substantial" on Jeffreys. Soften "the data do not prefer one distance
prior at any meaningful significance".

**m3** (Ref3) §4.1 l.236 calls 95.9 the "95 per cent upper bound under reweighting", but
Table 5 lists [65.2,95.9] as the **68%** HPD. Contradiction — fix text or caption.

**m4** (Ref2) ESS formula never stated (Kish?). Reweighted n_eff (27,317) vs direct-run
n_eff (37,022) is across different sampling histories; only reweighted-vs-baseline is a
coverage diagnostic. State the formula; note the direct-run sample count (~201k).

**m5** (Ref2/3) `Planck2016` is "Planck 2015 results XIII" — stale. Use Planck 2018
(Planck Collaboration 2020, A&A 641, A6).

**m6** (Ref3) `references.bib` key `Cornish2013` has `eprint=1007.4820`, but that arXiv
ID is Cornish (2010) "Fast Fisher Matrices and Lazy Likelihoods" — title/year/eprint
inconsistent. Reconcile.

**m7** (Ref2) Line 96–97 describes the *bright*-siren (counterpart) concept but cites
only `Schutz1986` (the statistical proposal). Add Holz & Hughes (2005).

**m8** (Ref2) Introduction cites essentially no GW170817 H0 reanalysis literature
(Hotokezaka et al. 2019; Nicolaou et al. 2020; Mukherjee et al. 2021; recent reviews).
Add to position the contribution. (The paper wisely does not claim "first".)

**m9** (Ref2) `Speagle2020Dynesty` is a weak primary reference for importance-sampling
weight degeneracy (l.101). Cite a proper IS/ESS reference.

**m10** (Ref3) Eight `@misc` bib entries carry `TODO: verify`; `Edwards2023Ripple`,
`Wong2023Jim`, `BlackJAX` lack eprint/DOI. Complete before submission.

**m11** (Ref3) Table 4 (`tab:waveform-h0`, l.310–311) is hardcoded, not `\input` from
`table4_cross_waveform.tex` (which has 3 rows). Data Availability claims Tables 1,4,5,6
are auto-generated — false for Table 4. Fix.

**m12** (Ref3) Cross-ref error: l.155 `\ref{sec:bimodality}` should be `\ref{sec:prior}`
(the capture-fraction comparison is in §4.1; l.286 references it correctly).

**m13** (Ref1) Ambiguous cross-ref: §4.2 l.277 "direct flat-in-redshift run reported in
Section sec:prior" — §4.1 reports both IMRX (0.159) and IMR (0.281); the 0.281 match is
the IMR run. Specify "the IMR direct flat-in-z run".

**m14** (Ref2) MAP from a 1 km/s/Mpc weighted histogram is noisy for an asymmetric
posterior (Table 5 reweighted MAP 73.5 vs 70.5 baseline/direct — likely bin noise). Add
the median, as Abbott does.

**m15** (Ref3) Table 5 caption describes only "four prior variants" but the table has a
second block (⟨v_p⟩=215,405). Extend caption.

**m16** (Ref1) Mode-B boundary dL=30 Mpc not justified — state if it is the inter-mode
saddle. The `ln(20/45)` correction is valid only because flat-in-z≈flat-in-dL at
z≈0.01 — state this.

**m17** (Ref1) §5.3 TF host-localised/full-sky ratio 1.44 (tighter prior slower) is
counterintuitive; section reads messy though caveated. Consider trimming.

**m18** (Ref3) l.98 `H0 ∝ v_r/dL`; strictly `H0 ∝ (v_r−v_p)/dL`. Eq. 2 is correct.

**m19** (Ref3) Fig. 1 caption "Both panels show a like-for-like reproduction" — a corner
plot has many panels; reword.

**m20** (Ref1) GW150914 validation: quantify agreement in σ (Mc 30.35 vs LVK 30.7 is
~1%); n_live=5000 cross-check dL=460 is ~20 Mpc from LVK 440.

---

## Part 4 — MNRAS Technical Checklist

| Item | Status | Action required |
|---|---|---|
| Abstract length | ~251 words | At/over the 250-word limit — trim a sentence. |
| Keywords | Acceptable | "methods: data analysis" + "software: data analysis" partly redundant; consider "distance scale". |
| Figure ordering | Pass | Figs 1–6 each first cited before appearing, in order. |
| Table numbering | **Fail** | Compiled doc has 4 tables (1–4). Prose, Data Availability, header hardcode "Tables 1,4,5,6" — replace with "Tables 1,2,3,4" or use `\ref{}`. |
| Equation numbering | Minor | Eqs 1–5 numbered; two `equation*` unnumbered (fine). Eqs 4 & 5 numbered but never `\ref`'d. |
| Cross-references | One error | l.155 `\ref{sec:bimodality}`→`\ref{sec:prior}` (m12). Others resolve. |
| Placeholder removal | **Fail** | `TODO` in Acknowledgements (l.382) and repo URL/DOI (l.388); `\date{}` placeholders (l.74); 8 bib `TODO`s. |
| Data availability | Incomplete | Repo URL/DOI is a TODO; Table 4 not actually auto-generated (m11). |
| Acknowledgements | Incomplete | "TODO ASK WILL" — supervisor, group, compute, funding missing. |
| Appendix A coverage | Minor mismatch | §1 (l.105) promises a slightly different sweep set than Appendix A delivers — align wording. |

---

## Open follow-ups for the continued discussion

1. The author may want LaTeX edits drafted for the technical-checklist items
   (table-number references, the l.155 cross-ref, Table 5 caption, the `Cornish2013`
   and `Planck2016` bib entries). These are mechanical and low-risk.
2. M1 (selection term) and M2 (seed scatter) require new runs / new analysis — these are
   the substantive blockers; the author's response strategy on these two determines
   whether the revision is genuinely "major" or can be argued down.
3. M3 (mass prior) likely requires re-running the four-variant comparison on the
   LVK-bounds prior — confirm whether those runs already exist in `Results/`.
