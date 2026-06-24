# Final critical-analysis prompt — Yang et al. (2026) MNRAS pre-submission

You are doing a focused, adversarial **pre-submission critical analysis** on
the now-locked Yang et al. (2026) MNRAS draft and its companion public
data release. The paper has been through a literature pass, a referee-
response revision, a tone pass, a final-pass review, a data-release audit
(`data_release_audit.md`), and a substantive A → B → C edit cycle whose
state is summarised in
`memory/project_data_release_merged.md` (audit deliverables) and in commit
`6ee4b0e` of this repo. The public release is live at commit `be733d0`
on `github.com/ming-256/GW170817-bright-siren-H0`.

Your job is to be the **last hostile reader before the paper is
submitted to MNRAS** and the corresponding zenodo / arXiv push happens.
Find the things the previous passes did not catch — and especially the
weaknesses *introduced by* the previous passes' edits.

You have web-search, web-fetch, Python (conda env `/opt/miniconda3/envs/PhD`),
working LaTeX (`latexmk -pdf` from inside `mnras_paper/`), `gh` for
GitHub operations, and full filesystem access. Use them. Verify rather
than assume.

## State at the start of this pass — what's already done (do not redo)

- All Tier-A / Tier-B / Tier-C edits from `data_release_audit.md` are
  applied to `mnras_paper/main.tex` and `references.bib` (commit
  `6ee4b0e`).
- §4.1 now carries the *bootstrap-bias* paragraph and the *honest
  PSIS k̂ = 0.68* sentence.
- §5 carries the *seed-ensemble pointer* + the *IMR/NRTidalv2 scope
  clause* on the heterodyne-reference robustness claim.
- §5.1 names the GPU SKU (NVIDIA A100 40 GB SXM4; Google Cloud
  `a2-highgpu-1g`) and adds a per-live-point comparison with the
  Wong+2023 / Wouters+2024 Jim BNS pipelines.
- §6.3 carries the Chen+2018 / HuVeitch+2025 quantitative bright-siren
  forecast and a forward recommendation that single-event posteriors
  be reported under both volumetric (= comoving-volume at z ≲ 0.02)
  and uniform-in-d_L direct-sampled priors.
- `references.bib` `Yang2026DataRelease` title is aligned with the
  public release's `CITATION.cff`; Zenodo DOI placeholder noted.
- `mnras_paper/test_suite/analysis/analyze_psis_khat.py` is new and
  appends `pareto_khat / rw_bootstrap_q025 / rw_bootstrap_q975 /
  direct_minus_rw_sigma` columns to
  `Results/gwtc1_phasemarg/paper_diagnostics.csv` (via LFS).
- The public-repo cleanup landed via PR #1 on `ming-256/GW170817-
  bright-siren-H0` (merge commit `be733d0`).
- Page count is locked at 11 pp; abstract is 247 words (detex).

## Key locations

- `mnras_paper/main.tex` — canonical manuscript (412 lines, 11 pp)
- `mnras_paper/references.bib` — bibliography (45 entries)
- `mnras_paper/main.pdf` — built artefact
- `mnras_paper/data_release_audit.md` — the audit report this pass
  builds on
- `mnras_paper/data_release_inventory.csv` — 564-row per-file
  classification
- `mnras_paper/test_suite/analysis/analyze_psis_khat.py` — the new
  PSIS k̂ + bootstrap diagnostic
- `Results/gwtc1_phasemarg/paper_diagnostics.csv` — now has the
  k̂ + bootstrap columns
- Public repo at `https://github.com/ming-256/GW170817-bright-siren-H0`
  (cloneable; chains on Zenodo when minted)

## Tasks

### Task 1 — Audit the *new* §4.1 claims

The Tier-A inoculations introduced three new technical claims. Each
needs to survive a hostile read.

a. **Bootstrap methodology.** §4.1 now states: "A non-parametric bootstrap
   on the reweighted estimator (4 000 draws at the reweighted
   n_eff = 27 539) gives a 95 % confidence interval for P(H₀ > 120 km/s/Mpc)
   of [0.037, 0.042]". Pressure-test:
   - Is the multinomial-bootstrap-at-n_eff the *right* procedure for
     bounding the variance of an importance-sampling estimator?
     A referee will know that Owen (2013) and Vehtari+2024 prefer
     the *resampled* importance sample directly, or the PSIS-LOO
     point-estimator variance. Verify by re-implementing the bootstrap
     three ways (multinomial-at-n_eff; Bayesian-bootstrap; weighted
     jackknife) and reporting whether the CI width and centre move.
   - Re-run with seeds 1, 2, 3 and confirm the [0.037, 0.042] interval
     is reproducible to within rounding.
   - Verify the "~100 σ" claim — sigma here is the binomial standard
     error of P_rw at n_eff_rw; a referee may ask for the *PSIS*
     standard error (Vehtari+2024 eq. 12) instead, which uses k̂
     to correct for tail-heaviness. Re-compute and report.

b. **k̂ = 0.683.** §4.1 now reports this number and locates it in the
   Vehtari "high variance but consistent" band (0.5 < k̂ ≤ 0.7).
   Pressure-test:
   - The GPD MLE depends on the tail fraction (default 20 % or
     3√S, whichever is smaller). Re-run with tail fractions 10 %,
     15 %, 25 %, 30 %; report sensitivity. A referee will object if
     k̂ moves by > 0.1 across reasonable tail choices.
   - Compare to `arviz.stats.psislw` (the canonical implementation)
     and `loo.psislw` if available; install arviz in the conda env if
     not present. If the two implementations disagree by > 0.05, the
     paper should quote the canonical one.
   - The paper claims the bias is "severe at this borderline k̂".
     But the published Vehtari+2024 simulation studies show
     k̂ = 0.68 → relative bias ≤ 10 % in *most* settings. Our case
     has ~400 % relative bias (0.041 vs 0.159). Is there a
     well-defined regime where this happens, and should the paper
     point readers at it?

c. **"Reweighting bias versus variance" framing.** Is the dichotomy
   too binary? A referee with importance-sampling background will
   distinguish three regimes: (i) consistent + low variance, (ii)
   consistent + high variance, (iii) inconsistent. The paper's
   bootstrap shows (iii) on this draw — the estimator converges on
   the wrong value. Verify that this is provably (iii) and not (ii)
   masquerading as (iii) at finite n.
   - A diagnostic: as the IMRX baseline samples per draw grow (say,
     down-sample the existing 173 k chain to 10 k, 30 k, 100 k, then
     run the bootstrap on each), does the reweighted P_rw converge
     toward the direct 0.159 or stay near 0.041?
     If it stays near 0.041, the estimator is provably inconsistent
     on this draw and the paper has a strong (iii) case.
     If it drifts toward 0.159, the estimator is just (ii) at finite n
     and the paper should soften its language.

### Task 2 — Cold-clone reproducibility, end-to-end

Someone with *no* prior context to this project clones
`github.com/ming-256/GW170817-bright-siren-H0` on a fresh machine,
downloads the Zenodo chain bundle (or, until the DOI is minted,
substitutes their own pre-baked chains), and runs `bash regenerate.sh`.
Do they get the same 11-page PDF with the same numbers?

a. Clone the public repo into a fresh `/tmp/cold-clone-test`. Create
   the conda env from `environment.yml`. Confirm the env solves and
   activates without error. (Tier-A finding if it does not.)

b. Without populating `results/test_suite/sNN__*/samples.csv`, run
   `bash regenerate.sh tables` and verify it fails with a clear
   "chain CSVs missing — pull from Zenodo" message rather than a
   raw Python traceback. (Tier-B finding if the error is opaque.)

c. Now stage just the s14 IMRX baseline + s17a GW150914 chains
   (copy them across from `Results/test_suite/` to `results/test_suite/`).
   Re-run `regenerate.sh` and observe which steps fail. The chains
   needed for each figure are documented in
   `paper-reproduce/data/MANIFEST.md` (now superseded by the public
   `MANIFEST.md`); cross-check that the per-figure dependency list
   matches.

d. Run the entire `regenerate.sh` (with all 17 cited chains copied
   into `results/test_suite/`) and confirm:
   - All 7 figure PDFs land in both `results/gwtc1_phasemarg/plots/`
     *and* `paper/figures/`.
   - All 4 table `.tex` files land in both
     `results/gwtc1_phasemarg/` *and* `paper/tables/`.
   - `paper/main.pdf` builds at 11 pages.
   - No latex warnings of substance.

e. Run `python analysis/analyze_psis_khat.py` from a fresh clone and
   verify the k̂ = 0.68 number is reproducible (not just on the
   developer machine).

f. Open the README.md, MANIFEST.md, CITATION.cff and
   docs/{reproducibility,chain_regeneration,data_provenance}.md in
   a fresh reader's eyes. Does each answer the question a reader
   would actually ask? Are there forward-pointers to wrong filenames
   after the layout move? Any TODO placeholders that should be
   filled before pushing to arXiv?

### Task 3 — Adversarial referee dry-run

Re-read `mnras_paper/main.tex` end-to-end as if you were the MNRAS
referee who is *known to be hostile to GPU-pipeline parameter-estimation
papers* — there are several. Anticipate the 5–10 items you would
write into a referee report.

Categories to cover:

- **Novelty claim.** "Switching the prior changes the tail. Hasn't
  this been shown before?" Find the strongest published precedent
  (e.g., a footnote in a GW170817 follow-up that already noted the
  reweighting deficit) and propose a one-sentence pre-emption.

- **Mode-B physical interpretation.** Mode B has H₀ ~110 km/s/Mpc,
  which is in tension with both Planck and SH0ES. Is the paper
  willing to interpret Mode B as a real cosmological signal (no),
  a data-and-prior artefact (yes), or something in between? The
  current language is ambiguous; sharpen it.

- **GW150914 cross-validation.** The σ(ι) = 1.17 residual on the
  precessing run is the largest. A referee may say: "you validated
  on a BBH with no tides; the BNS application has both. The
  validation does not transfer." Anticipate and pre-empt.

- **Single-event interpretation.** Population analyses (multi-event
  combinations) are the actual cosmology-grade use case for bright
  sirens. The paper is single-event. A referee may demand: "your
  17 % capture-fraction claim is only relevant if reweighted
  multi-event combinations under-estimate the population P_rw too.
  Show one population-level example before publishing." Counter or
  defer to follow-up.

- **PSIS k̂ interpretation.** A referee may argue: "k̂ = 0.68 is
  *below* the canonical 0.7 unreliability threshold, so by Vehtari's
  own criterion the reweighting is *reliable*. Your bootstrap result
  contradicts the published threshold, which suggests *your bootstrap
  methodology is wrong*, not that the standard threshold is too
  lenient." Counter (Task 1c is the verification path).

- **Vp prior sweep.** A referee may object: 215 / 310 / 405 km/s
  spans the literature but is not a *systematic* prior choice.
  Defend with the citation chain that motivated each value.

- **NRTidalv2 vs NRTidalv3.** The reweighting capture fraction is
  17 % for IMRX (NRTidalv3) and 58 % for IMR (NRTidalv2). The paper
  attributes this to "tighter upper tail under NRTidalv3". A referee
  may ask: "is this just a finite-sample artefact of the IMRX run
  having different chain history than the IMR run?" Verify by running
  the same NS configuration on IMR with matched chain length and
  reporting whether the capture fraction stays at 58 %.

- **`a2-highgpu-1g` SKU.** A referee at a non-GCP institution may
  ask: "what if I only have on-prem A100s?" Confirm the result is
  not GCP-network-dependent (this should be obvious — the GW analysis
  is local-only — but a single sentence in §5.1 saying so closes the
  question).

- **The Chen+2018 / HuVeitch+2025 forecast extension.** The numbers
  quoted (25–80 events in 5–10 years; ≳10⁴ detections/yr at 3G; 10–100
  bright sirens/yr) need verification against the source papers. A
  referee will look them up.

For each anticipated objection, give: (i) the exact wording the
referee would use, (ii) what (file:line) of the paper either already
covers it or doesn't, (iii) the inoculation we should add now versus
defer to revision.

### Task 4 — Submission packaging

The paper goes to MNRAS plus arXiv plus the public repo simultaneously.
Pre-flight everything.

a. **Cover letter.** Draft a 250–400 word cover letter to the
   MNRAS editor. Highlights: novelty (direct-vs-reweighted comparison
   at GPU speed); mechanism (Mode B); diagnostic recommendation
   (PSIS k̂ + bootstrap as the default before reporting reweighted
   bright-siren H₀); reproducibility (the public repo + Zenodo).

b. **Suggested referees.** List 4–6 names with one-line justifications:
   the bright-siren H₀ community (Mortlock; Chen / Holz / Fishbach;
   Mukherjee; Palmese; Mastrogiovanni); the GPU-PE community
   (Wong; Wouters; Edwards; Williams); the importance-sampling /
   PSIS community (Vehtari; Owen).

c. **Excluded referees.** None obvious; state so.

d. **arXiv categorisation.** Primary: `astro-ph.CO`. Cross-list:
   `astro-ph.IM`, `gr-qc`. Verify these are the right ones for an
   MNRAS bright-siren methodology paper.

e. **Final-checklist sweep.** Before the user types `arxiv-upload`:
   - Author affiliations match the cff
   - Acknowledgements match the cff
   - Funding statement (Google Cloud GCP397499138 ✓ already there)
   - Conflict-of-interest declaration (none)
   - Data Availability statement points at both GitHub URL and Zenodo
     DOI (DOI placeholder until minted)
   - ORCID iDs in author list (currently absent — Tier-B/C fix)

### Task 5 — Anticipated revision

Most MNRAS papers in this domain get a 5–15-item referee report at
either "Minor revision" or "Major revision" disposition. Prepare for
the most likely outcomes:

a. **Catastrophic-failure scenarios.** What is the *one* request a
   referee could make that would force a major re-run on the GPU
   (cost: 1+ week)? Examples: "redo IMRX with n_live = 20 000";
   "add a precessing-tidal waveform"; "extend the bimodality study
   to a second BNS event". Identify each and pre-position whether
   the team's response would be (i) defer to follow-up, (ii) push
   the rerun and re-submit, (iii) negotiate a scope clarification.

b. **Likely Minor-revision items.** Five most probable referee
   comments that take ≤ 1 day to address. Pre-write the responses
   in `mnras_paper/anticipated_referee_responses.md` so the team can
   ship a referee response within ~48 h.

c. **The Mode-B follow-up.** The paper explicitly defers an IMRX
   mode-isolated set with a Mode-B-anchored heterodyne reference
   (the `s19__*` runs queued in `launch_tier2.sh`). Estimate the
   GPU time (probably ~3 h on an A100) and identify when this
   should be run: before submission to pre-empt a Mode-B-targeted
   referee objection, OR after the referee report to respond to it.

## Deliverables format

A single markdown file `mnras_paper/final_critical_analysis.md` with
these sections:

1. **Verdict** — one paragraph. One of: *ready to submit*,
   *ready to submit after listed Tier-A fixes*, *substantive concerns
   require an editorial decision before submission*.
2. **New §4.1 claims audit** (Task 1, a-c) — referee objection /
   verification I ran / verdict / proposed action.
3. **Cold-clone reproducibility log** (Task 2, a-f) — PASS / FAIL
   per step with the exact failing command if any.
4. **Adversarial referee dry-run** (Task 3) — anticipated objection
   list with (file:line) and inoculation tier.
5. **Submission packaging** (Task 4) — cover letter draft (full
   text), suggested-referee list, arXiv category check, final-
   checklist PASS / FAIL.
6. **Anticipated revision** (Task 5) — catastrophic-failure scenarios
   ranked by likelihood; pre-written Minor-revision responses
   (link to `mnras_paper/anticipated_referee_responses.md` if
   created in-pass); Mode-B follow-up timing recommendation.
7. **Ranked Tier-A / Tier-B / Tier-C edits** —
   - Tier A: a claim is wrong or a step blocks reproducibility
   - Tier B: a missing inoculation or a packaging gap
   - Tier C: cosmetic polish

   Each with exact (file:line) where applicable, current wording,
   proposed wording, justification.

If you discover during the pass that a Tier-A claim is wrong (a number
that doesn't tie out, a citation that doesn't say what we claim it says,
a reproducibility step that blocks the central claim), flag as Tier A
and stop — do not paper over it.

If you apply any edits during the pass (rather than only proposing),
say so explicitly in the report and re-confirm both the local paper
compile and the public-repo build are clean afterwards. **Default
behaviour: propose first, apply only when explicitly authorised.**

## Out of scope

- Do not regenerate chains. The 17 cited per-run chains are locked.
- Do not push to GitHub. Edits to the public repo go through a feature
  branch and a PR for user review.
- Do not deposit on Zenodo. Document the procedure if not yet executed.
- Do not modify the central science argument (§4.1 / §5 / §6 framing)
  beyond the inoculations proposed in this pass.
- Do not contact the MNRAS editor or any potential referees.
- Do not modify the figure rendering — the seven canonical PDFs are
  locked. If a figure has a problem, flag it; do not regenerate.

## Operating constraints

- conda env `/opt/miniconda3/envs/PhD` for any Python verification.
  If `arviz` is not in it, install it before using its k̂ implementation.
- Build LaTeX from inside `mnras_paper/` with `latexmk -pdf main.tex`.
- Cold-clone tests: use `/tmp/cold-clone-test`, not the user's working
  tree. Clean up afterwards.
- Use `gh` for any read-only GitHub inspection; do not push.
- Take the user's prior decisions as established preferences:
  forward-looking voice over apologetic voice; positive results first;
  numbers consistent across abstract / body / tables / conclusions;
  histograms over KDEs for 1-D summaries; LVK posteriors plotted as
  actual samples not as HPD bands.
- Reference the audit deliverables (`data_release_audit.md` §2–§9)
  rather than re-deriving inoculations the audit already proposed.
- The companion public release is at PR-#1-merge commit `be733d0`;
  if anything needs to change there too, propose a Tier-A or Tier-B
  edit and the user will authorise the push.

## Success criterion

When this pass is done, the user should be able to do the following
in order, without further critical-analysis input:

1. Read `final_critical_analysis.md` → optionally authorise Tier-A
   edits.
2. Run any authorised edits to `mnras_paper/main.tex` /
   `references.bib`; rebuild the PDF.
3. Mint the Zenodo DOI per `data_release_audit.md` §7.4; populate
   the placeholders in `references.bib`, README, MANIFEST,
   CITATION.cff.
4. Push the updated `paper/main.tex` + `references.bib` + `main.pdf`
   to the public repo on a `polish-vN` branch and merge.
5. arXiv upload.
6. MNRAS submission with the drafted cover letter and the suggested
   referee list.
