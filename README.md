# GPU-Accelerated Bayesian Inference of Gravitational Waves

Gravitational wave parameter estimation using GPU-accelerated Bayesian nested sampling with JAX.

**Colab Notebook:** https://colab.research.google.com/drive/1oXgA-keo49iYv-94EOEI8VNeEVm_Ipfe?usp=sharing

## Overview

This project implements GPU-accelerated Bayesian inference for gravitational wave signals using:
- **JAX** for automatic differentiation and GPU acceleration
- **Blackjax** (nested sampling branch) for Bayesian inference
- **jimgw** for gravitational wave likelihood and detector simulation
- **ripple** for fast waveform generation
- **flowMC** for normalizing flow-based MCMC sampling

## Quick Start (Google Cloud Workstation)

For Google Cloud workstations (where only files persist), the repository includes an automated setup script:

```bash
# Run the setup script (automatically executed on workstation startup)
~/.workstation/customize_environment
```

The script will:
1. Install Python 3.12, CUDA 12, and system dependencies
2. Install `uv` for fast package management
3. Create a Python virtual environment
4. Verify local copies of GW-JAX-Team repositories exist (jimgw, ripple, flowMC)
5. Install all required packages with CUDA support from local repositories
6. Auto-activate the environment on login

### Automatic Startup

On Google Cloud workstations, the `~/.workstation/customize_environment` script runs automatically on startup, ensuring your environment is ready to use immediately.

## Manual Setup

### Prerequisites

- **Python 3.12** (required by jimgw, ripplegw, flowMC)
- CUDA 12.x
- Git
- 8GB+ GPU memory (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves.git
   cd GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves
   ```

2. **Create virtual environment:**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```

3. **Install uv (optional but recommended for faster installation):**
   ```bash
   pip install uv
   ```

4. **Install JAX with CUDA support (required first):**
   ```bash
   uv pip install "jax[cuda12]>=0.8.2" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
   ```

5. **Clone GW-JAX-Team repositories (if not already cloned):**
   ```bash
   # The repository includes local copies in libraries/ directory
   # If you cloned the full repo, these are already present
   # If not, clone them manually:
   mkdir -p libraries
   cd libraries
   git clone https://github.com/GW-JAX-Team/jim.git
   git clone https://github.com/GW-JAX-Team/ripple.git
   git clone https://github.com/GW-JAX-Team/flowMC.git
   cd ..
   ```

6. **Install GW-JAX-Team packages from local clones with CUDA support:**
   ```bash
   # Install from local clones with CUDA support
   cd libraries/ripple && uv pip install -e ".[cuda]" && cd ../..
   cd libraries/flowMC && uv pip install -e ".[cuda]" && cd ../..
   cd libraries/jim && uv pip install -e ".[cuda]" && cd ../..
   ```

7. **Install additional dependencies:**
   ```bash
   uv pip install git+https://github.com/handley-lab/blackjax@nested_sampling
   uv pip install git+https://git.ligo.org/lscsoft/ligo-segments.git
   uv pip install anesthetic astropy gwpy tqdm numpy scipy matplotlib h5py pandas
   ```

8. **Verify installation:**
   ```bash
   python -c "import jax; print('JAX devices:', jax.devices())"
   python -c "import jimgw, ripplegw, flowMC; print('All packages imported successfully')"
   ```

## Project Structure

```
GPU-Accelerated-Bayesian-Inference-of-Gravitational-Waves/
├── vendor/                          # Local copies of GW-JAX-Team repos
│   ├── jim/                         # jimgw - GW inference framework
│   ├── ripple/                      # ripple - Waveform generator
│   └── flowMC/                      # flowMC - MCMC sampler
├── EventData/                       # LIGO event data files
├── Results/                         # Output from inference runs
├── refactored_script_jax_refactor.py  # Main inference script
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Usage

### Running Inference on GW170817

The main script analyzes the GW170817 binary neutron star merger:

```bash
python refactored_script_jax_refactor.py
```

This will:
1. Load LIGO detector data (H1, L1, V1) for GW170817
2. Set up the waveform model (IMRPhenomD + NRTidalv2)
3. Define parameter priors
4. Run nested sampling
5. Save results to `Results/Test_jax_refactor.csv`

### Configuration

Key parameters in [refactored_script_jax_refactor.py](refactored_script_jax_refactor.py):

- `num_live = 1000` - Number of live points for nested sampling
- `num_delete = 500` - Number of points to delete per iteration
- `num_mcmc_steps` - MCMC steps per nested sampling iteration
- `BATCH_SIZE = 8` - Batch size for GPU processing

### Inference Parameters

The script infers 13 parameters:
- Chirp mass (M_c), mass ratio (q)
- Component spins (s1_z, s2_z)
- Inclination angle (iota)
- Luminosity distance (d_L)
- Coalescence time (t_c), phase (phase_c)
- Polarization angle (psi)
- Sky position (ra, dec)
- Tidal deformabilities (lambda_1, lambda_2)

## Performance

GPU acceleration provides significant speedup:
- **CPU:** ~hours per run
- **GPU (A100/V100):** ~minutes per run

## Dependencies

### Core Packages
- **JAX**: Autodiff and GPU acceleration
- **Blackjax**: Bayesian inference algorithms (nested sampling)
- **jimgw**: GW likelihood and detector handling
- **ripple**: Fast waveform generation
- **flowMC**: Normalizing flow MCMC

### Analysis Tools
- **anesthetic**: Nested sampling visualization
- **astropy**: Astronomical utilities
- **gwpy**: LIGO data access

See [requirements.txt](requirements.txt) for complete list.

## Local Repository Copies

The `libraries/jim/`, `libraries/ripple/`, and `libraries/flowMC/` directories contain cloned copies of:
- [jimgw](https://github.com/GW-JAX-Team/jim) - v0.3.0
- [ripple](https://github.com/GW-JAX-Team/ripple) - v0.0.9
- [flowMC](https://github.com/GW-JAX-Team/flowMC) - v0.4.5

**These are installed in editable mode with CUDA support**, allowing you to modify the source code and have changes take effect immediately without reinstallation:
- `pip install -e ./libraries/ripple[cuda]`
- `pip install -e ./libraries/flowMC[cuda]`
- `pip install -e ./libraries/jim[cuda]`

## Troubleshooting

### CUDA Out of Memory
Reduce `num_live` or `BATCH_SIZE` in the script.

### Import Errors
Ensure the virtual environment is activated:
```bash
source venv/bin/activate
```

### JAX Not Using GPU
Verify CUDA installation:
```bash
nvcc --version
python -c "import jax; print(jax.devices())"
```

## References

- GW-JAX-Team repositories: https://github.com/GW-JAX-Team
- GW170817 detection paper: [Abbott et al. 2017](https://arxiv.org/abs/1710.05832)
- JAX documentation: https://jax.readthedocs.io

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Contact

[Add contact information here]
