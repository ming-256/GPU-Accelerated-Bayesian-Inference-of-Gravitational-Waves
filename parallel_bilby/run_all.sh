#!/usr/bin/env bash
# ============================================================================
# run_all.sh — Generate data and submit/run all parallel_bilby jobs
#
# All results go into parallel_bilby/results/<label>/
# Timing for every stage is logged to results/timing_summary.txt
#
# Usage:
#   bash run_all.sh              # generate + submit all 3 runs (Slurm)
#   bash run_all.sh --gen-only   # generate data dumps only (no submit)
#   bash run_all.sh --local N    # run locally with N MPI processes (no Slurm)
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

MODE="${1:---submit}"
NPROCS="${2:-4}"

# ============================================================================
# Configuration
# ============================================================================
declare -a CONFIGS=(
    "GW150914/GW150914_IMRPhenomD.ini"
    "GW170817/GW170817_IMRPhenomD_NRTidalv2.ini"
    "GW170817/GW170817_TaylorF2.ini"
)

declare -a LABELS=(
    "GW150914_IMRPhenomD"
    "GW170817_IMRPhenomD_NRTidalv2"
    "GW170817_TaylorF2"
)

TOTAL=${#CONFIGS[@]}
RESULTS_DIR="${SCRIPT_DIR}/results"
TIMING_FILE="${RESULTS_DIR}/timing_summary.txt"

# Create results directory
mkdir -p "$RESULTS_DIR"

# ============================================================================
# Timing helpers
# ============================================================================
timer_start() { date +%s; }
timer_elapsed() {
    local start=$1
    local end
    end=$(date +%s)
    local secs=$((end - start))
    local h=$((secs / 3600))
    local m=$(( (secs % 3600) / 60 ))
    local s=$((secs % 60))
    printf "%02d:%02d:%02d (%d s)" "$h" "$m" "$s" "$secs"
}

log_timing() {
    local label="$1"
    local stage="$2"
    local elapsed="$3"
    local line
    line="$(date '+%Y-%m-%d %H:%M:%S')  ${label}  ${stage}  ${elapsed}"
    echo "$line" | tee -a "$TIMING_FILE"
}

# ============================================================================
# Initialize timing log
# ============================================================================
{
    echo "============================================================"
    echo "  Parallel Bilby — Timing Summary"
    echo "  Started: $(date)"
    echo "============================================================"
    echo ""
    printf "%-20s  %-30s  %-15s  %-20s\n" "TIMESTAMP" "RUN" "STAGE" "ELAPSED"
    echo "------------------------------------------------------------------------------------"
} >> "$TIMING_FILE"

GLOBAL_START=$(timer_start)

# ============================================================================
# Step 1: Data generation
# ============================================================================
echo "============================================================"
echo "  Parallel Bilby — Data Generation"
echo "  Results directory: $RESULTS_DIR"
echo "============================================================"

for i in "${!CONFIGS[@]}"; do
    INI="${CONFIGS[$i]}"
    LABEL="${LABELS[$i]}"
    echo ""
    echo "--- [$((i+1))/$TOTAL] Generating: $LABEL ---"
    echo "  Config: $INI"

    # cd into the config directory so prior-file paths resolve correctly
    CONFIG_DIR="$(dirname "$INI")"
    CONFIG_FILE="$(basename "$INI")"

    GEN_START=$(timer_start)

    pushd "$CONFIG_DIR" > /dev/null
    parallel_bilby_generation "$CONFIG_FILE"
    popd > /dev/null

    GEN_ELAPSED=$(timer_elapsed "$GEN_START")
    log_timing "$LABEL" "data_generation" "$GEN_ELAPSED"
    echo "  Done. (${GEN_ELAPSED})"
done

# ============================================================================
# Step 2: Submit or run
# ============================================================================
if [[ "$MODE" == "--gen-only" ]]; then
    TOTAL_ELAPSED=$(timer_elapsed "$GLOBAL_START")
    log_timing "ALL" "gen-only_total" "$TOTAL_ELAPSED"
    echo ""
    echo "Data generation complete. Total time: $TOTAL_ELAPSED"
    echo "Timing log: $TIMING_FILE"
    exit 0
fi

echo ""
echo "============================================================"
echo "  Parallel Bilby — Sampling"
echo "============================================================"

for i in "${!CONFIGS[@]}"; do
    LABEL="${LABELS[$i]}"
    OUTDIR="${RESULTS_DIR}/${LABEL}"
    PICKLE="${OUTDIR}/data/${LABEL}_data_dump.pickle"

    echo ""
    echo "--- [$((i+1))/$TOTAL] Running: $LABEL ---"

    if [[ ! -f "$PICKLE" ]]; then
        echo "  ERROR: Data dump not found at $PICKLE"
        echo "  Run with --gen-only first, or check generation output."
        log_timing "$LABEL" "sampling" "SKIPPED — no data dump"
        continue
    fi

    SAMP_START=$(timer_start)

    if [[ "$MODE" == "--local" ]]; then
        echo "  Running locally with $NPROCS MPI processes..."
        mpirun -n "$NPROCS" parallel_bilby_analysis "$PICKLE"

        SAMP_ELAPSED=$(timer_elapsed "$SAMP_START")
        log_timing "$LABEL" "sampling_local" "$SAMP_ELAPSED"
        echo "  Done. (${SAMP_ELAPSED})"
    else
        # Submit via Slurm (uses the auto-generated submit script)
        SUBMIT_SCRIPT="${OUTDIR}/submit/bash_${LABEL}.sh"
        if [[ -f "$SUBMIT_SCRIPT" ]]; then
            echo "  Submitting: $SUBMIT_SCRIPT"
            sbatch "$SUBMIT_SCRIPT"
            log_timing "$LABEL" "slurm_submitted" "N/A (async)"
        else
            echo "  WARNING: Submit script not found at $SUBMIT_SCRIPT"
            echo "  Check the outdir for the correct submit script name."
            ls "${OUTDIR}/submit/" 2>/dev/null || echo "  (submit/ directory missing)"
            log_timing "$LABEL" "sampling" "SKIPPED — no submit script"
        fi
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
echo "  Total wall time: $TOTAL_ELAPSED"
echo "  Timing log: $TIMING_FILE"
echo "  Results:    $RESULTS_DIR/"
echo "============================================================"
echo ""
echo "Results directory structure:"
ls -d "$RESULTS_DIR"/*/ 2>/dev/null || echo "  (no result subdirectories yet)"
