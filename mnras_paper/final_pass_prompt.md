# Final-pass review prompt — Yang et al. (2026) MNRAS submission

You are doing a final complete pass on a near-submission MNRAS draft. The paper
has already been through a literature-positioning review (`literature_review.md`),
a referee-response revision (`referee_response.md`), a Tier-A/B citation pass,
the closure of three deferred minor referee items (m17/m19/m20), and a tone
pass that stripped defensive language from the abstract, §4.3, §5, §6.4, §6.5,
and the Conclusions. Your job is to catch what those earlier passes did not.

You have web-search, web-fetch, Python (conda env `/opt/miniconda3/envs/PhD`),
and a working LaTeX install (`latexmk -pdf` from inside `mnras_paper/`). Use
them. Verify rather than assume.

## The paper in one paragraph

`mnras_paper/main.pdf` (11 pages, MNRAS class). Authors: Yang, M.; Prathaban, M.;
Yallup, D.; Handley, W. (2026), submitted.

The paper revisits the GW170817 bright-siren H₀ measurement of Abbott et al.
(2017, Nature 551, 85), testing whether switching from a volumetric
`π(d_L) ∝ d_L²` prior to a uniform-in-d_L prior can be implemented by post-hoc
reweighting of baseline samples rather than by re-running inference. Using a
GPU-native heterodyned nested-sampling pipeline (~13 min per
IMRPhenomXAS_NRTidalv3 run at n_live=5000 on one A100), it shows that direct
sampling under uniform-in-d_L raises `P(H₀ > 120 km/s/Mpc)` from 0.017 to 0.159,
moves the weighted-median H₀ from 77.6 to 87.6 km/s/Mpc, and leaves the binned
MAP at 70.5; post-hoc reweighting captures only 17 % of the tail shift. The
mechanism is a (d_L, ι) bimodality whose high-H₀/low-d_L branch (Mode B) the
volumetric prior assigns ~7 % of the prior mass that Mode A receives. The
reweighted estimator's effective sample size is lower than the baseline's,
independently flagging the coverage failure. GW150914 validation and a
cross-waveform check on TaylorF2 sit alongside the prior-sensitivity result.

## Recent state — what's already been done (do not redo)

- **Literature additions** (per `literature_review.md`): Mooley 2018, Mukherjee
  2021, Howlett & Davis 2020, Palmese 2024 (PRD 109, 063508), Salvarese & Chen
  2024 (ApJL 974, L16), Williams 2021 (nessai), Payne 2019, Vehtari 2024 PSIS,
  Palmese & Mastrogiovanni 2025 review, Chen 2018 forecast. All landed in
  `references.bib` and cited from `main.tex`. The duplicate
  `Abbott2017GW170817Properties` bib entry was deleted; the Wong 2023 Jim DOI
  was added.
- **m17 closed**: §6.3 Sky-prior matched-pair runtime sweep (`sec:skyprior`)
  was deleted in full; the four forward references (intro, §2.4, §6.4 scope
  paragraph, header comment) were cleaned.
- **m19 closed**: Fig. 1 caption already lacks "Both panels" wording.
- **m20 closed**: σ-widths sentence in §3.1 quotes σ(M_c)=1.02/1.01 M_⊙,
  σ(d_L)=84/85 Mpc, σ(q)=0.10/0.11, σ(ι)=0.41/0.35 rad (ratios 1.01/0.99/
  0.87/1.11). Numbers computed from
  `Results/test_suite/s17a__gw150914__imrphenomxphm__nlive8000_mcmc160__seed0000/samples.csv`
  vs the GWTC-2.1 mixed XPHM release in `EventData/GWOSC/GW150914/`.
- **Tone pass**: defensive openers ("We caution against over-interpreting",
  "Several limitations should be acknowledged", "We deliberately do not …")
  were rewritten to forward-looking voice; §6.5 was renamed
  "Scope and natural extensions" and trimmed from four items to two.
- **`Yang2026DataRelease` bib note** updated to reflect the live GitHub repo
  at `https://github.com/ming-256/GW170817-bright-siren-H0`.

## Key files

- `mnras_paper/main.tex` — manuscript source
- `mnras_paper/main.pdf` — current build (verify clean compile before reviewing)
- `mnras_paper/references.bib`
- `mnras_paper/literature_review.md` — prior-pass output; precedent for tone
- `mnras_paper/referee_response.md` — what referees asked and the resolution status
- `mnras_paper/GW150914_mass_prior_audit.md` — the M3 audit memo
- `Results/test_suite/` — sNN per-run chain CSVs and configs
- `Results/gwtc1_phasemarg/` — derived summary CSVs, table*.tex includes,
  figure PDFs that `main.tex` pulls in
- `Plots/build_paper_tables.py` and `Plots/_plot_utils.py` — the canonical
  table/figure generators
- `https://github.com/ming-256/GW170817-bright-siren-H0` — public data-release repo

## Tasks

For every finding, give (file:line) coordinates and the exact wording.

### Task 1 — numerical consistency sweep

Every number that appears in the abstract or conclusions must agree with the
body, the tables, and the underlying chain CSVs. Cross-check, with WebFetch
or Python as needed:

a. **Abstract vs Conclusions vs §4.1 Table 5 / Fig 3.** Headline numbers:
   `P(H₀>120) = 0.017 (baseline), 0.041 (reweighted), 0.159 (direct
   uniform-in-d_L)`; reweighted capture fraction `(0.041−0.017)/(0.159−0.017) ≈
   17 %`; weighted-median shift `77.6 → 87.6 km/s/Mpc`; binned-MAP `70.5
   km/s/Mpc`; `ΔlnZ ≲ 1.8`. Each must appear with the same precision wherever
   quoted.
b. **IMR cross-waveform capture fraction.** §4.3 and Appendix A both quote
   `≈ 58 %` for the IMR variant. Verify `(0.195−0.076)/(0.281−0.076)` rounds to
   58, and that the numerator/denominator numbers appear unchanged in Table 5
   and the corresponding chain CSVs.
c. **Bimodality (§5 Table 6).** `lnB(B/A) = −0.66 (seed 0)` and `+0.10 (seed 1)`.
   Both should appear with `ln(20/45)` volume correction explicit. Mode-B
   posterior weight: `0.325 IMRX, 0.428 IMR` (Fig 5 / `compare_bimodality_waveforms.py`).
d. **Volumetric-mass-fraction arithmetic.** `(30³−10³)/(75³−10³) = 26000/420875 =
   0.0618 ≈ 6 %`. Mode-B-vs-Mode-A: `26000 / (421875−27000) = 26000/394875 =
   0.0658 ≈ 7 %`. Both should appear in §5 and §6.
e. **GW150914 validation centroids and σ.** §3.1 quotes `M_c = 30.35 vs 30.7`
   and `d_L^med = 455 vs 440 Mpc`. The σ-widths sentence quotes σ ratios
   1.01/0.99/0.87/1.11. Re-run the σ extraction
   from the s17a chain to confirm; if any drift > 1 %, update the §3.1
   sentence to match.
f. **Wall-clock numbers (§6).** `~13 min IMRX, ~9 min TF` at n_live=5000;
   `~5 h GW150914 XPHM` at n_live=8000, n_mcmc=160; `~4 h IMR heterodyned at
   n_live=10⁵`. Cross-check against the wall-clock columns in
   `Results/test_suite/scaling_*` or the run logs.
g. **n_eff values (§4.1).** `30,695 baseline (17.3 %)`, `37,022 direct
   (18.4 %)`, `27,317 reweighted`. Verify against the `analyze_*` scripts in
   `mnras_paper/test_suite/analysis/`.

### Task 2 — cross-reference and structure check

a. Run `latexmk -pdf` and capture all unresolved `\ref` / undefined citation
   warnings (the build should be clean; flag anything that isn't).
b. Verify that figure numbers in the body match their appearance order in the
   compiled PDF. After the §6.3 deletion the count is six figures and six
   tables; confirm Fig 5 is the bimodality-waveform-check and Fig 6 is the
   main bimodality figure. Confirm Table 5 is prior-sensitivity and Table 6
   is bimodality.
c. Equation refs: `\ref{eq:bayes}`, `\ref{eq:h0likelihood}`, `\ref{eq:reweight-fraction}`
   must resolve; the Bayes-factor `\ln \mathcal{B}_{\rm B/A}` equation should
   have a number if cited.
d. Section refs: `sec:method`, `sec:validation`, `sec:results`, `sec:performance`,
   `sec:discussion`, `sec:conclusions`, `sec:priors`, `sec:prior`, `sec:bimodality`,
   `sec:cross-waveform`, `sec:gw150914`, `sec:hetero-vs-unhet`, `sec:speedup`,
   `app:robustness` should all exist; `sec:skyprior` should not.
e. Check for orphan labels (defined but never `\ref`'d) and orphan refs.

### Task 3 — tone and voice check (continuation)

The prior tone pass swept the obvious defensive openers. Look for what it
missed. Specifically flag:

a. **Hedging adverbs** that weaken without adding information: "essentially",
   "only", "merely", "somewhat", "perhaps", "potentially", "arguably".
   Each instance: is it doing work, or is it self-deprecation?
b. **Negative-space framing**: sentences that say what we *don't* claim or
   *didn't* do without earning it. The prior pass kept the §6.4 pbilby-benchmark
   forward-looking clause and the §5 lnZ-scatter caution (both substantive);
   anything else of that shape is a candidate to flip or delete.
c. **Stutters from prior edits**: word repetitions that arose when adjacent
   sentences were rewritten (e.g., "unchanged… unchanged", "shift… shift").
d. **Passive constructions** that obscure agency in the science narrative.
   Active voice generally lands harder for methodological claims.
e. **Long noun phrases** that bury the verb (a typical academic-prose smell).
f. **Pre-emptive concessions** ("though this is admittedly…", "while we
   recognise that…").

For each flag, propose the rewritten sentence inline.

### Task 4 — citation completeness

a. Run `bibtex main` and confirm every `\cite{...}` resolves and every
   `references.bib` entry is actually cited somewhere (no dead bib entries).
b. Check that the citations added in the prior pass land in their right
   places: `Palmese2024GW170817H0` and `SalvareseChen2024` should both appear
   in the §1 intro reanalysis paragraph; `Vehtari2024PSIS` and
   `Payne2019Reweighting` in the §4.1 IS-failure paragraph; `Chen2018Forecast`
   in §6.1; `Williams2021Nessai` in §1 fast-PE landscape;
   `PalmeseMastrogiovanni2025` in §1 review-cite slot.
c. For any 2024–2026 entry, check the published DOI resolves and matches the
   bib metadata. Specifically re-check `HuVeitch2025` (compact APS DOI
   `10.1103/dj7k-tk37`) and `Wong2023Jim` (DOI `10.3847/1538-4357/acf5cd`).
d. Author lists for journal articles: tighten any remaining `{others}` where
   the contributor count is small enough to enumerate (e.g., Mooley 2018
   already enumerated; verify nothing else is unnecessarily anonymised).

### Task 5 — MNRAS technical compliance

a. **Abstract word count.** MNRAS limit is 250 words. Count the current
   abstract; if over, trim. The tone pass made it tighter but did not strictly
   recount.
b. **Keywords.** Current set is `gravitational waves -- methods: data analysis
   -- cosmological parameters -- stars: neutron -- software: data analysis`.
   "methods: data analysis" and "software: data analysis" are partly redundant
   per the response-letter technical checklist; consider replacing
   "software: data analysis" with `distance scale`.
c. **Title length.** MNRAS prefers ≤15 words for the short title and a
   reasonable full title. Current full title is ~17 words; check if the
   short `[Yang, Prathaban, Yallup \& Handley]` running head reads cleanly
   in the compiled PDF.
d. **Figure captions.** Verify every figure caption is self-contained
   (intelligible without the body text); MNRAS standard.
e. **Table captions.** Ditto.
f. **Equation numbering** consistent; each numbered equation referenced at
   least once.
g. **Bibliography style.** Confirm `mnras.bst` is used and the output reads
   cleanly (no doubled author lists, no missing journal names).
h. **Acknowledgements completeness.** Currently includes Handley Lab, HDPSP,
   Google Cloud GCP397499138, LVK data acknowledgement. Confirm no `TODO`
   placeholders remain.
i. **Data Availability completeness.** Cites `Yang2026DataRelease` (the live
   GitHub repo) and three LVK releases. Confirm the GitHub URL renders as a
   hyperlink and there are no `TODO` strings.

### Task 6 — narrative arc / story coherence

Read the paper end-to-end and answer:

a. Does the intro motivate the prior-sensitivity question on its own terms —
   not as a critique of Abbott+2017, but as a methodological question that
   matters for bright-siren cosmology going forward? The current draft has
   the right framing after the tone pass; verify nothing slid back.
b. Does §3 validate the pipeline convincingly enough that a reader trusts
   the §4 results without further argument?
c. Does §4 deliver the central result (Table 5 + Fig 3) clearly, with the
   tail / median / MAP triple all surfaced before the IS-diagnostic sub-paragraph?
d. Does §5 explain *why* §4's reweighting deficit happens — i.e., does the
   bimodality mechanism land as the explanation, not as a separate finding?
e. Does §6 frame the runtime as enabling capability ("multi-axis robustness
   studies now routine") rather than as a boast, and does it close with the
   forward-looking "natural extensions" rather than apology?
f. Do the Conclusions match the abstract numerically and tonally?

For any "no", propose the specific edit.

### Task 7 — final sanity checks

a. Compile from a clean state: `rm -f main.aux main.bbl main.blg main.log
   main.out main.fdb_latexmk main.fls && latexmk -pdf main.tex`. Confirm
   11 pages, no warnings, no `??` rendered.
b. Search the source for `TODO`, `FIXME`, `XXX`, `\textcolor{red}`, `???`,
   `placeholder`. Should return zero hits.
c. Spell-check the body and captions for any clear typos.
d. Check that `paper-reproduce/paper/main.tex` (the reproducible mirror) is
   in sync; if it is not, flag the diff but do not auto-sync.

## Deliverables format

A single markdown file `mnras_paper/final_pass_review.md` with sections:

1. **Verdict** — one paragraph. One of: *ship-ready*, *ship after the listed
   Tier-A fixes*, *needs another revision pass*. Be honest.
2. **Compile status** — pages, warnings, unresolved refs, undefined citations,
   anything else `pdflatex` flags.
3. **Numerical consistency findings** (per Task 1, per item a–g).
4. **Cross-reference and structure findings** (per Task 2).
5. **Tone and voice findings** (per Task 3) — each with file:line, current,
   proposed, justification.
6. **Citation completeness findings** (per Task 4).
7. **MNRAS technical compliance findings** (per Task 5).
8. **Narrative arc verdict** (per Task 6).
9. **Sanity-check status** (per Task 7).
10. **Suggested edits, ranked** — Tier-A (substantive: changes a claim or
    fixes an inconsistency), Tier-B (citation hygiene), Tier-C (cosmetic).
    Each with exact (file:line), current wording, proposed wording, justification.

If you apply edits during the pass (rather than only proposing), say so
explicitly in the report and re-confirm the compile is clean after the last
edit. Default behaviour: propose first, apply only when explicitly authorised
by the user.

## Out of scope

- Do not run the queued Tier-2 GPU jobs (`mnras_paper/test_suite/launch_tier2.sh`).
- Do not rewrite the central science argument or the §4.1 IS-failure framing
  beyond tone fixes.
- Do not modify the GitHub data-release repo.
- Do not regenerate any figures unless explicitly authorised (the existing
  PDFs are the canonical version).

## Operating constraints

- conda env `/opt/miniconda3/envs/PhD` for any Python verification.
- Build from inside `mnras_paper/` with `latexmk -pdf main.tex`; if `latexmk`
  reports "Nothing to do" but the prior compile failed, fall back to
  `pdflatex; bibtex; pdflatex; pdflatex`.
- Take the user's prior tone-pass decisions as established preferences:
  forward-looking voice over apologetic voice; positive results first,
  scope clauses last; no over-citation; numbers consistent across abstract /
  body / tables / conclusions.
- If you discover a substantive science problem (a number that doesn't tie
  out, a citation that doesn't say what the paper claims it says), flag as
  Tier-A and stop — do not paper over it.
