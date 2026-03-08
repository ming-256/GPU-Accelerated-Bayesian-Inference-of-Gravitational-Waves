#!/bin/bash
# Extended scaling study: n_live = {20000, 50000, 100000}
# Uses num_delete = 0.5 * n_live (updated in heterodyned_1.py)
# Runs baseline prior (heterodyned_1) with IMRPhenomD_NRTidalv2, phase marginalization
#
# Usage:
#   cd GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves
#   bash GW170817/Scripts/run_scaling_extended.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_DIR"

OUTPUT_DIR="Results/scaling_study"
LOG_DIR="$OUTPUT_DIR/logs"
SUMMARY="$OUTPUT_DIR/scaling_summary_extended.csv"

mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
WAVEFORM="IMRPhenomD_NRTidalv2"

# Write CSV header
echo "timestamp,waveform,n_live,num_delete_frac,dead_points,log_evidence,sigma_log_z,data_load_s,het_setup_s,init_s,jit_s,sampling_s,total_s" > "$SUMMARY"

for N_LIVE in 20000 50000 100000; do
    echo "=============================================="
    echo "  Running n_live = $N_LIVE"
    echo "=============================================="

    LOGFILE="$LOG_DIR/${TIMESTAMP}_${WAVEFORM}_nlive${N_LIVE}.log"

    python GW170817/Scripts/GW170817_heterodyned_1.py \
        --waveform "$WAVEFORM" \
        --data-source local \
        --psd-source gwtc1 \
        --ref-params gwtc1 \
        --phase-marginalization \
        --n-live "$N_LIVE" \
        --output-dir "$OUTPUT_DIR" \
        2>&1 | tee "$LOGFILE"

    # Parse timing from log
    DATA_LOAD=$(grep -oP 'Data loading:\s+\K[\d.]+' "$LOGFILE")
    HET_SETUP=$(grep -oP 'Heterodyne setup:\s+\K[\d.]+' "$LOGFILE")
    INIT=$(grep -oP 'Init \+ prior:\s+\K[\d.]+' "$LOGFILE")
    JIT=$(grep -oP 'JIT compilation.*:\s+\K[\d.]+' "$LOGFILE")
    SAMPLING=$(grep -oP 'Sampling:\s+\K[\d.]+' "$LOGFILE")
    TOTAL=$(grep -oP 'Total:\s+\K[\d.]+' "$LOGFILE")
    LOG_Z=$(grep -oP 'Log Evidence: \K[\d.-]+' "$LOGFILE")
    SIGMA_Z=$(grep -oP 'Log Evidence: [\d.-]+ \+/- \K[\d.]+' "$LOGFILE")
    DEAD=$(grep -oP 'Dead points: (\d+)' "$LOGFILE" | tail -1 | grep -oP '\d+')

    echo "${TIMESTAMP},${WAVEFORM},${N_LIVE},0.5,${DEAD},${LOG_Z},${SIGMA_Z},${DATA_LOAD},${HET_SETUP},${INIT},${JIT},${SAMPLING},${TOTAL}" >> "$SUMMARY"

    echo ""
    echo "  n_live=$N_LIVE complete. Sampling: ${SAMPLING}s, Total: ${TOTAL}s"
    echo ""
done

echo ""
echo "=============================================="
echo "  Extended scaling study complete"
echo "=============================================="
echo ""
cat "$SUMMARY"
