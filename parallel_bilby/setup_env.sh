#!/usr/bin/env bash
# ============================================================================
# setup_env.sh — Create a conda/venv environment for parallel_bilby on HPC
#
# Usage:
#   source setup_env.sh              # creates conda env + installs PolyChord
#   source setup_env.sh venv         # uses venv instead of conda
#   source setup_env.sh polychord    # install PolyChord only (env already exists)
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
METHOD="${1:-conda}"
ENV_NAME="pbilby"
POLYCHORD_DIR="${SCRIPT_DIR}/PolyChordLite"

# ----------------------------------------------------------------------------
# Install PolyChord from source
# ----------------------------------------------------------------------------
install_polychord() {
    echo "=== Installing PolyChord ==="

    if [[ ! -d "$POLYCHORD_DIR" ]]; then
        echo "  Cloning PolyChordLite..."
        git clone https://github.com/PolyChord/PolyChordLite.git "$POLYCHORD_DIR"
    else
        echo "  PolyChordLite already cloned at $POLYCHORD_DIR"
    fi

    pushd "$POLYCHORD_DIR" > /dev/null

    # Detect MPI — compile with MPI if mpirun is available
    if command -v mpirun &>/dev/null || command -v mpiexec &>/dev/null; then
        MPI_NPROCS=$(nproc 2>/dev/null || echo 2)
        echo "  Building PolyChord with MPI support (MPI=${MPI_NPROCS})..."
        make pypolychord MPI="${MPI_NPROCS}"
    else
        echo "  Building PolyChord without MPI..."
        make pypolychord MPI=
    fi

    python setup.py install --user
    popd > /dev/null

    echo "  PolyChord installed successfully."
}

# ----------------------------------------------------------------------------
# Conda environment
# ----------------------------------------------------------------------------
if [[ "$METHOD" == "conda" ]]; then
    echo "=== Creating conda environment '${ENV_NAME}' ==="

    if ! command -v conda &>/dev/null; then
        echo "ERROR: conda not found. Load it first (e.g. 'module load anaconda3')."
        exit 1
    fi

    conda create -n "${ENV_NAME}" python=3.11 -y
    conda activate "${ENV_NAME}"

    # Install LALSuite from conda-forge (best compatibility on HPC)
    conda install -c conda-forge lalsuite gwpy -y

    # Install bilby stack via pip
    pip install parallel-bilby bilby mpi4py pesummary pypolychord-bilby

    # Install PolyChord from source
    install_polychord

    echo "=== Done. Activate with: conda activate ${ENV_NAME} ==="

# ----------------------------------------------------------------------------
# Venv environment
# ----------------------------------------------------------------------------
elif [[ "$METHOD" == "venv" ]]; then
    echo "=== Creating venv '${ENV_NAME}' ==="

    python3 -m venv "${ENV_NAME}"
    source "${ENV_NAME}/bin/activate"

    pip install --upgrade pip
    pip install -r requirements.txt

    # Install PolyChord from source
    install_polychord

    echo "=== Done. Activate with: source ${ENV_NAME}/bin/activate ==="

# ----------------------------------------------------------------------------
# PolyChord only (env already exists)
# ----------------------------------------------------------------------------
elif [[ "$METHOD" == "polychord" ]]; then
    install_polychord

else
    echo "Usage: source setup_env.sh [conda|venv|polychord]"
    exit 1
fi
