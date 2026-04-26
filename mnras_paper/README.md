# MNRAS Paper Draft

Working draft for the GW170817 GPU-accelerated nested-sampling paper.

## Files

- `main.tex` - manuscript scaffold in MNRAS style.
- `references.bib` - starter BibTeX database; entries marked TODO should be verified before submission.
- `result_inventory.md` - source-of-truth result files, headline numbers, figure shortlist, and open checks.

For a fuller provenance map linking CSVs, plots, logs, and generating scripts, see
`../paper_knowledge_base/result_link_index.md`.

## Build

From this directory:

```bash
latexmk -pdf main.tex
```

If `mnras.cls` is unavailable, install the MNRAS LaTeX template or a TeX distribution package that provides it before building.
