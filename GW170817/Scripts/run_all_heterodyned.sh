#!/usr/bin/env bash
# Run all heterodyned sampling variants for GW170817.
# 3 scripts x 2 waveforms = 6 runs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_DIR"

LOG_DIR="Results/logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

COMMON_ARGS=(
    --data-source local
    --psd-source gwtc1
    --ref-params gwtc1
    --phase-marginalization
    --output-dir Results/gwtc1_phasemarg
)

SCRIPTS=(
    "GW170817/Scripts/GW170817_heterodyned_1.py"
    "GW170817/Scripts/GW170817_heterodyned_2.py"
    "GW170817/Scripts/GW170817_heterodyned_3.py"
)
TAGS=("baseline" "flatZ" "vp250")

WAVEFORMS=("IMRPhenomD_NRTidalv2" "TaylorF2")

TOTAL=$((${#SCRIPTS[@]} * ${#WAVEFORMS[@]}))
RUN=0
OVERALL_START=$SECONDS

for i in "${!SCRIPTS[@]}"; do
    for wf in "${WAVEFORMS[@]}"; do
        RUN=$((RUN + 1))
        TAG="${TAGS[$i]}_${wf}"
        LOG_FILE="$LOG_DIR/${TIMESTAMP}_${TAG}.log"

        echo "=== [$RUN/$TOTAL] ${TAGS[$i]} / $wf ==="
        echo "  Script: ${SCRIPTS[$i]}"
        echo "  Log:    $LOG_FILE"

        START=$SECONDS
        python "${SCRIPTS[$i]}" --waveform "$wf" "${COMMON_ARGS[@]}" 2>&1 | tee "$LOG_FILE"
        ELAPSED=$((SECONDS - START))

        echo "  Completed in ${ELAPSED}s"
        echo ""
    done
done

TOTAL_TIME=$((SECONDS - OVERALL_START))
echo "=== All $TOTAL runs completed in ${TOTAL_TIME}s ==="
