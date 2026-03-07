# Co-authored Paper Summary

## Citation

Metha Prathaban, David Yallup, James Alvey, Ming Yang, Will Templeton, and Will Handley.
"Gravitational-wave inference at GPU speed: A bilby-like nested sampling kernel within blackjax-ns."
MNRAS 000, 1–12 (2025). Preprint 5 September 2025. arXiv:2509.04336v1.

## Abstract Summary

- GPU-accelerated implementation of bilby's 'acceptance-walk' nested sampling kernel
- Integrated into the vectorized blackjax-ns framework
- BBH analyses with aligned spins using IMRPhenomD
- 20-40x speedups, statistically identical posteriors to bilby+dynesty
- Establishes a performance baseline for GPU-based nested sampling in GW inference

## Key Results

### 4-Second Simulated BBH Signal
- 3-detector network (O4 sensitivity), SNR 39.6
- 11 parameters (phase_c marginalized gives 10D)
- Both frameworks: 1000 effective live points
- **blackjax-ns (L4 GPU):** 1.25 hours → **38x speedup** → **2.4x cost reduction**
- **blackjax-ns (A100 GPU):** 0.93 hours → **51x speedup** → **0.6x cost** (A100 actually more expensive per analysis due to higher hourly rate)
- Posteriors in excellent agreement (Figure 1)
- Log evidence in excellent agreement (Figure 4)

### 100-Injection Study (BBH)
- O4 sensitivity, 3-detector network, SNR range 1.84-17.87
- PP plot: p-value 0.9130 (well-calibrated, Figure 7)
- Mean speedup: **32x** (range 20-50x)
- Mean cost reduction: **2.0x**
- Mean likelihood evaluations: 38.4M (blackjax-ns) vs 37.5M (bilby)
- Mean runtime: 0.82 hours per injection (blackjax-ns) vs 26.3 CPU-hours (bilby)

### 8-Second Simulated BBH Signal
- Tests scalability to longer signals (more frequency bins)
- 4x more frequency bins than 4s signal
- **Result:** Runtime increased more than proportionally → GPU saturated
- L4 GPU must batch frequency computations, reintroducing serial dependency
- **Speedup: 37x**, cost reduction: 2.3x
- Key insight: GPU parallelism has finite limits; heterodyning can mitigate this

### Disentangling Parallelisation Sources (Section 4.3)
- **Intra-likelihood parallelisation** (GPU-native waveform/likelihood): **3.3x speedup**
- **Inter-sample parallelisation** (batched NS, k=700 simultaneous MCMC chains): **11.1x speedup**
- **Combined: 37.1x** (for the test case)
- The batched sampling architecture provides the dominant speedup, not just the GPU likelihood

## Technical Details

### The 'Acceptance-Walk' Kernel
- Mirrors bilby+dynesty's standard inner sampling method
- MCMC walk using Differential Evolution (DE) proposals
- Walk length adaptive, but tuned at batch level (not per-iteration)
- 'Delay' parameter modified for batch-level tuning

### Sampler Configuration
- n_live (GPU) ≈ 1.4 × n_live (CPU) for equivalent effective live points
- num_delete = 0.5 × n_live (the batch size)
- This accounts for the 'saw-tooth' pattern in GPU live point count

### Volume Compression Matching (Section 3.2.1)
The paper derives that n_GPU ≈ 2ln(2) × n_CPU ≈ 1.4 × n_CPU to match the expected
prior volume compression per cycle between CPU (sequential deletion) and GPU (batch deletion).

## Figures in the Paper

1. **Figure 1:** Corner plot comparison (4s signal) — bilby+dynesty vs blackjax-ns
2. **Figure 2:** Live points vs iteration — saw-tooth pattern in GPU vs constant in CPU
3. **Figure 3:** Sample weights comparison
4. **Figure 4:** Log evidence comparison (4s signal)
5. **Figure 5:** SNR distribution of 100 injections
6. **Figure 6:** Accepted steps per iteration comparison
7. **Figure 7:** PP plot (100 injections, blackjax-ns) — p-value 0.9130
8. **Figure 8:** Runtime speedup distribution (100 injections)
9. **Figure 9:** Cost reduction distribution (100 injections)
10. **Figure 10:** Log evidence difference (100 injections)
11. **Figure 11:** Corner plot (8s signal)
12. **Figure 12:** Log evidence comparison (8s signal)
- **Figure A1:** PP plot for bilby+dynesty (100 injections) — p-value 0.9213
- **Figure B1:** Internal run statistics comparison (100 injections)
- **Figure C1:** Likelihood evaluation scaling with number of particles

## What This Paper Establishes (That Our Paper Builds On)

1. **The sampler works:** blackjax-ns with acceptance-walk kernel produces statistically identical results to bilby+dynesty
2. **The speedup is real:** 20-40x wall-time, 1.5-2.5x cost reduction
3. **The speedup comes from architecture:** Hardware parallelism (GPU) enables batched sampling
4. **There are limits:** GPU saturates for long signals with many frequency bins → heterodyning helps
5. **This is a baseline:** Future GPU-native kernels may be even faster

## What This Paper Does NOT Do (That Our Paper Adds)

1. No BNS analysis (only BBH)
2. No real event analysis (only simulated signals)
3. No H_0 inference
4. No heterodyned likelihood
5. No prior sensitivity analysis
6. No cosmological science
7. No comparison at high live-point counts (only ~1000-1400)

## MNRAS Rejection Details

### Scope
- Reviewers: "falls outside MNRAS scope"
- Suggested venue: RASTI (Research and Applications of Scientific and Technological Instruments)

### Criticism 1: CPU Parallelisation Description
- Introduction inaccurately described pBilby/dynesty capabilities
- Should properly cite Bilby Zenodo record
- Should acknowledge existing CPU parallelisation

### Criticism 2: Speedup Claims
- Abstract compared against unrealistic single-core baseline
- CPU-hours and GPU-hours treated as equivalent
- Dollar cost in abstract considered unusual
- Need better context for speedup claims

### Assessment
- The "significant reservations" reduce to two fixable issues
- Review may have been written by a pBilby author (focused heavily on pBilby description)
- The core problem: paper was too conservative in demonstrating what GPU acceleration genuinely enables
