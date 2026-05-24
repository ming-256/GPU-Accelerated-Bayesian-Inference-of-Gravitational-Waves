# Draft response to referee concern M3 (mass prior)

**Status:** draft, 2026-05-18. All numbers are final — both headline runs on
the LVK-matched prior already existed; no new run was needed.

## What the referee wrote (M3)

> Central result uses a physically implausible mass prior. §4.1 uses
> "default-mass" = component masses uniform [0.5,7.7] M_sun (not a BNS range).
> §4.3 uses LVK-bounds [0.87,1.74] M_sun "matching Abbott2017H0". [...] The
> headline uses the prior set with the smallest baseline tail. Fix: run the
> four-variant comparison on the LVK-bounds prior and make it the headline, or
> rigorously justify the [0.5,7.7] M_sun baseline.

## Our response

We thank the referee for pressing on the mass prior. Acting on this comment we
traced both prior sets to source and found that the manuscript had the two
sets **mislabelled**, in a way that inverts the referee's recommendation. We
have corrected this throughout the revised manuscript.

1. **The [0.5, 7.7] M_sun set is the genuine LVK prior, not an implausible
   choice.** It is the exact component-mass prior used by the LVK GW170817
   parameter estimation. Abbott et al. (2019), *Properties of the binary
   neutron star merger GW170817*, PRX 9, 011001, Sec. III D, state: "we assume
   a prior PDF p(ϑ) uniform in the detector-frame masses, with the constraint
   that 0.5 M_sun ≤ m1_det, m2_det ≤ 7.7 M_sun [...] and [...] 1.184 M_sun ≤
   Mc_det ≤ 2.168 M_sun." Our pipeline uses exactly these bounds (component
   masses [0.5, 7.7] M_sun, chirp-mass constraint [1.184, 2.168] M_sun). The
   same paper notes these limits "were chosen [...] for technical reasons" and
   that "the posterior does not have support near those limits" — i.e. the wide
   range is deliberate and the posterior is unaffected by it.

2. **The [0.87, 1.74] M_sun set matches no published LVK prior.** The
   manuscript's earlier claim that it was "matching Abbott2017H0" was incorrect:
   the Abbott et al. (2017) Hubble-constant paper (Nature 551, 85) sets no
   component-mass prior at all — it marginalises over every source parameter
   except distance and inclination (its Eq. 2) and inherits posterior samples
   from the GW170817 PE. The [0.87, 1.74] range is a constructed [m, 2m]
   interval and has been removed from the analysis as an LVK reproduction.

3. **The headline now uses the genuine LVK prior.** We have moved the
   cross-waveform GW170817 H0 result (§4.3, Table 4, Figs 2-3) onto the
   [0.5, 7.7] M_sun LVK-matched prior, so that §4.1 and §4.3 use one and the
   same prior — the LVK PE prior — throughout. Both headline runs already
   existed on this prior, so no new sampling was required. The
   IMRPhenomXAS_NRTidalv3 row is now identical to the §4.1 baseline run
   (MAP 70.5, 68% HPD [63.8, 87.6], 95% HPD [59.4, 111.3], P(H0>120) = 0.017,
   lnZ = 486.25 ± 0.11); the TaylorF2 family-check row is MAP 68.5, 68% HPD
   [61.4, 89.3], 95% HPD [56.9, 125.6], P(H0>120) = 0.065, lnZ = 487.25 ± 0.09.
   The central reweighting result of §4.1 was already computed on this prior and
   is therefore unchanged.

4. The terms "default-mass" and "LVK-bounds" have been removed; the manuscript
   now refers to a single "LVK-matched prior" and cites Abbott et al. (2019) for
   it. The supporting note `test_suite/DATA_EQUIVALENCE.md` has been corrected.

We note this resolves the referee's underlying worry — that the headline used
the prior with the most favourable baseline tail — in the opposite direction
from the suggested fix: the genuinely LVK-matched prior gives the *smaller*
baseline tail (P(H0>120) = 0.017), which is now the headline.

## Data provenance

No new runs were needed. The two LVK-matched headline runs already existed:

- IMRPhenomXAS_NRTidalv3 — `Results/test_suite/s14__gw170817__imrphenomxas_nrtidalv3__baseline__seed0000`
- TaylorF2 — `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv`

Both use the [0.5, 7.7] M_sun prior (no `--m-comp` flags), the official GWTC-1
PSD and the GWTC-1 heterodyne reference at n_live=5000. The earlier
`*_lvkbounds` runs at [0.87, 1.74] M_sun are retained in the repository but are
no longer used in the manuscript and are not LVK reproductions.
