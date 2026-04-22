#!/usr/bin/env bash
# Run unheterodyned IMRPhenomD_NRTidalv2 at 2500 live points
# for matched comparison with heterodyned scaling study.
#
# Estimated runtime: ~10-11 hours (within 12-hour cap)
#
# Usage:
#   bash GW170817/Scripts/run_unheterodyned_scaling.sh

set -e
cd "$(dirname "$0")/../.."

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

OUT_DIR="Results/scaling_study"
LOG_DIR="$OUT_DIR/logs"
SCRIPT="GW170817/Scripts/GW170817_unheterodyned_1.py"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$LOG_DIR"

NLIVE=2500
WAVEFORM="IMRPhenomD_NRTidalv2"
LOG="$LOG_DIR/${TIMESTAMP}_unheterodyned_${WAVEFORM}_nlive${NLIVE}.log"

echo "=============================================="
echo "  Unheterodyned scaling: n_live = $NLIVE"
echo "  Waveform: $WAVEFORM"
echo "  Log: $LOG"
echo "=============================================="

python $SCRIPT \
    --waveform "$WAVEFORM" \
    --phase-marginalization \
    --data-source local \
    --psd-source gwtc1 \
    --output-dir "$OUT_DIR" \
    --wide-prior \
    --nlive "$NLIVE" \
    --label-suffix "_nlive${NLIVE}" \
    2>&1 | tee "$LOG"

echo ""
echo "  n_live=$NLIVE complete."
echo "  Log: $LOG"
