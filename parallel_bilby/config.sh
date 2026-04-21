#!/usr/bin/env bash
# ============================================================================
# config.sh — User-editable HPC configuration
#
# Edit this file BEFORE running run_all.sh.  All settings here are read by
# run_all.sh to generate Slurm batch scripts and control local runs.
# ============================================================================

# ── Cluster resources ────────────────────────────────────────────────────────
# Number of NODES to allocate per job.
# Total MPI ranks = NODES × CORES_PER_NODE.
# Rule of thumb: total ranks ≈ nlive (2000) gives good parallelism.
NODES=7

# Physical cores per node (set to your cluster's value).
# Find yours with:  nproc  OR  sinfo -N -l | head -5
CORES_PER_NODE=76

# ── Wall-clock time limits (HH:MM:SS) ───────────────────────────────────────
# GW150914 (BBH, 8 s segment) — typically finishes in 1–4 h
WALLTIME_GW150914="24:00:00"

# GW170817 (BNS, 128 s segment) — typically 12–48 h depending on waveform
WALLTIME_GW170817="48:00:00"

# ── Slurm account / partition (leave empty if not required) ──────────────────
SLURM_ACCOUNT=""
SLURM_PARTITION=""
SLURM_EXTRA=""          # any extra #SBATCH lines, e.g. "--qos=normal"

# ── Sampler settings ─────────────────────────────────────────────────────────
NLIVE=2000              # number of live points (PolyChord)
NUM_REPEATS=40          # slice-sampling repeats per dead point

# ── GW170817 data/PSD settings ───────────────────────────────────────────────
# Paper comparison default: use the same GWTC-1/BayesWave PSD source as the
# JAX production runs.  Place GWTC1_GW170817_PSDs.dat in GW170817/ or set an
# absolute path here / via the GW170817_PSD_FILE environment variable.
DATA_SOURCE="${DATA_SOURCE:-fetch}"     # fetch or local
PSD_SOURCE="${PSD_SOURCE:-gwtc1}"        # gwtc1 or self
GW170817_PSD_FILE="${GW170817_PSD_FILE:-}"  # optional absolute PSD path
GW170817_DATA_DIR="${GW170817_DATA_DIR:-}"  # optional local GWOSC HDF5 dir
