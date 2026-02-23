#!/usr/bin/env bash
# ============================================================================
# run_all.sh — Generate data and submit/run all bilby analyses
#
# Reads cluster settings from config.sh.  All results go into results/.
#
# Usage:
#   bash run_all.sh                  # generate data + submit Slurm jobs
#   bash run_all.sh --gen-only       # generate data pickles only (no sampling)
#   bash run_all.sh --local          # generate + run locally with MPI
#   bash run_all.sh --local-serial   # generate + run locally (no MPI, testing)
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

MODE="${1:---submit}"

# ── Load user configuration ──────────────────────────────────────────────────
if [[ ! -f config.sh ]]; then
    echo "ERROR: config.sh not found. It should be in the same directory as run_all.sh."
    exit 1
fi
# shellcheck disable=SC1091
source config.sh

NPROCS=$(( NODES * CORES_PER_NODE ))

# ── Run definitions ──────────────────────────────────────────────────────────
# Each entry: SCRIPT|WAVEFORM_ARG|WALLTIME|LABEL
declare -a RUNS=(
    "GW150914/run_GW150914.py||${WALLTIME_GW150914}|GW150914_IMRPhenomD"
    "GW170817/run_GW170817.py|--waveform IMRPhenomD_NRTidalv2|${WALLTIME_GW170817}|GW170817_IMRPhenomD_NRTidalv2"
    "GW170817/run_GW170817.py|--waveform TaylorF2|${WALLTIME_GW170817}|GW170817_TaylorF2"
)

RESULTS_DIR="${SCRIPT_DIR}/results"
TIMING_FILE="${RESULTS_DIR}/timing_summary.txt"
mkdir -p "$RESULTS_DIR"

# ── Timing helpers ───────────────────────────────────────────────────────────
timer_start() { date +%s; }
timer_elapsed() {
    local secs=$(( $(date +%s) - $1 ))
    printf "%02d:%02d:%02d (%d s)" $((secs/3600)) $(((secs%3600)/60)) $((secs%60)) "$secs"
}
log_timing() {
    local line
    line="$(date '+%Y-%m-%d %H:%M:%S')  $1  $2  $3"
    echo "$line" | tee -a "$TIMING_FILE"
}

# ── Initialize timing log ───────────────────────────────────────────────────
{
    echo "============================================================"
    echo "  Bilby HPC — Timing Summary"
    echo "  Started: $(date)"
    echo "  Config:  NODES=${NODES}  CORES_PER_NODE=${CORES_PER_NODE}"
    echo "============================================================"
    echo ""
    printf "%-20s  %-35s  %-15s  %-20s\n" "TIMESTAMP" "RUN" "STAGE" "ELAPSED"
    echo "------------------------------------------------------------------------------------"
} >> "$TIMING_FILE"

GLOBAL_START=$(timer_start)

# ============================================================================
# Step 1: Data generation (runs on login node, needs internet)
# ============================================================================
echo "============================================================"
echo "  Step 1: Data Generation"
echo "  (downloading GWOSC data, estimating PSDs, saving pickles)"
echo "============================================================"

TOTAL=${#RUNS[@]}
declare -a PICKLE_PATHS=()

for i in "${!RUNS[@]}"; do
    IFS='|' read -r SCRIPT WAVEFORM_ARG WALLTIME LABEL <<< "${RUNS[$i]}"
    OUTDIR="${RESULTS_DIR}/${LABEL}"

    echo ""
    echo "--- [$((i+1))/$TOTAL] Generating: $LABEL ---"

    GEN_START=$(timer_start)

    # shellcheck disable=SC2086
    python3 "${SCRIPT}" ${WAVEFORM_ARG} --outdir "$OUTDIR" --gen-only \
        --nlive "${NLIVE}" --num-repeats "${NUM_REPEATS}"

    GEN_ELAPSED=$(timer_elapsed "$GEN_START")
    log_timing "$LABEL" "data_generation" "$GEN_ELAPSED"
    echo "  Done. ($GEN_ELAPSED)"

    # Find the pickle
    PICKLE=$(find "$OUTDIR" -name '*_data_dump.pickle' -print -quit 2>/dev/null || echo "")
    PICKLE_PATHS+=("$PICKLE")
done

if [[ "$MODE" == "--gen-only" ]]; then
    TOTAL_ELAPSED=$(timer_elapsed "$GLOBAL_START")
    log_timing "ALL" "gen-only_total" "$TOTAL_ELAPSED"
    echo ""
    echo "Data generation complete.  Total: $TOTAL_ELAPSED"
    echo "Pickles:"
    for p in "${PICKLE_PATHS[@]}"; do echo "  $p"; done
    echo "Timing log: $TIMING_FILE"
    exit 0
fi

# ============================================================================
# Step 2: Sampling (Slurm submit or local)
# ============================================================================
echo ""
echo "============================================================"
echo "  Step 2: Sampling"
echo "============================================================"

for i in "${!RUNS[@]}"; do
    IFS='|' read -r SCRIPT WAVEFORM_ARG WALLTIME LABEL <<< "${RUNS[$i]}"
    PICKLE="${PICKLE_PATHS[$i]}"
    OUTDIR="${RESULTS_DIR}/${LABEL}"

    echo ""
    echo "--- [$((i+1))/$TOTAL] Sampling: $LABEL ---"

    if [[ -z "$PICKLE" || ! -f "$PICKLE" ]]; then
        echo "  ERROR: pickle not found for $LABEL — skipping"
        log_timing "$LABEL" "sampling" "SKIPPED"
        continue
    fi

    # ── Local run (no Slurm) ─────────────────────────────────────────────
    if [[ "$MODE" == "--local" || "$MODE" == "--local-serial" ]]; then
        SAMP_START=$(timer_start)

        if [[ "$MODE" == "--local" ]]; then
            echo "  Running with mpirun -n $NPROCS ..."
            # shellcheck disable=SC2086
            mpirun -n "$NPROCS" python3 "${SCRIPT}" ${WAVEFORM_ARG} \
                --outdir "$OUTDIR" --from-pickle "$PICKLE" \
                --nlive "${NLIVE}" --num-repeats "${NUM_REPEATS}"
        else
            echo "  Running serial (no MPI, for testing)..."
            # shellcheck disable=SC2086
            python3 "${SCRIPT}" ${WAVEFORM_ARG} \
                --outdir "$OUTDIR" --from-pickle "$PICKLE" \
                --nlive "${NLIVE}" --num-repeats "${NUM_REPEATS}"
        fi

        SAMP_ELAPSED=$(timer_elapsed "$SAMP_START")
        log_timing "$LABEL" "sampling_local" "$SAMP_ELAPSED"
        echo "  Done. ($SAMP_ELAPSED)"

    # ── Slurm submission ─────────────────────────────────────────────────
    else
        SUBMIT_DIR="${OUTDIR}/submit"
        mkdir -p "$SUBMIT_DIR"
        SUBMIT_SCRIPT="${SUBMIT_DIR}/slurm_${LABEL}.sh"

        # Build Slurm batch script
        {
            echo "#!/bin/bash"
            echo "#SBATCH --job-name=${LABEL}"
            echo "#SBATCH --output=${OUTDIR}/slurm_%j.out"
            echo "#SBATCH --error=${OUTDIR}/slurm_%j.err"
            echo "#SBATCH --nodes=${NODES}"
            echo "#SBATCH --ntasks-per-node=${CORES_PER_NODE}"
            echo "#SBATCH --time=${WALLTIME}"
            [[ -n "${SLURM_ACCOUNT:-}" ]]   && echo "#SBATCH --account=${SLURM_ACCOUNT}"
            [[ -n "${SLURM_PARTITION:-}" ]] && echo "#SBATCH --partition=${SLURM_PARTITION}"
            [[ -n "${SLURM_EXTRA:-}" ]]     && echo "#SBATCH ${SLURM_EXTRA}"
            echo ""
            echo "# Activate environment"
            echo "source ${SCRIPT_DIR}/pbilby_venv/bin/activate"
            echo ""
            echo "cd ${SCRIPT_DIR}"
            echo ""
            echo "echo \"Starting: \$(date)\""
            echo "echo \"Nodes: ${NODES}, Tasks/node: ${CORES_PER_NODE}, Total MPI ranks: ${NPROCS}\""
            echo ""
            echo "mpirun -n ${NPROCS} python3 ${SCRIPT} ${WAVEFORM_ARG} \\"
            echo "    --outdir ${OUTDIR} --from-pickle ${PICKLE} \\"
            echo "    --nlive ${NLIVE} --num-repeats ${NUM_REPEATS}"
            echo ""
            echo "echo \"Finished: \$(date)\""
        } > "$SUBMIT_SCRIPT"

        chmod +x "$SUBMIT_SCRIPT"
        echo "  Submitting: $SUBMIT_SCRIPT"
        sbatch "$SUBMIT_SCRIPT"
        log_timing "$LABEL" "slurm_submitted" "N/A (async)"
    fi
done

# ============================================================================
# Summary
# ============================================================================
TOTAL_ELAPSED=$(timer_elapsed "$GLOBAL_START")
log_timing "ALL" "total" "$TOTAL_ELAPSED"

echo ""
echo "============================================================"
echo "  All jobs dispatched."
echo "  Total wall time:  $TOTAL_ELAPSED"
echo "  Timing log:       $TIMING_FILE"
echo "  Results:          $RESULTS_DIR/"
echo "============================================================"
