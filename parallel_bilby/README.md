# Parallel Bilby — HPC Comparison Runs

Self-contained parallel_bilby configurations for GW150914 and GW170817, using
the **same waveform models and priors** as our JAX analysis for direct comparison.
Transfer this entire `parallel_bilby/` folder to your HPC cluster.

**Sampler:** PyPolyChord (PolyChord nested sampling via bilby)
**Likelihood:** Relative binning (heterodyned) — `RelativeBinningGravitationalWaveTransient`

## Directory structure

```
parallel_bilby/
├── README.md                              # this file
├── requirements.txt                       # pip dependencies
├── setup_env.sh                           # environment setup (conda/venv) + PolyChord
├── run_all.sh                             # generate data + submit all jobs + timing
├── GW150914/
│   ├── GW150914_IMRPhenomD.ini            # parallel_bilby config
│   └── GW150914_IMRPhenomD.prior          # prior file
├── GW170817/
│   ├── GW170817.prior                     # shared prior file (BNS)
│   ├── GW170817_IMRPhenomD_NRTidalv2.ini  # config — IMRPhenomD_NRTidalv2
│   └── GW170817_TaylorF2.ini              # config — TaylorF2
└── results/                               # ← ALL outputs land here
    ├── timing_summary.txt                 # wall-clock timing for every stage
    ├── GW150914_IMRPhenomD/
    │   ├── data/   ...data_dump.pickle
    │   ├── result/ ...result.json         # posterior samples
    │   └── submit/ ...bash script
    ├── GW170817_IMRPhenomD_NRTidalv2/
    │   └── ...
    └── GW170817_TaylorF2/
        └── ...
```

## Waveform matching

| Event    | Our JAX waveform              | Bilby approximant        | Type              |
|----------|-------------------------------|--------------------------|-------------------|
| GW150914 | `RippleIMRPhenomD`            | `IMRPhenomD`             | BBH, aligned spin |
| GW170817 | `RippleIMRPhenomD_NRTidalv2`  | `IMRPhenomD_NRTidalv2`   | BNS, tidal        |
| GW170817 | `RippleTaylorF2`              | `TaylorF2`               | BNS, tidal        |

All three are aligned-spin, (2,2)-mode only — ensuring apples-to-apples comparison.

---

## Prerequisites

- **Fortran compiler** (gfortran) — required to build PolyChord
- **MPI** (OpenMPI or MPICH) — required for parallel runs
- **Python ≥ 3.9**
- **conda** or **pip/venv**

On most HPC clusters:
```bash
module load gcc openmpi anaconda3    # names vary by cluster
```

---

## Installation

### Step 1: Install PolyChord from source

PolyChord must be built from source (it is **not** pip-installable).

```bash
# Clone the repository
git clone https://github.com/PolyChord/PolyChordLite.git
cd PolyChordLite

# Build with MPI (set MPI= for no MPI, or MPI=<nprocs> for MPI)
make pypolychord MPI=
python setup.py install --user

# Go back
cd ..
```

**With MPI** (recommended for HPC — add number of compile processes):
```bash
make pypolychord MPI=4
python setup.py install --user
```

**Verify installation:**
```bash
python -c "import pypolychord; print('PyPolyChord OK')"
```

### Step 2: Install bilby stack

**Option A — Automated setup (recommended):**
```bash
# Conda (installs everything including PolyChord):
source setup_env.sh conda

# OR venv:
source setup_env.sh venv
```

**Option B — Manual install:**
```bash
pip install -r requirements.txt
```

The `setup_env.sh` script will:
1. Create a conda/venv environment
2. Install LALSuite, bilby, parallel-bilby, pypolychord-bilby, mpi4py
3. Clone and build PolyChord from source automatically

**Option C — Install only PolyChord** (if bilby is already installed):
```bash
source setup_env.sh polychord
```

### Verify everything works

```bash
python -c "
import bilby
import pypolychord
import lal
import lalsimulation
print('bilby:', bilby.__version__)
print('PyPolyChord: OK')
print('LALSuite: OK')
"
```

---

## Running

### Generate data + submit all jobs (Slurm)

```bash
cd parallel_bilby/
bash run_all.sh              # generates data dumps → sbatch submits all 3
                              # results go to results/<label>/
                              # timing logged to results/timing_summary.txt
```

Or step by step:
```bash
bash run_all.sh --gen-only   # generate data dumps only (no submission)
bash run_all.sh              # submit to Slurm
```

### Run a single job manually

```bash
# Step 1: Generate the data dump
cd GW150914/
parallel_bilby_generation GW150914_IMRPhenomD.ini

# Step 2: Run with MPI (output goes to results/GW150914_IMRPhenomD/)
mpirun -n 64 parallel_bilby_analysis results/GW150914_IMRPhenomD/data/GW150914_IMRPhenomD_data_dump.pickle
```

### Run locally (testing, no Slurm)

```bash
bash run_all.sh --local 4    # runs all 3 with 4 MPI processes each
                              # timing recorded for each sampling run
```

### Check results after completion

```bash
ls results/                           # all run directories + timing_summary.txt
cat results/timing_summary.txt        # wall-clock timing for every stage
```

---

## Slurm configuration — nodes, tasks, and how to find yours

The `nodes` and `ntasks-per-node` settings in the `.ini` files are **cluster-dependent**.
You need to match them to your HPC system. Here's how to find the right values:

### Where to configure

Edit the `## Slurm Settings` section at the bottom of each `.ini` file:

```ini
## Slurm Settings
nodes = 4
ntasks-per-node = 16
time = 24:00:00
```

### How to find your cluster's values

1. **Cores per node** — check with your cluster:
   ```bash
   # Method 1: Slurm
   sinfo -N -l | head -5        # shows CPUs per node

   # Method 2: direct
   nproc                         # cores on current node
   lscpu | grep "^CPU(s):"      # same info

   # Method 3: cluster docs
   # Check your HPC's documentation/wiki for node specs
   ```

2. **Set `ntasks-per-node`** = number of physical cores per node (not hyperthreads).
   Common values: 16, 28, 32, 40, 48, 64, 128.

3. **Set `nodes`** based on desired total MPI ranks:
   - Total MPI ranks = `nodes × ntasks-per-node`
   - Rule of thumb: total ranks ≈ `nlive` (2000) or a fraction of it
   - More nodes = faster per iteration, but Slurm queue wait may be longer

4. **Set `time`** based on estimated runtime (see table below) with some margin.

### Example configurations by cluster type

| Cluster type            | `ntasks-per-node` | `nodes` (GW150914) | `nodes` (GW170817) |
|-------------------------|--------------------|---------------------|---------------------|
| 16-core (older)         | 16                 | 4                   | 10                  |
| 28-core (Broadwell)     | 28                 | 3                   | 6                   |
| 48-core (AMD Rome)      | 48                 | 2                   | 4                   |
| 128-core (AMD Milan)    | 128                | 1                   | 2                   |

### Adding account/partition

Most clusters require a project account and/or partition. Add these via
`extra-lines` in the Slurm section **or** edit the generated submit script:

```ini
# In the .ini file:
nodes = 4
ntasks-per-node = 16
time = 24:00:00

# Add any extra Slurm directives your cluster needs:
# extra-lines = --account=myproject --partition=batch --qos=normal
```

Or after generation, edit the submit script directly:
```bash
vi results/GW150914_IMRPhenomD/submit/bash_GW150914_IMRPhenomD.sh
# Add: #SBATCH --account=myproject
```

### PBS/Torque clusters

If your cluster uses PBS instead of Slurm, generate the data dump first, then
write your own submission script calling:
```bash
mpirun parallel_bilby_analysis results/<label>/data/<label>_data_dump.pickle
```

---

## Sampler settings

All runs use **PyPolyChord** (PolyChord nested sampling):

| Setting        | Value | Description                              |
|----------------|-------|------------------------------------------|
| `nlive`        | 2000  | Number of live points                    |
| `nprior`       | -1    | Prior samples (−1 = 10 × nlive)          |
| `num-repeats`  | 40    | Slice sampling repeats per iteration     |

The likelihood uses **relative binning** (heterodyning) via bilby's
`RelativeBinningGravitationalWaveTransient` with `epsilon = 0.5`, matching
the heterodyned likelihood used in our JAX analysis.

---

## Analysis settings (matched to JAX)

### GW150914 — BBH
| Parameter       | Value                       |
|-----------------|-----------------------------|
| Waveform        | IMRPhenomD                  |
| Likelihood      | Relative binning (ε=0.5)   |
| Duration        | 8 s                         |
| f_min, f_max    | 20 Hz, 1024 Hz              |
| f_ref           | 20 Hz                       |
| Detectors       | H1, L1                      |
| M_c prior       | Uniform [10, 80] M☉         |
| q prior         | Uniform [0.125, 1]          |
| Spin prior      | Uniform [-1, 1] (aligned)   |
| d_L prior       | PowerLaw(α=2) [1, 2000] Mpc |
| Mass constraint | m₁, m₂ ∈ [1, 100] M☉       |
| t_c prior       | Uniform [−0.05, +0.05] s    |
| Phase marg.     | Yes                         |

### GW170817 — BNS
| Parameter       | Value                           |
|-----------------|---------------------------------|
| Waveform        | IMRPhenomD_NRTidalv2 / TaylorF2 |
| Likelihood      | Relative binning (ε=0.5)       |
| Duration        | 128 s                           |
| f_min, f_max    | 23 Hz, 2048 Hz                  |
| f_ref           | 20 Hz                           |
| Detectors       | H1, L1, V1                      |
| M_c prior       | Uniform [1.184, 2.168] M☉       |
| q prior         | Uniform [0.125, 1]              |
| Spin prior      | Uniform [-0.05, 0.05] (low-spin)|
| d_L prior       | PowerLaw(α=2) [1, 75] Mpc       |
| Mass constraint | m₁, m₂ ∈ [0.5, 7.7] M☉         |
| t_c prior       | Uniform [−0.1, +0.1] s          |
| λ₁, λ₂ prior   | Uniform [0, 5000]               |
| Phase marg.     | Yes                             |

---

## Expected output

All results are consolidated in `results/`:

```
results/
├── timing_summary.txt                            # ← timing for all stages
├── GW150914_IMRPhenomD/
│   ├── data/
│   │   └── GW150914_IMRPhenomD_data_dump.pickle   # data + PSD + reference waveform
│   ├── result/
│   │   └── GW150914_IMRPhenomD_result.json        # bilby result (posteriors)
│   └── submit/
│       └── bash_GW150914_IMRPhenomD.sh            # auto-generated Slurm script
├── GW170817_IMRPhenomD_NRTidalv2/
│   └── ...
└── GW170817_TaylorF2/
    └── ...
```

### Timing log

`results/timing_summary.txt` records wall-clock time for each stage:

```
TIMESTAMP             RUN                             STAGE            ELAPSED
------------------------------------------------------------------------------------
2026-02-19 14:00:01   GW150914_IMRPhenomD             data_generation  00:02:15 (135 s)
2026-02-19 14:02:16   GW170817_IMRPhenomD_NRTidalv2   data_generation  00:05:30 (330 s)
2026-02-19 14:07:46   GW170817_TaylorF2               data_generation  00:04:10 (250 s)
2026-02-19 14:11:56   GW150914_IMRPhenomD             sampling_local   01:23:45 (5025 s)
...
2026-02-19 20:30:00   ALL                             total            06:30:00 (23400 s)
```

For Slurm jobs, sampling time is recorded in the Slurm output logs rather than
the timing file (since `sbatch` returns immediately). Check with:
```bash
sacct -j <JOBID> --format=JobID,Elapsed,MaxRSS,State
```

### Load results in Python

```python
import bilby
result = bilby.result.read_in_result("results/GW150914_IMRPhenomD/result/GW150914_IMRPhenomD_result.json")
result.plot_corner()
print(result.posterior[['chirp_mass', 'mass_ratio', 'luminosity_distance']].describe())
print(f"Sampling time: {result.sampling_time:.1f} s")   # bilby records this internally
```

---

## Estimated runtimes

Runtimes with relative binning + PolyChord (faster than full likelihood):

| Run                           | ~CPU-hours | Wall time (10 nodes × 16 cores) |
|-------------------------------|------------|----------------------------------|
| GW150914 IMRPhenomD           | ~200       | ~1-2 h                           |
| GW170817 IMRPhenomD_NRTidalv2 | ~3000      | ~18 h                            |
| GW170817 TaylorF2             | ~2000      | ~12 h                            |

GW170817 is much slower due to the 128 s segment (vs 8 s for GW150914).

---

## Troubleshooting

**PolyChord build fails:**
- Ensure `gfortran` and `make` are available: `module load gcc`
- Check MPI: `module load openmpi` or `module load mpich`

**`ImportError: No module named pypolychord`:**
- Rebuild: `cd PolyChordLite && python setup.py install --user`
- Or add to path: `export PYTHONPATH=$PYTHONPATH:$(pwd)/PolyChordLite/lib`

**Data download fails (GWOSC):**
- Ensure internet access from compute nodes, or pre-download data
- Some clusters require proxy settings for HTTPS

**MPI errors:**
- Ensure `mpi4py` was built against the same MPI as PolyChord
- Rebuild `mpi4py`: `pip install --no-cache-dir mpi4py`
