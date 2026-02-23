#!/usr/bin/env bash
# ============================================================================
# setup_env.sh — Create a venv and install all dependencies for bilby + PolyChord
#
# Usage:
#   source setup_env.sh              # full install (venv + pip + PolyChord)
#   source setup_env.sh polychord    # PolyChord only (venv already active)
#
# Prerequisites:
#   - Python >= 3.9
#   - Fortran compiler (gfortran)
#   - MPI (OpenMPI or MPICH) — required for multi-node runs
#
# On most HPC clusters, load modules first:
#   module load gcc openmpi python    # names vary by cluster
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-full}"
ENV_NAME="pbilby_venv"
ENV_DIR="${SCRIPT_DIR}/${ENV_NAME}"
POLYCHORD_DIR="${SCRIPT_DIR}/PolyChordLite"

# ── Colours for output ──────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ── Check prerequisites ─────────────────────────────────────────────────────
check_prereqs() {
    local ok=true

    if ! command -v python3 &>/dev/null; then
        error "python3 not found. Load a python module or install Python >= 3.9."
        ok=false
    fi

    if ! command -v gfortran &>/dev/null && ! command -v ifort &>/dev/null; then
        warn "No Fortran compiler found. PolyChord build may fail."
        warn "Try: module load gcc"
    fi

    if ! command -v mpirun &>/dev/null && ! command -v mpiexec &>/dev/null; then
        warn "No MPI found. PolyChord will be built WITHOUT MPI (single-node only)."
        warn "For multi-node runs: module load openmpi (or mpich)"
    fi

    if [[ "$ok" == "false" ]]; then
        error "Fix the above issues and re-run."
        return 1
    fi
}

# ── Install PolyChord from source ───────────────────────────────────────────
install_polychord() {
    info "Installing PolyChord from source..."

    if [[ ! -d "$POLYCHORD_DIR" ]]; then
        info "  Cloning PolyChordLite..."
        git clone https://github.com/PolyChord/PolyChordLite.git "$POLYCHORD_DIR"
    else
        info "  PolyChordLite already present at $POLYCHORD_DIR"
    fi

    pushd "$POLYCHORD_DIR" > /dev/null

    # Clean previous builds
    make clean 2>/dev/null || true

    if command -v mpirun &>/dev/null || command -v mpiexec &>/dev/null; then
        local nprocs
        nprocs=$(nproc 2>/dev/null || echo 2)
        info "  Building with MPI support (MPI=${nprocs})..."
        make pypolychord MPI="${nprocs}"
    else
        info "  Building without MPI..."
        make pypolychord MPI=
    fi

    pip install .
    popd > /dev/null

    # Verify
    if python3 -c "import pypolychord" 2>/dev/null; then
        info "  PyPolyChord installed successfully."
    else
        error "  PyPolyChord import failed. Check the build log above."
        return 1
    fi
}

# ── Full install ─────────────────────────────────────────────────────────────
if [[ "$MODE" == "full" ]]; then
    check_prereqs

    info "Creating venv at ${ENV_DIR}..."
    python3 -m venv "${ENV_DIR}"
    # shellcheck disable=SC1091
    source "${ENV_DIR}/bin/activate"

    info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel

    info "Installing Python dependencies from requirements.txt..."
    pip install -r "${SCRIPT_DIR}/requirements.txt"

    # PolyChord from source (must be compiled, not pip-installable)
    install_polychord

    info "Verifying installation..."
    python3 -c "
import bilby; print(f'  bilby {bilby.__version__}')
import pypolychord; print('  PyPolyChord OK')
import lal; print('  LALSuite OK')
import mpi4py; print('  mpi4py OK')
print('All checks passed.')
"

    echo ""
    info "Setup complete."
    info "Activate with:  source ${ENV_DIR}/bin/activate"
    info "Then run:        bash run_all.sh"

# ── PolyChord only ──────────────────────────────────────────────────────────
elif [[ "$MODE" == "polychord" ]]; then
    install_polychord

else
    echo "Usage: source setup_env.sh [full|polychord]"
    return 1 2>/dev/null || exit 1
fi
