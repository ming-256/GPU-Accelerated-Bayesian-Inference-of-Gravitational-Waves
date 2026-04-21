# JAX vs pBilby GW170817 configuration equivalence matrix

Date: 2026-04-21

This matrix records the fine-grained settings that must be checked before
claiming a like-for-like GW170817 CPU/GPU comparison.

## Matched science configuration

| Item | JAX A100 production | pBilby CPU reference | Status |
|---|---:|---:|---|
| Event | GW170817 | GW170817 | matched |
| Detectors | H1, L1, V1 | H1, L1, V1 | matched |
| Trigger GPS | 1187008882.43 | 1187008882.43 | matched |
| Duration | 128 s | 128 s | matched |
| Post-trigger duration | 2 s | 2 s | matched |
| Analysis band | 23-2048 Hz | 23-2048 Hz | matched |
| Strain source | GWOSC v2/local | GWOSC v2/local or fetch | matched when configured |
| PSD source for paper | GWTC-1/BayesWave | GWTC-1/BayesWave | matched when `PSD_SOURCE=gwtc1` |
| Primary waveform | IMRPhenomD_NRTidalv2 | IMRPhenomD_NRTidalv2 | matched family |
| Waveform cross-check | TaylorF2 | TaylorF2 | available |
| Reference frequency | 20 Hz | 20 Hz | matched |
| Tidal parametrization | lambda_1, lambda_2 | lambda_1, lambda_2 | matched |
| Aligned spins | s1_z, s2_z in [-0.05, 0.05] | chi_1, chi_2 in [-0.05, 0.05] | matched |
| Distance prior | volumetric on [1,75] Mpc | PowerLaw alpha=2 on [1,75] Mpc | matched |
| H0 prior | LogUniform [20,250] | LogUniform [20,250] | matched |
| Peculiar velocity prior | Uniform [-1000,1000] | Uniform [-1000,1000] | matched |
| Component mass prior | explicit Jacobian in M_c,q | UniformInComponents priors | matched |
| Component mass constraints | [0.5,7.7] Msun | [0.5,7.7] Msun | matched |
| Phase marginalization | enabled for paper runs | enabled by default | matched |
| Time marginalization | disabled | disabled | matched |
| Distance marginalization | disabled | disabled | matched |
| Time jitter | absent/disabled | disabled | matched |
| Standard siren recession term | N(3327 \| vp + H0 dL, 72) | same | matched |
| Peculiar velocity term | N(310 \| vp, 150) | same | matched |

## Matched or controlled benchmarking settings

| Item | JAX A100 production | pBilby CPU reference | Status |
|---|---:|---:|---|
| JAX heterodyned live points | 5000 | configurable `NLIVE` | match only if `NLIVE=5000` |
| Current pBilby default live points | n/a | 2000 | feasibility run, not matched-nlive |
| JAX unheterodyned live points | 1500 | configurable `NLIVE` | match with `NLIVE=1500 --full-only` |
| JAX batch deletion | 0.5 x n_live | not applicable to PolyChord | sampler difference |
| JAX inner MCMC steps | 8 x ndim | not applicable to PolyChord | sampler difference |
| pBilby sampler | n/a | PyPolyChord | intended CPU reference |
| pBilby slice repeats | n/a | `NUM_REPEATS=40` | must be reported |
| pBilby MPI ranks | n/a | `NODES x CORES_PER_NODE`, default 532 | must be reported |
| GPU hardware | 1 x NVIDIA A100 | n/a | must be reported |
| CPU hardware | n/a | CSD3-style MPI nodes | must be reported |

## Not identical by construction

| Item | JAX | pBilby | Consequence |
|---|---|---|---|
| Heterodyned binning | custom fixed `N_BINS=501` | Bilby `epsilon`/`chi`; actual count derived at runtime | Do not claim identical bins. Report both. |
| Relative-binning phase basis | JAX custom PN phase grid | Bilby `RelativeBinningGravitationalWaveTransient` PN grid | Validate with posterior comparison. |
| Nested sampler | BlackJAX nested slice sampling | PyPolyChord | Compare wall time and posteriors, not internal iteration counts. |
| Parallelism | GPU batched deletion + vectorized likelihood | MPI PolyChord likelihood parallelism | Report hardware-specific wall-clock and compute resources. |
| Waveform implementation | Ripple/JAX | LALSimulation via Bilby | Same approximant family, different implementation stack. |

## Required run set

1. Primary CPU reference:
   `bash run_all.sh --primary-only`
   - GW170817, IMRPhenomD_NRTidalv2, pBilby relative binning, phase marginalized.
   - Default feasibility setting is `NLIVE=2000`, 532 ranks.
   - For matched live-point comparison with A100, set `NLIVE=5000`.

2. Full likelihood validation:
   `bash run_all.sh --full-only`
   - GW170817, IMRPhenomD_NRTidalv2, full Bilby likelihood, phase marginalized.
   - To match the JAX full-likelihood validation, set `NLIVE=1500`.

3. Optional combined submission:
   `bash run_all.sh --primary-only --include-full`

## Paper wording guardrail

Use:

> We match the astrophysical model, priors, data segment, PSD source, reference
> frequency, and marginalization policy. The CPU comparison uses Bilby's
> production relative-binning implementation and PyPolyChord, while the GPU
> analysis uses our fixed-bin JAX heterodyned likelihood and BlackJAX nested
> sampling.

Avoid:

> The pBilby and JAX runs use identical heterodyning bins and identical sampler
> settings.

