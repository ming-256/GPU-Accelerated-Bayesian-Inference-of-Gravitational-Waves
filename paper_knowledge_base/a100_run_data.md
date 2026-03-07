# A100 Run Data

All runs performed on: **NVIDIA Tesla A100** (a2-highgpu-1g, Google Cloud Workstations)

## Summary Tables

### GW170817 Heterodyned Runs (H_0 Analysis, 5000 live points, 14D, phase marginalised)

All heterodyned runs use 501 frequency bins, GWTC-1 PSDs, GWTC-1 reference parameters.
num_delete = 0.5 × n_live = 2500.

#### Run Set 1 (run_all_heterodyned.sh, 2026-02-19)

| Run | Waveform | Prior Variant | Dead Pts | log Z | σ(log Z) | Data Load | Het Setup | Init | JIT | Sampling | Total |
|-----|----------|--------------|----------|-------|----------|-----------|-----------|------|-----|----------|-------|
| baseline | IMRPhenomD_NRTidalv2 | volumetric d_L | 198,000 | 486.66 | 0.10 | 3.9s | 17.7s | 21.2s | 41.6s | 772.6s | 884.6s |
| baseline | TaylorF2 | volumetric d_L | 199,500 | 486.85 | 0.11 | 3.9s | 11.8s | 11.8s | 18.2s | 161.6s | 235.3s |
| flatZ | IMRPhenomD_NRTidalv2 | flat-in-z | 201,000 | 487.00 | 0.09 | 3.9s | 18.2s | 18.8s | 42.3s | 777.2s | 889.0s |
| flatZ | TaylorF2 | flat-in-z | 199,500 | 487.91 | 0.09 | 4.0s | 11.6s | 9.5s | 18.6s | 160.0s | 231.0s |
| vp250 | IMRPhenomD_NRTidalv2 | σ_vp=250 | 198,000 | 485.96 | 0.10 | 3.9s | 17.8s | 21.2s | 41.7s | 773.4s | 885.7s |
| vp250 | TaylorF2 | σ_vp=250 | 195,000 | 487.29 | 0.10 | 3.9s | 11.9s | 11.8s | 18.2s | 158.8s | 231.7s |

**Batch total: 3402s (~57 minutes) for all 6 runs**

#### Run Set 2 (BatchRun.py, 2026-02-22) — Repeat runs for consistency

| Run | Waveform | Prior Variant | Dead Pts | log Z | σ(log Z) | Sampling | Total |
|-----|----------|--------------|----------|-------|----------|----------|-------|
| flatZ | IMRPhenomD_NRTidalv2 | flat-in-z | 195,000 | 487.63 | 0.09 | 746.9s | 856.7s |
| flatZ | TaylorF2 | flat-in-z | 198,000 | 487.33 | 0.10 | 160.9s | 232.4s |
| vp250 | IMRPhenomD_NRTidalv2 | σ_vp=250 | 193,500 | 486.89 | 0.11 | 744.7s | 855.5s |
| vp250 | TaylorF2 | σ_vp=250 | 195,000 | 487.18 | 0.09 | 158.5s | 231.3s |
| baseline | IMRPhenomD_NRTidalv2 | volumetric d_L | 199,500 | 486.07 | 0.10 | 771.5s | 883.7s |
| baseline | TaylorF2 | volumetric d_L | 199,500 | 486.56 | 0.10 | 162.8s | 236.6s |

### GW170817 Unheterodyned Runs (1500 live points, 14D, phase marginalised)

259,201 frequency bins (full likelihood, no relative binning).

#### Host-Localised Priors (RA/Dec constrained to NGC 4993 region)

| Waveform | Dead Pts | log Z | σ(log Z) | Data Load | Init | JIT | Sampling | Total |
|----------|----------|-------|----------|-----------|------|-----|----------|-------|
| IMRPhenomD_NRTidalv2 | 45,000 | 491.65 | 0.18 | 4.0s | 18.8s | 471.4s | 19,543.1s | 20,042.0s |
| TaylorF2 | 47,250 | 490.46 | 0.18 | 4.0s | 11.7s | 157.0s | 8,437.6s | 8,615.3s |

#### Full-Sky Priors (narrow M_c/q/spin but full RA/Dec)

| Waveform | Dead Pts | log Z | σ(log Z) | Data Load | Init | JIT | Sampling | Total |
|----------|----------|-------|----------|-----------|------|-----|----------|-------|
| IMRPhenomD_NRTidalv2 | 51,750 | 485.55 | 0.21 | 3.9s | 18.3s | 319.0s | 20,128.1s | 20,474.4s |
| TaylorF2 | 51,750 | 486.74 | 0.19 | 3.9s | 11.1s | 100.2s | 5,860.9s | 5,981.2s |

#### Unheterodyned from BatchRun.py (standard constrained priors)

| Waveform | Dead Pts | log Z | σ(log Z) | JIT | Sampling | Total |
|----------|----------|-------|----------|-----|----------|-------|
| IMRPhenomD_NRTidalv2 | 42,000 | 494.66 | 0.16 | 313.2s | 15,999.6s | 16,339.4s |
| TaylorF2 | 40,500 | 496.04 | 0.17 | 101.3s | 4,511.8s | 4,632.5s |

### GW150914 Heterodyned Run (5000 live points, 10D, phase marginalised)

| Waveform | PSD Source | Dead Pts | log Z | σ(log Z) | Data Load | Het Setup | Init | JIT | Sampling | Total |
|----------|-----------|----------|-------|----------|-----------|-----------|------|-----|----------|-------|
| IMRPhenomD | gwtc2p1 | 127,500 | 260.95 | 0.08 | 3.1s | 15.5s | 16.1s | 30.2s | 171.9s | 247.6s |

## Key Performance Metrics

### Heterodyned Sampling Rates (A100)

| Waveform | Dead pts/s | Sampling Time | Frequency Bins |
|----------|-----------|---------------|----------------|
| IMRPhenomD_NRTidalv2 | ~254-259 | ~770s | 501 (het) |
| TaylorF2 | ~1220-1238 | ~160s | 442 (het) |
| IMRPhenomD (GW150914) | ~733 | ~172s | 383 (het, 2 det) |

### Unheterodyned Sampling Rates (A100)

| Waveform | Priors | Dead pts/s | Sampling Time | Frequency Bins |
|----------|--------|-----------|---------------|----------------|
| IMRPhenomD_NRTidalv2 | host-localised | ~2.3-2.8 | ~19,543s | 259,201 |
| TaylorF2 | host-localised | ~5.5-9.5 | ~8,438s | 259,201 |
| IMRPhenomD_NRTidalv2 | full-sky | ~2.3-2.8 | ~20,128s | 259,201 |
| TaylorF2 | full-sky | ~7-9.5 | ~5,861s | 259,201 |

### Heterodyning Speedup (A100, sampling time only)

| Waveform | Unheterodyned | Heterodyned | Speedup |
|----------|--------------|-------------|---------|
| IMRPhenomD_NRTidalv2 | ~16,000-20,000s | ~770s | **~21-26x** |
| TaylorF2 | ~4,500-8,400s | ~160s | **~28-53x** |

### JIT Compilation Times (A100)

| Configuration | JIT Time |
|--------------|----------|
| Heterodyned IMRPhenomD_NRTidalv2 (501 bins) | ~41s |
| Heterodyned TaylorF2 (442 bins) | ~18s |
| Heterodyned IMRPhenomD (383 bins, GW150914) | ~30s |
| Unheterodyned IMRPhenomD_NRTidalv2 (260k bins) | ~313-471s |
| Unheterodyned TaylorF2 (260k bins) | ~100-157s |

## Evidence Comparison Across Prior Variants (A100, Heterodyned)

### IMRPhenomD_NRTidalv2

| Prior | Run 1 log Z | Run 2 log Z | Run 3 log Z |
|-------|------------|------------|------------|
| baseline (volumetric) | 486.66 ± 0.10 | 486.07 ± 0.10 | — |
| flatZ (flat-in-redshift) | 487.00 ± 0.09 | 487.63 ± 0.09 | 486.47 ± 0.10 |
| vp250 (σ_vp=250) | 485.96 ± 0.10 | 486.89 ± 0.11 | 485.96 ± 0.09 |

### TaylorF2

| Prior | Run 1 log Z | Run 2 log Z | Run 3 log Z |
|-------|------------|------------|------------|
| baseline (volumetric) | 486.85 ± 0.11 | 486.56 ± 0.10 | — |
| flatZ (flat-in-redshift) | 487.91 ± 0.09 | 487.33 ± 0.10 | 487.17 ± 0.10 |
| vp250 (σ_vp=250) | 487.29 ± 0.10 | 487.18 ± 0.09 | 487.19 ± 0.09 |

## Notes on Run Configurations

- **Heterodyned runs:** n_live=5000, num_delete=2500, 501 heterodyne bins
- **Unheterodyned runs:** n_live=1500, num_delete=750, 259,201 frequency bins
- **All GW170817 runs:** 14 parameters (phase marginalised), 128s data, 3 detectors (H1, L1, V1)
- **GW150914 run:** 10 parameters (phase marginalised), 4s data(?), 2 detectors (H1, L1)
- **Data source:** local (pre-cached GWOSC data)
- **PSD source:** gwtc1 (for GW170817), gwtc2p1 (for GW150914)
- **Reference params for heterodyning:** GWTC-1 median posteriors

## Comparison: A100 vs L4 (from thesis, Table 5)

Thesis runs were on L4. The A100 runs above supersede those. For reference:

| Model | Event | L4 Runtime (thesis) | A100 Runtime (new) | A100 Speedup vs L4 |
|-------|-------|--------------------|--------------------|-------------------|
| A (het, H0, IMR_NRT) 5K live | GW170817 | ~31:26 | ~12:52 (sampling) | ~2.4x |
| baseline TaylorF2, het, 5K live | GW170817 | N/A | ~2:41 (sampling) | — |
| F (het, IMRPhenomD) 5K live | GW150914 | ~5:03 | ~2:52 (sampling) | ~1.8x |

Note: Thesis Table 5 shows Model A at 10K live points = 31:26. The A100 at 5K live points = ~13min sampling. Scaling is approximately linear, so at 10K the A100 would be ~26min, vs L4 at ~31min. The A100 advantage is more modest than the raw TFLOPS ratio would suggest because the heterodyned likelihood is already small enough to fit comfortably on the L4.

## Wall-Clock Runtime Summary for Paper

**Headline numbers (A100, heterodyned, 5000 live points):**

| Analysis | Waveform | Sampling | Total (incl. overhead) |
|----------|----------|----------|----------------------|
| GW170817 H_0 (baseline) | IMRPhenomD_NRTidalv2 | **12 min 52s** | **14 min 45s** |
| GW170817 H_0 (baseline) | TaylorF2 | **2 min 41s** | **3 min 55s** |
| GW150914 validation | IMRPhenomD | **2 min 52s** | **4 min 8s** |
| Full prior sensitivity (6 runs) | Both waveforms | — | **57 minutes total** |

**For comparison — unheterodyned on same A100:**

| Analysis | Waveform | n_live | Total |
|----------|----------|--------|-------|
| GW170817 (host-localised) | IMRPhenomD_NRTidalv2 | 1500 | **5h 34min** |
| GW170817 (host-localised) | TaylorF2 | 1500 | **2h 24min** |
| GW170817 (full-sky) | IMRPhenomD_NRTidalv2 | 1500 | **5h 41min** |
| GW170817 (full-sky) | TaylorF2 | 1500 | **1h 40min** |
