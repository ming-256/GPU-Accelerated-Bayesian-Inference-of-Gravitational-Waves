# Prompt for a new session — execute the public data release

Copy-paste everything below the line into a fresh Claude session that has
access to **both** repositories:

- `ming-256/GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves` (this
  private working repo — read access is enough)
- `ming-256/GW170817-bright-siren-H0` (the public data-release repo — write
  access needed)

Zenodo upload and GitHub-release publishing are interactive and will be done
by me (the user); the session should prepare everything up to that point.

---

Execute the public data release for the Yang et al. (2026) MNRAS paper
"Rapid Hubble constant inference from GW170817 using GPU-accelerated nested
sampling". The plan has already been audited and written down — do not
re-derive it. Your working documents, in the private repo, are:

- `mnras_paper/data_release_audit.md` — the authoritative plan. §5.2 is the
  target public-repo layout, §5.3 the current→target path map, §5.4 the
  keep-out list, §6 the README/MANIFEST drafts, §7.4 the Zenodo procedure,
  §8 the Tier A/B/C fix list.
- `mnras_paper/data_release_inventory.csv` — 563 rows classifying every file
  (cited / dead / keep-private) with recommended actions.

Do the following, in order:

## 1. Publish the plotting and analysis scripts to the public GitHub repo

1. On a feature branch of `GW170817-bright-siren-H0` (e.g.
   `prepare-data-release`), restructure to the §5.2 layout: the 9 curated
   figure/table scripts (`scripts/`, including `_plot_utils.py` and
   `build_paper_tables.py`), the 9 analysis scripts (`analysis/`), the
   summary CSVs (`results/gwtc1_phasemarg/`, `results/test_suite/`
   run catalogue and sweep summaries — **not** the per-run `sNN__*/`
   chain directories), and `paper/{figures,tables}/` mirrors.
2. Prune the dead files listed in the inventory CSV from the public surface
   (they stay in the private repo).
3. Add the supporting files from audit §6 and §8 Tier B: `MANIFEST.md`,
   `CITATION.cff`, `environment.yml`, `regenerate.sh`, `run_chains.sh`,
   `docs/{reproducibility,chain_regeneration,data_provenance}.md`, and
   `LICENSE` (MIT for code, CC-BY-4.0 for data/figures).
4. Verify on a clean clone that `regenerate.sh` reproduces the seven figure
   PDFs, the four table `.tex` includes, and `paper/main.pdf` from the
   committed CSVs (CPU-only, ~3 min). Fix paths until it does.
5. Open a PR on the public repo for review; do not merge without approval.

## 2. Prepare the chain deposit for Zenodo

1. Collect the 17 cited nested-sampling chains
   (`Results/test_suite/sNN__*/samples.csv` plus each run's config/log) as
   listed in the run catalogue; package them as one or more compressed
   bundles (~5 GB total, well under Zenodo's 50 GB/record limit).
2. Generate a `SHA256SUMS` file and a bundle-level README explaining the
   directory placement expected by `regenerate.sh`
   (`results/test_suite/sNN__*/samples.csv`).
3. Write the Zenodo metadata (title "GW170817 nested-sampling chains for
   the Yang et al. 2026 release", 4 authors, description, keywords, licence
   CC-BY-4.0) as a `zenodo_metadata.yml`/JSON I can paste into the upload
   form. I will do the interactive upload; stage the bundles somewhere I can
   download them and give me exact step-by-step upload instructions
   (audit §7.4 has the procedure, including the GitHub→Zenodo integration
   for the code snapshot DOI: tag `v1.0.0`, create a GitHub Release, Zenodo
   mints the DOI automatically).

## 3. Backfill the DOIs once I report them back

1. In the private repo: update `Yang2026DataRelease` in
   `mnras_paper/references.bib` (and `mnras_paper/arxiv/references.bib`)
   to the DOI-augmented form given in audit §7.1, update the Data
   Availability section of `main.tex` accordingly, regenerate `main.bbl`
   for both copies, and recompile.
2. In the public repo: replace every `TODO` DOI placeholder in README,
   CITATION.cff, and MANIFEST with the minted DOIs; cross-link the chain
   record and the code-snapshot record via Zenodo "Related identifiers".

Throughout: commit in small, reviewable units; never push chains or any
file on the audit §5.4 keep-out list to GitHub; and report anything in the
audit that no longer matches reality (files moved/renamed since 2026-05-24)
instead of guessing.
