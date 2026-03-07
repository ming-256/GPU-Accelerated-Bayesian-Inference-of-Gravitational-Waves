# MNRAS Paper Strategy

## Title (Working)

"Rapid Hubble constant inference from GW170817 using GPU-accelerated nested sampling"

Alternative: "GPU-accelerated H_0 inference from GW170817: prior sensitivity and the heterodyned likelihood at scale"

## Key Principle: Science-First

The co-authored paper (Prathaban et al.) was rejected from MNRAS as a methods paper.
This paper MUST lead with astrophysics. The GPU acceleration is the enabling technology,
not the subject.

## Paper Structure (~8-10 pages MNRAS format)

### 1. Introduction (~1.5 pages)
- Hubble tension: CMB (Planck) vs distance ladder (SH0ES), 4-6σ
- Standard sirens as independent probe; GW170817 as the only bright siren
- Importance of rapid PE for multi-messenger follow-up
- Computational challenge: standard PE takes ~10,000 CPU-hours for BNS
- **Correctly describe CPU parallelisation landscape:** pBilby parallelises likelihood evaluation and can distribute across many cores. Cite Bilby Zenodo record. Our argument is about the scaling regime at high live-point counts + heterodyning, not about CPU methods being serial.
- This paper: apply GPU-accelerated nested sampling (Prathaban et al. 2025) to GW170817, perform H_0 inference, and critically re-examine prior sensitivity

### 2. Method (~1.5 pages, brief — cite Prathaban et al. for sampler details)
- Nested sampling framework (brief, cite BlackJAX, Yallup et al. 2025)
- Heterodyned (relative binning) likelihood (Cornish 2013, Zackay et al. 2018)
- Phase marginalisation
- H_0 inference: joint likelihood (GW + recession velocity + peculiar velocity)
- Prior choices: volumetric d_L, flat-in-log H_0, uniform v_p, and alternatives
- Waveform models: IMRPhenomD_NRTidalv2 and TaylorF2

### 3. Results (~4 pages) — THE CORE
#### 3.1 Pipeline Validation with GW150914
- Brief (1 paragraph + figure reference). Corner plot vs GWTC-2.1. Cite Prathaban et al. for detailed BBH validation.

#### 3.2 GW170817 Parameter Estimation
- Corner plots comparing to LVK (IMRPhenomPv2_NRTidal) posteriors
- Show both IMRPhenomD_NRTidalv2 and TaylorF2 results
- Discuss waveform systematics (minor differences expected, quantify)

#### 3.3 H_0 Inference
- **Baseline H_0 posterior** reproducing Abbott et al. (2017b)
- Comparison with Planck and SH0ES bands
- Consistency check: joint H_0 sampling does not perturb GW source parameters

#### 3.4 Prior Sensitivity Analysis (FLAGSHIP SCIENTIFIC RESULT)
- **Reweighting reproduction:** Replicate Abbott et al. (2017b) reweighting approach, show it matches their result
- **Direct sampling critique:** Direct sampling under flat-in-z prior reveals materially different H_0 posterior
  - Broader distribution, more probability mass at high H_0
  - Reweighting fails due to poor sample coverage at low d_L
  - Illustrate with d_L marginal comparison (directly sampled vs reweighted)
- **Peculiar velocity sensitivity:** σ_vp = 250 km/s — quantify shift
- **Bayesian evidence comparison:** Table of log Z for all models
- **Key conclusion:** The H_0 measurement is more sensitive to the distance prior choice than previously reported. Fast inference pipelines enable robust sensitivity analysis via direct simulation rather than post-processing.

#### 3.5 Waveform Systematics
- Compare H_0 from IMRPhenomD_NRTidalv2 vs TaylorF2
- Quantify systematic shift relative to statistical uncertainty

#### 3.6 Computational Performance
- **Like-for-like comparison table:** Heterodyned A100 vs pBilby on CSD3 (when available)
  - Same waveform, same priors, same n_live
  - Report wall-clock time and (if appropriate) cost
- **Scaling study:** Runtime vs n_live (500, 1000, 2500, 5000, optionally higher)
- **Heterodyning impact:** Unheterodyned vs heterodyned on same A100
- **Headline:** At 5000 live points with heterodyning, complete H_0 analysis in ~13 minutes
- **DO NOT** compare against single-core baseline
- **DO NOT** put dollar costs in abstract

### 4. Discussion (~1 page)
- Implications for prior sensitivity in future bright siren analyses
- Scalability to 3G detectors (longer signals, higher SNR, more events)
- Limitations: waveform model availability in Ripple, aligned-spin assumption
- Future: population analyses, dark sirens, multi-event H_0

### 5. Conclusions (~0.5 pages)

## Abstract Framing

The abstract should follow this structure:
1. Context: H_0 tension, bright sirens, GW170817
2. What we did: GPU-accelerated nested sampling with heterodyned likelihood for GW170817 H_0
3. Validation: Reproduce LVK H_0 result
4. Scientific result: Prior sensitivity — direct sampling reveals reweighting limitation
5. Technical result: "We perform a careful like-for-like comparison with standard CPU methods and achieve consistent results at comparable cost. When the heterodyned likelihood is used at scale (5000 live points), we complete the full H_0 analysis in ~13 minutes on a single A100 GPU — a regime that is not tractable with current CPU methods and will become increasingly relevant as GPU hardware continues to improve."

## Results Still Needed

### Essential (already have or can produce from existing data)
- [x] GW170817 H_0 posterior (baseline) — have multiple A100 runs
- [x] Prior sensitivity: flatZ sampled vs reweighted — have A100 runs
- [x] Prior sensitivity: vp250 — have A100 runs
- [x] Bayesian evidence table — have from multiple runs
- [x] GW150914 validation corner plot — have A100 run
- [x] Heterodyned vs unheterodyned comparison — have A100 data
- [x] Both waveforms (IMRPhenomD_NRTidalv2 and TaylorF2) — have both

### Needed (new computations)
- [ ] **Scaling study:** Run at n_live = {500, 1000, 2500, 5000, 10000} on A100, measure runtime
- [ ] **pBilby reference run:** Same GW170817 configuration on CSD3 CPU cluster
- [ ] **Posterior convergence plot:** H_0 posterior as function of n_live (shows convergence)
- [ ] Updated plots from A100 results (repo plotting scripts should handle this)

### Nice-to-have
- [ ] Small BNS injection study (5-10 events) with PP plot
- [ ] Likelihood evaluation scaling plot (like Fig C1 in co-authored paper, but for A100)

## Differentiation from Co-authored Paper

| Aspect | Prathaban et al. | This paper |
|--------|-----------------|------------|
| System | BBH (simulated) | BNS (real: GW170817) |
| Science | Pipeline validation, benchmarking | H_0 inference, prior sensitivity |
| Likelihood | Standard frequency-domain | Heterodyned (relative binning) |
| Live points | ~1000-1400 | Up to ~5000+ |
| Waveform | IMRPhenomD | IMRPhenomD_NRTidalv2, TaylorF2 |
| Parameters | 11D BBH | 14-15D BNS + H_0 + v_p |
| Key result | Functionally equivalent to Bilby | Prior reweighting critique + extreme scaling |
| MNRAS scope | Methods (rejected as out-of-scope) | Astrophysics enabled by methods |
| Hardware | L4 GPU | A100 GPU |

## Key References to Cite

- Abbott et al. 2017b (Nature 551, 85) — original GW170817 H_0 measurement
- Abbott et al. 2017a (PRL 119, 161101) — GW170817 discovery
- Prathaban et al. 2025 (arXiv:2509.04336) — the co-authored sampler paper
- Yallup et al. 2025 — BlackJAX nested sampling
- Edwards et al. 2023 — Ripple waveform library
- Wong et al. 2023 — Jim GW inference library
- Cornish 2013, Zackay et al. 2018 — heterodyning/relative binning
- Hu & Veitch 2024/2025 — costs of PE in 3G era
- Krishna et al. 2023 — accelerated PE with relative binning in Bilby
