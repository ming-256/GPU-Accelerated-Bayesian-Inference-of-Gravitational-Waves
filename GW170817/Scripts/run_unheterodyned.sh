#!/usr/bin/env bash
# Run unheterodyned nested sampling for GW170817.
# Produces full-sky and host-localised results for both waveforms.
#
# Output directory: Results/gwtc1_phasemarg/
#
# Full-sky:        *_narrow_prior.csv  (full-sky RA/dec, narrow M_c/q/spin)
# Host-localised:  *.csv               (RA/dec pinned to NGC 4993, same M_c/q/spin)
#
# Usage:
#   bash GW170817/Scripts/run_unheterodyned.sh              # run all 4
#   bash GW170817/Scripts/run_unheterodyned.sh host          # host-localised only
#   bash GW170817/Scripts/run_unheterodyned.sh fullsky       # full-sky only

set -e
cd "$(dirname "$0")/../.."

OUT_DIR="Results/gwtc1_phasemarg"
SCRIPT="GW170817/Scripts/GW170817_unheterodyned_1.py"
COMMON_ARGS="--phase-marginalization --data-source local --psd-source gwtc1 --output-dir $OUT_DIR"

MODE="${1:-all}"


# --------------------------------------------------------------------------- #
# Host-localised runs (RA/dec constrained to NGC 4993)
# --------------------------------------------------------------------------- #
if [ "$MODE" = "all" ] || [ "$MODE" = "host" ]; then
    echo ""
    echo "================================================================"
    echo "  HOST-LOCALISED (NGC 4993) — IMRPhenomD_NRTidalv2"
    echo "================================================================"
    python $SCRIPT --waveform IMRPhenomD_NRTidalv2 $COMMON_ARGS \
        --wide-prior

    echo ""
    echo "================================================================"
    echo "  HOST-LOCALISED (NGC 4993) — TaylorF2"
    echo "================================================================"
    python $SCRIPT --waveform TaylorF2 $COMMON_ARGS \
        --wide-prior
fi

# --------------------------------------------------------------------------- #
# Full-sky runs (narrow M_c/q/spin, full RA/dec)
# --------------------------------------------------------------------------- #
if [ "$MODE" = "all" ] || [ "$MODE" = "fullsky" ]; then
    echo "================================================================"
    echo "  FULL-SKY — IMRPhenomD_NRTidalv2"
    echo "================================================================"
    python $SCRIPT --waveform IMRPhenomD_NRTidalv2 $COMMON_ARGS \
        --label-suffix "_full_sky"

    echo ""
    echo "================================================================"
    echo "  FULL-SKY — TaylorF2"
    echo "================================================================"
    python $SCRIPT --waveform TaylorF2 $COMMON_ARGS \
        --label-suffix "_full_sky"
fi

echo ""
echo "All unheterodyned runs complete."
echo "Results saved to $OUT_DIR/"
