# Deferred runs — what we can still run and should run

Compiled 2026-05-18 while preparing the internal-review draft. Nothing in this
list is run yet; the draft is built entirely on data already in `Results/`.
Each item says what to run, why (which referee concern it answers), and how.

The mass-prior fix (referee M3) needed **no** new run — both LVK-matched
headline runs already existed. The items below are the remaining run-dependent
referee concerns.

---

## 1. n_mcmc convergence sweep — referee M7 (high priority)

**Why.** Science runs use `5*n_dim = 70` slice steps; the GW150914 validation
deliberately uses 160 "so the comparison is not sampler-limited", implying 70
may be marginal. The headline is a tail probability, and under-stepped slice
sampling biases tails first. No n_mcmc sweep currently exists for the 14-d
GW170817 problem.

**Run.** IMRPhenomXAS_NRTidalv3, GW170817, baseline (LVK-matched) and direct
flat-in-z, at `n_mcmc / n_dim in {5, 10, 20}` (i.e. 70 / 140 / 280 steps),
`n_live=5000`, seed 0. Six runs, ~15-20 min each on an A100.
Pass the step count through `GW170817_heterodyned_1.py` (add an `--n-mcmc`
argument if not already exposed).

**Pass criterion.** Headline `P(H0>120)` stable to within run-to-run scatter
across the three step counts.

---

## 2. Seed ensemble for honest lnZ scatter — referee M2 (high priority)

**Why.** The two-seed bimodality "replication" is internally inconsistent at the
quoted +/-0.1 lnZ precision (unrestricted lnZ 486.48 vs 487.52 — a 1.04 gap).
The +/-0.1 per-run lnZ uncertainty claim cannot be supported by two seeds.

**Run.** Repeat the GW170817 IMR/NRTidalv2 bimodality set (Mode A, Mode B,
unrestricted) for ~5-8 independent seeds, `n_live=5000`. ~15 min each.
Report the empirical run-to-run lnZ standard deviation and propagate it into
the Mode-B/Mode-A Bayes factor and the "DeltalnZ <~ 1.8 not decisive" claim.

---

## 3. IMRX mode-isolated bimodality — referee M4 (medium priority)

**Why.** Every mode-isolated run is IMRPhenomD_NRTidalv2, but the abstract and
§4.2 attribute the (d_L, iota) bimodality mechanism to the locked primary IMRX.
The NRTidalv3 bridging argument is asserted, not shown.

**Run.** Mode-A (`d_L in [30,75]`) and Mode-B (`d_L in [10,30]`) direct
flat-in-z runs with IMRPhenomXAS_NRTidalv3, `n_live=5000`, seed 0 — mirroring
the s10 IMR runs. Two runs, ~15-20 min each.
The `--dL-lo/--dL-hi` flags already exist (`heterodyned_2.py`).

---

## 4. GW150914 mass-prior check — follow-up to M3 (medium priority)

**Why.** The GW170817 "LVK-bounds" mislabel was found and fixed. The GW150914
side uses an `s06 ... lvkbounds` run; its mass bounds have not been verified
against the GW150914 parameter-estimation prior. This may be an analogous
mislabel.

**Action (mostly desk work, not a run).** Check the GW150914 PE component-mass
prior in the LVK GWTC-2.1 release / the GW150914 properties paper, compare to
the bounds actually used by `s06`, and correct `DATA_EQUIVALENCE.md` and the
GW150914 text if they disagree. A re-run is only needed if `s06` used a
non-LVK restriction.

---

## 5. Selection-term check N_s(H0) — referee M1 (analysis, not a run)

**Why.** The direct flat-in-z variant imposes a redshift prior but Eq. 2 omits
the H0-dependent selection term `1/N_s(H0)` that Abbott's formalism (Eqs 11-12)
requires for a z-prior. The neglected term acts in the high-H0 tail that
carries the headline signal.

**Action.** Compute `N_s(H0)` for this configuration and show it is flat well
below the 0.142 effect, or include it and show stability. This is an
integral/analysis task, not a nested-sampling run.

---

## 6. Matched parallel-bilby CPU benchmark — out of scope (low priority)

The manuscript already states (and the referee accepts) that no CPU baseline is
claimed. A like-for-like GW170817 parallel-bilby run with IMRX, identical
priors and live-point count would let the speedup be quantified, but it is
explicitly left for future work and is not required for this revision.

---

## Already resolved without a run

- **Referee M3 (mass prior).** Fixed. Headline moved to the LVK-matched
  [0.5, 7.7] M_sun prior using runs that already existed:
  `s14 ...imrphenomxas_nrtidalv3...baseline` (IMRX) and
  `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv`
  (TaylorF2). See `referee_response_M3.md`.
