#!/usr/bin/env bash
# s16 q-suite: probe why our (q | GW170817) is narrower than LVK GWTC-1.
#
# All runs: XAS_NRTv3, n_live=5000, n_bins=501 (unless overridden), full-sky,
# LVK low-spin (component s_z in [-0.05, 0.05] — already matches LVK).
# Mass bounds match s07 baseline_lvkbounds: --m-comp-lo 0.87 --m-comp-hi 1.74
#
# Run from repo root on the GPU box. Each run ~10–15 min on A100.
set -euo pipefail

REPO=$(cd "$(dirname "$0")/../../.." && pwd)
DRIVER="$REPO/GW170817/Scripts/GW170817_heterodyned_1.py"
OUT="$REPO/Results/test_suite"
COMMON=(--waveform IMRPhenomXAS_NRTidalv3 --data-source local
        --psd-source gwtc1 --ref-params gwtc1 --phase-marginalization
        --n-live 5000 --n-bins 501
        --m-comp-lo 0.87 --m-comp-hi 1.74)

# q01 — pure GW (drop H_0/v_p): tests projection from siren parameters
RUN="s16__gw170817__imrphenomxas_nrtidalv3__qtest_gwonly__seed0000"
mkdir -p "$OUT/$RUN"
python "$DRIVER" "${COMMON[@]}" --gw-only --output-dir "$OUT/$RUN" \
    2>&1 | tee "$OUT/$RUN/sampler.log"

# q02 — tighter heterodyne resolution: rules out reference-induced concentration
RUN="s16__gw170817__imrphenomxas_nrtidalv3__qtest_nbins2001__seed0000"
mkdir -p "$OUT/$RUN"
python "$DRIVER" "${COMMON[@]/--n-bins 501/--n-bins 2001}" \
    --output-dir "$OUT/$RUN" 2>&1 | tee "$OUT/$RUN/sampler.log"

# q04 — drop phase marginalization: rules out PM approximation distortion
RUN="s16__gw170817__imrphenomxas_nrtidalv3__qtest_nophasemarg__seed0000"
mkdir -p "$OUT/$RUN"
python "$DRIVER" --waveform IMRPhenomXAS_NRTidalv3 --data-source local \
    --psd-source gwtc1 --ref-params gwtc1 \
    --n-live 5000 --n-bins 501 --m-comp-lo 0.87 --m-comp-hi 1.74 \
    --output-dir "$OUT/$RUN" 2>&1 | tee "$OUT/$RUN/sampler.log"

echo "All s16 q-tests done."
