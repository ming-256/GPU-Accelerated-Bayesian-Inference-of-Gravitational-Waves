# Critical analysis + data-release audit prompt — Yang et al. (2026) MNRAS submission

You are doing a combined critical-analysis-and-reproducibility pass on a
submission-ready MNRAS draft. The paper has already been through a
literature-positioning review (`literature_review.md`), a referee-response
revision (`referee_response.md`), a Tier-A/B citation pass, the closure of
three deferred minor referee items (m17/m19/m20), a tone pass, and a
final-pass review (`final_pass_review.md`) that landed five Tier-A fixes
(abstract word count, σ-ratios, TF2 wall-clock, TF2 lnZ, MAP hedge) plus
five Tier-B and ~15 Tier-C edits. The mnras_paper and paper-reproduce/paper
directories are now in sync.

Your job has two intertwined halves: (i) push the paper through an
adversarial-referee read to find substantive weaknesses the previous passes
did not surface; (ii) audit, clean up, and condense the data, scripts, and
artefacts into the public GitHub repository
`https://github.com/ming-256/GW170817-bright-siren-H0` so that a reader who
clones it can reproduce every paper claim under a single conda env in a
single coherent workflow.

You have web-search, web-fetch, Python (conda env `/opt/miniconda3/envs/PhD`),
working LaTeX (`latexmk -pdf` from inside `mnras_paper/`), `gh` for GitHub
operations, and full filesystem access to the project. Use them. Verify
rather than assume.

## The paper in one paragraph

`mnras_paper/main.pdf` (11 pages, MNRAS class, abstract 249 words).
Authors: Yang, M.; Prathaban, M.; Yallup, D.; Handley, W. (2026), submitted.

GPU-native heterodyned nested-sampling re-analysis of the GW170817
bright-siren H₀ measurement of Abbott et al. (2017, Nature 551, 85). Central
claim: switching the distance prior from volumetric (`π(d_L) ∝ d_L²`) to
uniform-in-d_L by direct sampling raises `P(H₀ > 120 km/s/Mpc)` from 0.017 to
0.159 (binned MAP stays at 70.5; weighted median moves 77.6 → 87.6), while
post-hoc reweighting of the same baseline draws recovers only P=0.041 — about
17 % of the directly-sampled shift. The mechanism is a (d_L, ι) bimodality
whose high-H₀/low-d_L branch (Mode B; |lnB(B/A)|<1 in two independent seeds)
the volumetric prior assigns ~7 % of Mode A's mass. The reweighted-vs-baseline
n_eff comparison (27,317 vs 30,695 on the same draw) independently flags the
coverage failure. GW150914 cross-validates with XPHM; TaylorF2 cross-checks
the waveform axis on GW170817.

## State at the start of this pass — what's already done (do not redo)

- All previous-pass items closed (literature, referee-response, m17/m19/m20,
  tone pass, final-pass A+B+C edits all applied).
- `mnras_paper/main.tex` and `paper-reproduce/paper/main.tex` are in sync
  except for the intentional mirror-layout differences (graphicspath form,
  table-input paths, header comment phrasing).
- `references.bib` is identical between canonical and mirror; all 45 entries
  cited, all DOIs verified (2024–2026 entries spot-checked through Crossref).
- The numerical consistency sweep verified every number in the abstract /
  body / tables / conclusions against the underlying chain CSVs.
- The figure inventory is locked at six canonical PDFs (gw150914 corner,
  H0 prior sensitivity, bimodality cross-waveform check, main bimodality,
  H0 waveform comparison, scaling study — plus the GW170817 corner overlay,
  total seven figure floats; four table floats).

## Key locations

- `mnras_paper/main.tex` — canonical manuscript source
- `mnras_paper/main.pdf` — current build (11 pages, 249-word abstract)
- `mnras_paper/references.bib` — bibliography
- `mnras_paper/final_pass_review.md` — most recent pass output
- `mnras_paper/final_pass_prompt.md` — pre-existing prompt template (mirror this style)
- `mnras_paper/figures/` — figure source PDFs (`bimodality_imr_vs_imrx.pdf`,
  `seed_ensemble_lnZ.pdf`, `selection_term_Ns.pdf`, plus `figures/output/`
  and `figures/v2/` subtrees with auto-generated overlays)
- `mnras_paper/test_suite/` — analysis scripts, launch scripts, run
  catalogue (`run_catalog.csv`), session-plan markdowns
- `mnras_paper/test_suite/analysis/` — `analyze_*.py`,
  `compare_bimodality_waveforms.py`, `compile_test_suite_report.py`
- `mnras_paper/test_suite/scripts/` — `sN__*` launch scripts
- `Plots/build_paper_tables.py` — canonical table-and-summary generator;
  emits `Results/gwtc1_phasemarg/table{1,5,6}*.tex` plus `paper_tables.csv`,
  `paper_diagnostics.csv`, `evidence_table.csv`
- `Plots/_plot_utils.py` — shared plotting helpers
- `Plots/plot_*.py` — per-figure generators (`plot_bimodality.py`,
  `plot_GW170817_waveform_corner.py`, `plot_H0_GW170817_waveform_comparison.py`,
  `plot_H0_prior_sensitivity.py`, `compare_bimodality_waveforms.py`,
  `plot_scaling_study.py` if present, etc.)
- `Results/gwtc1_phasemarg/` — derived summary CSVs, table .tex includes,
  figure PDFs, `evidence_table.csv`, `paper_diagnostics.csv`
- `Results/test_suite/` — per-run directories
  (`s04`–`s19` × waveform × variant × seed), each with `samples.csv`,
  `sampler.log`, `config.json`, `finish.json`
- `paper-reproduce/paper/` — local mirror of the manuscript (already in sync)
- `paper-reproduce/scripts/` — if present; otherwise the scripts live in
  `Plots/` and `mnras_paper/test_suite/analysis/`
- `EventData/GWOSC/GW150914/` and `EventData/GWOSC/GW170817/` — LVK strain
  + PSD + reference PE deposits the analysis reads
- Public repo: `https://github.com/ming-256/GW170817-bright-siren-H0`
  — verify its current state before designing the cleaned layout. Note the
  paper cites this URL via `Yang2026DataRelease`.

## Tasks

### Task 1 — adversarial critical analysis

Re-read `mnras_paper/main.tex` end-to-end as if you were a hostile referee
with deep gravitational-wave parameter-estimation expertise and a default
prior of "this isn't novel enough for MNRAS". For every Task-1 finding,
give (file:line), the candidate referee objection, and either (i) the
counter-evidence already in the paper that pre-empts it, or (ii) a proposed
inoculation — a single sentence or short paragraph the authors could add.

Pressure-test at minimum the following. Add others if you find them.

a. **Bimodality as heterodyne-reference artefact.** §5 reports the Mode-B
   weight from a Mode-B-anchored heterodyne reference and an unrestricted
   GWTC-1-anchored cross-check. Is one cross-check enough? What would a
   referee say about the residual bias of the heterodyne expansion in a
   region that the reference waveform does not cover well? Look in
   `mnras_paper/test_suite/analysis/analyze_ref_params.py` and any sN
   directory with `refOptimize` in the name to see what was actually
   tested, and report whether the paper's claim ("the heterodyne-reference
   choice does not bias the Mode-A/Mode-B weight ratio", line ~283) is
   supported by sufficient evidence.

b. **n_eff as a coverage diagnostic.** §4.1 leans on Kish n_eff to flag
   the reweighting failure. A referee with PSIS chops will ask: is Kish
   n_eff actually the right diagnostic? The paper cites
   `Vehtari2024PSIS` and mentions k̂>0.7 as an alternative. Why not
   compute and report k̂ directly? Is the n_eff comparison even
   well-defined when the reweighted draw has a different effective
   sample distribution than the baseline NS draw? Verify whether
   `paper_diagnostics.csv` contains a k̂ column; if not, propose adding it.

c. **Distance-prior choice.** The paper compares volumetric and
   uniform-in-d_L. A referee will ask: why not a comoving-volume prior
   (Hogg 1999, eq.~30)? Why not a uniform-in-redshift prior? What's the
   forward-looking recommendation for the bright-siren community —
   pick a single prior and report it, or always report under the
   "two extremes" (volumetric and uniform-in-d_L) that the paper
   already gives? The §6 Discussion should address this.

d. **Mode-B Bayes-factor seed scatter.** Two seeds give lnB(B/A) =
   −0.66 and +0.10. Both satisfy |lnB|<1. But that's only 2 seeds.
   Would a third seed land outside that band? Is the unrestricted-run
   lnZ scatter of 1.04 between seeds (paper line ~283) consistent with
   the within-run ±0.1 figure under Gaussian assumptions? Compute the
   expected within-run-vs-between-run lnZ scatter and check.

e. **Locked-XAS choice with no tides+precession check.** The paper says
   "no waveform in our \jax\ inventory simultaneously includes precession
   and tides". A referee will ask: how much could a tides-with-precession
   waveform move the H₀ result? The §3.1 σ(ι) ratio is the precession-
   sensitive width (1.17), and the paper notes that as the largest
   residual. Is there a published estimate of the precession-induced
   H₀ bias for GW170817 (e.g., Finstad et al. 2018, Mooley 2018)?
   If yes, cite it. If no, say so and frame as an open question.

f. **Wall-clock claims are A100-specific.** §5.1 quotes wall-clock on a
   single A100. A referee will ask: which A100 (40 GB SXM4? 80 GB PCIe?)?
   What's the carbon footprint vs the matching CPU pipeline? Does the
   paper need a one-sentence model + framework + driver version line in
   §5.1 to make the claim reproducible?

g. **Selection function cancellation.** §2.3 + footnote at line ~150
   argue that the selection normalisation `N_s(H_0)` is H₀-independent
   because π(d_L|H_0) is independent of H₀ in every prior considered.
   A referee will ask: is that true for a uniform-in-redshift prior
   (which the paper claims is numerically equivalent at z ≲ 0.02)?
   Verify the equivalence claim numerically by running the
   `analyze_selection_term.py` script and reporting the
   uniform-in-redshift case alongside the uniform-in-d_L one.

h. **Reweighting failure framing.** §4.1 frames the reweighting deficit
   as a "coverage failure". A referee will ask: it's a population-level
   coverage failure in the prior-sensitivity sense, but is the reweighting
   itself biased or just high-variance? Run a bootstrap on the reweighted
   draw and report the reweighted P(H₀>120) distribution. If the bootstrap
   confidence band does NOT include the directly-sampled 0.159, the
   paper has a stronger claim ("reweighting is systematically biased on
   GW170817", not "reweighting under-covers").

i. **Cross-event generalisation.** The paper is GW170817-only. A referee
   will ask: is the conclusion specific to GW170817 (broad posterior,
   low-d_L bimodality), or does it generalise to future bright sirens?
   Is there enough material for a one-paragraph forecast in §6.3 or §6.5?
   Look in `Chen2018Forecast` (already cited) for the population numbers
   and propose a 2-3 sentence quantitative forecast extension.

j. **Other.** Open category. Any other adversarial reads — narrative gaps,
   load-bearing claims with thin support, citations that the paper relies
   on heavily but a referee might challenge — list here.

For each item a–j give:
- Referee objection in one sentence
- Current paper coverage (file:line) of the objection, if any
- Verdict: addressed / partly addressed / unaddressed
- If unaddressed, a one-paragraph proposed inoculation (or "no fix needed,
  defer to follow-up")

### Task 2 — reproducibility audit

For every claim in the paper that could be independently verified by a
reader, identify the minimal (script, input file) pair needed to regenerate
it, then verify the pair exists, runs, and produces the claimed output.

a. **Every figure.** For each of the seven figure floats (gw150914 corner,
   H0 prior sensitivity, bimodality cross-waveform check, main bimodality,
   H0 waveform comparison, GW170817 corner, scaling study), report:
   - Source script (path)
   - Input file(s) (path)
   - Output PDF path
   - Does the source script exist? Does it run end-to-end? Does the output
     PDF match the figure embedded in the compiled PDF?

b. **Every table.** Same for the four table floats. Specifically check
   that `Plots/build_paper_tables.py` generates `table1_gw150914.tex`,
   `table5_prior_sensitivity.tex`, `table6_bimodality.tex` consistently
   with the current values in the manuscript.

c. **Every abstract number.** The Tier-A pass already verified these
   against the chain CSVs. Re-confirm that the relevant
   `Results/test_suite/sN__*/samples.csv` files are present and
   reproducible from a fresh checkout.

d. **Every appendix number.** Appendix A item-by-item (sampler hyperparam,
   PSD source, heterodyne reference, vp centre, IMR companion sweep).

e. **Build a Makefile or `regenerate.sh`** that takes a fresh checkout
   to: (i) regenerated summary CSVs and table .tex files;
   (ii) regenerated figure PDFs; (iii) compiled `main.pdf`.
   The chains themselves are NOT in scope for the Makefile — they are
   regenerated by a separate `run_chain.sh` that needs a GPU.

For each verification step, log: PASS / FAIL (and why) / SKIPPED (and why).

### Task 3 — inventory, dead-code culling, and condensation

Walk every file in:
- `paper-reproduce/`
- `Plots/`
- `mnras_paper/test_suite/`
- `Results/gwtc1_phasemarg/`
- The relevant subset of `Results/test_suite/` (the sN runs the paper
  actually cites: s05/s07/s08/s09/s10/s12/s13/s14/s17a/s18 — confirm
  by grepping the manuscript for sN references)

For each file, classify into one of:
1. **NEEDED for reproducibility** — script or data file that a reader
   must have to regenerate a paper claim.
2. **NEEDED for verification** — used by the prior reviews
   (`final_pass_review.md`, `referee_response.md`, the audit memos in
   `mnras_paper/`) but not by the paper itself.
3. **NOT NEEDED** — exploratory, deprecated, or replaced by a later
   pipeline iteration. Candidate for removal from the public repo
   (NOT from the local working repo — just from the GitHub mirror).

Surface category-3 candidates as a list. Do not delete anything in this
pass; the user will authorise deletion separately. Common patterns to
look for:
- `compare_*.py` scripts that produced overlays now superseded by the
  current canonical figures
- `analyze_*.py` scripts that fed a section of the paper that has since
  been deleted (e.g., the §6.3 sky-prior subsection was removed in m17;
  `analyze_sky_prior_runtime.py` is likely orphan)
- `figures/output/` subtree — the auto-generated previous-pass figures
  not currently referenced by `main.tex` (verify against
  `grep includegraphics main.tex`)
- `figures/v2/` subtree — same
- `Plots/plot_*.py` scripts whose output is not in the figure inventory
- Per-run directories in `Results/test_suite/` whose chain CSVs are not
  used by any current figure or table (the sN runs that fed deleted
  paragraphs)
- Session-plan markdown files in `mnras_paper/test_suite/session_plans/`
  that documented earlier exploratory phases

Output: a CSV `mnras_paper/data_release_inventory.csv` with columns
`path, classification (needed-paper / needed-verification / dead), reason,
recommended_action`.

### Task 4 — public-repo design

Design the directory layout for `https://github.com/ming-256/GW170817-bright-siren-H0`.
Confirm via WebFetch / `gh repo view ming-256/GW170817-bright-siren-H0`
whether the repo currently exists and what's in it; document the gap
between current state and the target.

Target layout:
```
GW170817-bright-siren-H0/
├── README.md                  # paper TL;DR, citation, quick-start
├── MANIFEST.md                # file-by-file provenance
├── LICENSE                    # MIT or BSD-3 (ask user)
├── CITATION.cff               # for GitHub's "cite this" widget
├── environment.yml            # exact conda env to reproduce
├── regenerate.sh              # CPU-only: rebuild tables, figures, PDF
├── run_chains.sh              # GPU-only: regenerate sN__* samples.csv
├── paper/
│   ├── main.tex               # mirror of mnras_paper/main.tex (layout-adjusted)
│   ├── references.bib
│   ├── figures/               # canonical figure PDFs
│   ├── tables/                # table_*.tex includes
│   └── main.pdf               # built artifact
├── scripts/
│   ├── build_paper_tables.py
│   ├── _plot_utils.py
│   ├── plot_bimodality.py
│   ├── plot_h0_prior_sensitivity.py
│   ├── plot_waveform_corner.py
│   ├── plot_waveform_h0_comparison.py
│   ├── plot_gw150914_corner.py
│   ├── plot_scaling_study.py
│   └── compare_bimodality_waveforms.py
├── analysis/                  # the per-sweep summarisers, if a reader
│                              # wants to recompute appendix numbers
│   ├── analyze_bimodality.py
│   ├── analyze_bimodality_imrx.py
│   ├── analyze_het_bins_sweep.py
│   ├── analyze_num_delete_sweep.py
│   ├── analyze_psd_sensitivity.py
│   ├── analyze_ref_params.py
│   ├── analyze_selection_term.py
│   └── compile_test_suite_report.py
├── results/
│   ├── gwtc1_phasemarg/       # summary CSVs and figure-source PDFs
│   │   ├── evidence_table.csv
│   │   ├── paper_diagnostics.csv
│   │   ├── paper_tables.csv
│   │   ├── table1_gw150914.tex
│   │   ├── table5_prior_sensitivity.tex
│   │   ├── table6_bimodality.tex
│   │   └── plots/             # canonical figure PDFs
│   └── test_suite/
│       ├── run_catalog.csv    # which sN directory is which run
│       ├── bimodality_summary.csv
│       ├── bimodality_imrx_summary.csv
│       ├── bimodality_waveform_check.csv
│       ├── gw150914_waveform_comparison.csv
│       ├── gw170817_waveform_comparison.csv
│       ├── het_bins_sweep_summary.csv
│       ├── num_delete_sweep_summary.csv
│       ├── psd_sensitivity_summary.csv
│       └── (per-run dirs are documented but NOT redistributed — see
│              run_chains.sh)
└── docs/
    ├── reproducibility.md     # how to rebuild from a fresh clone
    ├── chain_regeneration.md  # how to rerun chains on a GPU
    └── data_provenance.md     # where each summary CSV came from
```

For each file in the target layout, identify:
- Source path in the current repo
- Whether it needs transformation (e.g., updating import paths from
  `from _plot_utils import ...` to `from scripts._plot_utils import ...`)
- Size (so large files get flagged for Git LFS or exclusion)

Deliverable: a markdown table mapping current path → target path with
notes.

### Task 5 — README and MANIFEST drafts

Draft both files. The README should:
- Open with the paper TL;DR (3-4 sentences)
- Quote the headline numerical result
- Provide the citation in BibTeX form (matching `Yang2026DataRelease`)
- Quick-start: `conda env create -f environment.yml && bash regenerate.sh`
- Link to docs/reproducibility.md for the full recipe
- Note hardware requirements (CPU only for figures/tables; one NVIDIA
  A100-class GPU + 40 GB VRAM for chain regen)
- Acknowledgement matching the paper

The MANIFEST should table-row every file in the repo with provenance.
Use the inventory CSV from Task 3.

### Task 6 — end-to-end verification

Take the proposed `regenerate.sh` (or equivalent Makefile) and run it
against a clean checkout of the proposed layout. Verify:
- All seven figure PDFs are produced and visually match the
  `mnras_paper/figures/` originals (byte-exact is unlikely;
  matplotlib version differences. Use `pdfinfo` + image-diff on
  rasterised PDFs as a sanity check.)
- All three table .tex files are produced and string-compare against the
  current `Results/gwtc1_phasemarg/table*.tex` (these should be
  byte-exact since they're emitted from a deterministic generator).
- The compiled `paper/main.pdf` is 11 pages and contains the abstract
  text starting "The bright-siren measurement of the Hubble constant
  from GW170817".

Run `latexmk -pdf paper/main.tex` and confirm no warnings of substance.

If any step fails, report (i) the failing command, (ii) the missing or
mismatched output, (iii) the proposed fix (without applying it).

### Task 7 — final consistency between paper and public repo

a. **The `Yang2026DataRelease` bib entry.** Confirm the URL field exactly
   matches the public repo URL. Verify the bib entry's other fields
   (title, year, author) match the repo's README.md and CITATION.cff.

b. **Reproducibility-budget claim.** §5.1 says a reader can rebuild the
   prior-sensitivity sweep "inside an hour" on a single A100. The
   GitHub repo's `run_chains.sh` should give a concrete time estimate
   (with hardware target) so the claim is testable.

c. **Data Availability statement (line ~389).** Verify each cited
   release is hyperlinked and accessible:
   - `Yang2026DataRelease` → GitHub repo
   - `LVK_GW170817_DataRelease` (LIGO P1800061)
   - `LVK_H0_DataRelease` (LIGO P1700296)
   - `GWTC2p1_GW150914_Zenodo`

d. **Zenodo deposit.** The bib entry currently points to GitHub only.
   For long-term archival, the standard MNRAS practice is to deposit
   the same release on Zenodo and cite both. Report whether a Zenodo
   DOI exists; if not, document the procedure (via GitHub's Zenodo
   integration) without executing it.

## Deliverables format

A single markdown file `mnras_paper/data_release_audit.md` with these sections:

1. **Verdict** — one paragraph. One of: *public-repo-ready*,
   *public-repo-ready after listed fixes*, *substantive cleanup required*.
2. **Critical analysis findings** (per Task 1, items a–j) — each with
   referee objection, current paper coverage, verdict, proposed inoculation.
3. **Reproducibility audit** (per Task 2, items a–e) — table of figures
   and tables with regeneration status; the proposed `regenerate.sh` /
   `Makefile` content.
4. **Inventory and dead-code list** (per Task 3) — link to the inventory
   CSV `data_release_inventory.csv` and a short summary of categories.
5. **Public-repo layout** (per Task 4) — table mapping current path →
   target path with transformation notes.
6. **Drafted README and MANIFEST** (per Task 5) — embedded inline in the
   audit report so the user can copy-paste them when ready to push.
7. **End-to-end verification log** (per Task 6) — PASS/FAIL per step.
8. **Paper–repo consistency findings** (per Task 7).
9. **Suggested edits, ranked** —
   - Tier A (substantive: a science claim needs a one-paragraph
     inoculation; reproducibility step blocks regeneration)
   - Tier B (repo hygiene: file moves, env spec)
   - Tier C (cosmetic: README polish, CITATION.cff metadata)

   Each with exact (file:line) where applicable, current wording or
   path, proposed wording or path, justification.

If you apply any edits during the pass (rather than only proposing), say so
explicitly in the report and re-confirm both the local paper compile and
the proposed-repo build are clean after the last edit. Default behaviour:
propose first, apply only when explicitly authorised by the user.

## Out of scope

- Do not regenerate chains (the regeneration recipe in `run_chains.sh`
  is the deliverable; a reader with a GPU runs it themselves).
- Do not deposit anything on Zenodo or push commits to the GitHub repo
  unless explicitly authorised — document the procedure instead.
- Do not modify the figures' rendered content. The existing PDFs in
  `mnras_paper/figures/` and `Results/gwtc1_phasemarg/plots/` are
  canonical.
- Do not delete files from the local repo. The cleanup is for the
  GitHub mirror only; the local working repo keeps everything.
- Do not rewrite the central science argument or the §4.1 / §5 / §6
  framing beyond the Tier-A inoculations proposed under Task 1.

## Operating constraints

- conda env `/opt/miniconda3/envs/PhD` for any Python verification.
- Build LaTeX from inside `mnras_paper/` with `latexmk -pdf main.tex`.
- Build the public-repo paper from inside the proposed `paper/` directory
  with `latexmk -pdf main.tex`.
- Use `gh` (already authenticated for `ming-256`) for any GitHub
  inspection; do not push.
- Take the user's prior-pass decisions as established preferences:
  forward-looking voice over apologetic voice; positive results first,
  scope clauses last; numbers consistent across abstract / body /
  tables / conclusions; histograms over KDEs for 1-D summaries; LVK
  posteriors plotted as actual samples not as HPD bands.
- If you discover a substantive science problem (a number that doesn't
  tie out, a citation that doesn't say what the paper claims it says,
  a reproducibility gap that blocks the central claim), flag as Tier A
  and stop — do not paper over it.
