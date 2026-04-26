# Waveform recommendation (Ripple inventory, 2026-04-25)

Ripple supports the following waveform models:

```
TaylorF2
IMRPhenomD                IMRPhenomXAS
IMRPhenomD_NRTidalv2      IMRPhenomXAS_NRTidalv3
IMRPhenomPv2              IMRPhenomXPHM (MSA)
```

**Critical constraint:** the only tidal models are aligned-spin (NRTidalv2, NRTidalv3 attach to D and XAS bases). The only precessing models (Pv2, XPHM) are BBH and have no tides. **There is no precessing tidal waveform in Ripple.**

---

## GW150914 (BBH validation)

**Recommendation: `IMRPhenomXPHM`** (precessing + higher modes, MSA approximation).

- LVK GWTC-2.1+ production waveform for GW150914.
- Includes precession (multi-spin via Multi-Scale Analysis) and the (2,1), (3,3), (3,2), (4,4) higher-order modes.
- Built on the IMRPhenomXAS aligned-spin base.

The current paper's IMRPhenomD validation gives a $d_L$ posterior peaked ~30 Mpc below the LVK reference ($\sim 380$ Mpc vs $\sim 410$ Mpc). XPHM is the canonical fix and the analysis becomes a direct LVK reproduction rather than "close but offset".

Cost: $\sim 8$ min on A100 with $n_{\rm live}=5000$ (slightly higher than the IMRPhenomD baseline of 4 min because XPHM has extra spin parameters and higher-mode terms).

---

## GW170817 (BNS science target)

The trade-off is unavoidable: **tides vs precession**, pick one per waveform. For a BNS this should be **tides on the primary** plus a precession-only systematic.

### Tier 1 — primary (run all three prior variants: baseline, flatZ, vp250)

**`IMRPhenomXAS_NRTidalv3`**

- **Tides:** NRTidalv3 is the most recent NR-calibrated tidal phase prescription, behaves better at high frequency than NRTidalv2.
- **Base:** IMRPhenomXAS is a strict upgrade of IMRPhenomD — better calibration to NR over the full mass-ratio and aligned-spin range.
- **Aligned-spin only.** No precession.

This is the strict scientific upgrade over the current `IMRPhenomD_NRTidalv2` primary. The sampler parameter set and prior are identical to the current run, so no extra prior work is needed.

### Tier 2 — precession-only systematic (baseline + flatZ)

**`IMRPhenomPv2`** (BBH precessing, **no tides**)

- This deliberately **drops tidal information** to bracket precession's effect on the $H_0$ inference.
- Use a **low-spin prior** consistent with `Abbott2017H0`: spin magnitudes uniform in $[0, 0.05]$, tilts isotropic, azimuths uniform in $[0, 2\pi]$. Tidal deformabilities are not sampled for this waveform.
- Requires 4 extra in-plane spin parameters in the sampler — small code change (see `CODE_CHANGES_NEEDED.md` §2).
- **Reading the result:** if the IMRPhenomPv2 $H_0$ posterior is close to `IMRPhenomD_NRTidalv2` baseline (which is the real benchmark, since Pv2 lacks tides), precession has a sub-statistical effect on $H_0$ for GW170817. If it is materially different, you have a precession-vs-tides ambiguity that cannot be resolved without a precessing tidal waveform.

### Tier 3 — keep as cross-checks

- **`IMRPhenomD_NRTidalv2`** — keep as anchor. The current paper figures are built around this; do not delete.
- **`TaylorF2`** — keep as the waveform-family check.

### Skip

- **`IMRPhenomXPHM` on GW170817** — adds higher modes on top of Pv2's precession, but still lacks tides. For GW170817's near-equal-mass BNS, higher-mode contribution is small; the marginal value over Pv2 alone does not justify the GPU time. Run only if Tier-2 leaves the precession question open.

---

## Honest framing for the paper

The "best available" GW170817 waveform suite under the Ripple constraint is:

| Waveform | Role | Tides | Precession | HOM |
|---|---|:---:|:---:|:---:|
| IMRPhenomXAS_NRTidalv3 | primary upgrade | ✓ | — | — |
| IMRPhenomD_NRTidalv2 | back-compat anchor | ✓ | — | — |
| IMRPhenomPv2 | precession systematic | — | ✓ | — |
| TaylorF2 | waveform-family check | — | — | — |

The manuscript discussion-section limitation should be stated as:

> "Ripple does not currently expose a precessing tidal waveform; we therefore cannot run a like-for-like reproduction of the LVK bright-siren analysis (which used IMRPhenomPv2_NRTidal). We instead bracket the relevant systematics with two complementary models: IMRPhenomXAS_NRTidalv3 includes the most recent NR-calibrated tides on a modern aligned-spin base, and IMRPhenomPv2 includes precession but lacks tides. The agreement of $H_0$ posteriors across these waveforms quantifies the residual waveform systematic for our analysis."

This frames the constraint as a clear statement rather than an apology, and turns it into a scientific result (the cross-check itself).
