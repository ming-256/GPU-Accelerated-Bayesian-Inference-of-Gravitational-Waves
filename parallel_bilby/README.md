# Bilby HPC — CPU Comparison Runs

Self-contained bilby analyses for **GW150914** and **GW170817**, using the
**same waveform models, priors, and likelihood** as our JAX GPU analysis for
direct wall-clock comparison.

Transfer this entire `parallel_bilby/` folder to your HPC cluster.

**Sampler:** PyPolyChord (PolyChord nested sampling, MPI-parallelised)
**Likelihood:** Relative binning (heterodyned) + analytic phase marginalisation
**Standard siren:** GW170817 includes H_0 and v_p with NGC 4993 EM counterpart

---

## Quick start

```bash
# 1. Load modules (names vary by cluster)
module load gcc openmpi python

# 2. Install everything (creates venv + builds PolyChord)
source setup_env.sh

# 3. Edit cluster settings
vi config.sh          # set NODES, CORES_PER_NODE, walltime, account

# 4. Run
bash run_all.sh       # generates data (login node) then submits Slurm jobs
```

---

## Directory structure

```
parallel_bilby/
├── README.md                   # this file
├── config.sh                   # ★ USER EDITS THIS — nodes, cores, walltime
├── setup_env.sh                # automated venv + PolyChord install
├── run_all.sh                  # orchestration: data gen → Slurm submit
├── requirements.txt            # pip dependencies
├── GW150914/
│   ├── run_GW150914.py         # standalone bilby analysis (BBH)
│   └── GW150914_IMRPhenomD.prior
├── GW170817/
│   ├── run_GW170817.py         # standalone bilby analysis (BNS + H_0, v_p)
│   └── GW170817.prior          # includes H_0, v_p priors
└── results/                    # ← ALL outputs land here
    ├── timing_summary.txt
    ├── GW150914_IMRPhenomD/
    │   ├── timing.txt
    │   └── ...bilby result files...
    ├── GW170817_IMRPhenomD_NRTidalv2/
    │   └── ...
    └── GW170817_TaylorF2/
        └── ...
```

---

## What to edit: `config.sh`

All cluster-specific settings are in **one file**.  Edit before running:

```bash
# ── Cluster resources ────────────────────────────────────────────────
NODES=4                        # nodes per job
CORES_PER_NODE=16              # physical cores per node (nproc)

# ── Wall-clock time (HH:MM:SS) ──────────────────────────────────────
WALLTIME_GW150914="24:00:00"   # BBH — typically 1–4 h
WALLTIME_GW170817="48:00:00"   # BNS — typically 12–48 h

# ── Slurm account / partition ────────────────────────────────────────
SLURM_ACCOUNT=""               # e.g. "myproject"
SLURM_PARTITION=""             # e.g. "batch"
SLURM_EXTRA=""                 # e.g. "--qos=normal"

# ── Sampler ──────────────────────────────────────────────────────────
NLIVE=2000                     # live points
NUM_REPEATS=40                 # slice-sampling repeats
```

### How to find CORES_PER_NODE

```bash
nproc                          # on a compute node
sinfo -N -l | head -5          # from login node
lscpu | grep "^CPU(s):"        # alternative
```

### How many nodes?

Total MPI ranks = `NODES x CORES_PER_NODE`.  Aim for total ranks ~ `NLIVE`.

| Cluster type        | CORES_PER_NODE | NODES (GW150914) | NODES (GW170817) |
|----------------------|----------------|-------------------|-------------------|
| 16-core (older)      | 16             | 4                 | 8                 |
| 48-core (AMD Rome)   | 48             | 2                 | 4                 |
| 128-core (AMD Milan) | 128            | 1                 | 2                 |

---

## Installation

### Prerequisites

- Python >= 3.9
- Fortran compiler (`gfortran`) — needed to build PolyChord
- MPI (`openmpi` or `mpich`) — needed for multi-node parallel runs

```bash
module load gcc openmpi python   # typical HPC modules
```

### Automated setup (recommended)

```bash
source setup_env.sh
```

This will:
1. Create a Python venv at `pbilby_venv/`
2. `pip install` all dependencies from `requirements.txt`
3. Clone and build PolyChord from source with MPI support
4. Verify the installation

### Verify

```bash
source pbilby_venv/bin/activate
python -c "
import bilby; print('bilby', bilby.__version__)
import pypolychord; print('PyPolyChord OK')
import lal; print('LALSuite OK')
import mpi4py; print('mpi4py OK')
"
```

---

## Running

### Option A: Slurm (standard HPC)

```bash
bash run_all.sh              # data gen + submit 3 Slurm jobs
```

This runs two steps:
1. **Data generation** (serial, on login node): downloads GWOSC strain data,
   estimates PSDs, saves pickles.  Requires internet access.
2. **Sampling** (MPI, on compute nodes): loads pickle, runs PolyChord.
   Auto-generates and submits Slurm batch scripts.

To generate data without submitting:
```bash
bash run_all.sh --gen-only
```

### Option B: Local with MPI (testing / single node)

```bash
bash run_all.sh --local          # uses NODES x CORES_PER_NODE MPI ranks
bash run_all.sh --local-serial   # single process (quick sanity check)
```

### Option C: Run a single analysis manually

```bash
source pbilby_venv/bin/activate

# GW150914:
python GW150914/run_GW150914.py --gen-only
mpirun -n 64 python GW150914/run_GW150914.py \
    --from-pickle results/GW150914_IMRPhenomD/GW150914_IMRPhenomD_data_dump.pickle

# GW170817 (IMRPhenomD_NRTidalv2):
python GW170817/run_GW170817.py --waveform IMRPhenomD_NRTidalv2 --gen-only
mpirun -n 128 python GW170817/run_GW170817.py \
    --waveform IMRPhenomD_NRTidalv2 \
    --from-pickle results/GW170817_IMRPhenomD_NRTidalv2/GW170817_IMRPhenomD_NRTidalv2_data_dump.pickle

# GW170817 (TaylorF2):
python GW170817/run_GW170817.py --waveform TaylorF2 --gen-only
mpirun -n 128 python GW170817/run_GW170817.py \
    --waveform TaylorF2 \
    --from-pickle results/GW170817_TaylorF2/GW170817_TaylorF2_data_dump.pickle
```

---

## Analysis details

### Waveform matching (JAX vs bilby)

| Event    | JAX waveform               | Bilby approximant        | Type              |
|----------|----------------------------|--------------------------|-------------------|
| GW150914 | `RippleIMRPhenomD`         | `IMRPhenomD`             | BBH, aligned spin |
| GW170817 | `RippleIMRPhenomD_NRTidalv2` | `IMRPhenomD_NRTidalv2` | BNS, tidal        |
| GW170817 | `RippleTaylorF2`           | `TaylorF2`               | BNS, tidal        |

All are aligned-spin, (2,2)-mode only.

### GW150914 — BBH (10 sampled parameters + phase marginalised)

| Parameter     | Prior                           |
|---------------|---------------------------------|
| M_c           | Uniform [10, 80] M_sun          |
| q             | Uniform [0.125, 1]              |
| chi_1, chi_2  | Uniform [-1, 1]                 |
| d_L           | PowerLaw(alpha=2) [1, 2000] Mpc |
| theta_jn      | Sine [0, pi]                    |
| psi           | Uniform [0, pi]                 |
| ra            | Uniform [0, 2pi]                |
| dec           | Cosine [-pi/2, pi/2]            |
| geocent_time  | Uniform [trigger +/- 0.05 s]    |
| m_1, m_2      | Constraint [1, 100] M_sun       |
| phase         | Analytically marginalised       |

### GW170817 — BNS + standard siren (14 sampled parameters + phase marginalised)

| Parameter     | Prior                             |
|---------------|-----------------------------------|
| M_c           | Uniform [1.184, 2.168] M_sun      |
| q             | Uniform [0.125, 1]                |
| chi_1, chi_2  | Uniform [-0.05, 0.05]             |
| d_L           | PowerLaw(alpha=2) [1, 75] Mpc     |
| theta_jn      | Sine [0, pi]                      |
| psi           | Uniform [0, pi]                   |
| ra            | Uniform [0, 2pi]                  |
| dec           | Cosine [-pi/2, pi/2]              |
| geocent_time  | Uniform [trigger +/- 0.1 s]       |
| lambda_1      | Uniform [0, 5000]                 |
| lambda_2      | Uniform [0, 5000]                 |
| H_0           | LogUniform [20, 250] km/s/Mpc     |
| v_p           | Uniform [-1000, 1000] km/s        |
| m_1, m_2      | Constraint [0.5, 7.7] M_sun       |
| phase         | Analytically marginalised         |

### Standard siren likelihood (GW170817 only)

The total log-likelihood is `log L_GW + log L_vr + log L_vp`, where:

```
L_vr = N(3327 | v_p + H_0 * d_L, 72)    recession velocity of NGC 4993
L_vp = N(310  | v_p, 150)                peculiar velocity constraint
```

These match the JAX script terms exactly.  The GW likelihood uses relative
binning with fiducial parameters from GWTC-1 medians.

### Likelihood settings

| Setting               | Value |
|-----------------------|-------|
| Likelihood type       | RelativeBinningGravitationalWaveTransient |
| epsilon               | 0.5   |
| Phase marginalisation | Yes   |
| Distance marginalisation | No |
| Time marginalisation  | No    |

### Sampler settings

| Setting      | Value |
|-------------|-------|
| Sampler      | PyPolyChord (PolyChord nested sampling) |
| nlive        | 2000  |
| num_repeats  | 40    |
| nprior       | -1 (= 10 x nlive) |

---

## Output

All results are consolidated in `results/`:

```
results/
├── timing_summary.txt                     # wall-clock timing for all stages
├── GW150914_IMRPhenomD/
│   ├── timing.txt                         # per-run timing breakdown
│   ├── GW150914_IMRPhenomD_data_dump.pickle
│   ├── GW150914_IMRPhenomD_result.json    # bilby posteriors + evidence
│   └── submit/slurm_GW150914_IMRPhenomD.sh
├── GW170817_IMRPhenomD_NRTidalv2/
│   └── ...
└── GW170817_TaylorF2/
    └── ...
```

### Load results in Python

```python
import bilby
result = bilby.result.read_in_result(
    "results/GW150914_IMRPhenomD/GW150914_IMRPhenomD_result.json")
result.plot_corner()
print(f"Log evidence: {result.log_evidence:.2f}")
print(f"Sampling time: {result.sampling_time:.1f} s")
```

### Check Slurm job status

```bash
squeue -u $USER                # running jobs
sacct -j <JOBID> --format=JobID,Elapsed,MaxRSS,State
cat results/GW150914_IMRPhenomD/slurm_*.out   # stdout log
```

---

## Estimated runtimes

With relative binning + PolyChord (2000 live points):

| Run                           | ~CPU-hours | Wall time (4 nodes x 16 cores) |
|-------------------------------|------------|-------------------------------|
| GW150914 IMRPhenomD           | ~200       | ~3 h                          |
| GW170817 IMRPhenomD_NRTidalv2 | ~3000      | ~48 h                         |
| GW170817 TaylorF2             | ~2000      | ~30 h                         |

GW170817 is much slower due to the 128 s segment (vs 8 s for GW150914) and
the additional H_0/v_p parameters (14D vs 10D).

---

## Troubleshooting

**PolyChord build fails:**
- Ensure `gfortran` and `make` are available: `module load gcc`
- Check MPI: `module load openmpi` or `module load mpich`

**`ImportError: No module named pypolychord`:**
- Rebuild: `source setup_env.sh polychord`

**Data download fails (GWOSC):**
- Run `--gen-only` on a login node with internet access
- Some clusters need proxy: `export HTTPS_PROXY=...`

**MPI errors at runtime:**
- Ensure `mpi4py` was built against the same MPI as PolyChord
- Rebuild: `pip install --no-cache-dir mpi4py`
- Check `mpirun --version` matches loaded module

**PBS/Torque clusters (no Slurm):**
- Run `bash run_all.sh --gen-only` to generate data pickles
- Write your own PBS submission script calling:
  ```bash
  mpirun python3 GW170817/run_GW170817.py --waveform IMRPhenomD_NRTidalv2 \
      --from-pickle results/GW170817_IMRPhenomD_NRTidalv2/..._data_dump.pickle
  ```
