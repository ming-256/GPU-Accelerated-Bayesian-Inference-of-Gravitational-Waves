# Project Context

## Overview

This project develops and applies a GPU-accelerated Bayesian inference pipeline for
gravitational wave (GW) parameter estimation, with the primary scientific goal of
inferring the Hubble constant (H_0) from the bright siren event GW170817.

The pipeline is built on:
- **JAX** (Google's autodiff/XLA framework) for GPU execution
- **BlackJAX** nested sampling (vectorized nested slice sampling, Yallup et al. 2025)
- **Ripple** (Edwards et al. 2023) for JAX-native waveform generation
- Components adapted from **Jim** (Wong et al. 2023) for detector data handling

## Relationship Between Documents

### Master's Thesis (Final_Report-1.pdf)
- **Title:** "GPU-Accelerated Gravitational Wave Parameter Estimation and Hubble Constant Inference"
- **Author:** Ming Yang, St. John's College, Cambridge
- **Date:** November 23, 2025
- **Status:** SUPERSEDED — all results have been redone on A100 hardware with improved scripts
- **Value:** Contains the methodology, theoretical framework, and analysis structure that the paper will build on
- **Hardware:** NVIDIA L4 Tensor Core GPU (Google Cloud) for JAX runs; CSD3 Ice Lake CPUs for Bilby
- **Key thesis results (now superseded but structurally informative):**
  - H_0,JAX = 70.4 +14.9/-6.5 km/s/Mpc (MAP, 68.3% CI) — matches LVK H_0 = 70.0 +12.0/-8.0
  - Prior sensitivity: direct sampling under flat-in-z prior reveals broader H_0 posterior than reweighting suggests
  - Heterodyning speedup: 22x for GW150914, 900x for GW170817 (relative to unheterodyned JAX)
  - Raw GPU vs single-core CPU: ~32x speedup on L4

### Co-authored Paper (2509.04336v1.pdf)
- **Title:** "Gravitational-wave inference at GPU speed: A bilby-like nested sampling kernel within blackjax-ns"
- **Authors:** Metha Prathaban, David Yallup, James Alvey, Ming Yang, Will Templeton, Will Handley
- **Date:** September 5, 2025
- **Status:** Submitted to MNRAS, REJECTED on scope grounds (reviewers suggested RASTI)
- **Focus:** BBH (binary black hole) analyses — simulated 4s and 8s signals
- **Key results:**
  - Functionally equivalent posteriors to bilby+dynesty (validated via PP plots, 100-injection study)
  - 20-40x wall-time speedups, 1.5-2.5x cost reductions on L4 GPU
  - Disentangled intra-likelihood vs inter-sample parallelisation (3.3x vs 11.1x)
- **Relationship to this paper:** Introduces the sampler and GPU framework for BBH. This paper extends to BNS (GW170817) and adds H_0 science.

### This Paper (to be written)
- **Target:** MNRAS
- **Focus:** Application of the GPU framework to BNS (GW170817), H_0 inference, prior sensitivity analysis
- **Differentiation from co-authored paper:** Science-first (H_0, prior critique), not methods-first
- **Hardware:** NVIDIA A100 (a2-highgpu-1g, Google Cloud)

## The GW170817 Event

- **Date:** August 17, 2017
- **Type:** Binary neutron star (BNS) merger
- **Detectors:** LIGO-Hanford (H1), LIGO-Livingston (L1), Virgo (V1)
- **EM counterpart:** GRB 170817A (gamma-ray burst, 1.7s after merger), kilonova AT 2017gfo in NGC 4993
- **Host galaxy:** NGC 4993, redshift z = 0.00980 ± 0.00079
- **Recessional velocity:** v_r = 3327 ± 72 km/s (CMB frame, from 2MASS)
- **Peculiar velocity estimate:** <v_p> = 310 ± 150 km/s (Carrick et al. 2015)
- **LVK H_0 result:** 70.0 +12.0/-8.0 km/s/Mpc (Abbott et al. 2017b, Nature 551, 85)
- **Significance:** Only confirmed bright siren to date; first standard siren H_0 measurement

## The Hubble Tension (Context)

- **Planck (CMB, early universe):** H_0 = 67.4 ± 0.5 km/s/Mpc (Ade et al. 2016)
- **SH0ES (SNe, late universe):** H_0 = 73.04 ± 1.04 km/s/Mpc (Riess et al. 2016, 2022)
- **Tension:** 4-6σ disagreement
- **GW170817 H_0:** Consistent with both, but uncertainty too large to discriminate
- **Future:** Population of bright sirens from 3G detectors could resolve the tension

## H_0 Inference Methodology

The H_0 is inferred by jointly fitting GW source parameters and cosmological parameters:

**Combined likelihood (Equation 9 in thesis):**
```
ln L_total = ln L_xGW + ln L_vr + ln L_<vp>
```

Where:
- L_xGW = P(x_GW | d_L, cos ι, λ̄) — standard GW likelihood
- L_vr = N[v_p + H_0*d_L, σ²_vr](v_r) — recession velocity likelihood
- L_<vp> = N[v_p, σ²_vp](<v_p>) — peculiar velocity likelihood

**Priors (following Abbott et al. 2017b):**
- d_L: volumetric, π(d_L) ∝ d²_L, range [10, 75] Mpc
- H_0: flat-in-log, π(H_0) ∝ 1/H_0, range [45, 250] km/s/Mpc
- v_p: flat (uniform), range [-1000, 1000] km/s
- cos ι: uniform on [-1, 1]

**Key innovation:** Direct joint sampling of H_0 and v_p alongside GW parameters (vs LVK two-step approach of PE then post-processing).

## Prior Sensitivity Analysis

Abbott et al. (2017b) tested two alternative assumptions:
1. Flat-in-redshift prior: π(z) = const, instead of volumetric π(d_L) ∝ d²_L
2. Increased peculiar velocity uncertainty: σ_vp = 250 km/s instead of 150 km/s

They concluded both had <1σ impact on H_0. However:
- They implemented the flat-in-z prior via **reweighting** existing volumetric-prior samples
- Reweighting fails when the target prior up-weights regions with poor sample coverage
- The volumetric prior produces few samples at low d_L (high H_0), exactly where the flat-in-z prior has more weight
- **Our direct sampling under flat-in-z** reveals a materially broader H_0 posterior with more probability mass at high H_0
- This is the key scientific contribution of this paper

## Waveform Models Used

| Model | Type | Features | Used for |
|-------|------|----------|----------|
| IMRPhenomD | BBH aligned-spin | No precession, no tides | GW150914 validation |
| IMRPhenomD_NRTidalv2 | BNS aligned-spin + tidal | Tidal deformability (Λ₁, Λ₂) | GW170817 primary |
| TaylorF2 | PN inspiral-only | Tidal effects via PN expansion | GW170817 cross-check |
| IMRPhenomPv2_NRTidal | BNS precessing + tidal | Full precession | LVK reference (not in Ripple) |

Note: Ripple does not yet support precessing BNS waveforms. The aligned-spin assumption is justified for GW170817 given its low effective precession parameter.
