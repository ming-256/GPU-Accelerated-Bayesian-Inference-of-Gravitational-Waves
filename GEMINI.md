# GPU-Accelerated Bayesian Inference of Gravitational Waves

## Project Overview
This project implements GPU-accelerated Bayesian parameter estimation for gravitational wave signals (e.g., GW150914, GW170817) using JAX, Blackjax (nested sampling), Jim (gravitational wave likelihood), and Ripple (fast waveforms). It significantly speeds up analysis compared to traditional CPU-based frameworks. A major focus is on Hubble constant ($H_0$) inference from Binary Neutron Star (BNS) mergers and investigating the impact of prior reweighting vs. direct sampling. The repository also contains the manuscript and knowledge base for a target submission to the Monthly Notices of the Royal Astronomical Society (MNRAS).

## Key Directories
*   `GW150914/` & `GW170817/`: Contains event-specific JAX inference scripts (e.g., `GW170817_heterodyned_*.py`, `GW170817_unheterodyned_*.py`), run orchestration scripts, and prior configurations.
*   `parallel_bilby/`: Code for CPU baseline comparison runs using `pBilby` (PyPolyChord and Bilby). Features matching models to compare against the JAX framework.
*   `Plots/`: A comprehensive suite of Python scripts (`plot_*.py`) and orchestrators (`run_all_plots.sh`) for generating paper figures and analyzing result data.
*   `Results/`: Directory containing inference outputs (CSVs, HDF5), logs, and summary statistics from runs.
*   `mnras_paper/`: LaTeX source code and build files for the MNRAS paper draft.
*   `paper_knowledge_base/`: Markdown documentation acting as the central truth for project strategy, literature review, hardware specs, run timing data, and result-to-script mappings.

## Building and Running

### Environment Setup
Requires Python 3.12, CUDA 12.x, and a GPU (8GB+ recommended). A setup script is provided for Google Cloud Workstations (`~/.workstation/customize_environment`).

### GPU Inference (JAX)
Navigate to the event script directory and run the specific analysis script.
```bash
# Example for GW170817 heterodyned runs
cd GW170817/Scripts
python GW170817_heterodyned_1.py
# Or use the provided bash scripts for batch processing
bash run_all_heterodyned.sh
```

### CPU Baseline (pBilby)
For cluster execution or local MPI testing.
```bash
cd parallel_bilby
source setup_env.sh
# Edit config.sh for cluster resources if needed
bash run_all.sh --primary-only
```

### Plotting and Analysis
Generate all paper plots by running the orchestration script or running specific scripts for targeted plots.
```bash
cd Plots
bash run_all_plots.sh
# Or run an individual plot script
python plot_H0_synoptic.py
```

### Paper Compilation
Compile the LaTeX manuscript using `latexmk`.
```bash
cd mnras_paper
latexmk -pdf main.tex
```

## Development Conventions
*   **Scientific Reproducibility:** Extensive logging, parameter tracking, and hardware configuration details must be preserved for any run intended for publication. Reference `paper_knowledge_base/result_link_index.md` to ensure scripts map correctly to results.
*   **Performance Metrics:** For new models or samplers, compare wall-clock time and sample efficiency against both established CPU baselines (Bilby) and previous JAX iterations.
*   **Code Style:** Standard Python scientific computing conventions (using `numpy`, `scipy`, `matplotlib`, `jax`). Scripts tend to be monolithic procedural files tailored for specific hardware batching/execution environments.
