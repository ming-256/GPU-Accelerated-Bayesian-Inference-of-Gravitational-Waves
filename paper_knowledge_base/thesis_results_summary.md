# Thesis Results Summary (Superseded by A100 Runs)

These results are from the master's thesis (Final_Report-1.pdf), run on an NVIDIA L4 GPU.
They are **superseded** by the A100 runs in the GitHub repository, but are documented here
for reference and for understanding the methodology.

## H_0 Result (Thesis)

**Baseline (Model A):** H_0,JAX = 70.4 +14.9/-6.5 km/s/Mpc (MAP, 68.3% CI)
**LVK reference:** H_0,LVK = 70.0 +12.0/-8.0 km/s/Mpc (Abbott et al. 2017b)

Excellent agreement. MAP values very consistent. Slight differences in CI width and
asymmetry attributable to waveform model differences (IMRPhenomD_NRTidalv2 vs
IMRPhenomPv2_NRTidal) and sampler behaviour.

## Prior Sensitivity (Thesis)

### Reweighting Reproduction
- Reweighted flat-in-z curve (thesis Fig 8a) closely matches Abbott et al. (2017b) Fig 8b
- Both show only minor shift from baseline — leads to conclusion that prior choice has little impact

### Direct Sampling Critique (KEY RESULT)
- Direct sampling under flat-in-z prior (thesis Fig 9, blue curve) shows **markedly different** H_0 posterior
- Much broader distribution with significantly more probability mass at high H_0
- The sampler explores low-d_L solutions that are inaccessible via reweighting
- Thesis Fig 10 shows d_L marginal: directly sampled flat-in-z has substantial probability at low d_L where reweighted samples have negligible coverage
- **Conclusion:** Reweighting was insufficient to capture the true impact of the flat-in-z prior. The H_0 inference is more sensitive to this prior choice than Abbott et al. (2017b) reported.

### Bayesian Evidence (Thesis Table 2)

| Model | ln Z ± σ |
|-------|----------|
| Baseline (volumetric d_L, σ_vp=150) | 638.97 ± 0.07 |
| Increased uncertainty (σ_vp=250) | 639.04 ± 0.06 |
| Flat-in-z prior | 639.64 ± 0.06 |

Bayes factor between flat-in-z and baseline: B = 1.95 ("barely worth mentioning" on Jeffreys scale).
The slightly higher evidence for flat-in-z is likely from better fit at low-d_L / high-H_0.

## GW150914 Validation (Thesis)

- Thesis Figures 2 and 3: corner plots comparing JAX pipeline to LVK (GWTC-2.1) and Bilby (Wong et al. 2023)
- Broad agreement with LVK despite waveform model difference (IMRPhenomD vs IMRPhenomXPHM)
- Excellent internal consistency between heterodyned and unheterodyned JAX runs
- Good agreement with Bilby using same IMRPhenomD waveform

## GW170817 Parameter Estimation (Thesis)

- Thesis Figures 4, 5: corner plots for GW170817
- Good agreement for d_L and iota (key for H_0)
- Mass ratio q peaks at higher value in JAX runs vs LVK — attributed to waveform model difference
  (IMRPhenomD_NRTidalv2 vs IMRPhenomPv2_NRTidal) and possibly wrap-around parameter handling
- Joint H_0 fitting (Model A) does not perturb core GW parameters (thesis Fig 6)

## Runtime Comparison (Thesis, L4 GPU — Table 5)

### Key entries from thesis Table 5 (all times HH:MM:SS)

| Model | Event | Live Pts (K) | Runtime | Runtime/K Live Pts |
|-------|-------|-------------|---------|-------------------|
| A (het, H_0, constrained) | GW170817 | 2.5 | 8:24 | 3:22 |
| A | GW170817 | 7.5 | 22:38 | 3:01 |
| A | GW170817 | 10 | 31:26 | 3:09 |
| A | GW170817 | 15 | 45:29 | 3:02 |
| A (Flat-in-z) | GW170817 | 10 | 59:51→29:55 | 3:00 |
| B (het, no H_0) | GW170817 | 5 | 12:02 | 2:24 |
| B | GW170817 | 10 | 23:50 | 2:23 |
| C (no het, no H_0) | GW170817 | 1.216 | 44:19:57 | 36:27:27 |
| D (het, H_0, general) | GW170817 | 5 | 52:48→26:24 | 5:17 |
| E (het, no H_0, general) | GW170817 | 5 | 19:58 | 4:00 |
| F (het, GW150914) | GW150914 | 5 | 10:06→5:03 | 1:01 |
| Bilby (456 CPUs) | GW170817 | 1.216 | 4:37:32 | 3:48:14 |
| Bilby (532 CPUs) | GW170817 | 1.596 | 3:49:17 | 2:23:39 |

### Heterodyning Speedup (L4)
- GW150914: 22x (Model F vs G)
- GW170817: 900x (Model B vs C, per K live points)

### JAX vs Bilby (Unheterodyned, L4 vs CSD3)
- Model C (1.3K live, unheterodyned, L4): ~46 hours wall-clock
- Bilby (1.216K live, 456 CPUs): ~4.5 hours wall-clock
- Single-GPU equivalent: 32x speedup vs single CPU core
- But CPU cluster with 456 cores is faster in wall-clock time for unheterodyned

### Key Insight from Thesis
- Heterodyning provides the dominant speedup (900x for BNS)
- GPU hardware parallelism provides ~32x over single core
- Combined: heterodyned GPU is competitive with or faster than large CPU clusters
- At high live-point counts (>5K), heterodyned GPU enters a regime where CPU clusters would need impractical core counts

## Analysis Models (Thesis Table 1)

| Model | Event | Priors | N_params | Heterodyned | H_0 Analysis | Waveform |
|-------|-------|--------|----------|-------------|-------------|----------|
| Bilby | GW170817 | Constrained | 17 | No | No | IMRPhenomPv2_NRTidal |
| A | GW170817 | Constrained | 15 | Yes | Yes | IMRPhenomD_NRTidalv2 |
| B | GW170817 | Constrained | 13 | Yes | No | IMRPhenomD_NRTidalv2 |
| C | GW170817 | Constrained | 13 | No | No | IMRPhenomD_NRTidalv2 |
| D | GW170817 | General | 15 | Yes | Yes | IMRPhenomD_NRTidalv2 |
| E | GW170817 | General | 13 | Yes | No | IMRPhenomD_NRTidalv2 |
| F | GW150914 | General | 11 | Yes | No | IMRPhenomD |
| G | GW150914 | General | 11 | No | No | IMRPhenomD |
| A (Flat-in-z) | GW170817 | As A | 15 | Yes | Yes | IMRPhenomD_NRTidalv2 |
| A (Uncertainty) | GW170817 | As A, σ_vp=250 | 15 | Yes | Yes | IMRPhenomD_NRTidalv2 |
