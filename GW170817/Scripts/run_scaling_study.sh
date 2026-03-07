#!/usr/bin/env bash
# Scaling study: run GW170817 heterodyned baseline at multiple live-point counts.
# Produces timing data for runtime-vs-n_live plot in the paper.
#
# Usage:
#   bash GW170817/Scripts/run_scaling_study.sh [waveform]
#
# Arguments:
#   waveform  - IMRPhenomD_NRTidalv2 (default) or TaylorF2
#
# Outputs:
#   Results/scaling_study/scaling_{waveform}_{n_live}.csv   (posterior samples)
#   Results/scaling_study/scaling_summary.csv                (timing summary)
#   Results/scaling_study/logs/                              (full logs)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_DIR"

WAVEFORM="${1:-IMRPhenomD_NRTidalv2}"
LIVE_POINTS=(500 1000 2500 5000 10000)

OUT_DIR="Results/scaling_study"
LOG_DIR="$OUT_DIR/logs"
SUMMARY="$OUT_DIR/scaling_summary.csv"
mkdir -p "$LOG_DIR"

COMMON_ARGS=(
    --data-source local
    --psd-source gwtc1
    --ref-params gwtc1
    --phase-marginalization
    --waveform "$WAVEFORM"
    --output-dir "$OUT_DIR"
)

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "================================================================"
echo "SCALING STUDY: $WAVEFORM"
echo "Live points: ${LIVE_POINTS[*]}"
echo "Output: $OUT_DIR"
echo "================================================================"
echo ""

# Write CSV header if file doesn't exist
if [ ! -f "$SUMMARY" ]; then
    echo "timestamp,waveform,n_live,dead_points,log_evidence,sigma_log_z,data_load_s,het_setup_s,init_s,jit_s,sampling_s,total_s" > "$SUMMARY"
fi

TOTAL=${#LIVE_POINTS[@]}
RUN=0
OVERALL_START=$SECONDS

for N in "${LIVE_POINTS[@]}"; do
    RUN=$((RUN + 1))
    LOG_FILE="$LOG_DIR/${TIMESTAMP}_${WAVEFORM}_nlive${N}.log"

    echo "=== [$RUN/$TOTAL] n_live=$N / $WAVEFORM ==="
    echo "  Log: $LOG_FILE"

    START=$SECONDS
    python GW170817/Scripts/GW170817_heterodyned_1.py \
        "${COMMON_ARGS[@]}" \
        --n-live "$N" \
        2>&1 | tee "$LOG_FILE"
    ELAPSED=$((SECONDS - START))

    # Parse timing from log
    DATA_LOAD=$(grep -oP 'Data loading:\s+\K[\d.]+' "$LOG_FILE" | tail -1 || echo "N/A")
    HET_SETUP=$(grep -oP 'Heterodyne setup:\s+\K[\d.]+' "$LOG_FILE" | tail -1 || echo "N/A")
    INIT=$(grep -oP 'Init \+ prior:\s+\K[\d.]+' "$LOG_FILE" | tail -1 || echo "N/A")
    JIT=$(grep -oP 'JIT compilation:\s+\K[\d.]+' "$LOG_FILE" | tail -1 || echo "N/A")
    SAMPLING=$(grep -oP 'Sampling:\s+\K[\d.]+' "$LOG_FILE" | tail -1 || echo "N/A")
    TOTAL_TIME=$(grep -oP 'Total:\s+\K[\d.]+' "$LOG_FILE" | tail -1 || echo "N/A")
    DEAD_PTS=$(grep -oP '(\d+) dead points \[' "$LOG_FILE" | tail -1 | grep -oP '^\d+' || echo "N/A")
    LOG_Z=$(grep -oP 'Log Evidence: \K[\d.-]+' "$LOG_FILE" | tail -1 || echo "N/A")
    SIGMA_Z=$(grep -oP 'Log Evidence: [\d.-]+ \+/- \K[\d.]+' "$LOG_FILE" | tail -1 || echo "N/A")

    echo "$TIMESTAMP,$WAVEFORM,$N,$DEAD_PTS,$LOG_Z,$SIGMA_Z,$DATA_LOAD,$HET_SETUP,$INIT,$JIT,$SAMPLING,$TOTAL_TIME" >> "$SUMMARY"

    echo "  Completed in ${ELAPSED}s (sampling: ${SAMPLING}s)"
    echo ""
done

TOTAL_ELAPSED=$((SECONDS - OVERALL_START))
echo "================================================================"
echo "SCALING STUDY COMPLETE"
echo "Waveform: $WAVEFORM"
echo "Total time: ${TOTAL_ELAPSED}s"
echo "Summary: $SUMMARY"
echo "================================================================"
