# arXiv submission bundle

Self-contained, flattened copy of the MNRAS manuscript for upload to arXiv.
**Do not hand-edit `main.tex` here** — it is generated from the working-tree
master `../main.tex` by `../make_arxiv_bundle.sh`. The only difference from the
master is the `\graphicspath` (set to `{./}`) and the four `\input` paths
(bare filenames instead of `../Results/gwtc1_phasemarg/...`).

To regenerate after any change to the master, tables, or figures:

```bash
cd mnras_paper && bash make_arxiv_bundle.sh
```

That rebuilds this directory, recompiles it from scratch (pdflatex → bibtex →
pdflatex ×2) to prove it is self-contained, and writes
`../arxiv-submission.tar.gz` (source only — no PDF or build artifacts).

## Upload

Upload `arxiv-submission.tar.gz`. arXiv's AutoTeX will compile it. The bundle
contains:

- `main.tex`, `main.bbl`, `references.bib`
- `mnras.cls`, `mnras.bst` (included for safety; arXiv's TeX Live also ships them)
- 4 table fragments (`table1`, `table5`, `table6`, `tableW`)
- 7 figure PDFs

`main.bbl` is included so arXiv does not depend on a BibTeX run. Compiles to
12 pages with zero undefined references and zero missing files.

## arXiv metadata

| Field | Value |
|---|---|
| **Primary category** | `astro-ph.CO` (Cosmology and Nongalactic Astrophysics) — bright-siren H0 |
| **Cross-list** | `gr-qc` (gravitational waves); `astro-ph.IM` (GPU nested-sampling methods) |
| **Optional `astro-ph.HE`** | reasonable given the BNS source; not required |
| **MSC / ACM class** | leave blank (not applicable to astro-ph) |
| **Title** | Rapid Hubble constant inference from GW170817 using GPU-accelerated nested sampling: prior sensitivity and the limits of post-hoc reweighting |
| **Journal-ref / comments** | "Submitted to MNRAS" (add the journal-ref once accepted) |
| **License** | choose at submission (default arXiv non-exclusive, or CC BY 4.0) |

`\documentclass[usenatbib]{mnras}` is the correct MNRAS format; arXiv renders
it natively. The MNRAS *keywords* live in the manuscript and are independent of
the arXiv category fields above.
