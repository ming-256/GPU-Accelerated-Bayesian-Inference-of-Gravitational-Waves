# Codebase Reference

## Repository Location
`C:\Users\Ming\Desktop\CamProject\GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves`

GitHub: https://github.com/mrosep/blackjax_ns_gw (per co-authored paper reference)

## Directory Structure

```
GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves/
├── paper_knowledge_base/          # THIS FOLDER — knowledge base for paper drafting
├── GW150914/Scripts/              # BBH validation scripts
│   └── GW150914_heterodyned.py    # 954 lines, heterodyned NS for GW150914
├── GW170817/Scripts/              # BNS analysis scripts (MAIN)
│   ├── GW170817_heterodyned_1.py  # Baseline H_0 analysis (963 lines)
│   ├── GW170817_heterodyned_2.py  # Flat-in-z prior variant
│   ├── GW170817_heterodyned_3.py  # σ_vp=250 variant
│   ├── GW170817_unheterodyned_1.py # Full likelihood (no relative binning)
│   ├── GW170817_bilby.py          # Bilby reference
│   ├── BatchRun.py                # Batch execution wrapper
│   ├── run_all_heterodyned.sh     # Master run script (6 variants)
│   ├── run_unheterodyned.sh       # Unheterodyned run script
│   └── Old/                       # Legacy versions
├── parallel_bilby/                # pBilby reference runs (FOR FUTURE CPU COMPARISON)
│   ├── GW150914/
│   │   ├── GW150914_IMRPhenomD.ini
│   │   └── run_GW150914.py
│   ├── GW170817/
│   │   ├── GW170817.prior
│   │   ├── GW170817_IMRPhenomD_NRTidalv2.ini
│   │   ├── GW170817_TaylorF2.ini
│   │   └── run_GW170817.py
│   ├── config.sh                  # HPC config: NODES=7, CORES_PER_NODE=76
│   ├── run_all.sh                 # Data gen + Slurm submission (210 lines)
│   └── setup_env.sh
├── Plots/                         # 48 plotting/analysis scripts
│   ├── _plot_utils.py             # Shared utilities, color schemes, data loaders
│   ├── plot_H0*.py                # 10+ H_0 posterior plot scripts
│   ├── plot_corner*.py            # 7+ corner plot scripts
│   ├── compute_evidence_table.py  # Bayesian evidence statistics
│   ├── compute_summary_stats.py   # Parameter summary statistics
│   ├── compute_waveform_systematics.py
│   ├── run_all_plots.sh           # Master plot orchestration (83 lines)
│   └── Old/
├── Results/gwtc1_phasemarg/       # Output directory
│   ├── plots/                     # 59+ generated figures (PDF/PNG)
│   ├── evidence_table.csv
│   └── summary_stats.csv
├── EventData/GWOSC/               # Cached GWOSC strain data
├── metha.py                       # Minimal reference implementation (478 lines)
├── PhaseMarg_Heterodyned.csv      # Large result dataset (52 MB)
└── README.md
```

## Key Scripts — Detailed Reference

### GW170817_heterodyned_1.py (Baseline H_0 Analysis)
- **Location:** `GW170817/Scripts/GW170817_heterodyned_1.py`
- **Lines:** 963
- **Parameters:** 14D (or 15D without phase marg): M_c, q, s1_z, s2_z, iota, d_L, t_c, psi, ra, dec, lambda_1, lambda_2, H_0, v_p (+ phase_c if not marginalised)
- **Priors:** Constrained (informed by LVK), volumetric d_L ∝ d²_L, flat-in-log H_0
- **Command-line args:**
  ```
  --waveform {IMRPhenomD_NRTidalv2, TaylorF2}
  --data-source {fetch, local}
  --psd-source {self, gwtc1, bilby, kazewong}
  --ref-params {gwtc1, optimize}
  --phase-marginalization
  --output-dir DIR
  ```
- **Default settings:** n_live=5000, num_delete=2500, 501 heterodyne bins

### GW170817_heterodyned_2.py (Flat-in-z Prior)
- Same as above but with flat-in-redshift prior for d_L
- π(z) = const within bounds, converted to d_L via cosmology (Astropy)

### GW170817_heterodyned_3.py (σ_vp = 250 km/s)
- Same as baseline but with increased peculiar velocity uncertainty

### GW170817_unheterodyned_1.py (Full Likelihood)
- **n_live:** 1500 (lower because each step is much slower)
- **num_delete:** 750
- **Frequency bins:** 259,201 (full grid, no relative binning)
- **Checkpoints:** Every 5 steps
- **No H_0 parameters** — pure GW PE (for comparing heterodyned vs unheterodyned posteriors)
- **Supports:** host-localised priors (NGC 4993 region) or full-sky priors

### GW150914_heterodyned.py (BBH Validation)
- **Parameters:** 10D (or 11D): M_c, q, s1_z, s2_z, iota, d_L, t_c, psi, ra, dec (+ phase_c)
- **Waveform:** IMRPhenomD
- **Detectors:** H1, L1 (no V1)
- **n_live:** 5000, num_delete=2500

### BatchRun.py
- Orchestrates multiple runs sequentially
- Logs to `Results/logs/` with timestamps

### run_all_heterodyned.sh
- Runs 6 configurations: {baseline, flatZ, vp250} × {IMRPhenomD_NRTidalv2, TaylorF2}
- Common args: `--data-source local --psd-source gwtc1 --ref-params gwtc1 --phase-marginalization`

## Plotting Infrastructure

### Key Plotting Scripts

| Script | Output | Description |
|--------|--------|-------------|
| `plot_H0_baseline_IMRPhenomD.py` | H_0 posterior + Planck/SH0ES bands | Single waveform baseline |
| `plot_H0_IMRPhenomD_variants.py` | Three H_0 variants overlaid | baseline/flatZ/vp250 |
| `plot_H0_IMRPhenomD_reweighted.py` | Reweighted vs sampled comparison | Key for prior sensitivity argument |
| `plot_H0_summary_all_methods.py` | Comprehensive H_0 overview | All methods on one plot |
| `plot_corner_GW150914.py` | GW150914 corner vs GWTC-1 | Validation figure |
| `plot_corner_IMRPhenomD_hetero_vs_unhetero.py` | Heterodyned vs unheterodyned | Internal consistency |
| `plot_corner_combined_waveforms.py` | Both waveforms + GWTC-1 | Waveform systematics |
| `plot_corner_reweighted_vs_sampled_flatZ.py` | d_L/ι comparison | Illustrates reweighting failure |
| `compute_evidence_table.py` | evidence_table.csv | log Z, σ, ESS, KL divergence |
| `compute_summary_stats.py` | summary_stats.csv | MAP, median, 68%/95% CIs |
| `compute_waveform_systematics.py` | Statistics table | Waveform-dependent H_0 biases |
| `plot_speedup_comparison.py` | ESS/walltime comparison | Performance figure |

### Shared Utilities (_plot_utils.py)
- `load_nested_csv()`: Load anesthetic NestedSamples from CSV
- `load_reweighted_csv()`: Load plain CSV with weights
- Color scheme: gwtc (blue), imr_baseline (maroon), tf2_baseline (purple), flatZ (teal), etc.
- Reference bands: Planck (green), SH0ES (orange)
- Output dir: `Results/gwtc1_phasemarg/plots/`

### Running All Plots
```bash
cd Plots && bash run_all_plots.sh
```

## Output File Naming Convention

### Heterodyned Results
```
PhaseMarg_Heterodyned_{waveform}_local_psd-{psd_source}_ref-{ref_source}_{variant}.csv
```
Examples:
- `PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv`
- `PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_flatZ.csv`

### Unheterodyned Results
```
PhaseMarg_Unheterodyned_{waveform}_local_psd-{psd_source}[_suffix].csv
```
Examples:
- `PhaseMarg_Unheterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1.csv`
- `PhaseMarg_Unheterodyned_TaylorF2_local_psd-gwtc1_full_sky.csv`

### GW150914 Results
```
GW15_PhaseMarg_Heterodyned_IMRPhenomD_local_psd-gwtc2p1_ref-gwtc1.csv
```

## JAX Configuration

All scripts use:
```python
os.environ['XLA_PYTHON_CLIENT_PREALLOCATE'] = 'false'
jax.config.update('jax_enable_x64', True)  # 64-bit precision
```

## Nested Sampling Configuration

| Parameter | Heterodyned | Unheterodyned |
|-----------|------------|---------------|
| n_live | 5000 | 1500 |
| num_delete | 2500 (0.5 × n_live) | 750 (0.5 × n_live) |
| num_mcmc_steps | n_dims × 5 | n_dims × 5 |
| Termination | dlogZ < 0.1 or fractional evidence < 0.1% | Same |

## Detector Configuration

| Event | Detectors | Duration | f_min | f_max | df | Freq bins |
|-------|-----------|----------|-------|-------|-----|-----------|
| GW170817 | H1, L1, V1 | 128s | 20 Hz | 2048 Hz | 0.007812 Hz | 259,201 |
| GW150914 | H1, L1 | 4s (?) | 20 Hz | 1024 Hz | — | — |

## Heterodyning Configuration

| Event | Waveform | Het bins | Bin shape |
|-------|----------|----------|-----------|
| GW170817 | IMRPhenomD_NRTidalv2 | 501 | (3, 501) |
| GW170817 | TaylorF2 | 501 → 442 used | (3, 442) |
| GW150914 | IMRPhenomD | 501 → 383 used | (2, 383) |
