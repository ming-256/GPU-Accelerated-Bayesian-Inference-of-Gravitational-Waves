# GPU-Accelerated Bayesian Inference of Gravitational Waves

GPU-accelerated Bayesian parameter estimation for gravitational-wave signals
using JAX, with nested sampling from BlackJAX-NS. The scientific focus is
Hubble-constant inference from the binary-neutron-star merger GW170817, and in
particular what happens when the luminosity-distance prior is changed by
direct re-sampling rather than by post-hoc reweighting.

This is the **working repository**: exploratory scripts, every run we did,
the manuscript, and the project knowledge base. If you want the curated,
citable release that accompanies the paper, use that instead:

> **https://github.com/ming-256/GW170817-bright-siren-H0**
> Zenodo (concept DOI, resolves to newest version): [10.5281/zenodo.21038511](https://doi.org/10.5281/zenodo.21038511)

That release is self-contained — chains, sampling pipeline, analysis code and
manuscript — and rebuilds every figure and table with `bash regenerate.sh`.

## The paper

> Yang M. H., Prathaban M., Yallup D., Handley W. (2026).
> *Rapid Hubble constant inference from GW170817 using GPU-accelerated
> nested sampling: prior sensitivity and the limits of post-hoc reweighting.*
> MNRAS (submitted). [arXiv:2606.30504](https://arxiv.org/abs/2606.30504)

Source is in `mnras_paper/`; `mnras_paper/arxiv/` is the self-contained
submission bundle.

## Layout

| Path | What is in it |
|------|---------------|
| `GW170817/Scripts/` | the GW170817 samplers: `GW170817_heterodyned_{1,2,3}.py` (baseline / flat-in-z / sigma_vp=250), `GW170817_unheterodyned_1.py`, plus `run_*.sh` drivers and `BatchRun.py` |
| `GW150914/Scripts/` | `GW150914_heterodyned.py`, the XPHM validation run |
| `Plots/` | figure, table and summary generators (`plot_*.py`, `build_*.py`, `compute_*.py`) and `run_all_plots.sh` |
| `Results/` | run outputs: `test_suite/<run_id>/` per-run chains and logs, `gwtc1_phasemarg/` host-localised chains and figures, `scaling_study/`, `logs/` |
| `EventData/GWOSC/` | LVK strain for GW170817 and GW150914 (Git LFS) |
| `mnras_paper/` | manuscript, bibliography, figures, test-suite session plans and audits |
| `paper_knowledge_base/` | project strategy, literature review, hardware notes, result-to-script index |
| `parallel_bilby/` | CPU baseline runs with parallel-bilby, for the speed comparison |
| `memory/`, `GEMINI.md` | working notes and agent context |

Large binaries (strain HDF5, chain CSVs) are tracked with **Git LFS**. Run
`git lfs install && git lfs pull` after cloning, or you will get ~130-byte
pointer files instead of data.

## Environment

Python 3.12, CUDA 12, and a GPU with 8 GB+ (the paper's runs used a single
NVIDIA A100 40 GB).

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install uv

# JAX with CUDA first
uv pip install "jax[cuda12]>=0.8.2" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

# The GW-JAX-Team stack. Clone into libraries/ (gitignored) and install editable.
mkdir -p libraries && cd libraries
git clone https://github.com/GW-JAX-Team/ripple.git
git clone https://github.com/GW-JAX-Team/flowMC.git
git clone https://github.com/GW-JAX-Team/jim.git
cd ..
uv pip install -e "libraries/ripple[cuda]" -e "libraries/flowMC[cuda]" -e "libraries/jim[cuda]"

# Nested sampling kernel + analysis tools
uv pip install git+https://github.com/handley-lab/blackjax@nested_sampling
uv pip install anesthetic astropy gwpy tqdm numpy scipy matplotlib h5py pandas
```

Versions used for the paper: ripple v0.0.9, jimgw v0.3.0, flowMC v0.4.5,
BlackJAX on the `nested_sampling` branch.

Verify:

```bash
python -c "import jax; print(jax.devices())"
python -c "import jimgw, ripplegw, flowMC; print('ok')"
```

## Running an analysis

Run from the repository root — the scripts resolve data paths relative to it.

```bash
# One GW170817 run: baseline d_L prior, IMRPhenomXAS_NRTidalv3
python GW170817/Scripts/GW170817_heterodyned_1.py \
    --waveform IMRPhenomXAS_NRTidalv3 \
    --data-source local --psd-source gwtc1 --ref-params gwtc1 \
    --phase-marginalization --n-live 5000 \
    --output-dir Results/gwtc1_phasemarg
```

Which script you run selects the distance prior:

| Script | Prior / variant |
|--------|-----------------|
| `GW170817_heterodyned_1.py` | baseline, Beta(3,1) — volumetric, LVK convention |
| `GW170817_heterodyned_2.py` | flat-in-z, sampled directly |
| `GW170817_heterodyned_3.py` | baseline with sigma_vp = 250 km/s |
| `GW170817_unheterodyned_1.py` | baseline, unheterodyned likelihood |

`--help` lists the rest (`--num-delete`, `--n-bins`, `--seed`,
`--m-comp-lo/--m-comp-hi`, `--fixed-sky`, PSD and reference-parameter
sources).

The paper's runs were driven by `mnras_paper/test_suite/session_plans/session_*.sh`,
which also write each run's `config.json` provenance record and update
`mnras_paper/test_suite/run_catalog.csv`. Sampler settings for the science
runs: `n_live=5000`, `n_delete=2500`, `n_mcmc=8*n_dim`, 501 heterodyne bins,
20–2048 Hz, phase-marginalised (14 parameters).

Figures and tables:

```bash
bash Plots/run_all_plots.sh
```

## Performance

A heterodyned GW170817 run at `n_live=5000` takes about 13 minutes on one
A100; the unheterodyned equivalent takes tens of hours. Measured speed-ups at
matched `n_live` run from ~31x at 500 live points to ~68x at 2500.

## Data sources

- GW170817 strain, PSDs and GWTC-1 posteriors — [LIGO P1800061](https://dcc.ligo.org/LIGO-P1800061/public), [P1700296](https://dcc.ligo.org/LIGO-P1700296/public), [P1900011](https://dcc.ligo.org/LIGO-P1900011/public)
- GW150914 strain — [GWOSC O1 archive](https://gwosc.org/archive/)
- GW150914 reference PE — [Zenodo 10.5281/zenodo.6513631](https://doi.org/10.5281/zenodo.6513631) (LVK GWTC-2.1)

## Licence

Code MIT, data CC BY 4.0, matching the public release. See the `LICENSE` file
in https://github.com/ming-256/GW170817-bright-siren-H0.

## Contact

Ming Han Yang — mhy32@cantab.ac.uk
