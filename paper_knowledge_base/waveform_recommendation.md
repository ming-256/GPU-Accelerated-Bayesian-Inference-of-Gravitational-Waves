# Waveform Choice for pBilby Comparison

## Recommendation: IMRPhenomD_NRTidalv2

### Rationale

1. **Scientific relevance:** IMRPhenomD_NRTidalv2 includes tidal effects, which are the
   physically meaningful contribution for BNS events. TaylorF2 is a PN-only inspiral model
   that lacks merger/ringdown. For a science paper on GW170817 (a BNS event), the tidal
   waveform is the more defensible choice.

2. **Closer to LVK reference:** Abbott et al. (2017b) used IMRPhenomPv2_NRTidal. Our
   IMRPhenomD_NRTidalv2 is the aligned-spin, non-precessing version of the same tidal model
   family. This makes posterior comparison more meaningful. TaylorF2 is a fundamentally
   different approximant (PN inspiral-only, no tidal corrections in our implementation).

3. **Performance narrative is stronger:** IMRPhenomD_NRTidalv2 takes ~13 minutes on A100
   (vs ~2.7 min for TaylorF2). The comparison against Bilby/pBilby is more impressive when
   the waveform is the more expensive one — if the GPU handles the harder waveform in 13
   minutes, that's a stronger statement than handling the easy waveform in 3 minutes.

4. **Runtime is still compelling:** 13 minutes for a full 14D H_0 analysis with 5000 live
   points is well within the "interactive" regime. No need to cherry-pick the faster waveform.

5. **TaylorF2 can still be shown:** Present TaylorF2 as a waveform systematics check
   (different approximant gives consistent H_0), not as the primary analysis. This adds
   scientific value without requiring a pBilby comparison.

### What to Run on pBilby

- **Waveform:** IMRPhenomD_NRTidalv2
- **n_live:** Match what's feasible on CSD3 allocation (~1000–2000, constrained by core-hours)
- **Priors:** Constrained (host-localised), matching the blackjax-ns baseline
- **Phase marginalisation:** Enabled (bilby supports this natively)
- **Script:** `parallel_bilby/GW170817/GW170817_IMRPhenomD_NRTidalv2.ini`
- **Config:** 7 nodes × 76 cores = 532 MPI ranks

### Comparison Strategy

| Metric | blackjax-ns (A100) | pBilby (CSD3) |
|--------|-------------------|---------------|
| n_live | 5000 (or match pBilby) | 1000–2000 |
| Wall-clock | ~13 min (5K) | TBD (hours) |
| Hardware | 1 × A100 GPU | 7 × 76-core nodes |
| Core-hours | 0.22 GPU-hours | ~500+ CPU core-hours |
| Cost (on-demand) | ~$0.93 | ~$25+ (at C2 rates) |

Show BOTH:
1. At matched n_live: GPU is N× faster in wall-clock
2. At matched wall-clock: GPU achieves M× more live points (better posterior resolution)
