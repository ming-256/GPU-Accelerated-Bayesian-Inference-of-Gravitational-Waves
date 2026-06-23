#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# make_arxiv_bundle.sh
#
# Regenerate the self-contained arXiv submission bundle in mnras_paper/arxiv/
# from the working-tree master (mnras_paper/main.tex) and the canonical
# generated tables/figures under ../Results.
#
# The master main.tex intentionally pulls tables/figures from ../../Results so
# that it always rebuilds against the canonical pipeline outputs. arXiv needs a
# flat, self-contained directory, so this script copies every dependency into
# arxiv/ and rewrites the \graphicspath and the four \input paths to bare
# filenames. The only textual difference between ../main.tex and arxiv/main.tex
# is those five path lines.
#
# Usage:  cd mnras_paper && bash make_arxiv_bundle.sh
# Output: arxiv/ (source bundle) + arxiv-submission.tar.gz (upload this)
# ---------------------------------------------------------------------------
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
cd "$here"

R="../Results/gwtc1_phasemarg"
OUT="arxiv"

# MNRAS class/style: not in the repo; resolved from the local TeX install.
PDFLATEX="${PDFLATEX:-/c/Program Files/MiKTeX/miktex/bin/x64/pdflatex}"
BIBTEX="${BIBTEX:-/c/Program Files/MiKTeX/miktex/bin/x64/bibtex}"
KPSEWHICH="${KPSEWHICH:-/c/Program Files/MiKTeX/miktex/bin/x64/kpsewhich}"

# Clear contents rather than the directory inode itself: on Windows the dir
# can be transiently locked by an indexer, which makes `rm -rf "$OUT"` fail.
mkdir -p "$OUT"
rm -rf "${OUT:?}"/* "${OUT:?}"/.[!.]* 2>/dev/null || true

# --- table fragments (4) ---------------------------------------------------
for t in table1_gw150914 table5_prior_sensitivity table6_bimodality tableW_waveform; do
  cp "$R/$t.tex" "$OUT/"
done

# --- figures (7) -----------------------------------------------------------
# Six live under Results/.../plots; one (imr_vs_imrx) lives under figures/.
for f in corner_GW150914_waveform_comparison corner_IMRPhenomD_hetero_vs_unhetero \
         H0_prior_sensitivity bimodality H0_waveform_comparison \
         corner_GW170817_waveform_comparison; do
  cp "$R/plots/$f.pdf" "$OUT/"
done
cp figures/bimodality_imr_vs_imrx.pdf "$OUT/"

# --- bibliography ----------------------------------------------------------
cp main.bbl references.bib "$OUT/"

# --- MNRAS class + style (belt-and-suspenders; arXiv's TeX Live also ships them)
cls="$("$KPSEWHICH" mnras.cls 2>/dev/null)"; [ -n "$cls" ] || { echo "mnras.cls not found"; exit 1; }
bst="$("$KPSEWHICH" mnras.bst 2>/dev/null)"; [ -n "$bst" ] || { echo "mnras.bst not found"; exit 1; }
cp "$cls" "$bst" "$OUT/"

# --- flattened main.tex ----------------------------------------------------
# Rewrite the two external-path constructs with literal string replacement
# (Python) to avoid regex backslash-escaping pitfalls:
#   * the multi-line \graphicspath{...} block -> \graphicspath{{./}}
#   * \input{../Results/gwtc1_phasemarg/X.tex} -> \input{X.tex}
cp main.tex "$OUT/main.tex"
python - "$OUT/main.tex" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s = re.sub(r"\\graphicspath\{.*?\n\}", r"\\graphicspath{{./}}", s, count=1, flags=re.S)
s = s.replace("../Results/gwtc1_phasemarg/", "")
open(p, "w", encoding="utf-8", newline="\n").write(s)
PY

# --- verify it compiles from scratch, self-contained -----------------------
( cd "$OUT"
  "$PDFLATEX" -interaction=nonstopmode -halt-on-error main.tex >/dev/null
  "$BIBTEX"   main >/dev/null
  "$PDFLATEX" -interaction=nonstopmode -halt-on-error main.tex >/dev/null
  "$PDFLATEX" -interaction=nonstopmode -halt-on-error main.tex >/dev/null )

# --- tarball: SOURCE ONLY (no build artifacts, no PDF) ----------------------
tar -czf arxiv-submission.tar.gz -C "$OUT" \
  main.tex main.bbl references.bib mnras.cls mnras.bst \
  table1_gw150914.tex table5_prior_sensitivity.tex \
  table6_bimodality.tex tableW_waveform.tex \
  corner_GW150914_waveform_comparison.pdf \
  corner_IMRPhenomD_hetero_vs_unhetero.pdf \
  H0_prior_sensitivity.pdf bimodality.pdf bimodality_imr_vs_imrx.pdf \
  H0_waveform_comparison.pdf corner_GW170817_waveform_comparison.pdf

# --- drop build artifacts from the working bundle dir ----------------------
( cd "$OUT" && rm -f main.aux main.log main.out main.blg main.fls \
  main.fdb_latexmk pass1.log pass2.log pass3.log bibtex.log )

echo "OK: $OUT/main.pdf built; arxiv-submission.tar.gz written ($(du -h arxiv-submission.tar.gz | cut -f1))"
