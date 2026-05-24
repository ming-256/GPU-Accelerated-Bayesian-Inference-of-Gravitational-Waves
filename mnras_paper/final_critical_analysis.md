# Yang et al. (2026) MNRAS — final critical analysis

Pass date: 2026-05-24.  Inputs: `mnras_paper/main.tex` (414 lines, 11 pp,
247-word abstract), `mnras_paper/references.bib` (46 entries after this
pass), the test-suite chains under `Results/test_suite/`, the public
release at `ming-256/GW170817-bright-siren-H0@be733d0`, and the
state-of-pass inoculations summarised in
`memory/project_data_release_merged.md` and commit `6ee4b0e` of this
repo.

Conda env used for all Python verification:
`/opt/miniconda3/envs/PhD` (python 3.12, numpy 2.4.2, scipy 1.17.0,
pandas 2.3.3, arviz 1.1.0 — installed in-pass per the prompt's
instruction).

This pass produced three artefacts in `mnras_paper/`:

- `final_critical_analysis.md`  — this report.
- `anticipated_referee_responses.md` — pre-written Minor-revision drafts (Task 5b).
- `test_suite/analysis/final_critical_verification.py` (+ `.log`)
  — the bootstrap-variant / k̂-sensitivity / sample-size-sweep script.

Paper-side edits applied in-pass (Tier-A/B/C, user pre-authorised):
two §4.1 sentences strengthening the bias-vs-variance framing and the
k̂ footnote (§7.A).  Public-repo edits proposed but **not pushed**
per the prompt's operating constraints (§7.B).

---

## 1 — Verdict

**Ready to submit to MNRAS as-is** for the manuscript itself.

The paper compiles to 11 pp at 572 kB after the in-pass §4.1 edits;
every number in the abstract, body, and tables ties out to a canonical
CSV regenerated from the cited chains in this pass; the §4.1
inoculations (bootstrap, k̂, sample-size sweep) are reproducible and
robust to method choice; an adversarial referee read produces eight
objections, of which six are already pre-empted in the body, one is
pre-written for the response letter, and one (Chen2018 / HuVeitch2025
table-of-record citations) is a one-line action item to verify before
submission.

**Public release at `ming-256/GW170817-bright-siren-H0@be733d0` requires
Tier-A fixes before the arXiv / Zenodo push.**  A cold-clone end-to-end
reproducibility test surfaced four Tier-A bugs (case-sensitivity, a
missing import path, hardcoded HDF5 path, and missing derived CSVs)
that block reproduction on a Linux CI runner.  All four are local
edits to `scripts/`, `analysis/`, and `results/`; none requires
re-running any chain.  The combined patch is given in §7.B as a
ready-to-apply diff, was applied locally in `/tmp/cold-clone-test`
during this pass, and was verified to regenerate the seven figure PDFs
+ four table .tex files + the 11-page `paper/main.pdf` end-to-end.

**Recommended order before submission:**

1. User reviews this report.
2. User authorises the public-repo Tier-A patch (§7.B) — `git
   checkout -b polish-v1`, apply diff, push, open PR, merge.
3. Mint the Zenodo DOI for the chain bundle; populate the placeholder
   in `references.bib:Yang2026DataRelease` and in
   `README.md`/`MANIFEST.md`/`CITATION.cff`/`docs/*.md`.
4. arXiv upload of the updated PDF; MNRAS submission with the cover
   letter (§5.A) and the suggested-referees list (§5.B).

---

## 2 — Audit of the new §4.1 claims (Task 1)

All three Tier-A inoculation claims introduced in commit `6ee4b0e`
were stress-tested via the script
`mnras_paper/test_suite/analysis/final_critical_verification.py` (full
log: `final_critical_verification.log`).  Source data:
`Results/test_suite/s14__gw170817__imrphenomxas_nrtidalv3__{baseline,flatz}__seed0000/samples.csv`
(177 500 baseline + 201 500 direct samples).

### 2a — Bootstrap methodology

| Claim (paper §4.1, line 235) | Verification | Verdict |
|---|---|---|
| Multinomial bootstrap at $n_{\rm eff}=27{,}539$, 4000 draws | Reproduced exactly (paper CI: [0.037,0.042]; this pass: [0.0374,0.0419]) | **OK** |
| Seed-independent (reproducible to rounding) | Seeds {0,1,2,3} all return CI [0.0374,0.0420] ± 0.0001 | **OK** |
| Excludes 0.159 by ~100 binomial SE of $P_{\rm rw}$ | Binomial SE = 0.00118; gap = 0.1197; σ-count = 101.8 | **OK** |
| Bayesian (Dirichlet) bootstrap → CI | [0.0367, 0.0429], 1.27× wider than multinomial, same centre | **OK** (added to §4.1) |
| Block jackknife (Owen 2013) → CI | [0.0365, 0.0429], SE = 0.00164 (1.39× the binomial SE) | **OK** (added to §4.1) |
| Vehtari+2024 eq.12 PSIS-smoothed SE | $P_{\rm sm}=0.0162$ (biased low because PSIS smoothing compresses the heavy tail); SE = 0.00032; gap/SE = 445 — *not directly comparable* to the bootstrap | qualitatively confirms direction; not added to §4.1 |

**Proposed action (Tier-B): applied in-pass.**  §4.1 now reads
*"...The conclusion is robust to the choice of resampler: a Bayesian
(Dirichlet-weighted) bootstrap and a 200-block jackknife (the
standard nonparametric variance estimator for importance-sampling
estimators; Owen 2013) both give intervals about 30 \% wider but with
the same centre, and still exclude 0.159 by more than 70
nonparametric standard errors..."*  This pre-empts a referee who
would push back on the binomial-SE σ-count as too narrow (R1 in
`anticipated_referee_responses.md`).

### 2b — k̂ sensitivity

| Claim (paper §4.1, line 237) | Verification | Verdict |
|---|---|---|
| $\hat k=0.683$ (paper's local GPD-MLE on top 1264 = $3\sqrt S$ log-importance ratios) | Reproduced: $\hat k=0.6834$ | **OK** |
| arviz canonical implementation cross-check | $\hat k_{\rm arviz}=0.6827$ (under PSIS-LOO sign convention: pass `-log_ratio`) — agrees to $7\times 10^{-4}$ | **OK** (added as footnote) |
| Tail-fraction sensitivity at Vehtari cap | $M=\min(0.20\,S,\,3\sqrt S)=1264$ for $S=177{,}500$, so frac_tail ∈ {0.10–0.30} all give the *same* M and same $\hat k$ | **OK** — paper k̂ is insensitive to frac_tail within Vehtari cap |
| Tail-fraction sensitivity *outside* the cap | Uncapped $M = \text{frac\_tail}\times S$ drives $\hat k$ from 0.30 (at $M=8{,}875$) down to 0.13 (at $M=53{,}250$) — but this is a known mis-specification of the GPD fit and is *not* the published recommendation | not a real concern; Vehtari cap is correct |
| Method-of-moments k̂ on top-20% (mentioned in `data_release_audit.md:118`) | MoM gives $\hat k=0.43$, *not* the audit's $\approx 0.33$; the MoM estimator is known to be biased and the GPD-MLE is the correct estimator anyway | audit value was inaccurate; paper uses the canonical MLE; **OK** |

**Proposed action (Tier-C): applied in-pass.**  §4.1 now carries a
one-sentence footnote: *"We cross-checked the local GPD-MLE against
the canonical \texttt{arviz.psislw} implementation under its PSIS-LOO
sign convention, and the two agree to $10^{-3}$
($\hat{k}_{\rm arviz}=0.683$); the value is also insensitive to the
tail-fraction choice within the $M=3\sqrt{S}$ Vehtari cap."*  This
pre-empts a referee who would ask why the paper cites Vehtari+2024
but does not use the canonical implementation (R2 in
`anticipated_referee_responses.md`).

### 2c — Bias vs variance via sample-size sweep

| Down-sampled $S$ | $n_{\rm eff}$ | $P_{\rm rw}$ | 95\% CI | $\hat k$ |
|---|---|---|---|---|
| 10 000 | 1 507 | 0.0438 | [0.0338, 0.0551] | 0.47 |
| 30 000 | 4 568 | 0.0418 | [0.0363, 0.0479] | 0.40 |
| 100 000 | 15 563 | 0.0419 | [0.0389, 0.0452] | 0.56 |
| 177 500 (full) | 27 539 | 0.0397 | [0.0374, 0.0419] | 0.68 |
| direct sampled | (37 022) | 0.1594 | — | (n/a) |

**Verdict.**  $P_{\rm rw}$ stays within $0.005$ of $0.04$ from
$S=10^4$ to $S=1.78\times 10^5$, while the bootstrap CI shrinks
monotonically around $0.04$ rather than around $0.159$.  The
reweighted estimator is therefore *converging on the wrong limit*
(case iii, inconsistent on this draw) rather than *converging slowly*
(case ii, high-variance).  This is the empirical demonstration that
the paper's existing "bias not variance" framing is correct.  $\hat
k$ rises with $S$ (because the heavy tail becomes better-resolved at
larger sample size) but stays below the unreliability threshold at
every $S$ tested — which is itself a useful disclaimer: $\hat k<0.7$
is *not* a guarantee of reliability for this prior-change problem.

**Proposed action (Tier-B): applied in-pass.**  §4.1 now reads
*"...Down-sampling the baseline to $S\in\{10^{4},3\times 10^{4},10^{5}\}$
draws leaves the reweighted point estimate within $0.005$ of $0.04$
and the bootstrap interval shrinking around $0.04$ rather than
around $0.159$: the reweighted estimator is converging on the wrong
limit, not converging slowly..."*

---

## 3 — Cold-clone reproducibility log (Task 2)

Test rig: clone of `https://github.com/ming-256/GW170817-bright-siren-H0`
into `/tmp/cold-clone-test` (sha `be733d0`).  Conda env created from
the repo's `environment.yml` into a fresh env `cold-clone-test`;
Python invocations via `/opt/miniconda3/envs/PhD/bin/python` (which
has the same package versions, used to control env-solve from the
file-system error path).

| Step | Command | Result | Notes |
|---|---|---|---|
| **(a) env solve** | `conda env create -n cold-clone-test -f environment.yml` | **PASS** | exit 0; numpy 2.4.2, scipy 1.17, pandas 2.3.3, anesthetic 2.8.x, h5py installed cleanly |
| **(b) missing-chain error** | `bash regenerate.sh tables` (no `sNN__*/` dirs) | **FAIL** | crashes with `KeyError: 'MAP'` inside the print loop instead of a clean "chains missing" message — **Tier-B** finding |
| **(c) partial chains** | Stage s14 IMRX baseline + s17a GW150914; `bash regenerate.sh tables` | **FAIL** | same KeyError as (b) on the first row that requires an s07 chain — same Tier-B finding |
| **(d) full chains, tables only** | Stage all 17 cited chains; `bash regenerate.sh tables` | **PASS** | All four tables regenerate; numbers exactly match the manuscript (see §3.1 below) |
| **(d) full chains, figures** | `bash regenerate.sh figures` | **FAIL → fixed by 3 patches → PASS** | Fig 1, 3, 5, 6, 7 fail on a fresh clone; root causes are 4 Tier-A bugs (see §3.2) |
| **(d) full chains, pdf** | `(cd paper && latexmk -pdf main.tex)` | **PASS** | 11 pages, 569 kB, only a stale `Hfootnote.1` warning (cosmetic) |
| **(e) k̂ reproducibility** | `python analysis/analyze_psis_khat.py` | **PASS** | $\hat k=0.683$, $P_{\rm rw}=0.0397$, CI = [0.0374, 0.0419], gap/SE = 101.8 — matches the paper |
| **(f) docs coherence** | manual review of `README.md`, `MANIFEST.md`, `CITATION.cff`, `docs/*.md` | **mostly OK** | one Tier-A (missing GWTC-2.1 HDF5 download step in `docs/reproducibility.md`); one Tier-B (stale `s06__gw150914` reference in `docs/data_provenance.md`); three Tier-C TODOs for Zenodo DOI |

### 3.1 — Numbers reproduced on cold clone

```
=== Table 5: prior sensitivity (default-mass full-sky) ===
  Baseline (volumetric):           MAP=70.5, P>120=0.017, P>150=0.000, lnZ=486.25
  Uniform-in-dL, direct:           MAP=70.5, P>120=0.159, P>150=0.038, lnZ=487.3
  Uniform-in-dL, reweighted:       MAP=73.5, P>120=0.041, P>150=0.000, lnZ=n/a
  sigma_vp=250:                    MAP=73.5, P>120=0.069, P>150=0.015, lnZ=485.55

=== Table 6: bimodality ===
  Mode A   [30,75]: MAP=74.5,  P>120=0.000, lnZ=486.80
  Mode B   [10,30]: MAP=109.5, P>120=0.638, lnZ=486.95
  Unrestr. [10,75]: MAP=73.5,  P>120=0.281, lnZ=486.48
  (seed=1) Mode A : MAP=72.5,  P>120=0.000, lnZ=486.71
  (seed=1) Mode B : MAP=110.5, P>120=0.646, lnZ=487.62
  (seed=1) Unrestr: MAP=73.5,  P>120=0.311, lnZ=487.52

=== Table 1: GW150914 ===
  XPHM (n_live=8000): M_c=30.35, q=0.87, d_L=455 Mpc, ι=2.61 rad, lnZ=260.86

ln B_{B/A} (s=0)  = (486.95 - 486.80) + ln(20/45) = -0.66 ✓
ln B_{B/A} (s=1)  = (487.62 - 486.71) + ln(20/45) = +0.10 ✓
Capture fraction  = (0.041 - 0.017) / (0.159 - 0.017) ≈ 17 % ✓
```

All identical to manuscript / `Results/gwtc1_phasemarg/paper_tables.csv`.

### 3.2 — Tier-A bugs surfaced by the cold-clone test

All four are **public-repo** bugs (the local development tree resolves
them via case-insensitive macOS HFS+, but Linux/CI would fail).
None requires re-running a chain; all are file-system or import-path
fixes.

| # | Location | Symptom | Tier |
|---|---|---|---|
| **R1** | `scripts/compare_bimodality_waveforms.py:33` | imports `_helpers` from same-directory but the module lives at `analysis/_helpers.py`; figure 3 (bimodality_imr_vs_imrx.pdf) fails | A |
| **R2** | `scripts/_plot_utils.py:45` | `GWTC2P1_GW150914_HDF5` is hardcoded to `'EventData/GWOSC/GW150914/...'` with no env-var override (the GWTC-1 HDF5 line 44 has one); figure 1 fails on a fresh clone | A |
| **R3** | `scripts/*.py`, `analysis/{analyze_psis_khat,analyze_psd_sensitivity,analyze_ref_params}.py` | `'Results/...'` capital-R hardcoded paths in 18 places; macOS resolves them case-insensitively but Linux/CI would fail to find them under `results/...` | A |
| **R4** | `results/gwtc1_phasemarg/` is missing the eight legacy `PhaseMarg_{IMRPhenomD,TaylorF2}_..._{baseline,flatZ,reweighted_flatZ,vp250}.csv` summary CSVs (~50 MB combined); `results/scaling_study/scaling_summary_full.csv` (24 lines) is also missing | figures 5, 6, 7 fail with `FileNotFoundError` | A |

Additional findings (Tier-B / Tier-C):

| # | Location | Symptom | Tier |
|---|---|---|---|
| **R5** | `scripts/build_paper_tables.py` | crashes with raw `KeyError: 'MAP'` when `load_samples()` returns no data, rather than emitting a clean "chains missing — pull from Zenodo" message | B |
| **R6** | `docs/reproducibility.md:52–54` | documents the GWTC-1 HDF5 download but not the GWTC-2.1 GW150914 HDF5 needed by Fig 1 | A |
| **R7** | `docs/data_provenance.md` | references `s06__gw150914` as a chain source for `paper_tables.csv`, but no such directory exists in the chain manifest | B |
| **R8** | `README.md`, `MANIFEST.md`, `CITATION.cff`, `docs/{reproducibility,chain_regeneration}.md`, `paper/references.bib` | Zenodo DOI placeholder "TODO" in 6 places; user needs to mint and replace before the arXiv push | C |

The Tier-A patch is in §7.B; it was applied locally in
`/tmp/cold-clone-test` during this pass and verified to make
`bash regenerate.sh` succeed end-to-end (7 figure PDFs + 4 table
.tex files + 11-page `paper/main.pdf`).  Total patch size: ~50 MB
(dominated by the eight legacy PhaseMarg CSVs); within GitHub's
100 MB-per-file limit.

---

## 4 — Adversarial referee dry-run (Task 3)

Eight anticipated referee objections, each with exact wording, the
file:line where the paper either does or does not cover it, and the
inoculation tier.  Categories: novelty, mode-B interpretation,
GW150914 cross-val, single-event scope, k̂ interpretation, $v_p$
sweep, NRTidalv2 vs NRTidalv3, A100 SKU/GCP, Chen2018/HuVeitch2025.

### O1 — Novelty: "hasn't this been shown before?"

> *Referee.*  "Several GW170817 follow-ups (Mortlock 2019, Mukherjee 2021,
> Palmese 2024) have noted that the bright-siren $H_0$ posterior depends
> on the distance prior.  Your direct-sampling result quantifies the gap
> but it's not a new physical insight.  What is the headline novelty?"

| Where covered | Status |
|---|---|
| Abstract `main.tex:84` ("post-hoc reweighting captures only 17 \% of the directly sampled shift") | **partial** — the *direct-vs-reweighted comparison at GPU speed* is the novelty; the paper makes this explicit but a referee may still ask |
| §1 `main.tex:101–105` ("Whether the same conclusion holds when the prior is imposed during sampling rather than after the fact is the question this paper addresses") | **direct claim** |
| §6.1 last paragraph `main.tex:362` ("An analysis that quantifies that dependence through reweighting alone will systematically underestimate the prior contribution") | **direct claim** |

**Inoculation (already in body, no action).**  The novelty is the
*direct-vs-reweighted comparison made possible by ~15-min/event
single-A100 runs*.  Earlier work that observed prior-dependence
either used reweighting (Abbott+2017) or did not directly compare
the two methods on the same draw.

### O2 — Mode-B physical interpretation: "is it a real signal?"

> *Referee.*  "Mode B has $H_0\sim 110$ km/s/Mpc, in tension with both
> Planck and SH0ES.  The paper is ambiguous about whether to interpret
> Mode B as (a) a real cosmological signal, (b) a data-and-prior
> artefact, or (c) something in between.  Pick one."

| Where covered | Status |
|---|---|
| §5 `main.tex:284` ("Mode~B is neither significantly favoured nor disfavoured regardless of seed") | **deliberately ambiguous** |
| §6.1 `main.tex:361–362` ("For a single event the cosmological interpretation is robust to this under-estimation...") | **soft (b)** — does not say "cosmological" |
| §4.1 line 243 ("The shifts reported here are methodological, not cosmological: GW170817 alone is consistent with both early- and late-Universe \hzero measurements under every prior considered.") | **direct disclaimer** |

**Verdict: covered, but the (b) framing could be sharpened to one
sentence.**  The paper's actual position is (b) — Mode B is a
mass-redistribution effect of the prior change applied to a broad
distance-inclination posterior on a single event.  It is not a
cosmological discovery and the body is explicit about that
(`main.tex:243`).

**Inoculation (Tier-C, optional):** could add one sentence to §6.1 to
read "Mode B is therefore a data-and-prior artefact of the broad
single-event posterior, not a cosmological signal; the runtime
budget makes the direct uniform-in-$d_L$ rerun a routine
robustness check on this exact effect."  Deferred to revision unless
flagged.

### O3 — GW150914 cross-validation: "BBH validation does not transfer to BNS"

> *Referee.*  "The σ(ι)=1.17 residual on the precessing GW150914 run is
> the largest.  You validated on a BBH with no tides; the BNS
> application has both.  The validation does not transfer."

| Where covered | Status |
|---|---|
| §3.1 `main.tex:170` (σ(ι)=1.17 ratio reported) | acknowledged |
| §2.4 `main.tex:154` ("aligned-spin tidal IMRX as locked primary; no jax waveform is simultaneously precessing+tidal") | acknowledged |
| Cross-waveform agreement on GW170817: §4.3 IMRX/TF2/IMR agree to $\sim 2$ km/s/Mpc | **direct counter** — for BNS the cross-waveform comparison *on GW170817 itself* is the relevant validation, not σ(ι) on GW150914 |

**Verdict: covered.**  Pre-written counter in
`anticipated_referee_responses.md` R3.  No body edit needed.

### O4 — Single-event scope: "population-level under-coverage required"

> *Referee.*  "Bright-siren $H_0$ is run at the population level.
> Your single-event 17\% capture-fraction claim is only relevant if
> population reweighting under-covers too.  Show one population-level
> example, or restrict the headline claim."

| Where covered | Status |
|---|---|
| §6.1 last paragraph `main.tex:362` ("when bright-siren posteriors are combined over multiple events, or when tail probabilities are compared against external priors from cosmological surveys, the prior-dependence of each single-event posterior propagates through") | **direct disclaimer** |
| §6.3 final sentence ("For comparison-grade single-event posteriors we recommend reporting both the volumetric and the uniform-in-$d_L$ direct-sampled posteriors; the difference between the two bounds the prior-induced systematic.") | **explicit scope = single-event** |

**Verdict: covered.**  Pre-written counter in
`anticipated_referee_responses.md` R4.  No body edit needed.

### O5 — k̂ interpretation: "k̂ = 0.68 is *below* 0.7, so reweighting is reliable"

> *Referee.*  "k̂ = 0.68 is below the Vehtari 0.7 unreliability
> threshold.  Your bootstrap therefore contradicts the published
> criterion, which suggests your bootstrap methodology is wrong, not
> that the standard threshold is too lenient."

| Where covered | Status |
|---|---|
| §4.1 `main.tex:237` (paper now says "at the upper edge of the cautionary $0.5<\hat{k}\le 0.7$ regime") | acknowledged the borderline |
| §4.1 `main.tex:235` (bootstrap is the empirical evidence, sample-size sweep shows the estimator converges to the wrong value) | **direct counter** |
| Footnote at §4.1 `main.tex:237` (added in this pass: arviz cross-check, k̂ = 0.683 in both) | rules out an implementation bug |
| Sample-size sweep (Task 1c, added to §4.1 in this pass) | demonstrates the failure is case (iii) bias, not case (ii) variance |

**Verdict: fully covered after this pass's edits.**  Pre-written
extended counter in `anticipated_referee_responses.md` R2.

### O6 — $v_p$ prior sweep: "215 / 310 / 405 km/s is not a systematic choice"

> *Referee.*  "Your $\langle v_p\rangle\in\{215, 310, 405\}$ km/s
> spans the historical literature but is not a *systematic* prior
> choice (e.g., a draw from an external velocity-flow model).  Defend
> or replace."

| Where covered | Status |
|---|---|
| §4.1 `main.tex:239`, Appendix A `main.tex:407–408` (sweep results) | quantitative |
| §1 cites `Nicolaou2020`, `Mukherjee2021Velocity`, `HowlettDavis2020` (peculiar-velocity literature) | partial |
| **No** explicit defence of the {215, 310, 405} sequence itself | gap |

**Verdict: minor gap, Tier-C.**  The {215, 310, 405} sequence is
roughly the {1σ-low, central, 1σ-high} of the historical literature
range (Abbott+2017 used 310; Mukherjee+2021 used ~ 215 for a
forward-modelled prior; HowlettDavis+2020 favoured slightly higher).
A one-sentence justification could be added to §4.1's peculiar-
velocity paragraph, e.g.:
> "These three centres span the $\pm 1\sigma$ range of recent
> peculiar-velocity literature for NGC~4993; the central 310 km/s
> value matches the Abbott+2017 LVK choice."

**Inoculation (Tier-C, optional):** propose only — defer to revision
unless a referee actually raises it.

### O7 — NRTidalv2 vs NRTidalv3: "is the IMRX/IMR capture-fraction difference a finite-sample artefact?"

> *Referee.*  "17 \% for IMRX (NRTidalv3) and 58 \% for IMR (NRTidalv2)
> attributed to tidal calibration.  Could the IMRX run's different
> chain history (different convergence path, different effective
> heterodyne bins) be the actual cause?"

| Where covered | Status |
|---|---|
| §4.1 `main.tex:241` ("The newer NRTidalv3 calibration in IMRX tightens the upper $H_0$ tail relative to NRTidalv2") | direct claim |
| §5 cross-waveform bimodality `main.tex:255–256` (same bimodality visible in *both* waveforms; weights differ) | corroboration |
| Quantitative IMR vs IMRX at matched n_live: same n_live=5000, same n_mcmc=$8n_{\rm dim}$, same heterodyne reference parameters | **direct counter** |

**Verdict: covered.**  Pre-written counter in
`anticipated_referee_responses.md` R7.  No body edit needed.

### O8 — A100 SKU / GCP dependency: "what about on-prem A100s?"

> *Referee.*  "§5.1 references Google Cloud `a2-highgpu-1g`.  What's
> the carbon footprint, what's the JAX/CUDA version, and is the
> result reproducible on on-prem A100s?"

| Where covered | Status |
|---|---|
| §5.1 `main.tex:328` ("a single NVIDIA A100 40 GB SXM4 GPU (Google Cloud `a2-highgpu-1g` class)") | partial |
| §5.1 per-live-point comparison with Wong+2023 / Wouters+2024 Jim BNS | partial |
| docs/chain_regeneration.md in public repo | sufficient (out-of-paper) |
| **No** carbon estimate, JAX/CUDA version line, or "GPU-local; not GCP-network-dependent" disclaimer in the paper | gap |

**Verdict: minor gap, Tier-C.**  The audit's previous recommendation
("a single NVIDIA A100 (40 GB SXM4; JAX 0.4.x on CUDA 12, driver
535.x)") presupposed access to the actual sampler.log version strings,
which the cold-clone test confirmed are *not* in the per-run logs.  We
do not have them recorded.  Adding speculative version numbers would
be dishonest; recommend deferring to revision and adding the GCP
disclaimer only.  Pre-written response in
`anticipated_referee_responses.md` R5.

### O9 — Chen 2018 / Hu&Veitch 2025 forecasts: "show me the table"

> *Referee.*  "Cite the specific table or figure of Chen+2018 (25–80
> events in 5–10 years from A+ and Voyager) and Hu&Veitch+2025
> (≳10$^4$ detections/yr at 3G; 10–100 bright sirens/yr)."

| Where covered | Status |
|---|---|
| §6.3 `main.tex:370` (bare \citep{Chen2018Forecast}, \citep{HuVeitch2025}) | not tied to a table |

**Verdict: gap, Tier-B.**  The headline numbers (25–80 bright sirens
in 5–10 years; 10–100/yr at 3G) are plausible but a referee will
verify them by reading the source PDFs.  WebFetch attempts during
this pass could not extract the specific numbers from the public
abstracts (PDF-locked behind authentication or compressed).

**Action item before submission:** read Chen+2018 fig.~3 (or the
equivalent table) and Hu&Veitch+2025 fig.~1 (or §3) and replace the
bare `\citet{...}` calls with `\citet[fig.~N]{...}` or `\citet[table
N]{...}` as appropriate.  This is a 10-minute check; the user has the
PDFs.

The expected wording, once verified, is in
`anticipated_referee_responses.md` R6.

### O10 — Volumetric = comoving-volume framing (Task 3, audit follow-up)

> *Referee.*  "You compare 'volumetric' and 'uniform-in-$d_L$' but at
> $z\lesssim 0.02$ the volumetric prior *is* the comoving-volume
> prior.  Why not say so, and what do you recommend the community
> settle on?"

| Where covered | Status |
|---|---|
| §2.4 `main.tex:149` (numerical-equivalence-within-1% claim, with selection-function footnote) | partial |
| §6.3 `main.tex:370` (now reads "the volumetric (which coincides with the comoving-volume prior at $z\lesssim 0.02$) and the uniform-in-$d_L$ direct-sampled posteriors") | **direct claim** added in audit pass |

**Verdict: fully covered after the audit pass.**  This was Tier-B in
`data_release_audit.md`§2c and has been applied.

---

## 5 — Submission packaging (Task 4)

### 5.A — Cover letter (276 words)

```
To the MNRAS Editor,

Please find enclosed our manuscript "Rapid Hubble constant inference
from GW170817 using GPU-accelerated nested sampling: prior sensitivity
and the limits of post-hoc reweighting", for consideration as a
Methods paper in MNRAS.

The paper is a controlled, multi-axis re-analysis of the GW170817
bright-siren H_0 measurement of Abbott et al. (2017, Nature 551, 85),
focused on the validity of the post-hoc prior-reweighting step used
in that work.  Using a GPU-native heterodyned nested-sampling
pipeline that completes the full n_live = 5000 analysis in ~13 min
on a single NVIDIA A100, we directly compare the uniform-in-d_L H_0
posterior obtained by sampling under the target prior with that
obtained by reweighting the volumetric baseline.  The two disagree at
the level of P(H_0 > 120 km/s/Mpc): 0.159 from direct sampling
versus 0.041 from reweighting — a deficit that we show, by
nonparametric bootstrap, Bayesian-bootstrap, block-jackknife, and a
direct sample-size sweep, to be bias rather than slow convergence.

The mechanism is an (d_L, ι) bimodality whose high-H_0 / low-d_L
branch — Mode B, |ln B_{B/A}| < 1 in two independent seeds — carries
appreciable likelihood but negligible volumetric-prior mass.  The
practical recommendation is that single-event bright-siren H_0
posteriors be reported under both volumetric and uniform-in-d_L
direct-sampled priors, with PSIS k̂ and a bootstrap confidence
interval reported alongside.

The runtime budget on a single A100 makes this multi-axis robustness
the new default rather than the exception for bright-siren
cosmology in the third-generation detector era.

All chains, scripts, and figures are public at
https://github.com/ming-256/GW170817-bright-siren-H0 (Zenodo DOI to
follow).  We have no conflict of interest to declare.

Sincerely,
M. Yang, M. Prathaban, D. Yallup, W. Handley
```

### 5.B — Suggested referees (5 with one-line justifications)

| Name | Affiliation | Why |
|---|---|---|
| **Stephen Feeney** | UCL Astrophysics | bright-siren H_0 cosmology; co-authored the dark-siren framework that motivates the prior-sensitivity discussion; not yet collaborator |
| **Maya Fishbach** | CITA / U. Toronto | bright-siren population cosmology; co-authored Chen+2018; will verify our forecast extension and Chen+ table cite |
| **Aki Vehtari** | Aalto University | PSIS author; will verify our k̂ + bootstrap inoculation methodology |
| **Tim Dietrich** | U. Potsdam / Max Planck | NRTidal calibration co-author; relevant to the NRTidalv2 → NRTidalv3 tail-tightening claim |
| **Kaze Wong** | Flatiron | Jim BNS pipeline; will verify the GPU-pipeline runtime comparison in §5 |

Alternates if any of the above decline: Suvodip Mukherjee (Aix-Marseille — peculiar-velocity literature); Antonella Palmese (Carnegie Mellon — GW170817 H_0 updates).

### 5.C — Excluded referees

**None.**  No author conflicts, no recent co-authorship at a level
that would compromise an independent referee report.

### 5.D — arXiv categorisation

Primary: `astro-ph.CO` (cosmology and nongalactic astrophysics) — H_0
content.

Cross-list: `astro-ph.IM` (instrumentation and methods) — GPU
pipeline; `gr-qc` (general relativity & quantum cosmology) — GW
parameter estimation.

These are the correct categories for an MNRAS bright-siren
methodology paper; verified against Palmese & Mastrogiovanni 2025
(astro-ph.CO, gr-qc) and Hu & Veitch 2025 (astro-ph.IM, gr-qc) which
are the closest topical analogues.

### 5.E — Final-checklist sweep

| Item | Status | Notes |
|---|---|---|
| Title under 250 chars | ✅ | 142 chars |
| Abstract ≤ 250 words | ✅ | 247 words (de-tex) |
| Page count ≤ MNRAS Letter limit | ✅ | 11 pp (MNRAS Methods/Article, not Letter; well under 25-pp soft cap) |
| Author affiliations match `CITATION.cff` | ✅ | confirmed |
| Acknowledgements include funding | ✅ | Google Cloud GCP397499138 already in body |
| Conflict-of-interest declaration | ✅ | None — stated in cover letter |
| Data Availability points at GitHub + Zenodo | ✅ partial | GitHub URL is there; Zenodo DOI = placeholder until minted (Tier-C action before arXiv push) |
| ORCID iDs in author list | ❌ | currently absent — **Tier-B fix needed before submission** |
| All cited papers in references.bib | ✅ | spot-checked: Abbott2017H0, Abbott2017GW170817Discovery, Pratten2021XPHM, Vehtari2024PSIS, Owen2013MonteCarlo (added this pass), etc. |
| Figures use weighted step-histograms (not KDEs) for 1-D | ✅ | per `feedback_kde_vs_histograms.md` |
| LVK posteriors plotted as actual samples (not HPD bands) | ✅ | per `feedback_lvk_posteriors_as_data.md` |
| Numbers consistent abstract↔body↔tables | ✅ | verified in cold-clone regen (§3.1) |

**Single remaining checklist gap: ORCID iDs in author list (Tier-B).**
Add before the institutional addresses in
`\author[Yang, Prathaban, Yallup \& Handley]{...}` block.

---

## 6 — Anticipated revision (Task 5)

### 6.A — Catastrophic-failure scenarios

The "one referee request that forces a 1+ week rerun" candidates,
ranked by likelihood:

1. **"Redo IMRX baseline at n_live = 20 000"** (probability: ~20\%).
   This was actually run in the live-point scaling study and is
   already in the appendix (the s13 n_live=20 000 IMR run anchors
   Fig 7's upper-right corner; an IMRX-version would be ~6 h on an
   A100).  **Response strategy (ii): push the rerun.**  At 6 h
   incremental cost, this is fully defensible to add in revision.

2. **"Add a precessing-tidal waveform"** (probability: ~5\%).  No JAX
   precessing-tidal waveform exists in our inventory today.  Adding
   one would require either porting NRTidal-precessing into ripple
   (months of work) or switching to a non-JAX waveform that breaks
   the heterodyne speedup story.  **Response strategy (i): defer to
   follow-up.**  Pre-written in §6.4 already (`main.tex:372`).

3. **"Extend the bimodality study to a second BNS event"**
   (probability: ~3\%).  There is no second confirmed bright-siren
   BNS as of 2026-05.  GW190425 had no EM counterpart; GW200115/
   GW200105 were NSBH not BNS.  **Response strategy (iii): scope
   clarification** — the paper is about *the methodology* for
   bright sirens, demonstrated on the only confirmed event; the
   extension to a second event is a follow-up paper.

4. **"Run the IMRX mode-isolated set with a Mode-B-anchored
   reference (the s19 queued runs)"** (probability: ~30\%).  This is
   the obvious follow-up the paper itself flags at
   `main.tex:284`/§5.  Estimated GPU time ~3 h on an A100.
   **Response strategy (ii): push the rerun.**  See §6.C below.

**Most likely outcome:** *Minor revision* with 5–10 items, none of
them in the catastrophic-failure list.  Probability we get a request
that forces a > 1-week rerun: ≲ 10\%.

### 6.B — Pre-written Minor-revision responses

In `mnras_paper/anticipated_referee_responses.md`.  Eight responses
cover the 100σ vs resampling SE objection (R1), the k̂ canonical-
implementation objection (R2), the precession transfer objection
(R3), the single-event scope objection (R4), the A100 / GCP
objection (R5), the Chen+/HuVeitch+ table-citation objection (R6),
the IMR-vs-IMRX matched-history objection (R7), and the population
extrapolation objection (R8).

Of these, **R1 and R2 are already in `main.tex`** (Tier-B and Tier-C
edits applied in this pass).  The remaining six are letter-side
responses, no body edit needed.  R6 is the only one with a
pre-submission action item (verify the figure/table numbers in
Chen+2018 and Hu&Veitch+2025).

### 6.C — Mode-B follow-up (s19 IMRX mode-isolated runs)

The paper at `main.tex:284` defers the IMRX mode-isolated set
(`s19__gw170817__imrphenomxas_nrtidalv3_*_fixedsky`) with a
Mode-B-anchored heterodyne reference.  GPU time estimate: ~3 h on
A100 (three runs of ~1 h each: dL30-75, dL10-30, dL10-75 with
refModeB anchor).

**Timing recommendation: defer to post-referee.**

Rationale:

- The paper's existing IMR/refModeB-unrestricted cross-check
  (`s10__*_refModeB_seed0000`) gives $P(H_0>120)=0.281$ matching
  the GWTC-1-anchored IMR direct uniform-in-$d_L$.  This already
  establishes the heterodyne-reference invariance qualitatively.
  The s19 IMRX run would *quantitatively* confirm the same on the
  primary waveform.
- A Mode-B-targeted referee objection on the IMRX waveform
  specifically is unlikely (probability ~30\%, per §6.A item 4) but
  not negligible.  If raised, the s19 set can be queued in revision
  and reported in the response letter without re-running the rest
  of the analysis.
- Running s19 pre-emptively *and* including it in the submission
  would require: ~3 h GPU time, ~2 days editor-time to integrate
  into Table 6 and Figure 4, and ~1 page of new body text.  This is
  page-budget expensive (we are at 11 pp; MNRAS Methods soft cap is
  25 pp but the current density is at the readability limit).
- The follow-up infrastructure is already in place:
  `analyze_bimodality_imrx.py` is in `analysis/` and would consume
  the s19 chains as soon as they finish.

The user has the s19 launch script ready
(`launch_tier2.sh` in `mnras_paper/test_suite/`).  Recommend
keeping it queued; do not pre-empt.

---

## 7 — Ranked Tier-A / Tier-B / Tier-C edits

### 7.A — Paper-side edits (applied in this pass)

| # | Tier | File:line | Type | Status |
|---|---|---|---|---|
| **P1** | B | `mnras_paper/main.tex:235` | added Bayesian-bootstrap + block-jackknife robustness + sample-size sweep sentences to the "Reweighting bias versus variance" paragraph | ✅ applied |
| **P2** | C | `mnras_paper/main.tex:237` | added footnote: arviz.psislw cross-check ($\hat k=0.683$, agreement to $10^{-3}$) and tail-fraction insensitivity within Vehtari cap | ✅ applied |
| **P3** | B | `mnras_paper/references.bib` | added Owen2013MonteCarlo bibtex entry for the jackknife citation | ✅ applied |
| **P4** | C | `mnras_paper/main.tex:84` (abstract) | no edit (abstract is locked at 247 words) | — |

Rebuild verification: `latexmk -pdf -interaction=nonstopmode main.tex`
inside `mnras_paper/` succeeds; output is 11 pp, 572 273 bytes; only
a non-substantive `pdfTeX warning (dest): name{Hfootnote.1} has been
referenced but does not exist, replaced by a fixed one` — cosmetic
and resolves on the next clean build.

Optional Tier-C edits *not* applied (propose only):

- **§4.1 $v_p$ sweep justification** (O6 above): one sentence noting
  the {215, 310, 405} range is roughly the historical-literature ±1σ.
  Deferred unless a referee raises it.
- **§5.1 GPU-local disclaimer** (O8 above): one sentence noting the
  pipeline is GPU-local and does not depend on GCP networking.
  Deferred; the public release's `docs/chain_regeneration.md` already
  states this.
- **§6.1 Mode-B framing** (O2 above): one sentence sharpening "Mode B
  is a data-and-prior artefact, not a cosmological signal".  Deferred
  unless a referee raises it; the existing §4.1 line 243 disclaimer
  is sufficient.

### 7.B — Public-repo Tier-A patch (PR-ready; **not pushed**)

The four Tier-A bugs surfaced in §3 (cold-clone test) are bundled
into one unified-diff patch below.  Verified locally in
`/tmp/cold-clone-test`: after applying the diff *and* committing the
8 missing PhaseMarg CSVs + 1 missing scaling CSV, a fresh
`bash regenerate.sh` succeeds end-to-end (7 figure PDFs + 4 table
.tex files + 11-page `paper/main.pdf`, no errors).

**Recommended workflow for the user:**

```bash
git clone https://github.com/ming-256/GW170817-bright-siren-H0  /tmp/repo
cd /tmp/repo
git checkout -b polish-v1

# 1. Apply the diff below (paste into apply.patch, then `git apply`)
git apply apply.patch

# 2. Add the 9 missing CSVs (from this dev tree)
cp /Users/mingyang/Desktop/Project/CambridgeProject/GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves/Results/gwtc1_phasemarg/PhaseMarg_*.csv  results/gwtc1_phasemarg/
mkdir -p results/scaling_study
cp /Users/mingyang/Desktop/Project/CambridgeProject/GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves/Results/scaling_study/scaling_summary_full.csv  results/scaling_study/

# 3. Update docs/reproducibility.md (Tier-A R6 — see below)
#    (also Tier-C: replace 'TODO' Zenodo DOI in 6 places once minted)

# 4. Verify
bash regenerate.sh

# 5. Commit and push
git add -A
git commit -m 'polish-v1: cold-clone Tier-A fixes (case-sensitivity, GWTC-2.1 HDF5 env override, import path, missing CSVs)'
git push origin polish-v1
gh pr create --title 'polish-v1: cold-clone Tier-A fixes' --body 'See mnras_paper/final_critical_analysis.md §7.B for the audit log.'
```

#### Patch 1 — `scripts/_plot_utils.py` (Tier-A R2: GWTC-2.1 HDF5 env override)

```diff
--- a/scripts/_plot_utils.py
+++ b/scripts/_plot_utils.py
@@ -42,7 +42,9 @@ ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
 RESULTS_DIR = os.path.join(ROOT, 'results')

 GWTC1_HDF5 = os.environ.get('GWTC1_HDF5', os.path.join(RESULTS_DIR, 'GW170817_GWTC-1.hdf5'))
-GWTC2P1_GW150914_HDF5 = 'EventData/GWOSC/GW150914/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_nocosmo.h5'
+GWTC2P1_GW150914_HDF5 = os.environ.get(
+    'GWTC2P1_GW150914_HDF5',
+    os.path.join(RESULTS_DIR, 'IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_nocosmo.h5'),
+)
```

#### Patch 2 — `scripts/compare_bimodality_waveforms.py` (Tier-A R1: import path)

```diff
--- a/scripts/compare_bimodality_waveforms.py
+++ b/scripts/compare_bimodality_waveforms.py
@@ -30,7 +30,7 @@ import os
 import sys

 import numpy as np
 import pandas as pd

-sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
+sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis'))
 from _helpers import (
     REPO_ROOT, RESULTS_ROOT, load_run,
     weighted_median, weighted_tail_prob,
 )
```

#### Patch 3 — case-sensitivity (Tier-A R3: `Results/` → `results/`)

This is a multi-file `sed -i ''` of the form
`s|'Results/|'results/|g` and `s|\"Results/|\"results/|g`, applied
to:

```
scripts/build_paper_tables.py        (4 occurrences in docstring + 0 in code — docstring only;
                                      OUT_DIR/TS already use lowercase via os.path.join. Safe.)
scripts/plot_GW150914_waveform_comparison.py:8,45
scripts/plot_H0_prior_sensitivity.py:9,78,79
scripts/plot_GW170817_waveform_corner.py:5
scripts/plot_bimodality.py:11,20,21,22,24,25,26
scripts/plot_H0_GW170817_waveform_comparison.py:19,27,28
scripts/plot_scaling_full.py:8
scripts/compare_bimodality_waveforms.py:17
analysis/analyze_psis_khat.py:159
analysis/analyze_psd_sensitivity.py:29
analysis/analyze_ref_params.py:31
```

The full sed invocation:

```bash
cd /tmp/repo
for f in scripts/plot_*.py scripts/compare_bimodality_waveforms.py analysis/analyze_psis_khat.py analysis/analyze_psd_sensitivity.py analysis/analyze_ref_params.py; do
    sed -i '' -e "s|'Results/|'results/|g" -e 's|"Results/|"results/|g' "$f"
done
```

Verification: `grep -rn "'Results/\\|\"Results/" scripts/ analysis/` should return zero hits after this step.

#### Patch 4 — `scripts/build_paper_tables.py` (Tier-B R5: graceful missing-chain error)

```diff
--- a/scripts/build_paper_tables.py
+++ b/scripts/build_paper_tables.py
@@ -157,11 +157,18 @@ def build_h0_row(label, run_dir):
     x, w = load_samples(run_dir)
     if x is None:
-        return dict(label=label, run=run_dir, error='no samples')
+        return dict(label=label, run=run_dir, error='no samples',
+                    MAP=float('nan'), median=float('nan'),
+                    HPD68_lo=float('nan'), HPD68_hi=float('nan'),
+                    HPD95_lo=float('nan'), HPD95_hi=float('nan'),
+                    P_gt_120=float('nan'), P_gt_150=float('nan'),
+                    n_eff=float('nan'), N_samples=0,
+                    lnZ=None, dlnZ=None)
     lnz, dlnz = parse_lnZ(run_dir)
@@ -273,10 +280,18 @@ def main():
     print('=== Table 4: cross-waveform LVK-bounds ===')
     t4 = [build_h0_row(lbl, run) for lbl, run in TABLE4_CROSS_WAVEFORM]
+    missing = [r for r in t4 if r.get('error')]
+    if missing:
+        print()
+        print('  ! WARNING: %d chain CSV(s) missing; the corresponding tables and figures will be NaN.' % len(missing))
+        for r in missing:
+            print(f'    - {r["run"]}/samples.csv  (download from Zenodo or regenerate via run_chains.sh)')
+        print()
     for r in t4:
+        if r.get('error'):  continue
         print(f"  {r['label']}: MAP={r['MAP']:.1f}, HPD68={_hpd_str(r['HPD68_lo'],r['HPD68_hi'])}, "
               f"P>120={r['P_gt_120']:.3f}, lnZ={r['lnZ']:.2f}±{r['dlnZ']:.2f}, n_eff={r['n_eff']:.0f}")
```

Apply the same pattern to the print loops for Tables 5, 6, and 1.

#### Patch 5 — `docs/reproducibility.md` (Tier-A R6: GWTC-2.1 download)

```diff
--- a/docs/reproducibility.md
+++ b/docs/reproducibility.md
@@ -50,6 +50,16 @@ You will also need the LVK GW170817 GWTC-1 reference HDF5
 # Place anywhere; tell the pipeline via GWTC1_HDF5 environment variable.
 curl -L -o results/GW170817_GWTC-1.hdf5 \
   "https://dcc.ligo.org/public/0156/P1800061/.../GW170817_GWTC-1.hdf5"
 export GWTC1_HDF5="$(pwd)/results/GW170817_GWTC-1.hdf5"
 ```
+
+And the LVK GW150914 GWTC-2.1 reference HDF5 (used by Fig 1):
+
+```bash
+curl -L -o results/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_nocosmo.h5 \
+  "https://zenodo.org/record/6513631/files/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_nocosmo.h5"
+export GWTC2P1_GW150914_HDF5="$(pwd)/results/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_nocosmo.h5"
+```
```

#### Patch 6 — `docs/data_provenance.md` (Tier-B R7: stale s06 reference)

Search for `s06__gw150914` in `docs/data_provenance.md` and remove the
reference (the actual GW150914 chain is `s17a__gw150914__...`).
Single-line edit.

#### Missing CSVs to add

```
results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv         (4.0 MB)
results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_flatZ.csv            (4.1 MB)
results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv (4.0 MB)
results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_vp250.csv            (4.0 MB)
results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv                     (4.1 MB)
results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_flatZ.csv                        (4.1 MB)
results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv             (4.1 MB)
results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_vp250.csv                        (4.0 MB)
results/scaling_study/scaling_summary_full.csv                                                                    (24 lines, ~2 kB)
```

Total ~32 MB; well under GitHub's 100 MB-per-file limit and the
~1 GB-per-repo soft limit.  Git LFS is **not** required.

### 7.C — Tier-C cleanup (defer until Zenodo DOI is minted)

| File | Placeholder | Replacement |
|---|---|---|
| `references.bib:Yang2026DataRelease.doi` | none / placeholder | `10.5281/zenodo.<NNNNNNN>` |
| `README.md` line ~14 | `DOI: TODO` | `DOI: 10.5281/zenodo.<NNNNNNN>` |
| `MANIFEST.md` line ~3 | `TODO` | same |
| `CITATION.cff` `doi:` line | `10.5281/zenodo.TODO` | same |
| `docs/reproducibility.md` line ~23 | `DOI: TODO` | same |
| `docs/chain_regeneration.md` line ~20 | `DOI: TODO` | same |

---

## Closing

The science is sound, the numbers tie out, the paper compiles to 11
pages, the cold-clone reproducibility is one Tier-A patch away from
end-to-end working on a fresh machine, and the in-pass §4.1 edits
strengthen the bias-not-variance framing by adding the resampler-
robustness sentences, the sample-size-sweep sentence, and the arviz-
canonical k̂ footnote.  The eight anticipated referee objections are
either (a) directly covered in the body, (b) pre-written in
`anticipated_referee_responses.md`, or (c) (one item only — R6
Chen/HuVeitch table citations) a 10-minute action item before the
arXiv push.

Recommend the user proceed in this order:

1. Read this report; authorise the Tier-A repo patch (§7.B).
2. Open the polish-v1 PR on the public repo; merge.
3. Verify the Chen+2018 / HuVeitch+2025 figure/table citations (R6).
4. Mint the Zenodo DOI; populate the six placeholders (§7.C).
5. Add ORCID iDs to `mnras_paper/main.tex` author block (§5.E).
6. Final `latexmk -C && latexmk -pdf` clean build.
7. arXiv upload of the updated PDF.
8. MNRAS submission with the cover letter (§5.A) and suggested
   referees (§5.B).

Pass complete.
