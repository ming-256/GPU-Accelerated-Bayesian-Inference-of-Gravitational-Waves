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
#   bash run_all.sh --primary-only   # GW170817 IMRPhenomD_NRTidalv2 only
#   bash run_all.sh --preflight      # environment/file checks only
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

MODE="--submit"
PRIMARY_ONLY=false
PREFLIGHT_ONLY=false

for arg in "$@"; do
    case "$arg" in
        --submit|--gen-only|--local|--local-serial)
            MODE="$arg"
            ;;
        --primary-only)
            PRIMARY_ONLY=true
            ;;
        --preflight)
            PREFLIGHT_ONLY=true
            ;;
        *)
            echo "ERROR: unknown argument: $arg"
            exit 1
            ;;
    esac
done

# ── Load user configuration ──────────────────────────────────────────────────
if [[ ! -f config.sh ]]; then
    echo "ERROR: config.sh not found. It should be in the same directory as run_all.sh."
    exit 1
fi
# shellcheck disable=SC1091
source config.sh

NPROCS=$(( NODES * CORES_PER_NODE ))

preflight() {
    echo "============================================================"
    echo "  Preflight checks"
    echo "============================================================"

    python3 - <<'PY'
import importlib
import contextlib
import io
import sys

required = ["bilby", "gwpy", "lal", "lalsimulation", "mpi4py", "pypolychord"]
missing = []
for name in required:
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            module = importlib.import_module(name)
        version = getattr(module, "__version__", "unknown")
        print(f"  OK: {name} {version}")
    except Exception as exc:
        missing.append((name, str(exc)))
        print(f"  FAIL: {name}: {exc}")

if missing:
    sys.exit(1)

import bilby

prior = bilby.gw.prior.PriorDict("GW170817/GW170817.prior")
expected = {
    "chirp_mass": "UniformInComponentsChirpMass",
    "mass_ratio": "UniformInComponentsMassRatio",
}
for key, class_name in expected.items():
    actual = type(prior[key]).__name__
    if actual != class_name:
        print(f"  FAIL: GW170817 prior {key} is {actual}, expected {class_name}")
        sys.exit(1)
    print(f"  OK: GW170817 prior {key} uses {actual}")
PY

    if [[ "${PSD_SOURCE}" == "gwtc1" ]]; then
        local psd_file="${GW170817_PSD_FILE:-}"
        if [[ -z "$psd_file" ]]; then
            for candidate in \
                "${SCRIPT_DIR}/GW170817/GWTC1_GW170817_PSDs.dat" \
                "${SCRIPT_DIR}/GW170817/data/GWTC1_GW170817_PSDs.dat" \
                "${SCRIPT_DIR}/../EventData/GWOSC/GW170817/GWTC1_GW170817_PSDs.dat"; do
                if [[ -f "$candidate" ]]; then
                    psd_file="$candidate"
                    break
                fi
            done
        fi

        if [[ -z "$psd_file" || ! -f "$psd_file" ]]; then
            echo "  FAIL: PSD_SOURCE=gwtc1 but GWTC1_GW170817_PSDs.dat was not found."
            echo "        Copy it to GW170817/ or set GW170817_PSD_FILE in config.sh."
            exit 1
        fi
        echo "  OK: GWTC-1 PSD file: $psd_file"
    fi

    if [[ "${DATA_SOURCE}" == "local" ]]; then
        local data_dir="${GW170817_DATA_DIR:-${SCRIPT_DIR}/GW170817/data}"
        for file in \
            H-H1_LOSC_CLN_4_V1-1187007040-2048.hdf5 \
            L-L1_LOSC_CLN_4_V1-1187007040-2048.hdf5 \
            V-V1_LOSC_CLN_4_V1-1187007040-2048.hdf5; do
            if [[ ! -f "${data_dir}/${file}" ]]; then
                echo "  FAIL: missing local strain file: ${data_dir}/${file}"
                exit 1
            fi
        done
        echo "  OK: local GW170817 strain files in $data_dir"
    fi

    echo "  Preflight passed."
}

# ── Run definitions ──────────────────────────────────────────────────────────
# Each entry: SCRIPT|WAVEFORM_ARG|WALLTIME|LABEL
if [[ "$PRIMARY_ONLY" == "true" ]]; then
    declare -a RUNS=(
        "GW170817/run_GW170817.py|--waveform IMRPhenomD_NRTidalv2|${WALLTIME_GW170817}|GW170817_IMRPhenomD_NRTidalv2"
    )
else
    declare -a RUNS=(
        "GW150914/run_GW150914.py||${WALLTIME_GW150914}|GW150914_IMRPhenomD"
        "GW170817/run_GW170817.py|--waveform IMRPhenomD_NRTidalv2|${WALLTIME_GW170817}|GW170817_IMRPhenomD_NRTidalv2"
        "GW170817/run_GW170817.py|--waveform TaylorF2|${WALLTIME_GW170817}|GW170817_TaylorF2"
    )
fi

RESULTS_DIR="${SCRIPT_DIR}/results"
TIMING_FILE="${RESULTS_DIR}/timing_summary.txt"
mkdir -p "$RESULTS_DIR"

if [[ "$PREFLIGHT_ONLY" == "true" ]]; then
    preflight
    exit 0
fi

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
    EXTRA_ARGS=()
    if [[ "$SCRIPT" == "GW170817/run_GW170817.py" ]]; then
        EXTRA_ARGS+=(--data-source "${DATA_SOURCE}" --psd-source "${PSD_SOURCE}")
        [[ -n "${GW170817_PSD_FILE:-}" ]] && EXTRA_ARGS+=(--psd-file "${GW170817_PSD_FILE}")
        [[ -n "${GW170817_DATA_DIR:-}" ]] && EXTRA_ARGS+=(--data-dir "${GW170817_DATA_DIR}")
    fi

    echo ""
    echo "--- [$((i+1))/$TOTAL] Generating: $LABEL ---"

    GEN_START=$(timer_start)

    # shellcheck disable=SC2086
    python3 "${SCRIPT}" ${WAVEFORM_ARG} --outdir "$OUTDIR" --gen-only \
        --nlive "${NLIVE}" --num-repeats "${NUM_REPEATS}" "${EXTRA_ARGS[@]}"

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
    EXTRA_ARGS=()
    if [[ "$SCRIPT" == "GW170817/run_GW170817.py" ]]; then
        EXTRA_ARGS+=(--data-source "${DATA_SOURCE}" --psd-source "${PSD_SOURCE}")
        [[ -n "${GW170817_PSD_FILE:-}" ]] && EXTRA_ARGS+=(--psd-file "${GW170817_PSD_FILE}")
        [[ -n "${GW170817_DATA_DIR:-}" ]] && EXTRA_ARGS+=(--data-dir "${GW170817_DATA_DIR}")
    fi

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
                --nlive "${NLIVE}" --num-repeats "${NUM_REPEATS}" "${EXTRA_ARGS[@]}"
        else
            echo "  Running serial (no MPI, for testing)..."
            # shellcheck disable=SC2086
            python3 "${SCRIPT}" ${WAVEFORM_ARG} \
                --outdir "$OUTDIR" --from-pickle "$PICKLE" \
                --nlive "${NLIVE}" --num-repeats "${NUM_REPEATS}" "${EXTRA_ARGS[@]}"
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
            if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
                echo "    --nlive ${NLIVE} --num-repeats ${NUM_REPEATS} \\"
                printf "   "
                printf " %q" "${EXTRA_ARGS[@]}"
                printf "\n"
            else
                echo "    --nlive ${NLIVE} --num-repeats ${NUM_REPEATS}"
            fi
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
