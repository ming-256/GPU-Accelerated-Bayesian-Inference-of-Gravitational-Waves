# Literature Review: GPU-Accelerated GW Inference (2024-2026)

## Direct Competitors / Comparators

### Jim (JAX-based GPU MCMC for GW)
- **Wouters+2024** (arXiv:2404.11397, PRD 110, 083033)
  - GW170817 BNS with IMRPhenomD_NRTidalv2: **33 min** on GPU (flowMC + relative binning)
  - GW170817 with TaylorF2: **26 min** on GPU
  - Our result: **13 min** (IMR_NRTv2) and **2.7 min** (TF2) — 2-10x faster
  - Key difference: Jim uses MCMC, we use nested sampling (get evidence for free)
  - Jim does NOT provide Bayesian evidence — this is our advantage

- **Polanska+2024** (arXiv:2410.21076, NeurIPS ML4PS)
  - Jim + learned harmonic mean for evidence estimation
  - 5-15x speedup over nested sampling on 16 CPU cores
  - But still does not match GPU nested sampling throughput

### Nested Slice Sampling (Companion papers from our group)
- **Yallup+2025** (arXiv:2509.24949) — GPU nested slice sampling for GW
  - ~100x speedup over CPU bilby with high ESS
  - Uses blackjax-ns (same framework as us)
  - Compared favourably with flowMC

- **Yallup+2026** (arXiv:2601.23252) — NSS algorithm paper
  - Formalises the vectorized nested slice sampling algorithm
  - Simple near-optimal tuning rule for slice width

### Relative Binning / Heterodyned Likelihood
- **Krishna+2023** (arXiv:2312.06009) — Relative binning in bilby
  - GW170817 in **14 hours on 1 CPU core** with relative binning
  - Relevant as the CPU+relative-binning baseline
  - Our comparison: 13 min on 1 GPU vs 14h on 1 CPU = ~65x speedup

- **Cornish 2021** (arXiv:2109.02728, PRD 104) — Original heterodyned likelihood
  - 2-4 orders of magnitude speedup depending on system mass
  - Foundation reference for our approach

- **Narola+2024** (arXiv:2308.12140, PRD 110) — Relative binning with HOM + precession
  - Extends to higher-order modes by binning each mode individually
  - Important for next-gen detectors; bin counts increase with HOM
  - For our aligned-spin BNS case, standard binning is sufficient

## H_0 from GW170817: Latest Results

- **Palmese+2024** (arXiv:2305.19914, PRD 109)
  - Updated bright siren: H_0 = 75.5 +5.3/-5.4 (7% precision)
  - Uses afterglow observations to improve inclination constraint

- **LVK GWTC-4.0 Cosmology** (arXiv:2509.04348, 2025)
  - O4a results: H_0 = 76.6 +13.0/-9.5 (dark + bright sirens combined)
  - GW170817 remains single most informative event

- **Borghi+2024** (arXiv:2404.16092, MNRAS 535)
  - Dark sirens: H_0 = 70.4 +13.6/-11.7
  - Combining 15 dark sirens + GW170817 reduces uncertainty by ~40%

## State-of-the-Art BNS Waveforms

- **NRTidalv3** — Abac+2024 (arXiv:2311.07456, PRD 109)
  - Improves on NRTidalv2: larger NR dataset, high mass ratio, dynamical tides
  - GW170817 PE results **consistent with NRTidalv2**
  - Available as IMRPhenomXAS_NRTidalv3 and SEOBNRv5_ROM_NRTidalv3

- **NRTidalv3 + HOM** — Abac+2025 (arXiv:2507.15426)
  - Higher-order mode corrections on tidal phase
  - Important for next-gen detectors

- **SEOBNRv5** family — Pompili+2023 (arXiv:2303.18039)
  - New foundation for EOB waveforms, tidal extensions available

**Implication:** Our use of IMRPhenomD_NRTidalv2 is appropriate. NRTidalv3 yields
consistent GW170817 results. Note in paper that v3 exists and gives consistent results.

## Other GPU/Alternative Samplers

- **Beta-flows acceleration** — Prathaban+2024 (arXiv:2411.17663, MNRAS 541)
  - Reduces likelihood evaluations by ~10x via prior repartitioning
  - Applicable on top of any nested sampler

- **Costless correction** — Prathaban+2024 (arXiv:2404.16428, MNRAS 533)
  - Corrects chain-based nested sampling uncertainty at no extra cost

- **JAXNS** — Albert 2020 (arXiv:2012.15286)
  - Pure-JAX nested sampler, orders of magnitude faster than CPU alternatives
  - Not applied to GW but relevant GPU NS implementation

- **pocomc/SMC** — Williams+2025 (arXiv:2506.18977, MNRAS 543)
  - Sequential Monte Carlo for GW, 2.7x faster than NS on CPU
  - Relevant alternative sampler but CPU-only

## Key Positioning for Our Paper

1. **Fastest BNS H_0 inference:** 13 min vs Jim's 33 min (both GPU, same waveform)
2. **Evidence for free:** Unlike Jim/flowMC, nested sampling provides log Z directly
3. **Prior sensitivity gap:** No dedicated study exists — our contribution is novel
4. **Waveform robustness:** NRTidalv2 gives consistent results with v3
5. **Regime demonstration:** 5000+ live points is intractable on CPUs
