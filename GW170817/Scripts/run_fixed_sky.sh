#!/usr/bin/env bash
# Session s19: fixed-sky GW170817 runs (Abbott+2017 reproduction attempt).
#
# Runs IMRPhenomD_NRTidalv2 and IMRPhenomXAS_NRTidalv3 with --fixed-sky
# (±0.001 rad around NGC 4993, emulating Abbott+2017's EM-counterpart-fixed
# sky position).  LVK mass bounds and phase marginalisation match s15.
#
# Usage (from project root):
#   bash GW170817/Scripts/run_fixed_sky.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_DIR"

LOG_DIR="$PROJECT_DIR/Results/logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

SCRIPT="$PROJECT_DIR/GW170817/Scripts/GW170817_heterodyned_1.py"

COMMON=(
    --data-source local
    --psd-source gwtc1
    --ref-params gwtc1
    --phase-marginalization
    --m-comp-lo 0.87
    --m-comp-hi 1.74
    --n-live 5000
    --num-delete 2500
    --n-bins 501
    --seed 0
    --fixed-sky
)

declare -A WAVEFORM_DIRS
WAVEFORM_DIRS["IMRPhenomD_NRTidalv2"]="$PROJECT_DIR/Results/test_suite/s19__gw170817__imrphenomd_nrtidalv2__baseline_lvkbounds_fixedsky__seed0000"
WAVEFORM_DIRS["IMRPhenomXAS_NRTidalv3"]="$PROJECT_DIR/Results/test_suite/s19__gw170817__imrphenomxas_nrtidalv3__baseline_lvkbounds_fixedsky__seed0000"

TOTAL=2
RUN=0
OVERALL_START=$SECONDS

for WF in "IMRPhenomD_NRTidalv2" "IMRPhenomXAS_NRTidalv3"; do
    RUN=$((RUN + 1))
    OUTDIR="${WAVEFORM_DIRS[$WF]}"
    LOG_FILE="$LOG_DIR/${TIMESTAMP}_s19_fixedsky_${WF}.log"

    mkdir -p "$OUTDIR"

    echo "=== [$RUN/$TOTAL] s19 fixed-sky / $WF ==="
    echo "  Output: $OUTDIR"
    echo "  Log:    $LOG_FILE"

    START=$SECONDS
    python "$SCRIPT" --waveform "$WF" --output-dir "$OUTDIR" "${COMMON[@]}" 2>&1 | tee "$LOG_FILE"
    ELAPSED=$((SECONDS - START))

    echo "  Completed in ${ELAPSED}s"
    echo ""
done

TOTAL_TIME=$((SECONDS - OVERALL_START))
echo "=== Both s19 runs completed in ${TOTAL_TIME}s ==="
