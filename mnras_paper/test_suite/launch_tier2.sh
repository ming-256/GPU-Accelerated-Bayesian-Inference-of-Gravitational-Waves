#!/usr/bin/env bash
# ============================================================================
# Tier 2 GPU runs for the MNRAS referee response.
#
# Launches every run the referees M2 / M4 / M7 require, into the existing
# Results/test_suite/sNN__... convention. Outputs are consumed by:
#   mnras_paper/test_suite/analysis/analyze_seed_ensemble.py  (M2)
#   mnras_paper/test_suite/analysis/analyze_bimodality_imrx.py (M4)
#   mnras_paper/test_suite/analysis/analyze_nmcmc_sweep.py    (M7)
#
# Hardware assumption: one NVIDIA A100 GPU + the PhD conda env.
# Total serial wall-clock: ~9 h. Trivially fan-out-able across GPUs by
# running blocks (or individual lines) in separate shells; runs within a
# block are independent.
#
# All runs use:
#   --data-source local        (GWOSC HDF5 in EventData/GWOSC/GW170817/)
#   --psd-source gwtc1         (official BayesWave GWTC-1 PSDs)
#   --ref-params gwtc1         (GWTC-1 heterodyne reference parameters)
#   --phase-marginalization    (14-d, matches science runs)
#   --n-live 5000 --num-delete 2500 --n-bins 501  (matches s14/s10 baselines)
#
# Run from the repo root:
#   cd /path/to/GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves
#   bash mnras_paper/test_suite/launch_tier2.sh
#
# ============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# 0. Environment + safety
# ---------------------------------------------------------------------------
# Adjust if your conda installation is elsewhere.
CONDA_BASE="${CONDA_BASE:-/opt/miniconda3}"
# shellcheck disable=SC1091
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate PhD

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

PY=GW170817/Scripts
RESULTS=Results/test_suite

# Common flag block (everything except --output-dir and the variant-specific bits).
COMMON_COMMON=(
    --data-source local --psd-source gwtc1 --ref-params gwtc1
    --phase-marginalization
    --n-live 5000 --num-delete 2500 --n-bins 501
)

# ---------------------------------------------------------------------------
# M4 — IMRX (NRTidalv3) mode-isolated bimodality
#     Two runs, ~15-20 min each → ~40 min total. Smallest block; run first.
#     The s14 unrestricted IMRX run already exists.
# ---------------------------------------------------------------------------
echo "=== M4: IMRX mode-isolated bimodality (2 runs) ==="

python "$PY/GW170817_heterodyned_2.py" \
    --waveform IMRPhenomXAS_NRTidalv3 \
    "${COMMON_COMMON[@]}" \
    --dL-lo 30 --dL-hi 75 --seed 0 \
    --output-dir "$RESULTS/s19__gw170817__imrphenomxas_nrtidalv3__flatz__dL30-75__refGWTC1__seed0000"

python "$PY/GW170817_heterodyned_2.py" \
    --waveform IMRPhenomXAS_NRTidalv3 \
    "${COMMON_COMMON[@]}" \
    --dL-lo 10 --dL-hi 30 --seed 0 \
    --output-dir "$RESULTS/s19__gw170817__imrphenomxas_nrtidalv3__flatz__dL10-30__refGWTC1__seed0000"

# ---------------------------------------------------------------------------
# M7 — IMRX slice-step (n_mcmc) convergence sweep
#     6 runs (3 step counts × 2 priors). Default code is 8*NUM_DIMS = 112;
#     paper text claims 5*NUM_DIMS = 70. Sweep tests {5, 10, 20}*14 = {70,
#     140, 280}. Wall-clock scales roughly linearly with n_mcmc.
#     Estimate: 70-step ≈ 12 min, 140-step ≈ 22 min, 280-step ≈ 40 min.
#     Total ≈ 2 × (12 + 22 + 40) ≈ 2h30.
#
#     Baseline branch uses heterodyned_1.py (matches s14 production runner).
#     Direct uniform-in-d_L branch uses heterodyned_2.py (the --dL-* runner).
# ---------------------------------------------------------------------------
echo "=== M7: n_mcmc convergence sweep (6 runs) ==="

for N in 70 140 280; do
    NTAG=$(printf "%03d" "$N")
    # Baseline (volumetric d_L^2 prior)
    python "$PY/GW170817_heterodyned_1.py" \
        --waveform IMRPhenomXAS_NRTidalv3 \
        "${COMMON_COMMON[@]}" \
        --n-mcmc "$N" --seed 0 \
        --output-dir "$RESULTS/s21__gw170817__imrphenomxas_nrtidalv3__baseline__nmcmc${NTAG}__seed0000"

    # Direct uniform-in-d_L
    python "$PY/GW170817_heterodyned_2.py" \
        --waveform IMRPhenomXAS_NRTidalv3 \
        "${COMMON_COMMON[@]}" \
        --dL-lo 10 --dL-hi 75 \
        --n-mcmc "$N" --seed 0 \
        --output-dir "$RESULTS/s21__gw170817__imrphenomxas_nrtidalv3__flatz__nmcmc${NTAG}__seed0000"
done

# ---------------------------------------------------------------------------
# M2 — Bimodality seed ensemble (IMR/NRTidalv2)
#     18 runs (6 new seeds × 3 modes). Existing seeds 0 (s10) and 1 (s18)
#     give N=2; add seeds {2..7} for N=8, enough to nail σ(lnZ).
#     Per-run ~15-20 min → ~5h total. Embarrassingly parallel across seeds.
# ---------------------------------------------------------------------------
echo "=== M2: bimodality seed ensemble (18 runs) ==="

for S in 2 3 4 5 6 7; do
    STAG=$(printf "%04d" "$S")

    # Mode A: d_L ∈ [30, 75], default heterodyne ref
    python "$PY/GW170817_heterodyned_2.py" \
        --waveform IMRPhenomD_NRTidalv2 \
        "${COMMON_COMMON[@]}" \
        --dL-lo 30 --dL-hi 75 --seed "$S" \
        --output-dir "$RESULTS/s20__gw170817__imrphenomd_nrtidalv2__flatz__dL30-75__refGWTC1__seed${STAG}"

    # Mode B: d_L ∈ [10, 30], default heterodyne ref
    python "$PY/GW170817_heterodyned_2.py" \
        --waveform IMRPhenomD_NRTidalv2 \
        "${COMMON_COMMON[@]}" \
        --dL-lo 10 --dL-hi 30 --seed "$S" \
        --output-dir "$RESULTS/s20__gw170817__imrphenomd_nrtidalv2__flatz__dL10-30__refGWTC1__seed${STAG}"

    # Unrestricted: d_L ∈ [10, 75], Mode-B-anchored heterodyne ref (matches s10/s18 convention)
    python "$PY/GW170817_heterodyned_2.py" \
        --waveform IMRPhenomD_NRTidalv2 \
        "${COMMON_COMMON[@]}" \
        --dL-lo 10 --dL-hi 75 --ref-modeB --seed "$S" \
        --output-dir "$RESULTS/s20__gw170817__imrphenomd_nrtidalv2__flatz__dL10-75__refModeB__seed${STAG}"
done

# ---------------------------------------------------------------------------
# Post-run analysis (CPU only, runs locally after the GPU jobs land)
# ---------------------------------------------------------------------------
echo "=== Running aggregator scripts ==="
python mnras_paper/test_suite/analysis/analyze_bimodality_imrx.py
python mnras_paper/test_suite/analysis/analyze_nmcmc_sweep.py
python mnras_paper/test_suite/analysis/analyze_seed_ensemble.py

echo "=== Done. CSVs in Results/test_suite/, figures in mnras_paper/figures/. ==="
