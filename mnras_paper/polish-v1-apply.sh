#!/usr/bin/env bash
# Apply the polish-v1 patches to a fresh clone of ming-256/GW170817-bright-siren-H0.
#
# Prerequisite: this script is run from inside the cloned public repo, and
# the Yang+2026 main development tree (with the original Results/ paths) is
# at $DEV_TREE.  By default DEV_TREE points at the path used to author this
# patch; override with `DEV_TREE=/path/to/main/repo bash polish-v1-apply.sh`.
#
# After this script: review the diff, then push the branch and open the PR.

set -euo pipefail

DEV_TREE="${DEV_TREE:-/Users/mingyang/Desktop/Project/CambridgeProject/GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves}"
PATCH_DIR="${PATCH_DIR:-$DEV_TREE/mnras_paper}"

# Sanity checks --------------------------------------------------------------

[ -d .git ] || { echo "Run this from a clone of the public repo (no .git found)"; exit 1; }
[ -f scripts/_plot_utils.py ] || { echo "scripts/_plot_utils.py missing — wrong directory?"; exit 1; }
[ -f "$PATCH_DIR/polish-v1-code.patch" ] || { echo "polish-v1-code.patch not found at $PATCH_DIR"; exit 1; }

# 1. Branch ------------------------------------------------------------------

git checkout -b polish-v1

# 2. Apply the code-only diff -------------------------------------------------

git apply "$PATCH_DIR/polish-v1-code.patch"
echo "  code patches applied: 8 source files + 2 docs files"

# 3. Copy the 8 PhaseMarg derived CSVs ----------------------------------------

mkdir -p results/gwtc1_phasemarg
for f in \
    PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv \
    PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_flatZ.csv \
    PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv \
    PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_vp250.csv \
    PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv \
    PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_flatZ.csv \
    PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv \
    PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_vp250.csv
do
    cp -f "$DEV_TREE/Results/gwtc1_phasemarg/$f"  "results/gwtc1_phasemarg/$f"
done
echo "  8 PhaseMarg derived CSVs staged from $DEV_TREE"

# 4. Copy the scaling-study summary CSV --------------------------------------

mkdir -p results/scaling_study
cp -f "$DEV_TREE/Results/scaling_study/scaling_summary_full.csv"  results/scaling_study/scaling_summary_full.csv
echo "  scaling_summary_full.csv staged"

# 5. Refresh paper_diagnostics.csv via analyze_psis_khat.py ------------------
#    (the case fix in patch 3 means the script now writes to results/ rather
#    than Results/; re-run from a clean state if you want the row mode to
#    match the new path)
#
#    Skipping by default; uncomment if needed:
# python analysis/analyze_psis_khat.py

# 6. Verify ------------------------------------------------------------------

echo
echo "Patch applied.  Stage the new CSVs and review:"
echo "    git add results/gwtc1_phasemarg/PhaseMarg_*.csv results/scaling_study/"
echo "    git diff --cached --stat"
echo
echo "To verify the full path works, you also need:"
echo "    - the 17 cited per-run chains at results/test_suite/sNN__*/ (Zenodo)"
echo "    - results/GW170817_GWTC-1.hdf5 (LVK P1800061)"
echo "    - results/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_nocosmo.h5 (LVK GWTC-2.1 Zenodo)"
echo "    - export GWTC1_HDF5=\$(pwd)/results/GW170817_GWTC-1.hdf5"
echo "    - export GWTC2P1_GW150914_HDF5=\$(pwd)/results/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_nocosmo.h5"
echo "Then run: bash regenerate.sh"
echo "Expected: 7 figure PDFs + 4 table .tex files + 11-page paper/main.pdf, no errors."
