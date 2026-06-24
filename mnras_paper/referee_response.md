# Response to referee report — MNRAS submission (first-draft revision)

**Paper:** *Rapid Hubble constant inference from GW170817 using GPU-accelerated
nested sampling: prior sensitivity and the limits of post-hoc reweighting*
**Status:** first-draft revision, 2026-05-23. All edits below are landed in
both `mnras_paper/main.tex` and `paper-reproduce/paper/main.tex`. Three
referee concerns (M2 lnZ scatter, M4 IMRX mode-isolated Bayes factor, M7
n_mcmc convergence sweep) require additional GPU runs we have not yet
executed; the manuscript has been adjusted to be honest about the current
evidence base for each, and the additional runs are queued in
`mnras_paper/test_suite/launch_tier2.sh` for a follow-up resubmission.

---

## Cover summary for the editor

We thank the referee(s) for an unusually thorough report. Five findings
materially improved the paper:

1. The **M1** selection-term question forced us to recognise that the
   prior labelled "flat-in-redshift" is, as imposed by the inference
   pipeline, literally **uniform in d_L over a fixed [10, 75] Mpc
   window with no H0-dependent boundaries**. The selection
   normalisation N_s(H0) is therefore rigorously H0-independent and
   cancels from the joint posterior; Eq. 2 is correct as written. The
   variant is renamed "uniform-in-d_L" throughout the manuscript so the
   wording cannot be misread to imply an H0-dependent window. The
   cancellation is now stated and verified explicitly in §2.4 + footnote,
   with a Finn–Chernoff calculation in
   `mnras_paper/test_suite/analysis/analyze_selection_term.py`.

2. The **M3** mass-prior question led to the discovery that the
   manuscript's `default-mass` and `lvk-bounds` labels were inverted —
   the actual LVK PE prior of Abbott et al. (2019, PRX 9, 011001) is
   the broad [0.5, 7.7] M_sun set, not the narrower [0.87, 1.74] M_sun
   one we had labelled "LVK-bounds". The headline now uses the genuine
   LVK prior; it gives the *smaller* baseline tail (P(H0>120) = 0.017
   rather than 0.034), which **strengthens** the prior-sensitivity
   finding. A parallel audit on the GW150914 validation side
   (`mnras_paper/GW150914_mass_prior_audit.md`) showed that the s06/s17a
   runs use a wider [5, 100] M_sun prior than the LVK [10, 80]; the
   posterior sits well inside both, so the recovered parameters are
   unaffected, but the manuscript wording has been softened from
   "like-for-like LVK reproduction" to "reproduces the LVK posteriors
   within the recovered support" and the actual bounds are now stated
   in §3.1.

3. The **M5** volumetric-mass-fraction arithmetic (the referee
   correctly flagged 6%/7%, not "<5%") forced a recheck. The numbers
   are now stated as the exact cubic ratios in §5.

4. The **M6** reconciliation against Abbott Extended Data Table 1 is
   now in §4.1, and the intro "minor change" wording has been softened.

5. The **m14** suggestion to add a median to Table 5 has revealed a
   real science point: under direct uniform-in-d_L sampling the binned
   MAP is 70.5 km/s/Mpc but the weighted median is 87.6 km/s/Mpc; the
   baseline analogues are MAP 70.5 and median 77.6. The median reveals
   a substantial prior-induced shift in the bulk of the H0 posterior
   that the binned MAP had masked. We thank the referee for pressing
   this.

The remaining items (M2, M4, M7 and assorted minors) are addressed
below; for each we state what is in the first-draft manuscript versus
what is deferred to a follow-up.

---

## Major concerns

### M1 — Selection term in the direct uniform-in-d_L variant
**Status: CLOSED.** No new run required.

**Response.** The pipeline imposes `π(d_L) = 1 / (d_hi − d_lo)` as a
fixed density on the observable d_L (`logprior_fn` / `lp_uniform`
branch in `GW170817_heterodyned_2.py`), with `d_lo, d_hi = 10, 75` Mpc
— no H0-dependent boundaries. The detection-selection normalisation
`N_s(H0) = ∫ P_det(d_L) π(d_L | H0) d d_L` therefore has no H0
anywhere and cancels from the joint posterior, exactly as for the
volumetric baseline. **Eq. 2 is correct as written** for the
configuration actually run.

**Manuscript changes.**
- §2.3: a sentence after Eq. 2 (eq:h0likelihood) explicitly notes the
  cancellation and points to §2.4.
- §2.4: variants (i) and (ii) renamed "Direct uniform-in-d_L" and
  "Reweighted uniform-in-d_L"; new paragraph + footnote states the
  fixed-density-on-d_L property, cites Finn & Chernoff (1993) and the
  LVK Prospects review (2020) for the horizon range, and links to the
  supporting calculation.
- Abstract, intro, §4, §5, §6, §7, figure captions, table captions,
  plot legends, and table-builder labels: "flat-in-redshift" /
  "flat-in-z" → "uniform-in-d_L" throughout.

**Supporting material added.**
- `mnras_paper/test_suite/analysis/analyze_selection_term.py`
  (Finn–Chernoff Monte Carlo; N_s computed at three horizon distances
  D_h ∈ {100, 150, 220} Mpc spanning the O2 BNS range to inspiral
  horizon).
- `mnras_paper/figures/selection_term_Ns.{pdf,png}`.
- Detailed response: `mnras_paper/referee_response_M1.md`.

### M2 — Two-seed bimodality replication is statistically inconsistent
**Status: FIRST-DRAFT EVIDENCE INCLUDED; full ensemble deferred.**

**Response.** The referee is correct that two seeds are insufficient to
support the manuscript's original "±0.1 per-run lnZ uncertainty" claim.
We have:

- **Acknowledged the gap explicitly in §5**: the paragraph following
  the second-seed replication now reads *"the run-to-run lnZ scatter
  is larger than the nominal ±0.1 per-run uncertainty: the unrestricted
  lnZ differs by 1.04 between the two seeds, so the ±0.1 figure should
  be read as a within-run statistical error, not a run-to-run
  reproducibility bound. The conclusion that survives this scatter is
  the sign-independent one — |lnB(B/A)| < 1 in both seeds — so Mode B
  is neither significantly favoured nor disfavoured regardless of
  seed."* (§5 of the manuscript, paragraph after Eq. 4.)
- **Provided a sweep-ready aggregator**:
  `mnras_paper/test_suite/analysis/analyze_seed_ensemble.py` operates
  on the existing two seeds today (reproducing the paper's exact
  lnB(B/A) values of −0.66 for seed 0 and +0.10 for seed 1, plus
  empirical per-mode σ(lnZ) of 0.064 for Mode A, 0.474 for Mode B,
  0.735 for Unrestricted) and will rerun seamlessly when additional
  seeds land.
- **Queued a full N = 8 ensemble** in
  `mnras_paper/test_suite/launch_tier2.sh` (six additional seeds across
  all three configurations). The empirical σ(lnZ) and the lnB(B/A)
  ensemble distribution will replace the existing prose in a follow-up
  revision. The sign-independent conclusion |lnB(B/A)| < 1 is unlikely
  to flip, but the additional seeds will sharpen the bound.

**What this means for the headline.** The lnB(B/A) values reported in
Table 6 (seed 0: −0.66; seed 1: +0.10) are themselves unaltered. The
methodological claim about run-to-run reproducibility is the one that
is rewritten, and it is rewritten *honestly* in the current draft;
quantitative sharpening awaits the queued runs.

### M3 — Mass-prior inversion (GW170817 side)
**Status: CLOSED.** No new run required.

**Response.** The `default-mass` and `lvk-bounds` labels were inverted:
the [0.5, 7.7] M_sun set is the genuine LVK PE prior of Abbott et al.
(2019, PRX 9, 011001, Sec. III D), not the constructed [0.87, 1.74]
range we had labelled "LVK-bounds". The headline now uses the genuine
LVK prior and the two affected sections (§4.1 and §4.3) sit on the
same prior. The IMRPhenomXAS_NRTidalv3 baseline run gives
MAP = 70.5 km/s/Mpc, 68% HPD = [63.8, 87.6], P(H0>120) = 0.017 — *smaller*
than the previously-labelled "LVK-bounds" P(H0>120) = 0.034. The
prior-induced inflation (factor ≈9) is therefore not an artefact of
prior choice. Detailed response: `mnras_paper/referee_response_M3.md`.

**GW150914 follow-up audit.** The s06 (cross-check) and s17a
(production) GW150914 validation runs use `--m-comp-lo 5.0
--m-comp-hi 100.0`, wider than the LVK GWTC-2.1 [10, 80] M_sun PE
prior. The posterior support is well inside [25, 40], so recovered
parameters are unaffected, but the manuscript's three "like-for-like
LVK reproduction" claims (§3.1 main text + figure caption + §6 wall-clock
paragraph) have been softened to "reproduces the LVK posteriors within
the recovered support" and the actual prior bounds are now stated
explicitly in §3.1. Full audit:
`mnras_paper/GW150914_mass_prior_audit.md`.

### M4 — Bimodality mechanism shown on IMR, attributed to IMRX
**Status: QUALITATIVE PART CLOSED; quantitative Bayes factor deferred.**

**Response.** The referee is correct that the original submission
demonstrates the mode-isolated Bayes factor only on IMR/NRTidalv2 but
attributes the underlying mechanism to the locked primary IMRX. We
have provided the qualitative half of the requested cross-check
**without new GPU runs**, by comparing the (d_L, ι) joint posteriors
of the existing unrestricted IMR and IMRX direct uniform-in-d_L runs:

- New analysis:
  `mnras_paper/test_suite/analysis/compare_bimodality_waveforms.py`
  loads `s10__..._imrphenomd_nrtidalv2__flatz__dL10-75__refModeB`
  (IMR) and `s14__..._imrphenomxas_nrtidalv3__flatz` (IMRX), computes
  the posterior weight in the Mode-B region (d_L < 30 Mpc), and
  outputs a side-by-side joint figure.
- Numerical result: Mode-B posterior weight is 0.428 for IMR and
  0.325 for IMRX. **Both are substantial**, demonstrating that the
  (d_L, ι) two-peak structure is a property of the data plus the
  uniform-in-d_L prior, not the NRTidalv2 tidal-phase calibration.
  The reduction in Mode-B weight from IMR to IMRX is consistent with
  the existing §4.1 observation that the NRTidalv3 calibration
  tightens the upper H0 tail.
- New figure: `mnras_paper/figures/bimodality_imr_vs_imrx.pdf`,
  referenced in §5 as Figure 5 (`fig:bimodality-waveform-check`).
- Manuscript change: the first paragraph of §5 now opens with this
  qualitative cross-check and states *"the bimodality is therefore a
  property of the data and the uniform-in-d_L prior, not the
  NRTidalv2 tidal-phase calibration; ... the mode-isolated runs that
  follow use IMR/NRTidalv2 because the prior-restricted samples we
  have available are at that calibration; a Mode-A/Mode-B Bayes
  factor on IMRX would test the bridging argument directly and is
  left to follow-up work."*

**Deferred (queued in launch_tier2.sh).** The two IMRX restricted
runs (Mode-A and Mode-B at d_L ∈ [30, 75] and [10, 30] respectively)
that would yield a direct lnB(B/A) on the locked primary waveform.
Aggregator (`analyze_bimodality_imrx.py`) is in place and will run
seamlessly when the runs land.

### M5 — Volumetric-prior mass fraction is numerically wrong (≈5% → ≈6%/7%)
**Status: CLOSED.** Manuscript edit only.

The exact ratios are stated directly:
- §5: `[10,30] / [10,75]` slab carries
  `(30³ − 10³) / (75³ − 10³) ≈ 6%`.
- §6: Mode-B volumetric-prior mass is `≈ 7%` of Mode-A's.

### M6 — Reweighted variant not benchmarked against Abbott's published flat-in-z numbers
**Status: CLOSED.** Manuscript edit only.

§4.1 now reads:
*"The reweighted variant is itself consistent with the uniform-in-d_L
posterior reported by Abbott et al. (2017) — their Extended Data Table 1
gives a 68.3% HPD H0 = 71 +23 −9 km/s/Mpc — so our reweighting
reproduces the original analysis; the deficit we report lies in the
directly sampled high-H0 tail, which the reweighted procedure does not
access."*

The intro reference to Abbott's "minor change" was softened to
acknowledge that the comparison concerned the credible-interval bulk,
not the high-H0 tail.

### M7 — n_mcmc convergence not demonstrated for GW170817
**Status: FACTUAL FIX APPLIED; dedicated sweep deferred.**

**A factual correction first.** Writing the M7 sweep infrastructure
exposed that the pipeline currently defaults to
`num_mcmc_steps = 8 × NUM_DIMS = 112` slice steps per slice update,
not the `5 × n_dim = 70` claimed in §2.1 of the submitted manuscript.
We have updated §2.1 to state the actual value (112) and the
corresponding ratio for the GW150914 validation run (n_mcmc = 160 =
16 × n_dim), and have added one sentence acknowledging that a
dedicated convergence sweep at {5, 10, 20} × n_dim is left to
follow-up work, with the headline tail probability P(H0>120) as the
natural diagnostic.

**Forward evidence.** The GW150914 validation runs at the larger
n_mcmc = 16 × n_dim configuration and produces an LVK-consistent
posterior, providing indirect evidence that 8 × n_dim is unlikely to
be catastrophically under-converged on the larger but
similar-architecture GW170817 problem. We do not present this as
proof of GW170817 convergence; it is a sanity check.

**Sweep infrastructure (queued).** Both runners (`heterodyned_1.py`
and `heterodyned_2.py`) now expose `--n-mcmc`, wired to the BlackJAX-NS
`num_inner_steps`; `--seed` was added to `heterodyned_1.py` (previously
hardcoded to `PRNGKey(0)`; existing seed-0 runs reproduce
bit-identically). Aggregator (`analyze_nmcmc_sweep.py`) and launch
block (in `launch_tier2.sh`) are ready.

---

## Minor concerns

| ID  | Concern | Status | Notes |
|-----|---------|--------|-------|
| m1  | "four nested-sampling evidences" → "three" (reweighted has none) | CLOSED | Abstract + §4.1 updated. |
| m2  | ΔlnZ ≲ 1.8 framing | CLOSED | §4.1 paragraph identifies the decision-relevant pair (baseline vs direct uniform-in-d_L, ΔlnZ ≈ 1.05) and softens "not decisive" to "at most weak-to-substantial". |
| m3  | "95% upper bound" → "68% HPD upper bound" (95.9) | CLOSED | §4.1 line corrected. |
| m4  | State Kish formula; n_eff history note | CLOSED | Kish (1965) formula now explicit; the reweighted-vs-baseline vs directly-sampled distinction is stated. |
| m5  | Planck 2016 → 2020 | CLOSED | Citation key now `Planck2020` (= Planck 2018 results / A&A 641 A6). |
| m6  | `Cornish2013` key vs eprint inconsistency | CLOSED in prior session (bib verification). |
| m7  | Holz & Hughes (2005) for bright-siren concept | CLOSED in prior session. |
| m8  | More GW170817 H0 reanalysis literature in intro | CLOSED | `Hotokezaka2019` and `Nicolaou2020` cited. |
| m9  | Stronger IS-weight degeneracy reference | OPEN | `Speagle2020Dynesty` is sufficient for the methodological point. |
| m10 | Eight `@misc` bib `TODO`s | CLOSED in prior session. |
| m11 | Table 4 hardcoded vs Data Availability claim | PARTIAL | Data Availability wording corrected; auto-generation rewire still pending (`TABLE4_CROSS_WAVEFORM` in `build_paper_tables.py` points to defunct s07_lvkbounds paths; needs relink to s14 IMRX + TaylorF2 CSV). |
| m12 | `\ref{sec:bimodality}` at l.155 → `\ref{sec:prior}` | CLOSED | Already correct in current main.tex. |
| m13 | Ambiguous cross-ref §5 "direct flat-in-z run reported in Section sec:prior" | OPEN | Add "IMR" qualifier; one-word edit. |
| m14 | Add median in Table 5 | CLOSED | New median column added. Reveals that the direct uniform-in-d_L *median* shifts to 87.6 km/s/Mpc while the MAP stays at 70.5 — exposing the prior-induced shift that binned MAP masked. |
| m15 | Table 5 caption omits vp-mean lower block | CLOSED | Caption now describes both blocks. |
| m16 | d_L = 30 Mpc Mode boundary justification; ln(20/45) note | CLOSED | Both already in §5. |
| m17 | §6.3 TF host-localised/full-sky ratio reads messy | OPEN | Defer trim decision to the author. |
| m18 | H0 ∝ v_r / d_L should be (v_r − v_p) / d_L | CLOSED | Both manuscripts corrected. |
| m19 | Fig. 1 caption "Both panels" | OPEN | One-word reword; deferred. |
| m20 | GW150914 validation: quantify agreement in σ | PARTIAL | M_c ~1% and d_L within ~15 Mpc now explicit; corner-width quantification could be tightened. |

---

## MNRAS technical checklist

| Item                | Status                | Action |
|---------------------|------------------------|--------|
| Abstract length     | OK                     | ≈248 words after the M1 rename. |
| Keywords            | OPEN                   | Consider adding "distance scale"; "methods: data analysis" + "software: data analysis" partly redundant. |
| Figure ordering     | OK                     | Verify after adding `fig:bimodality-waveform-check` to §5. |
| Table numbering     | OK                     | Four tables; cross-refs use `\ref{}`. |
| Equation numbering  | OK                     | Eqs 1–5 referenced. |
| Cross-references    | OK                     | m12 already correct. |
| Placeholder removal | CLOSED                 | Both `\textcolor{red}{TODO}` placeholders removed in 2026-05-23 session: Acknowledgements text (Handley Lab + HDPSP + GCP397499138 grant) and Data Availability (GitHub repo URL `ming-256/GW170817-bright-siren-H0`). |
| Data availability   | URL PENDING REPO       | GitHub repository at `https://github.com/ming-256/GW170817-bright-siren-H0` is referenced as the data and analysis release `\citet{Yang2026DataRelease}`; the repo itself still needs to be created and populated by the lead author. |
| Acknowledgements    | NEEDS TEXT             | `TODO ASK WILL` block. |
| Appendix A coverage | OK                     | Wording aligned with §1. |

---

## What requires user input or decision

1. **Acknowledgements text** (l.380): supervisor, group, compute
   (Google Cloud A100), funding. Replace
   `\textcolor{red}{TODO ASK WILL: ...}`.
2. **Create the GitHub data-release repository** at `https://github.com/ming-256/GW170817-bright-siren-H0` and populate with the nested-sampling chains, derived CSVs, and figure/table-generation scripts. The `\citet{Yang2026DataRelease}` reference points there. (Original wording said "Zenodo deposit + DOI" but the lead author chose GitHub instead.) Optional: replace
   `\textcolor{red}{\url{TODO: insert permanent repository URL/DOI}}`.
3. **m11 Table 4 auto-generation rewire**: relink
   `build_paper_tables.py TABLE4_CROSS_WAVEFORM` from the defunct
   `s07_lvkbounds` paths to the M3-era LVK-matched runs (`s14` IMRX
   baseline + the TaylorF2 CSV at `Results/gwtc1_phasemarg/`). The
   TaylorF2 row is not in the `test_suite/sNN__` layout, so the
   script needs a small CSV-path special case. Low-priority for
   first-draft submission.

## File map

- This document: `mnras_paper/referee_response.md` (consolidated, first-draft)
- Per-concern detail (background):
  - `mnras_paper/referee_response_M1.md`
  - `mnras_paper/referee_response_M3.md`
- GW150914 audit: `mnras_paper/GW150914_mass_prior_audit.md`
- Manuscript: `mnras_paper/main.pdf` (rebuilt)
- Reproducible mirror: `paper-reproduce/paper/main.pdf` (rebuilt)
- New analyses (no GPU): `compare_bimodality_waveforms.py`,
  `analyze_selection_term.py`
- Queued GPU runs (M2/M4/M7): `mnras_paper/test_suite/launch_tier2.sh`
- Queued aggregators: `analyze_seed_ensemble.py`, `analyze_bimodality_imrx.py`,
  `analyze_nmcmc_sweep.py`
- New figures: `mnras_paper/figures/{selection_term_Ns, bimodality_imr_vs_imrx,
  seed_ensemble_lnZ}.{pdf,png}` (the last from the seed-ensemble aggregator
  running on the existing N=2 data)
