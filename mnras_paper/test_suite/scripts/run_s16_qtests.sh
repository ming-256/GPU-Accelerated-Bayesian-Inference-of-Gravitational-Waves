#!/usr/bin/env bash
# s16 q-suite: probe why our (q | GW170817) is narrower than LVK GWTC-1.
#
# All runs: n_live=5000, n_bins=501 (unless overridden), full-sky,
# LVK low-spin (component s_z in [-0.05, 0.05] — bounds match LVK).
# Mass bounds match s07 baseline_lvkbounds: --m-comp-lo 0.87 --m-comp-hi 1.74
#
# Run from repo root on the GPU box. Each run ~10–15 min on A100.
#
# Diagnosis recap (see launcher audit, 2026-04-29): with --m-comp-lo/hi set
# and the (M_c, q) -> (m1, m2) Jacobian on (line ~330 of the launcher), the
# project's effective q-prior already matches LVK lowSpin. The dominant
# remaining axis is aligned-spin vs precessing waveform; the secondary axis
# is the spin-prior shape (square vs ball projection). Tests q01/q02/q04
# rule out cosmological coupling, heterodyne resolution, and the phase-marg
# approximation; q05/q06 close the spin-prior-shape axis on the two science
# waveforms (the precession axis is closed by the s07 IMRPhenomPv2 run).
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

# q05 — IMRPhenomD_NRTidalv2 with the LVK ball-projection spin prior.
# Replaces the default uniform p(s_z) on [-0.05, 0.05] with the parabolic
# projection of an isotropic 3-D ball |chi| <= 0.05. Closes the spin-prior-
# shape axis vs the s07 baseline (which used uniform p(s_z)).
RUN="s16__gw170817__imrphenomd_nrtidalv2__qtest_spinball__seed0000"
mkdir -p "$OUT/$RUN"
python "$DRIVER" --waveform IMRPhenomD_NRTidalv2 --data-source local \
    --psd-source gwtc1 --ref-params gwtc1 --phase-marginalization \
    --n-live 5000 --n-bins 501 --m-comp-lo 0.87 --m-comp-hi 1.74 \
    --lvk-spin-ball \
    --output-dir "$OUT/$RUN" 2>&1 | tee "$OUT/$RUN/sampler.log"

# q06 — IMRPhenomXAS_NRTidalv3 with the LVK ball-projection spin prior.
# Same configuration as q05 with the locked primary waveform.
RUN="s16__gw170817__imrphenomxas_nrtidalv3__qtest_spinball__seed0000"
mkdir -p "$OUT/$RUN"
python "$DRIVER" "${COMMON[@]}" --lvk-spin-ball \
    --output-dir "$OUT/$RUN" 2>&1 | tee "$OUT/$RUN/sampler.log"

echo "All s16 q-tests done."
