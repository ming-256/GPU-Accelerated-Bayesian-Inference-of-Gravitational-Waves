# Final-pass review — Yang et al. (2026) MNRAS submission

Reviewer pass: 2026-05-24. Build verified from `mnras_paper/main.tex` (412 lines)
against `references.bib` (45 entries, 433 lines).

This review covers Tasks 1–7 of `final_pass_prompt.md`. All findings are tagged
**Tier A** (substantive — changes a claim or fixes an inconsistency),
**Tier B** (citation hygiene / numerical drift within rounding-but-noticeable),
or **Tier C** (cosmetic / tone). One Tier-A precondition fix was applied
during the pass to obtain a clean compile (graphicspath entry — see §2 below);
all other findings are proposed, not applied.

---

## 1. Verdict

**Ship after the listed Tier-A fixes.**

The paper compiles to 11 pages with no unresolved refs, no undefined citations,
no `??` in the rendered PDF, and zero TODO / placeholder strings beyond the
journal-standard `Accepted XXX. Received YYY; in original form ZZZ` line.
Bibtex runs clean (45 entries, all cited, all 2024–2026 DOIs resolve correctly,
including the new APS short-DOI for HuVeitch2025).

Six Tier-A findings stand between this draft and a clean submission. Five of
them are numerical/compliance items (abstract 257–259 words against MNRAS's
250-word ceiling; two σ-ratio digits at §3.1 line 171; TF2 wall-clock at
line 329; TF2 lnZ in the §4.3 table at line 317; one hedging adverb at
§4.1 line 225 that undercuts the central "mode stays, tail moves" framing).
The sixth is the consequence of the first: trimming the abstract by ~10 words
to land under the MNRAS limit. None of these is a substantive science problem;
they are inconsistencies between text and chain CSVs (or between text and the
journal style guide) that a final pass is meant to catch.

Beyond the Tier-A set, the bibliography is in good shape, the narrative arc
holds (intro motivates the prior-sensitivity question as systematics
quantification rather than as critique; §3 validates; §4 delivers the result;
§5 supplies the mechanism; §6 frames runtime as enabling; Conclusions match
the abstract tonally and numerically), and the tone-pass has converged on
everything structural — the residual hedging is concentrated in four to six
sentences in §4.1, §6.3, and Appendix A, and is the kind of cleanup a single
30-min editing pass can sweep.

If the user authorises the Tier-A fixes, I'd recommend applying them all in
one pass with the proposed wording below, re-compiling, then trimming the
abstract last (so the word-count check is performed against the final text).

---

## 2. Compile status

**Result:** 11 pages, clean compile after a one-line preamble fix.

- `\graphicspath{...}` (line 38–42) listed `figures/output/`, `figures/v2/`,
  and `../Results/gwtc1_phasemarg/plots/`, but **not** `figures/` itself —
  so `figures/bimodality_imr_vs_imrx.pdf` (the §5 cross-waveform check,
  Fig 3 in the compiled doc) could not be resolved. The PDF exists; it's
  the canonical figure; the path was the gap.
- **Fix applied during this pass** (necessary to evaluate the rest of Tasks 2–7):
  added `{figures/}{../mnras_paper/figures/}` to the graphicspath. One line,
  no figure regeneration, listed in the Tier-A applied-edit section at
  the bottom of the report.
- Post-fix compile: `Output written on main.pdf (11 pages, 567199 bytes)`,
  no `LaTeX Warning`, no unresolved `\ref`, no undefined citations,
  `Latexmk: All targets () are up-to-date`. Five cosmetic `Underfull \hbox`
  warnings (badness 2065–10000) on lines 246–249, 258–261, and 407–409 from
  long compound words in inline-math captions; standard MNRAS-class
  hyphenation noise, no action required.
- A second-pass `pdfTeX warning (dest): name{Hfootnote.1} has been referenced
  but does not exist, replaced by a fixed one` appears on the first compile
  of a clean build but disappears on the second pass; not a real warning.

**Unresolved refs / undefined citations / orphan labels:**

| Item | Status | Tier |
|---|---|---|
| All 28 `\ref` / `\eqref` calls resolve | PASS | — |
| All 57 `\cite*` calls resolve | PASS | — |
| `sec:skyprior` (deleted per m17) | correctly absent | PASS |
| `eq:bayes` (line 118) | **orphan** — labeled but never `\ref`'d | C |
| Bayes-factor equation (line 280–282) | numbered, no label, not referenced | C |
| Heterodyne speedup equation (line 335–337) | numbered, no label, not referenced | C |
| All section / fig / tab labels referenced | PASS (modulo the orphans above) | — |

Figure count: **7** (`fig:gw150914`, `fig:h0prior`,
`fig:bimodality-waveform-check`, `fig:bimodality`, `fig:waveform-h0`,
`fig:waveform-corner`, `fig:scaling`). Table count: **4** (`tab:gw150914`,
`tab:h0priors`, `tab:bimodality`, `tab:waveform-h0`).

NOTE on the prompt's "Fig 5 = bimodality-waveform-check, Fig 6 = bimodality":
in the compiled PDF these are actually Fig 3 and Fig 4. The prompt's
"Table 5 / Table 6" refer to filename convention
(`table5_prior_sensitivity.tex` and `table6_bimodality.tex`), not compiled
table numbers — those map to Table 2 and Table 3 in the compiled PDF. The
ordering inside the paper is correct (validation → results → bimodality
mechanism → waveform check → performance); the prompt's nomenclature
trails the compiled numbering, not the other way around.

---

## 3. Numerical consistency findings (Task 1)

### 1a. Abstract / §4.1 / Conclusions / Table 5 / Fig 3 cross-consistency — **PASS**

All headline numbers tie out across abstract (line 84), §4.1 (lines 225–242),
§6.1 (lines 359–365), Conclusions (line 379), and the Table 5 `\input` at
`Results/gwtc1_phasemarg/table5_prior_sensitivity.tex`:

| Quantity | Value | Location | Verified against |
|---|---|---|---|
| P(H₀>120) baseline | 0.017 | abstract, §4.1, conclusions, Table 5 | s14 baseline samples.csv → 0.01705 |
| P(H₀>120) direct | 0.159 | abstract, §4.1, conclusions, Table 5 | s14 flatz → 0.15944 |
| P(H₀>120) reweighted | 0.041 | abstract, §4.1, conclusions | s14 reweighted_flatz → 0.04080 |
| weighted median baseline | 77.6 | abstract, conclusions, Table 5 | 77.586 |
| weighted median direct | 87.6 | abstract, conclusions, Table 5 | 87.621 |
| binned MAP | 70.5 | abstract, §4.1, conclusions, Table 5 | 70.5 (1-km/s/Mpc grid) |
| ΔlnZ spread | ≲1.8 | abstract, §4.1, conclusions | max(487.30,486.25,485.55) − min = 1.75 |
| baseline-vs-direct ΔlnZ | ≈1.05 | §4.1 line 234 | 487.30 − 486.25 = 1.05 |
| capture fraction | ≈ 17 % | abstract, eq(2), §6.1, conclusions | (0.041−0.017)/(0.159−0.017) = 16.90% |

All cross-consistent. The 16.90 % capture-fraction round-to-17 is fine.

### 1b. IMR cross-waveform 58 % — **PASS** with one **Tier-B**

Arithmetic: (0.195 − 0.076) / (0.281 − 0.076) = **58.05 %** ✓. The four
IMR P(H₀>120) values appear identically at §4.1 line 240 and Appendix A
line 408, and all four were re-verified from the canonical IMR chain CSVs in
`Results/gwtc1_phasemarg/`:

| Variant | Paper | Chain |
|---|---|---|
| IMR baseline | 0.076 | 0.07584 |
| IMR direct flatz | 0.281 | 0.28120 |
| IMR reweighted | 0.195 | 0.19497 |
| IMR vp250 | 0.067 | 0.06719 |

**Tier B at line 408** (Appendix A, "IMR companion full sweep"): the four MAPs
quoted (71.5, 75.2, 74.1, 72.3) match a legacy KDE-derived MAP convention, not
the canonical 1 km/s/Mpc histogram method used everywhere else in the paper.
Re-deriving on the canonical grid gives **(71.5, 73.5, 71.5, 70.5)** — three
of the four differ. Capture-fraction arithmetic is unaffected (uses
P(H₀>120), not MAPs), so the §4.1 conclusion stands; but the Appendix-A MAP
column should either be re-derived on the canonical grid or annotated to
indicate the different MAP convention.

### 1c. Bimodality §5 lnB and Mode-B weights — **PASS**

| Item | Paper | Check |
|---|---|---|
| ln(20/45) volume correction | "−0.81" | exactly −0.8109 ✓ |
| lnB(B/A) seed=0 | (486.95 − 486.80) − 0.811 = +0.15 − 0.81 = **−0.66** | matches Table 6 |
| lnB(B/A) seed=1 | (487.62 − 486.71) − 0.811 = +0.91 − 0.81 = **+0.10** | matches Table 6 |
| Mode-B weight, IMRX (s14 flatz) | 0.325 | 0.3247 (w[dL<30] / w[total]) ✓ |
| Mode-B weight, IMR (s10 refModeB) | 0.428 / 0.43 (Fig 3 caption) | 0.4276 ✓ |
| Unrestricted lnZ seed difference | "differs by 1.04" | 487.52 − 486.48 = 1.04 ✓ |

### 1d. Volumetric-mass-fraction arithmetic — **PASS**

- §5 line 285: (30³ − 10³) / (75³ − 10³) = 26000 / 420875 = **6.18 %** ≈ 6 % ✓
- §6.3 line 365: 26000 / (75³ − 30³) = 26000 / 394875 = **6.58 %** ≈ 7 % ✓

Both rounded values are consistent with what is printed.

### 1e. GW150914 σ-widths and ratios — **Tier A**

The σ ratios at line 171 print as `1.01, 0.99, **0.87**, **1.11**`. Re-extracted
σ from `Results/test_suite/s17a__gw150914__imrphenomxphm__nlive8000_mcmc160__seed0000/samples.csv`
(weighted, from the `weight` column) against the LVK GWTC-2.1 XPHM PE
posterior_samples h5 give:

| Param | our σ (3 dp) | LVK σ (3 dp) | true ratio | paper |
|---|---|---|---|---|
| M_c | 1.021 | 1.005 | 1.016 → **1.02** | 1.01 (minor) |
| d_L | 83.67 | 84.94 | 0.985 → **0.99** | 0.99 ✓ |
| q   | 0.101 | 0.113 | 0.894 → **0.89** | **0.87** ← TIER A |
| ι   | 0.411 | 0.350 | 1.174 → **1.17** | **1.11** ← TIER A |

The q and ι ratios in the paper are inconsistent with both (a) the
displayed σ widths and (b) the higher-precision underlying values. The σ
ratio for M_c also misrounds (1.02, not 1.01).

**Proposed corrected sentence (line 171):**

> The 1$\sigma$ widths match closely: $\sigma(\mathcal{M}_c)=1.02$ vs $1.00\,M_\odot$, $\sigma(d_L)=84$ vs $85\,\rm Mpc$, $\sigma(q)=0.10$ vs $0.11$, and $\sigma(\iota)=0.41$ vs $0.35\,\rm rad$ (ratios $1.02$, $0.99$, $0.89$, $1.17$); the largest residual is on the precession-sensitive $\iota$.

### 1e-bis. GW150914 centroid mismatch with caption text — **Tier B**

Table 1 caption (line 175) says "LVK GWTC-2.1 \XPHM\ public PE … reports
$\mathcal{M}_c\approx 30.7\,M_\odot$, $q\approx 0.83$, $d_L\approx 440\,\rm Mpc$,
$\iota\approx 2.62\,\rm rad$". The C01:IMRPhenomXPHM PE h5 (the overlay file
that Fig 1 actually plots) gives medians **(30.44, 0.85, 463, 2.63)**. The
quoted 30.7 / 440 numbers correspond to the GWTC-2.1 paper's tabulated
summary values (C01:Mixed) or the legacy GW150914-discovery numbers, not
to the C01:IMRPhenomXPHM samples the paper compares against directly.

Either: (i) cite the GWTC-2.1 catalogue paper's tabulated values explicitly
("…GWTC-2.1 catalogue (Table N) reports…") so the source of the 30.7 / 440
is unambiguous, or (ii) replace with the actual C01:IMRPhenomXPHM medians
(30.4 / 463). Recommend (ii) for internal consistency with what the figure
plots.

### 1f. Wall-clock numbers — **PASS on three, Tier A on one**

| Run | Paper claim | Source log | Wall-clock | Verdict |
|---|---|---|---|---|
| IMRX baseline n_live=5000 | ~13 min | s14 sampler.log | 793.3 s = **13.22 min** | ✓ PASS |
| TF2 baseline | ~9 min | longest TF2 baseline (s07 lvkbounds) | 246.6 s = **4.1 min** | **TIER A** |
| GW150914 XPHM n_live=8000, n_mcmc=160 | ~5 h | s17a sampler.log | 18649.6 s = **5.18 h** | ✓ PASS |
| IMR heterodyned n_live=10⁵ | ~4 h | scaling_summary_full.csv | 14392.5 s = **4.00 h** | ✓ PASS |

**TIER A at line 329:** "the corresponding \TF\ run takes $\approx 9$\,min" —
no TF2 baseline in the inventory takes 9 min. The four logged TF2 baseline
runs (psdBilby, psdKazewong, lvkbounds, and the gwtc1 reference) all cluster
in 200–246 s (3.3–4.1 min). Possible explanation: the 9-min number predates
a JAX/JIT optimisation. **Proposed correction:** "$\approx 4$\,min" (or "$\approx
5$\,min" rounded generously). The IMRX:TF2 ratio in the abstract / §5.1 is
the speedup-relative ratio that motivates the cross-waveform check, so the
TF2 number being wrong does not affect any IMRX claim; it just overstates
the absolute TF2 wall-clock.

### 1g. n_eff values — **PASS on n_eff, Tier B on sample counts**

| Variant | Paper N | Actual N | Paper n_eff | Actual n_eff | Paper eff | True eff |
|---|---|---|---|---|---|---|
| IMRX baseline | 1.78×10⁵ | **1.726×10⁵** | 30,695 | 30,695.4 ✓ | 17.3 % | **17.8 %** |
| IMRX direct | 2.01×10⁵ | **1.938×10⁵** | 37,022 | 37,022.3 ✓ | 18.4 % | **19.1 %** |
| IMRX reweighted | (not quoted) | 1.725×10⁵ | 27,317 | 27,317.2 ✓ | (n/a) | 15.8 % |

The n_eff values are exact (to within 1 sample), confirming the Kish
calculation. The sample counts overstate by ~3 % (1.78×10⁵ vs actual
1.73×10⁵; 2.01×10⁵ vs actual 1.94×10⁵), which propagates to the
efficiencies (17.3 % understates 17.8 % by 0.5 pp; 18.4 % understates
19.1 % by 0.7 pp).

**Proposed correction (line 236):**

> From the same $1.73\times 10^{5}$-sample \IMRX\ baseline we measure $n_{\rm eff}=30{,}695$ (efficiency $17.8\,\%$); the directly sampled uniform-in-$d_L$ run has $n_{\rm eff}=37{,}022$ from its own $1.94\times 10^{5}$-sample draw (efficiency $19.1\,\%$), while the reweighted uniform-in-$d_L$ estimator has $n_{\rm eff}=27{,}317$ — \emph{lower} than the baseline despite reweighting from the same draw.

### 1h. Table 4 (waveform comparison) TF2 lnZ — **Tier A** (extra, found in the sweep)

Table at line 316–320 reports `\TF` lnZ as **487.25 ± 0.09**. The TF2 baseline
chain (`PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv`
and `evidence_table.csv`) records **486.90 ± 0.10**. The 487.25 value matches
the TF2 flatZ or vp250 variant, not the baseline.

**Proposed correction:**
```
\TF\ (family check) & 68.5 & $[61.4,89.3]$ & $[56.9,125.6]$ & $0.065$ & $486.90\pm0.10$ \\
```

(The 95 % HPD upper bound rounds to 126.0 vs the printed 125.6 — within
tail-sampling noise, Tier-C, no change needed.)

---

## 4. Cross-reference and structure findings (Task 2)

- **All required section labels exist:** `sec:method`, `sec:validation`,
  `sec:results`, `sec:performance`, `sec:discussion`, `sec:conclusions`,
  `sec:priors`, `sec:prior`, `sec:bimodality`, `sec:cross-waveform`,
  `sec:gw150914`, `sec:hetero-vs-unhet`, `sec:speedup`, `app:robustness`.
- **`sec:skyprior`** correctly **absent** (m17 closed).
- **Equation refs all resolve:** `eq:h0likelihood` (called at lines 137, 150),
  `eq:reweight-fraction` (called at lines 285, 359, 408).
- **Orphan labels (Tier C):**
  - `eq:bayes` (line 118) is labeled but never `\ref`'d. Either reference it
    once in §2.1 prose (e.g., "Equation~\ref{eq:bayes} is the standard
    posterior decomposition; …") or remove the label.
  - `sec:introduction`, `sec:waveforms`, `sec:summaries`, `sec:wallclock` are
    labeled but never `\ref`'d. Standard practice — keep them in case the
    galley wants cross-references; none of these is harmful.
- **Numbered equations with no label and no reference (Tier C):**
  - lnB Bayes-factor equation (line 280–282)
  - Heterodyne speedup factors equation (line 335–337)

  Both will appear as numbered displays (eq (4), eq (5)) but the numbers are
  never cited. Two clean options: (i) demote both to `\begin{equation*}`
  (unnumbered display) since neither is referenced; (ii) leave as-is —
  it's standard to number display equations for legibility even without
  back-reference. The prompt's "each numbered equation referenced at least
  once" criterion suggests (i); the journal style allows either.
- **Figure count: 7. Table count: 4.** All caption blocks are
  self-contained at 29–93 words; no figure caption requires the body text
  to interpret. Order matches the prose mention order in §3, §4, §5.

---

## 5. Tone and voice findings (Task 3)

The prior tone pass converged on the heavy defensive openers. Residual issues
cluster in §4.1, §5, §6.3, and Appendix A — all in the central science
paragraphs, which is the costliest place for hedging.

### 5a. Tier A — undermines a load-bearing claim

**§4.1, line 225**
Current:
> "The direct uniform-in-$d_L$ run leaves the posterior MAP essentially unchanged at $70.5\kmsmpc$ but materially broadens the 68 per cent HPD on the high side from $87.6$ to $103.8\kmsmpc$..."

Proposed:
> "The direct uniform-in-$d_L$ run leaves the posterior MAP unchanged at $70.5\kmsmpc$ but broadens the 68 per cent HPD on the high side from $87.6$ to $103.8\kmsmpc$..."

Justification: The MAP is binned at 1 km/s/Mpc resolution (§2.6) and the
value is identical to the baseline. "Essentially" implies wiggle that the
methodology rules out, and the abstract uses the unhedged "stays at" for
the same quantity. The body sentence should match the abstract's confidence.
This is the load-bearing "mode stays, tail moves" framing — strip the hedge.

### 5b. Tier C — hedging adverbs

| File:line | Current | Proposed | Why |
|---|---|---|---|
| line 95 | "favour a relatively low value" | "favour a low value" | "Relatively" not numerically meaningful; "significantly higher" in next clause sets the contrast. |
| line 229 | "captures only a small fraction of this shift" | "captures a small fraction of this shift" | The next clause quantifies at 17 %; "only" pre-disparages the number. |
| line 234 | "reaches only $95.9\kmsmpc$, short of" | "reaches $95.9\kmsmpc$, short of" | "Short of" already carries the comparison. |
| line 238 | "shifts the \hzero\ posterior only marginally" | "shifts the \hzero\ posterior modestly" | A factor-of-four tail change is not "only marginal". |
| line 365 | "reweighted samples are essentially blind to it" | "reweighted samples are blind to it" | Mechanism already nailed quantitatively above. |
| line 369 | "can in principle be combined with population-level analyses" | "can be combined with population-level analyses" | The runtime numbers earned the claim; "in principle" retreats from it. |
| line 406 | "close to indistinguishable…and depart only marginally" | "indistinguishable…and depart only in the high-\hzero\ tail" | Double hedge; commit. |

### 5c. Tier C — negative-space framing

| File:line | Current | Proposed | Why |
|---|---|---|---|
| line 283 | "Mode~B is neither significantly favoured nor disfavoured regardless of seed." | "the data are indifferent between Mode~A and Mode~B regardless of seed." | Double negative buried a clean finding. |
| line 361 | "this under-estimation does not change the cosmological interpretation: the GW170817 posterior is broad enough that..." | "the cosmological interpretation is robust to this under-estimation: both early- and late-Universe \hzero\ values lie within the GW170817 68 per cent HPD under any of the priors considered here." | Active polarity, same content. |
| line 361 (next sentence) | "risks a systematic bias in the direction of underestimating the prior contribution." | "will systematically underestimate the prior contribution." | "Risks…in the direction of underestimating" = three softeners; verb is the right tool. |
| line 401 | "sweeps that we ran but do not display as primary figures, since the central science finding…is unaffected by any of them." | "sweeps held in this appendix; the central science finding…survives every one of them." | Confident assertion in place of double negative. |

### 5d. Tier C — stutters from prior edits

| File:line | Issue | Proposed |
|---|---|---|
| line 234 | "prior… distance priors… prior variants… prior" (4× in one paragraph) | Drop "prior" from the penultimate clause: "the change in the high-\hzero\ tail across these variants is dominated by the prior, not by a data-driven update." |
| line 242 | "the shifts… the magnitude of the shift… a materially smaller shift" (3× "shift") | Replace middle two with "prior-induced change" and "value": "The point is that the magnitude of this prior-induced change is a property of the inference, and reweighting alone reports a materially smaller value than direct sampling does." |
| line 365 | "baseline volumetric prior and the target uniform-in-$d_L$ prior" | "baseline volumetric and target uniform-in-$d_L$ priors" — one plural. |
| line 369 | "prior sampling… target prior… prior-sensitivity rerun… prior-sensitivity studies" (4×) | Collapse: third → "such a rerun"; fourth → "these studies". |

### 5e. Tier C — passive constructions in science narrative

| File:line | Current | Proposed |
|---|---|---|
| line 97 | "recent reviews… are given by \citet{PalmeseMastrogiovanni2025}." | "\citet{PalmeseMastrogiovanni2025} review the methodology and its current status." |
| line 97 | "When the merger is accompanied by an electromagnetic counterpart that identifies a host galaxy, the host redshift can be combined with the gravitational-wave distance to infer \hzero…" | "If an electromagnetic counterpart identifies a host galaxy, its redshift combines with the gravitational-wave distance to give \hzero…" |
| line 162 | "KDEs are used only for two-dimensional corner contours…" | "We use KDEs only for two-dimensional corner contours…" (matches §2.6 first-person plural already in the paragraph). |

### 5f. Tier C — long noun phrases

| File:line | Current | Proposed |
|---|---|---|
| line 84 (abstract) | "relies on the assumption that switching from a volumetric luminosity-distance prior to a uniform-in-$d_L$ prior" | "assumes that switching from a volumetric to a uniform-in-$d_L$ luminosity-distance prior" |
| line 84 (abstract) | "the right default robustness tool for bright-siren cosmology, in place of post-hoc reweighting" | "the default robustness tool for bright-siren cosmology, replacing post-hoc reweighting" |
| line 97 | "A parallel line of work has argued that residual binary-viewing-angle uncertainty contributes…" | "\citet{SalvareseChen2024} argue that residual binary-viewing-angle uncertainty contributes…" |

The abstract rewrites also serve double-duty as word-count cuts (see §7
below).

### 5g. Tier C — pre-emptive concessions

None found that survived the prior pass. Search for "though this is
admittedly", "while we recognise that", "although we acknowledge", "in
fairness to" returns zero hits.

---

## 6. Citation completeness findings (Task 4)

**Result: clean.** No Tier-A issues. One optional Tier-B.

- `bibtex main` runs with **0 warnings, 0 errors**. All 45 bib entries are
  cited at least once in `main.tex` (no dead entries).
- All 7 prior-pass citation placements land correctly:
  `Palmese2024GW170817H0`, `SalvareseChen2024`, `PalmeseMastrogiovanni2025`
  at §1 line 97; `Vehtari2024PSIS`, `Payne2019Reweighting` at §4.1 line 236;
  `Chen2018Forecast` at §6.1 line 361; `Williams2021Nessai` at §1 line 103.
- All 14 checked 2024–2026 DOIs resolve correctly. The APS short-DOI
  `10.1103/dj7k-tk37` for `HuVeitch2025` is Crossref-registered and resolves
  to PRD **112**, 084039 (2025). `Wong2023Jim` DOI `10.3847/1538-4357/acf5cd`
  resolves to ApJ 958, 129 (2023). All 11 other 2024–2026 entries verified
  through Crossref.
- `Yang2026DataRelease`: GitHub repo at
  `https://github.com/ming-256/GW170817-bright-siren-H0` exists; README
  confirms it is the "GW170817 GPU-accelerated bright-siren H₀ — data and
  analysis release" companion to this paper. Hyperlinks render in the
  compiled PDF.
- Author-list audit: every entry with `{others}` is a large-collaboration
  paper (LVK, JAX project, BlackJAX, Ashton2019Bilby, Pratten2021XPHM,
  Riess2016, Riess2022) where enumeration is impractical. Mooley 2018
  is already enumerated to 10 authors matching Crossref exactly.

**Tier B (optional cosmetic):** `SalvareseChen2024` bib entry currently
carries only an arXiv eprint; the published version has DOI
`10.3847/2041-8213/ad7bbc`. Either keep arXiv-only (the citation is fully
resolvable as-is) or add the ApJL DOI for consistency with how the other
journal articles are recorded. Recommend adding it for clean galley
proofs but not blocking.

---

## 7. MNRAS technical compliance findings (Task 5)

### 7a. Abstract word count — **Tier A** (the load-bearing compliance issue)

`detex main.tex | wc -w` on the abstract block gives **257 words**; a
hand-tokenised count gives **259**. MNRAS limit is **250**. Either way, ~7–9
words over.

Two of the §5f rewrites above eliminate exactly nine words from the
abstract opener and closer:
- Opener: "relies on the assumption that switching from a volumetric
  luminosity-distance prior to a uniform-in-$d_L$ prior" →
  "assumes that switching from a volumetric to a uniform-in-$d_L$
  luminosity-distance prior" (saves 7 words).
- Closer: "the right default robustness tool for bright-siren cosmology,
  in place of post-hoc reweighting" → "the default robustness tool for
  bright-siren cosmology, replacing post-hoc reweighting" (saves 2 words).

Net cut: **9 words**, landing the abstract at 248–250 words. Recommend
applying both as the cleanest tone-and-count fix.

### 7b. Keywords — **Tier B** (per prompt's response-letter checklist)

Current: `gravitational waves -- methods: data analysis -- cosmological
parameters -- stars: neutron -- software: data analysis`.

The prompt notes "methods: data analysis" and "software: data analysis" are
partly redundant. Recommend replacing the latter with `distance scale`:

> `gravitational waves -- methods: data analysis -- cosmological parameters -- stars: neutron -- distance scale`

`distance scale` is the standard MNRAS keyword for H₀-axis papers and ties
the keyword set to the paper's actual deliverable.

### 7c. Title — **Tier C**

- Full title: 17–18 words ("Rapid Hubble constant inference from GW170817
  using GPU-accelerated nested sampling: prior sensitivity and the limits
  of post-hoc reweighting"). MNRAS preferred ≤15 but not enforced; the
  current title accurately previews the paper. No change recommended.
- Short title (running head): `[Rapid GW170817 \hzero inference]` — 4 words,
  reads cleanly. ✓.

### 7d. Figure captions — **PASS**

All seven figure captions are self-contained (29–93 words; mean 60). Each
identifies the event, the waveform, the prior, the panels (where multi-panel),
the comparison reference (where applicable), and the literature overlays.
None requires the body text to interpret. ✓.

### 7e. Table captions — **PASS**

All four table captions are self-contained (29–93 words). Each identifies
the prior set, n_live, the column meanings, and any cross-references.
Table 5 caption notes "All numbers generated by `Plots/build_paper_tables.py`
from the canonical sample CSVs" which is good provenance practice. ✓.

### 7f. Equation numbering — **Tier C**

5 numbered equations, 1 unnumbered. Two of the 5 are numbered without
being referenced (lnB at line 280, speedup factors at line 335). Three
options:
- (i) Leave as-is. Standard practice; the numbers act as visual anchors.
- (ii) Demote both to `equation*` for strict prompt compliance with "each
  numbered equation referenced at least once".
- (iii) Add a back-reference to the lnB equation in the next sentence
  ("Equation X gives lnB(B/A) = -0.66 for seed 0…") — this would also let
  the §6.3 sentence at line 365 cite the numerical evaluation directly.

Recommend (iii) for the lnB equation (adds value) and (ii) for the speedup
equation (it's a static lookup table, not a derivation).

### 7g. Bibliography style — **PASS**

`\bibliographystyle{mnras}` at line 392. Compiled output renders cleanly:
no doubled author lists, no missing journal names, all author-year fields
populated.

### 7h. Acknowledgements — **PASS**

Line 384 carries Handley Lab, HDPSP (MP), Google Cloud GCP397499138 (this work),
and the LVK data acknowledgement with the four canonical data-release
citations. No `TODO`, no placeholders.

### 7i. Data Availability — **PASS**

Line 389 cites `Yang2026DataRelease` (live GitHub repo), the LVK GWTC-1 and
H₀ data releases, and the GWTC-2.1 Zenodo deposit for GW150914. The
GitHub URL renders as a hyperlink in the PDF; no `TODO` strings.

---

## 8. Narrative arc verdict (Task 6)

End-to-end read confirms the structural arc holds. Per the six sub-questions:

**6a. Intro motivation.** The §1 framing reads forward-looking, not as a
critique of Abbott+2017: lines 96–98 set up the H₀ tension and the bright-siren
programme, line 99 introduces the GW170817 result with citations to the
recent reanalyses (Mooley, Hotokezaka, Nicolaou, Mukherjee, Howlett & Davis,
Palmese 2024, Salvarese & Chen) before pivoting to the prior-sensitivity
question, line 100 sets up the LD–ι degeneracy and the prior question
mechanistically, line 101 names the reweighting assumption explicitly, and
lines 103–105 land the methodological setup with the fast-PE landscape
citations. ✓.

**6b. §3 validation.** Subsection 3.1 (lines 169–171, plus Table 1) provides
the LVK XPHM cross-check; subsection 3.2 (lines 193–195) provides the
heterodyned-vs-unheterodyned consistency check on GW170817. Both report
quantitative agreement with the public references. The reader trusts the
§4 pipeline. ✓ (modulo the line-171 σ-ratio Tier-A fix above).

**6c. §4.1 central result clarity.** The "Direct-vs-reweighted comparison"
sub-paragraph (lines 225–234) delivers the tail / median / MAP triple in
order, followed by the 17 % capture-fraction equation, followed by the
ΔlnZ context, followed by the IS-diagnostic sub-paragraph (lines 236+).
This is the right ordering and the right granularity. ✓.

**6d. §5 bimodality as mechanism.** §5 opens with the cross-waveform
robustness check (lines 247–256) before isolating modes (lines 258–283),
then closes with the explicit "this is the mechanism behind the
reweighting capture fraction" sentence at line 285. The mechanism lands as
the explanation, not as a separate finding. ✓.

**6e. §6 runtime as enabling.** §6.3 is now titled "Where reweighting is
sufficient" (not "Where reweighting fails", which would frame as critique);
§6.4 frames runtime as "now permits such reruns routinely"; §6.5 is the
trimmed "Scope and natural extensions" with two forward-looking items
(no apologetic frame). ✓.

**6f. Conclusions match abstract.** Numerically: every headline number in
the Conclusions (line 379) matches the abstract verbatim
(0.017→0.159, 17 %, 77.6→87.6, 70.5, ΔlnZ≲1.8, |lnB|<1). Tonally: both end
on "the runtime budget makes direct prior-sensitivity reruns the right
default for bright-siren cosmology". ✓.

**Narrative-arc verdict:** holds. Only narrative drag I found was the
"essentially unchanged" hedge at line 225, which is the Tier-A tone item
above and the only sentence that pulls against the abstract's confident
framing. Fix that and the arc is publication-ready.

---

## 9. Sanity-check status (Task 7)

| Check | Result |
|---|---|
| Clean compile from scratch (`rm -f main.aux main.bbl main.blg main.log main.out main.fdb_latexmk main.fls && latexmk -pdf main.tex`) | ✓ 11 pages, no warnings of substance |
| `??` in compiled PDF (`pdftotext main.pdf - \| grep -nE '\?\?\|<<UNDEFINED>>'`) | ✓ none |
| `TODO` / `FIXME` / `XXX` / `placeholder` / `\textcolor{red}` / `???` in `main.tex` | ✓ none (only the standard `Accepted XXX. Received YYY` editorial placeholder at line 74) |
| Same grep on `references.bib` | ✓ none |
| Spell-check | aspell unavailable in this env; manual eyeball scan of body and captions returned no obvious typos |
| `paper-reproduce/paper/main.tex` (reproducible mirror) in sync with `mnras_paper/main.tex` | ✗ **OUT OF SYNC** — see §9a |

### 9a. paper-reproduce mirror diff — **Tier B**

`diff mnras_paper/main.tex paper-reproduce/paper/main.tex` returns **137
lines of diff**. The `paper-reproduce/paper/main.tex` is an earlier snapshot
that pre-dates several recent passes:

- Cites `Planck2016` (not `Planck2020`), `Cornish2013` (not `Cornish2010`)
- Lacks the §1 reanalysis paragraph that introduces Mooley/Hotokezaka/
  Nicolaou/Mukherjee/Howlett & Davis/Palmese2024/SalvareseChen2024
- Lacks the `\citet{PalmeseMastrogiovanni2025}` review cite at §1
- Lacks the `Williams2021Nessai` and `HuVeitch2025` cites at §1
- Still has the §6.3 sky-prior subsection mentioned in the header comment
- Abstract is the older "we test this assumption directly" version with
  inflated `1.78×10^5` sample count number, before the §4.1 IS-failure
  paragraph rewrite
- `\graphicspath` is the simpler `{{figures/}}` form

Per the prompt's instruction ("flag the diff but do not auto-sync"), this is
flagged here for the user to sync at their discretion. The mirror is the
reproducible artifact; the canonical version is `mnras_paper/main.tex`. A
single `cp mnras_paper/main.tex paper-reproduce/paper/main.tex` (after any
chosen edits land) would resolve this, along with copying any updated
`references.bib`, table includes, and figures the mirror needs.

Tier B because it affects the reproducible artifact, not the submitted PDF.

---

## 10. Suggested edits, ranked

### Tier A — substantive (fixes a claim or inconsistency)

#### A-1. Abstract word count (line 82–83)
Current abstract is 257–259 words; MNRAS limit is 250. Apply the two §5f
rewrites below to drop nine words.

**Edit 1 (opener of abstract):**
```
- ... relies on the assumption that switching from a volumetric luminosity-distance prior to a uniform-in-$d_L$ prior can be implemented by post-hoc reweighting of the baseline posterior samples, rather than by re-running the inference under the target prior.
+ ... assumes that switching from a volumetric to a uniform-in-$d_L$ luminosity-distance prior can be implemented by post-hoc reweighting of the baseline samples, rather than by re-running the inference under the target prior.
```
Saves 7 words and removes a buried noun phrase.

**Edit 2 (closer of abstract):**
```
- The runtime budget makes full-sample prior-sensitivity reruns the right default robustness tool for bright-siren cosmology, in place of post-hoc reweighting.
+ The runtime budget makes full-sample prior-sensitivity reruns the default robustness tool for bright-siren cosmology, replacing post-hoc reweighting.
```
Saves 2 words.

Total: −9 words, lands at ~250.

#### A-2. §3.1 σ-ratio digits (line 171)
The q and ι ratios in the body sentence are inconsistent with both the
displayed widths and the higher-precision CSV values. M_c ratio also
misrounds.

```
- ... $\sigma(\mathcal{M}_c)=1.02$ vs $1.01\,M_\odot$, $\sigma(d_L)=84$ vs $85\,\rm Mpc$, $\sigma(q)=0.10$ vs $0.11$, and $\sigma(\iota)=0.41$ vs $0.35\,\rm rad$ (ratios $1.01$, $0.99$, $0.87$, $1.11$); the largest residual is on the precession-sensitive $\iota$.
+ ... $\sigma(\mathcal{M}_c)=1.02$ vs $1.00\,M_\odot$, $\sigma(d_L)=84$ vs $85\,\rm Mpc$, $\sigma(q)=0.10$ vs $0.11$, and $\sigma(\iota)=0.41$ vs $0.35\,\rm rad$ (ratios $1.02$, $0.99$, $0.89$, $1.17$); the largest residual is on the precession-sensitive $\iota$.
```

#### A-3. §5.1 TF2 wall-clock (line 329)
Paper says ~9 min; no TF2 run in the inventory takes more than 4.1 min.

```
- The primary heterodyned GW170817 \hzero\ analysis with \IMRX\ and $n_{\rm live}=5000$ on the LVK-matched prior set completes in $\approx 13$\,min on a single NVIDIA A100 GPU; the corresponding \TF\ run takes $\approx 9$\,min.
+ The primary heterodyned GW170817 \hzero\ analysis with \IMRX\ and $n_{\rm live}=5000$ on the LVK-matched prior set completes in $\approx 13$\,min on a single NVIDIA A100 GPU; the corresponding \TF\ run takes $\approx 4$\,min.
```

#### A-4. §4.3 Table 4 TF2 lnZ (line 317)
Paper carries 487.25 ± 0.09 for the TF2 baseline row; the canonical
evidence table records 486.90 ± 0.10 for the TF2 baseline.

```
- \TF\ (family check)          & 68.5 & $[61.4,89.3]$ & $[56.9,125.6]$ & $0.065$ & $487.25\pm0.09$ \\
+ \TF\ (family check)          & 68.5 & $[61.4,89.3]$ & $[56.9,125.6]$ & $0.065$ & $486.90\pm0.10$ \\
```

#### A-5. §4.1 "essentially unchanged" hedge (line 225)
The abstract says "stays at"; the body sentence should match.

```
- The direct uniform-in-$d_L$ run leaves the posterior MAP essentially unchanged at $70.5\kmsmpc$ but materially broadens the 68 per cent HPD on the high side from $87.6$ to $103.8\kmsmpc$...
+ The direct uniform-in-$d_L$ run leaves the posterior MAP unchanged at $70.5\kmsmpc$ but broadens the 68 per cent HPD on the high side from $87.6$ to $103.8\kmsmpc$...
```

### Tier B — citation hygiene & numerical drift

#### B-1. §4.1 sample counts and efficiencies (line 236)
N_samples and efficiencies overstate by ~3 % and ~0.5–0.7 pp respectively.

```
- From the same $1.78\times 10^{5}$-sample \IMRX\ baseline we measure $n_{\rm eff}=30{,}695$ (efficiency $17.3\,\%$); the directly sampled uniform-in-$d_L$ run has $n_{\rm eff}=37{,}022$ from its own $2.01\times 10^{5}$-sample draw (efficiency $18.4\,\%$), while ...
+ From the same $1.73\times 10^{5}$-sample \IMRX\ baseline we measure $n_{\rm eff}=30{,}695$ (efficiency $17.8\,\%$); the directly sampled uniform-in-$d_L$ run has $n_{\rm eff}=37{,}022$ from its own $1.94\times 10^{5}$-sample draw (efficiency $19.1\,\%$), while ...
```

#### B-2. Keywords (line 87)
Replace `software: data analysis` with `distance scale` per the
response-letter checklist.

```
- gravitational waves -- methods: data analysis -- cosmological parameters -- stars: neutron -- software: data analysis
+ gravitational waves -- methods: data analysis -- cosmological parameters -- stars: neutron -- distance scale
```

#### B-3. Appendix A IMR MAPs (line 408)
The four IMR MAPs (75.2, 74.1, 72.3) use a legacy KDE-MAP convention, not
the canonical 1-km/s/Mpc grid used in Table 5. Either re-derive on the
canonical grid:

```
- ... \IMR\ companion full sweep.} The four-variant prior sensitivity sweep on \IMR\ gives baseline $\hzero^{\rm MAP}=71.5\kmsmpc$, $P(\hzero>120)=0.076$; uniform-in-$d_L$ direct $\hzero^{\rm MAP}=75.2\kmsmpc$, $P=0.281$; reweighted $\hzero^{\rm MAP}=74.1\kmsmpc$, $P=0.195$; $\sigmavp=250\kms$ $\hzero^{\rm MAP}=72.3\kmsmpc$, $P=0.067$.
+ ... \IMR\ companion full sweep.} The four-variant prior sensitivity sweep on \IMR\ gives baseline $\hzero^{\rm MAP}=71.5\kmsmpc$, $P(\hzero>120)=0.076$; uniform-in-$d_L$ direct $\hzero^{\rm MAP}=73.5\kmsmpc$, $P=0.281$; reweighted $\hzero^{\rm MAP}=71.5\kmsmpc$, $P=0.195$; $\sigmavp=250\kms$ $\hzero^{\rm MAP}=70.5\kmsmpc$, $P=0.067$.
```

(or annotate the line to indicate the MAP convention).

#### B-4. Table 1 caption (line 175) — LVK centroid source
Recommend changing the parenthetical numbers to match the C01:IMRPhenomXPHM
medians the figure actually overlays (30.4, 0.85, 463, 2.63), or cite the
GWTC-2.1 catalogue table for the 30.7/440 numbers explicitly.

```
- ... The LVK GWTC-2.1 \XPHM\ public PE \citep{Abbott2021GWTC2p1,GWTC2p1_GW150914_Zenodo} reports $\mathcal{M}_c\approx 30.7\,M_\odot$, $q\approx 0.83$, $d_L\approx 440\,\rm Mpc$, $\iota\approx 2.62\,\rm rad$ for direct comparison.
+ ... The LVK GWTC-2.1 \XPHM\ public PE \citep{Abbott2021GWTC2p1,GWTC2p1_GW150914_Zenodo} reports $\mathcal{M}_c\approx 30.4\,M_\odot$, $q\approx 0.85$, $d_L\approx 463\,\rm Mpc$, $\iota\approx 2.62\,\rm rad$ for direct comparison.
```

#### B-5. `paper-reproduce/paper/main.tex` mirror out of sync
137 lines of diff with `mnras_paper/main.tex`; older citations, missing
literature-pass §1 paragraph, sky-prior subsection in the header comment.
After Tier-A fixes land, copy the updated `main.tex`, `references.bib`,
table includes, and any figures the mirror needs to keep the reproducible
artifact in step. Do not sync until the user authorises.

#### B-6. `SalvareseChen2024` ApJL DOI (cosmetic)
Bib entry currently arXiv-only; add `doi = {10.3847/2041-8213/ad7bbc}` for
consistency with the other journal articles. Citation already resolves.

### Tier C — cosmetic / tone

All Tier-C tone edits from §5 above. Highest-leverage of these
(if applying a tight set rather than all 17):

- C-1. §1 line 95 — drop "relatively" before "low value".
- C-2. §4.1 line 229 — drop "only" before "a small fraction".
- C-3. §4.1 line 234 — drop "only" before "$95.9\kmsmpc$".
- C-4. §4.1 line 238 — "only marginally" → "modestly".
- C-5. §4.1 line 242 — break the "shift… shift… shift" stutter (proposed
  in §5d above).
- C-6. §4.1 line 234 — break the "prior… prior… prior" stutter (proposed
  in §5d above).
- C-7. §6.3 line 365 — drop "essentially" before "blind to it"; collapse
  "baseline volumetric prior and the target uniform-in-$d_L$ prior" to
  "baseline volumetric and target uniform-in-$d_L$ priors".
- C-8. §6.1 line 361 — replace "does not change" / "risks a systematic
  bias in the direction of underestimating" with active-voice rewrites
  (proposed in §5c above).
- C-9. §6.5 line 369 — drop "in principle"; break the four-`prior`
  stutter.
- C-10. Appendix A line 401 — flip "ran but do not display… unaffected" to
  "held in this appendix… survives every one" (proposed in §5c above).
- C-11. Appendix A line 406 — drop "close to" before "indistinguishable".
- C-12. §1 line 97 — make `PalmeseMastrogiovanni2025` an active-voice
  `\citet`.
- C-13. §2.6 line 162 — switch "KDEs are used" to "We use KDEs".
- C-14. Orphan label `eq:bayes` (line 118) — either add a `\ref{eq:bayes}`
  in §2.1 prose or delete the label.
- C-15. Numbered-but-unreferenced equations at lines 280 and 335 —
  consider demoting to `equation*` for strict "every numbered equation
  referenced" compliance.

---

## Applied edits during this pass

Per the prompt's default behaviour ("propose first, apply only when
explicitly authorised by the user"), only one edit was applied during
this pass, as a precondition for evaluating Tasks 2–7:

- **Preamble graphicspath (line 38–42 → 38–43):** added
  `{figures/}{../mnras_paper/figures/}` to the existing `\graphicspath`,
  so that `figures/bimodality_imr_vs_imrx.pdf` resolves. Without this
  fix the paper does not compile and the rest of the review cannot be
  performed. No figures regenerated; the canonical PDF is in
  `mnras_paper/figures/` and was used as-is.

Post-edit compile re-verified clean: 11 pages, no warnings of substance,
all refs/citations resolved, no `??` in the rendered PDF.

All other findings above are **proposed**, not applied. The user can
authorise the Tier-A set, the Tier-A+B set, or the full set; recommend
applying Tier-A in one batch, re-compiling, then deciding on B and C.
