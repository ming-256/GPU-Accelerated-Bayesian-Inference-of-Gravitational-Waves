# HPC parallel Bilby audit and planned changes

Date: 2026-04-21

## Purpose

This note records the implementation audit for the planned CPU/pBilby comparison
against the GPU/JAX GW170817 standard-siren analysis.  The goal is to prevent a
premature HPC submission with a configuration that is not actually like-for-like.

The intended paper claim is not "GPU code is faster than Bilby" in isolation.
The intended MNRAS claim is:

> Direct, rapid, GPU-accelerated nested sampling enables a robust re-examination
> of the GW170817 H0 prior sensitivity problem; the pBilby run is the mature
> CPU reference point used to validate the comparison and benchmark the scaling
> regime.

## Current implementation summary

### GPU/JAX baseline

Primary script:

- `GW170817/Scripts/GW170817_heterodyned_1.py`

Current baseline configuration:

- Event: GW170817.
- Detectors: H1, L1, V1.
- Duration: 128 s.
- Analysis band: 23 Hz to 2048 Hz.
- Waveforms: `IMRPhenomD_NRTidalv2` primary, `TaylorF2` cross-check.
- Likelihood: custom heterodyned/relative-binning likelihood.
- Phase marginalization: optional; paper runs use phase marginalization.
- Standard-siren terms:
  - `v_r = 3327 km/s`, `sigma_vr = 72 km/s`
  - `v_p_obs = 310 km/s`, `sigma_vp = 150 km/s`
  - likelihood term uses `v_p + H_0 d_L`
- Priors:
  - `M_c` in `[1.184, 2.168]`
  - `q` in `[0.125, 1]`
  - aligned spins in `[-0.05, 0.05]`
  - `d_L` in `[1, 75] Mpc`, volumetric via beta(3,1)
  - `H_0` log-uniform in `[20, 250]`
  - `v_p` uniform in `[-1000, 1000]`
  - hard component-mass constraint `m1, m2 in [0.5, 7.7]`
  - explicit Jacobian for uniform component-mass prior while sampling in
    `(M_c, q)`: `log(M_c) - 1.2 log(q) + 0.4 log(1+q)`.
- Sampling:
  - baseline `n_live = 5000`
  - baseline `num_delete = 0.5 n_live`
  - `num_inner_steps = 8 * ndim`

Prior-variant scripts:

- `GW170817/Scripts/GW170817_heterodyned_2.py`: flat-in-z variant.
- `GW170817/Scripts/GW170817_heterodyned_3.py`: `sigma_vp = 250 km/s`.

Important implementation detail:

- The flatZ and vp250 scripts currently use `num_delete = 0.3 n_live`, while
  the baseline uses `0.5 n_live`.  This may be intentional for stability, but
  it must be documented and should be convergence-checked before the paper
  treats evidence/runtimes across variants as directly comparable.

### parallel_bilby implementation

Primary script:

- `parallel_bilby/GW170817/run_GW170817.py`

Current CPU reference configuration:

- Event, detectors, duration, fmin/fmax, and standard-siren likelihood are
  broadly matched to the JAX baseline.
- Waveform generator uses `lal_binary_neutron_star` with approximant selected
  by `--waveform`.
- Uses Bilby `RelativeBinningGravitationalWaveTransient`.
- Phase marginalization is enabled.
- Uses `pypolychord` with `nlive` and `num_repeats`.
- `parallel_bilby/run_all.sh` does not use the `.ini` files; it calls the
  Python scripts directly and generates Slurm scripts itself.

Current Slurm defaults:

- `NODES=7`
- `CORES_PER_NODE=76`
- `NLIVE=2000`
- `NUM_REPEATS=40`

## External checks

Bilby documentation states that when sampling in chirp mass and mass ratio but
wanting a prior uniform in component masses, the intended prior classes are:

- `bilby.gw.prior.UniformInComponentsChirpMass`
- `bilby.gw.prior.UniformInComponentsMassRatio`

Relevant documentation:

- https://bilby-dev.github.io/bilby/gw_prior.html
- https://bilby-dev.github.io/bilby/api/bilby.gw.prior.UniformInComponentsChirpMass.html
- https://bilby-dev.github.io/bilby/api/bilby.gw.likelihood.relative.RelativeBinningGravitationalWaveTransient.html

This matches the Jacobian implemented in the JAX prior.

## Blocking issues before HPC submission

### 1. Mass prior mismatch

Current pBilby prior:

```text
chirp_mass = Uniform(...)
mass_ratio = Uniform(...)
mass_1 = Constraint(...)
mass_2 = Constraint(...)
```

This is not equivalent to the JAX baseline, which adds the component-mass
Jacobian.  The pBilby prior should use:

```text
chirp_mass = bilby.gw.prior.UniformInComponentsChirpMass(...)
mass_ratio = bilby.gw.prior.UniformInComponentsMassRatio(...)
```

with the same bounds and component-mass constraints.

Decision: fix this before any production HPC run.

### 2. PSD/source mismatch

The JAX production runs are documented as using `--psd-source gwtc1`, loading
the official GWTC-1/BayesWave PSD file from `EventData/GWOSC/GW170817`.

The pBilby script currently estimates PSDs from GWOSC using Welch:

```text
fftlength=32, overlap=16, Tukey, median
```

This is defensible as a Bilby-style run, but it is not a strict like-for-like
comparison against the documented A100 production runs.

Decision needed before code change:

- Option A, strict comparison: modify pBilby to load/interpolate the same
  GWTC-1 PSDs used by JAX.

Recommendation: implement Option A for the primary pBilby run.

### 3. Result provenance is incomplete in the checkout

The final plots are tracked, but most underlying CSV/HDF5/PSD files are ignored
or absent from this checkout.  For example:

- `Results/gwtc1_phasemarg/*.csv` is expected by plotting scripts but not
  present locally.
- `Results/GW170817_GWTC-1.hdf5` is expected by plotting utilities but ignored.
- `EventData/GWOSC/GW170817/GWTC1_GW170817_PSDs.dat` is expected by JAX PSD
  loading but ignored/absent locally.

This does not invalidate the plots, but it blocks reproducible paper assembly.

Decision: add a machine-readable run manifest and either restore the result
files locally from archival storage or document exact regeneration commands.

Action still needed: upload or restore the CSV, HDF5, and PSD inputs used for
the final plotted results.

### 4. Local validation environment is currently broken

The system Python can locate Bilby, GWPy, and LALSimulation, but importing Bilby
fails because NumPy cannot load `libgfortran.5.dylib`.  `pypolychord` is also
not installed in the current local environment.

Decision: local smoke tests should be done in a fresh venv or on the HPC setup
created by `parallel_bilby/setup_env.sh`.

### 5. `.ini` files may mislead future users

The `.ini` files describe pBilby runs, but `parallel_bilby/run_all.sh` directly
calls Python scripts and ignores those `.ini` files.  They should either be:

- converted into actual `bilby_pipe` inputs and used, or
- clearly marked as archival/documentary examples.

Decision: for this project, keep the Python path as primary and update the
README and comments so there is only one production workflow.

## Planned changes

### Phase 1: make the pBilby CPU reference scientifically comparable

1. Update `parallel_bilby/GW170817/GW170817.prior`.
   - Replace uniform `chirp_mass` and `mass_ratio` priors with Bilby's
     `UniformInComponentsChirpMass` and `UniformInComponentsMassRatio`.
   - Keep `mass_1`, `mass_2` constraints.
   - Keep spin, sky, distance, time, tidal, `H_0`, and `v_p` bounds unchanged.

2. Update `parallel_bilby/GW170817/run_GW170817.py`.
   - Add `--psd-source {gwtc1,self}` with default `gwtc1` for paper runs.
   - Add `--data-source {fetch,local}` if the HPC filesystem can carry local
     GWOSC HDF5 files; otherwise keep fetch for data and load only PSD locally.
   - Add a loader for `GWTC1_GW170817_PSDs.dat` equivalent to the JAX loader.
   - Write the full runtime configuration to a JSON or text manifest in the
     output directory.
   - Remove duplicate "Data loading" logger line.

3. Update `parallel_bilby/run_all.sh`.
   - Add a mode to run only the primary `GW170817_IMRPhenomD_NRTidalv2` job.
   - Avoid launching GW150914 and TaylorF2 by default for the first HPC
     submission.
   - Add a short preflight check that confirms `pypolychord`, `bilby`, `lal`,
     `mpi4py`, and required PSD/data files exist before submitting Slurm jobs.

4. Update `parallel_bilby/README.md`.
   - State that the production paper CPU reference is GW170817
     `IMRPhenomD_NRTidalv2`, phase-marginalized, relative-binned,
     standard-siren likelihood.
   - State exactly which differences remain relative to JAX, if any.

Acceptance criteria:

- A `--local-serial --primary-only` or equivalent dry run reaches likelihood
  construction without missing-file or prior-parsing errors.
- pBilby printed/recorded prior names show the component-mass prior classes.
- Output manifest records waveform, priors, PSD source, `nlive`,
  `num_repeats`, rank count, Bilby version, LALSuite version, and host.

Implementation status on 2026-04-21:

- `parallel_bilby/GW170817/GW170817.prior` now uses
  `UniformInComponentsChirpMass` and `UniformInComponentsMassRatio`.
- `parallel_bilby/GW170817/run_GW170817.py` now supports `--psd-source
  {gwtc1,self}`, `--data-source {fetch,local}`, local PSD/data paths, and JSON
  run manifests.
- `parallel_bilby/run_all.sh` now has `--primary-only` and `--preflight`, and
  preflight parses the GW170817 prior to verify the component-mass prior
  classes.
- `parallel_bilby/README.md` and `config.sh` now describe the paper CPU
  reference workflow.
- Static validation passes locally, but runtime preflight fails on the local
  machine because the current Python environment cannot import NumPy/Bilby and
  lacks `mpi4py`/`pypolychord`.  The production go/no-go must therefore be made
  on the HPC environment after `setup_env.sh`.

### Phase 2: controlled HPC submission

1. Submit one primary run:
   - event: GW170817
   - waveform: `IMRPhenomD_NRTidalv2`
   - `nlive=2000`
   - `num_repeats=40`
   - ranks: `7 * 76 = 532`
   - walltime: 48 h

2. Collect:
   - wall-clock runtime
   - effective samples
   - evidence and evidence error
   - posterior samples for `H_0`, `d_L`, `iota`, `M_c`, `q`, `lambda_1`,
     `lambda_2`
   - Slurm stdout/stderr
   - generated manifest

3. Decide whether a second CPU run is needed:
   - If posterior agreement is good and runtime is sufficient for the paper,
     do not spend more HPC allocation.
   - If pBilby posterior differs materially, run one controlled diagnostic:
     either `self` PSD on both sides or reduced `nlive` with fixed PSD to
     isolate PSD/prior/relative-binning differences.

Acceptance criteria:

- H0 and distance/inclination posteriors agree within expected sampler and
  waveform/relative-binning variation.
- Evidence differences are not interpreted unless likelihood and prior
  normalization are demonstrably matched.
- Runtime comparison is reported as measured hardware-specific wall-clock time,
  not as a single-core speedup.

### Phase 3: paper-plot and provenance cleanup

1. Restore or regenerate all CSV files expected by `Plots/run_all_plots.sh`.
2. Generate `Results/gwtc1_phasemarg/evidence_table.csv`.
3. Generate `Results/gwtc1_phasemarg/summary_stats.csv`.
4. Generate `Results/gwtc1_phasemarg/waveform_systematics.csv` or equivalent.
5. Add a `Results/manifest/` text or JSON summary for every plotted dataset.

Acceptance criteria:

- Running `bash Plots/run_all_plots.sh` from a clean checkout with archived
  result files reproduces the tracked figures.
- Every figure in the paper maps to an input dataset and command.

## Paper implications

Use the pBilby run as a validation and benchmarking anchor, not as the centre of
the paper.  The paper should lead with:

1. Baseline GW170817 H0 inference.
2. Direct flat-in-z sampling versus reweighting.
3. Waveform robustness.
4. Heterodyning and GPU performance as the enabling technology.
5. Measured pBilby comparison as a fair CPU reference.

Do not use the language "same model" until the mass-prior and PSD issues above
are resolved.  The defensible wording before fixes is:

> The pBilby workflow currently matches the event, waveform family, detector
> set, standard-siren likelihood, phase marginalization, and broad parameter
> bounds, but still needs prior and PSD alignment before it can be called a
> like-for-like production comparison.

## Go/no-go decision

Current status: code path prepared, but production HPC submission is still a
conditional go.

Ready after:

- the target HPC environment passes `bash run_all.sh --preflight
  --primary-only`;
- `GWTC1_GW170817_PSDs.dat` is present or `GW170817_PSD_FILE` is set;
- the first run is submitted as primary-only GW170817 IMRPhenomD_NRTidalv2;
- fresh pickles are generated with the new data/PSD provenance metadata.
