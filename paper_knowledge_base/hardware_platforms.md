# Hardware Platforms and Cost Reference

## GPU Hardware

### NVIDIA Tesla A100 (Current Production Hardware)
- **Cloud instance:** Google Cloud a2-highgpu-1g
- **GPU Memory:** 40 GB HBM2e (or 80 GB variant)
- **FP64 Performance:** 9.7 TFLOPS
- **FP32 Performance:** 19.5 TFLOPS
- **Memory Bandwidth:** 1,555 GB/s (40GB) or 2,039 GB/s (80GB)
- **Used for:** All current (2026) production runs in the GitHub repository

### NVIDIA L4 Tensor Core GPU (Thesis Hardware)
- **Cloud instance:** Google Cloud g2-standard-4 (or similar)
- **GPU Memory:** 24 GB GDDR6
- **FP32 Performance:** 30.3 TFLOPS (with sparsity)
- **Memory Bandwidth:** 300 GB/s
- **Used for:** All runs reported in the master's thesis (Final_Report)
- **Also used in:** Co-authored paper (Prathaban et al.) for blackjax-ns runs
- **Note:** L4 is an inference-optimised GPU; the A100 is a compute-optimised GPU. The A100 has much higher memory bandwidth, which matters for the unheterodyned likelihood where the frequency array is large.

### NVIDIA H100 (Reference, not used)
- **Cloud instance:** Google Cloud a3-highgpu-1g
- **GPU Memory:** 80 GB HBM3
- **FP64 Performance:** 34 TFLOPS
- **Memory Bandwidth:** 3,350 GB/s
- **Relevance:** Future work; would provide ~3x improvement over A100 in memory-bandwidth-limited regime

## CPU Hardware

### CSD3 (Cambridge Service for Data Driven Discovery)
- **Operator:** University of Cambridge Research Computing
- **CPU nodes:** Intel Xeon Ice Lake (Icelake partition)
- **Cores per node:** 76 (used in thesis Bilby runs)
- **RAM per core:** ~3.3 GiB
- **Used for:** All Bilby/CPU reference runs in the thesis
- **Allocation:** DiRAC (Distributed Research utilising Advanced Computing)
  - Service Level 3: 200,000 CPU core hours per quarter, 3,000 GPU hours per quarter
  - GPU hours are considered ~67x scarcer than CPU core hours
  - GPUs are 4.4x more expensive per PetaFlop-hour than CPUs

### CSD3 Comparison Points
- **4,256 cores** = approximate limit for a single CSD3 job allocation
  - This is a meaningful comparison: "at 5000 live points with heterodyning, a single A100 achieves in 13 minutes what would require [X] on CSD3"
- **532 MPI ranks** = configuration used in parallel_bilby scripts (7 nodes × 76 cores)
  - NODES=7, CORES_PER_NODE=76 (from parallel_bilby/config.sh)

## Google Cloud Pricing (Reference, as of April 2024 — from thesis Table 3)

### CPU Instances (C2 family, proxy for CSD3 Ice Lake)

| Config | vCPUs | RAM/vCPU | 1-Month | 1-Year | 3-Year |
|--------|-------|----------|---------|--------|--------|
| C2 (small) | 60 | 4 GiB | $2,288 | $1,442 | $916 |
| C2 (large, ~CSD3 node) | 480 | 4 GiB | $14,591 | $11,523 | $7,317 |

### GPU Instances

| GPU | vCPUs | RAM/vCPU | 1-Month | 1-Year | 3-Year |
|-----|-------|----------|---------|--------|--------|
| L4 | 4 | 4 GiB | $520 | $325 | $232 |
| A100 | 12 | 7.1 GiB | $2,682 | $1,689 | $939 |
| H100 | 26 | 9 GiB | $8,075 | $5,601 | $3,546 |

**Note:** GPU prices are for GPU accelerator only; a small additional CPU/RAM instance is needed.

### Hourly Rates (approximate, for cost-per-analysis comparisons)

| Resource | ~Hourly Rate (on-demand) | ~Hourly Rate (1-yr committed) |
|----------|-------------------------|------------------------------|
| C2 60-vCPU | ~$3.18 | ~$2.00 |
| L4 GPU | ~$0.72 | ~$0.45 |
| A100 GPU | ~$3.73 | ~$2.35 |

**Caveat:** Prices fluctuate and should be date-stamped in the paper. These are from April 2024. The paper should use the rates current at the time of computation.

## Cost Analysis Framework

### For the paper, present costs as follows:
1. **Wall-clock runtime** on specified hardware (static, reproducible)
2. **Hardware cost** at commercial on-demand rates (date-stamped, with caveat)
3. **Academic allocation equivalent** (DiRAC units, if meaningful)

### DO NOT:
- Put dollar costs in the abstract
- Compare GPU-hours to CPU-hours as equivalent units
- Compare against single-core CPU baseline

### Key comparison to make:
- pBilby on CSD3 (532 cores, N nodes) vs blackjax-ns on A100 (1 GPU)
- Same analysis configuration (waveform, priors, n_live)
- Report: wall-clock time, total compute-hours, approximate cost

## Cost Per Analysis (Estimated from A100 Runs)

### Heterodyned GW170817 H_0 (IMRPhenomD_NRTidalv2, 5000 live, A100)
- Wall-clock: ~15 min total
- A100 hourly rate: ~$3.73 (on-demand)
- **Cost: ~$0.93**

### Heterodyned GW170817 H_0 (TaylorF2, 5000 live, A100)
- Wall-clock: ~4 min total
- **Cost: ~$0.25**

### Full prior sensitivity suite (6 heterodyned runs, A100)
- Wall-clock: ~57 min total
- **Cost: ~$3.55**

### Unheterodyned GW170817 (IMRPhenomD_NRTidalv2, 1500 live, A100)
- Wall-clock: ~5.5 hours
- **Cost: ~$20.50**

### Reference Bilby Runs on CSD3 (Thesis-era, standard bilby, NOT pBilby)

These are the original CPU comparison points from the thesis. They used **standard bilby** (not
parallel_bilby) on CSD3 Ice Lake nodes with MPI parallelisation. Phase marginalisation was enabled.
The exact prior/waveform configuration has been lost, but these were GW170817 runs with constrained priors.

| n_live | Cores | Wall-Clock | Notes |
|--------|-------|------------|-------|
| 1,216 | 456 | 4h 37m 32s | Standard bilby, CSD3 |
| ~1,000–10,000 | — | 1h 18m 39s | Entry "10" pts — likely a typo (probably 1000 or 10000) |
| 1,596 | 532 | 3h 49m 17s | Standard bilby, CSD3 |

**Caveats:**
- These are NOT pBilby runs — they used standard bilby with MPI likelihood parallelisation
- The "10 live points" entry is almost certainly a typo (1,000 or 10,000 is plausible given the runtime)
- Exact waveform not recorded but likely IMRPhenomPv2_NRTidal (bilby default at the time)
- These serve as rough reference points only; the pBilby comparison runs (planned) will be the proper CPU baseline

### For comparison — pBilby on CSD3 (PENDING, to be filled in after pBilby runs)
- Wall-clock: TBD
- Core-hours: TBD
- Equivalent cloud cost: TBD

## Scaling Analysis Summary

### GPU Saturation for Heterodyned Likelihood

The heterodyned likelihood uses only ~500 frequency bins, which is small enough to saturate on the
GPU at relatively low live-point counts. The GPU parallelism is across both:
1. **Intra-likelihood** (frequency bins per waveform evaluation)
2. **Inter-sample** (num_delete simultaneous MCMC chains)

With only ~500 bins, the intra-likelihood parallelism saturates quickly. The inter-sample
parallelism (num_delete = 0.5 × n_live) becomes the dominant factor.

### Scaling Behaviour (from L4 thesis data)

| n_live | Runtime/K live pts | Regime |
|--------|-------------------|--------|
| 2,500 | 3:22 | GPU saturated — entering linear regime |
| 7,500 | 3:01 | Linear |
| 10,000 | 3:09 | Linear |
| 15,000 | 3:02 | Linear |

**Key finding:** For n_live ≥ ~2,500 (heterodyned, IMRPhenomD_NRTidalv2), runtime scales linearly
with n_live. The GPU overhead (JIT, data loading) is amortised. Below ~2,000 live points, the GPU
is underutilised and runtime-per-live-point is higher.

### Implication for Paper
The linear scaling means that at high live-point counts (e.g., 10,000+), the GPU advantage grows:
a CPU cluster would need proportionally more cores or wall-clock time, while the GPU simply
takes proportionally longer on the same single card. This is the regime where GPU is unambiguously
superior — and the regime that CPU clusters cannot easily reach.
