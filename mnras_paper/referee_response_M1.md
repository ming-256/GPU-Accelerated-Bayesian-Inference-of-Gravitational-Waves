# Draft response to referee concern M1 (selection term)

**Status:** finalised wording, 2026-05-23. No new nested-sampling run was
needed — M1 is an analysis question and is resolved by a one-dimensional
integral over a detection model. Numbers and the figure are produced by
`test_suite/analysis/analyze_selection_term.py` (figure
`figures/selection_term_Ns.pdf`, table
`Results/test_suite/selection_term_Ns.csv`).

## What the referee wrote (M1)

> The "direct flat-in-z" run omits the H0-dependent selection term required for
> a redshift prior. Abbott P1700296 Eqs 7–12: with a volumetric *distance*
> prior the selection normalisation N_s(H0) is constant and ignorable, but with
> a prior on *redshift* it becomes H0-dependent. Variant (i) imposes a z-prior;
> Eq. 2 has no 1/N_s(H0). The neglected term acts in the high-H0 region that
> carries the entire headline signal. Abbott bounded it at ≲5% — but the whole
> result is a few-per-cent tail statistic.
> *Fix:* include N_s(H0) and show stability, or compute it for this
> configuration and prove it is flat well below the 0.142 effect.

## Our response

We thank the referee for catching the ambiguity in the §2.4 prior wording.
We have computed the selection term explicitly and confirm that **Eq. 2 is
correct as written for the configuration actually run**: the omitted factor
1/N_s(H0) is an H0-independent constant and cancels from the H0 posterior.
The reasoning, the quantitative check, and the coordinated manuscript wording
changes are below.

A single labelling clarification anchors the response: the variant previously
called "direct flat-in-redshift" in §2.4 was, throughout, literally a prior
*uniform in d_L over a fixed [10, 75] Mpc window with no H0-dependent
boundaries*. This is the only form the inference pipeline ever imposes; the
old name was a (numerically accurate but operationally imprecise) cosmological
relabelling. We have renamed it **uniform-in-d_L** throughout the manuscript
to make the H0-independence of N_s self-evident at the prior level. The two
are equivalent within one per cent at GW170817's redshift, so no science
result moves.

### 1. The selection term and why the prior type decides its H0-dependence

Conditioning the bright-siren likelihood on GW detection introduces the
normalisation

  N_s(H0) = ∫ P_det(d_L) π(d_L | H0) d d_L,

where P_det(d_L) is the orientation- and sky-averaged probability that a BNS at
luminosity distance d_L clears the network detection threshold. P_det depends
on the *observable* d_L (through the signal amplitude) and on source
orientation — **it does not depend on H0**. Every H0-dependence of N_s
therefore enters through the prior factor π(d_L | H0).

This is exactly the referee's distinction. The volumetric baseline imposes
π(d_L) ∝ d_L² as a fixed density on the observable d_L: N_s is a pure
constant. A prior whose d_L density genuinely moved with H0 would make N_s
H0-dependent.

### 2. The uniform-in-d_L variant imposes a *fixed* density on d_L

The decisive point is how variant (i) is implemented. In
`GW170817/Scripts/GW170817_heterodyned_2.py` the d_L coordinate is sampled
with prior type 0 — **uniform over a fixed range [d_lo, d_hi] in Mpc**
(`logprior_fn`, the `lp_uniform` branch) — and the H0 coordinate carries an
independent log-uniform prior. The d_L prior density is

  π(d_L | H0) = 1 / (d_hi − d_lo),  independent of H0.

At GW170817's source redshift (z ≈ 0.01) this fixed uniform-in-d_L density is
numerically indistinguishable from a flat-in-redshift density to better than
one per cent — and that numerical equivalence is what the old name encoded.
The operational difference is precisely the referee's concern: a fixed density
on the observable d_L has no H0-dependent window, whereas a literal flat-in-z
prior with fixed z-range would. Substituting the fixed-density form into the
integral above, N_s(H0) has no H0 anywhere:

  N_s = ∫ P_det(d_L) / (d_hi − d_lo) d d_L = constant.

Variant (i) is therefore in exactly the same position as the volumetric
baseline: the selection normalisation is H0-independent and cancels from
p(H0 | d) ∝ π(H0) L(d | H0) / N_s. **No 1/N_s(H0) factor is missing from
Eq. 2.**

### 3. Quantitative check

`analyze_selection_term.py` evaluates N_s with a concrete detection model:
P_det(d_L) = P(Θ > 4 d_L / D_h), where Θ ∈ [0, 4] is the Finn & Chernoff
(1993, 1996) antenna-pattern projection parameter, Monte-Carlo sampled
(4 × 10⁶ draws) over inclination, sky position and polarisation, and D_h is
the network horizon distance. A *single-detector* Θ is used deliberately: it
has the widest spread of any network combination and so makes P_det fall off
fastest with distance — the choice that *maximises* any H0-dependence of N_s.

- **(a) As run — uniform in d_L over a fixed range.** N_s is H0-independent
  to machine precision for every horizon tested (D_h = 100, 150, 220 Mpc); see
  the flat lines in Fig. `selection_term_Ns` panel (a). This is not a
  numerical result — it follows from the integrand having no H0 dependence.

- **(b) Context — a hypothetical genuine flat-in-z prior.** Had the d_L
  window instead been made H0-dependent, [c z_lo/H0, c z_hi/H0], N_s(H0)
  would rise monotonically with H0 (panel b). Across the headline
  H0 > 120 km/s/Mpc tail the variation would be ≈ 6 per cent at a realistic
  O2 network horizon (D_h = 220 Mpc; the published O2 BNS range ≈ 100 Mpc
  implies a horizon of this order), rising to ≈ 23 per cent only for a
  deliberately pessimistic D_h = 100 Mpc. A genuine 3-detector network — with
  a far more concentrated Θ — would shrink this further, consistent with the
  ≲ 5 per cent bound quoted by Abbott et al. (2017). This case is shown only
  to demonstrate that the H0-independence in (a) is a property of the
  implemented prior, not an assumption: the term is genuinely small even in
  the form where it does not vanish.

### 4. Manuscript changes

We have made three coordinated changes:

1. **Rename throughout (cosmetic).** Variants (i) and (ii) in §2.4 are now
   labelled "Direct uniform-in-d_L" and "Reweighted uniform-in-d_L"
   respectively. All subsequent references in the abstract, introduction, §4
   (prior sensitivity), §5 (bimodality), §6 (discussion), §7 (conclusions),
   figure captions, and table captions have been updated for consistency. A
   single parenthetical in §2.4 records the equivalence to the
   "flat-in-redshift" prior of Abbott et al. (2017) over the same distance
   range, preserving the mapping to the original analysis.

2. **§2.4 prior-definitions paragraph (substantive).** A new sentence states
   that π(d_L) is imposed as a fixed density on the observable d_L with no
   H0-dependent window, so π(d_L | H0) has no H0-dependence for any of the
   three prior variants, and therefore N_s(H0) is constant in H0 and cancels
   from the joint posterior — exactly as for the volumetric baseline. A
   footnote records the Finn–Chernoff evaluation that confirms this to
   machine precision, pointing to
   `test_suite/analysis/analyze_selection_term.py`.

3. **Sentence after Eq. 2 (substantive).** A single sentence following the
   joint-likelihood definition (eq:h0likelihood) states that Eq. 2 carries no
   1/N_s(H0) factor because, for every prior variant in this work,
   π(d_L | H0) has no H0-dependence and hence N_s is H0-independent; the
   reader is referred to §2.4 for the prior-level explanation. This
   pre-empts the M1 reading at the point where the likelihood is first
   written down.

The science conclusions are unaltered: the direct run and the reweighting
target share the same fixed-d_L prior, so the reweighting capture-fraction
result of Eq. 5 is independent of this clarification.

## Data provenance

No runs. The result is the integral in `analyze_selection_term.py`; inputs are
the d_L/H0 prior bounds read from `GW170817_heterodyned_2.py` and a
Finn–Chernoff detection model. Outputs:
`Results/test_suite/selection_term_Ns.csv`,
`mnras_paper/figures/selection_term_Ns.{pdf,png}`.
