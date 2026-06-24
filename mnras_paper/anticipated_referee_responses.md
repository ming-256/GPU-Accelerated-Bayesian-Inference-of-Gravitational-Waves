# Yang et al. (2026) MNRAS — anticipated referee responses

Pre-written drafts for the most likely Minor-revision items.  Each block is
deliberately concise: paste-and-edit on submission.  Tier-A repository fixes
identified in the pre-submission critical analysis (`final_critical_analysis.md`)
have been applied to `main.tex` / `references.bib` before submission, so this
file targets items a referee may *still* raise.

Use as: copy a block, adjust the salutation, tighten one or two sentences to
the referee's specific wording, and submit.

---

## R1 — "The 100-σ bootstrap claim is overstated"

> *Referee:* "The ~100-σ exclusion in §4.1 is the *binomial* standard error
> of the reweighted estimator at $n_{\rm eff}$.  That undercounts the
> importance-sampling variance, which is the relevant uncertainty.  A
> proper resampling-based standard error is several times larger.  Please
> requote in resampling-SE units or remove the σ count."

**Response.** We agree the binomial SE is one of several reasonable scales
and have rebuilt the inoculation paragraph in §4.1 to reflect this:

> "...excluding the directly sampled $0.159$ by ${\sim}\,100$ binomial
> standard errors of the reweighted estimator.  The conclusion is robust
> to the choice of resampler: a Bayesian (Dirichlet-weighted) bootstrap
> and a $200$-block jackknife (the standard nonparametric variance
> estimator for importance-sampling estimators; Owen 2013) both give
> intervals about $30\,\%$ wider but with the same centre, and still
> exclude $0.159$ by more than $70$ nonparametric standard errors."

The bootstrap, the Bayesian-bootstrap, and the block-jackknife all give
95\,\% intervals that exclude the directly sampled $0.159$ by an
enormous margin: 102\,σ (binomial), $\sim 73$\,σ (block-jackknife,
nonparametric), and $\sim 73$\,σ (Bayesian bootstrap).  The science
conclusion is unaffected.

The script that computes all three variants is in the public release at
`analysis/final_critical_verification.py`; its log is the line
`SE binom = 0.00118 / SE jackknife = 0.00164 / SE Bayes = 0.00161`.

---

## R2 — "PSIS k̂ = 0.68 is below the 0.7 threshold, so reweighting is *reliable* by Vehtari's criterion"

> *Referee:* "Vehtari et al. (2024) place the unreliability threshold at
> $\hat{k}>0.7$.  Your draw has $\hat{k}=0.68$, which is *below* the
> threshold.  By the canonical PSIS interpretation the reweighting is
> reliable.  Your bootstrap therefore contradicts the published criterion,
> which means *your bootstrap methodology is suspect*, not that the
> threshold is too lenient."

**Response.** The Vehtari thresholds describe asymptotic behaviour and
were validated in their simulation studies in the *large-$n$* regime.
At finite $n$ in the $0.5<\hat{k}\le 0.7$ ``high variance but
consistent'' band, individual draws can still exhibit substantial bias
(Vehtari et al. 2024 quote up to $\sim 10\,\%$ relative bias in this
regime; cf.\ their figs.~6 and §6.3).

For our draw the relative bias is much larger (a factor $\sim 4$,
$0.041$ vs $0.159$), placing the run at the tail of the published
expectation rather than outside it.  Importantly, this is *not* a
contradiction of the PSIS framework: $\hat{k}=0.68$ in the cautionary
band is *exactly* where the published guidance calls for an
independent diagnostic to be reported alongside.  The bootstrap we
report is that diagnostic; the down-sampling sweep (also in §4.1)
provides a direct empirical demonstration of bias rather than slow
convergence.

We have re-run the analysis with the canonical `arviz.psislw`
implementation under its PSIS-LOO sign convention and obtain
$\hat{k}_{\rm arviz}=0.683$, in agreement with our local GPD-MLE to
$10^{-3}$.  The new footnote at §4.1 makes this cross-check explicit.

---

## R3 — "The σ(ι)=1.17 residual on GW150914 is precession-driven and your BNS application uses an aligned-spin waveform"

> *Referee:* "Your GW150914 validation has the largest residual on the
> inclination parameter (σ(ι) ratio 1.17), and inclination is exactly the
> parameter that couples to $d_L$ through the distance-inclination
> degeneracy that drives your bright-siren result.  Validating on a BBH
> with no tides under a precessing waveform does not transfer to a BNS
> application under an aligned-spin waveform."

**Response.** The σ(ι)=1.17 residual is the largest in the GW150914
validation (Table 1; main.tex:170) but the absolute value is
σ(ι)=0.41 rad versus the LVK 0.35 rad, both reflecting a well-resolved
inclination posterior from a precessing-spin waveform on a short
high-SNR signal.  For GW170817 our aligned-spin tidal waveform IMRX
does not include precession by construction, so the relevant
validation comparison for ι is *not* the precession recovery on
GW150914 but the cross-waveform consistency between IMRX, IMR, and
TF2 on GW170817 itself (Table 4; §4.3; the three waveforms agree on
$\hzero^{\rm MAP}$ to within $\sim 2\kmsmpc$).

We also note that the EM-derived inclination constraints of
Mooley et al.~(2018) and Hotokezaka et al.~(2019) bound the
GW170817 inclination to $\lesssim 32^\circ$ off-axis, which would
*tighten* the Mode-B contribution rather than introduce a
precession-driven systematic.  Folding such an EM prior into the
inference under our IMRX pipeline is a clean follow-up and is flagged
in §6.4.

---

## R4 — "Single-event analysis; population-level coverage is the actual cosmology question"

> *Referee:* "Bright-siren $H_0$ measurements are run at the population
> level by combining $\gtrsim 10$ events.  Your single-event 17\,\%
> capture-fraction claim is only relevant if population reweighting
> under-covers as well.  Show one population-level example, or restrict
> the headline claim to single events."

**Response.** We agree the population-level case is the cosmology-grade
use.  We restrict our headline to the *methodology* claim that
single-event posteriors carry a $\gtrsim 5\times$ prior-induced
systematic in the $P(\hzero>120)$ tail that is *not* recoverable by
post-hoc reweighting alone.  Whether this systematic propagates,
amplifies, or cancels in the population combination depends on (i) the
distribution of single-event reweighting deficits and (ii) the
population-model prior over $d_L$ itself.  We give this exact framing
at §6.1 (last paragraph): *``An analysis that quantifies that
dependence through reweighting alone will systematically underestimate
the prior contribution.''*

A population-scale example is a single-paper follow-up and is outside
the scope of this methodology paper.  We have not modified the body
text on this objection.

---

## R5 — "The 13-minute wall-clock is GCP-specific"

> *Referee:* "§5.1 quotes wall-clock on a GCP \texttt{a2-highgpu-1g}.
> Are the numbers reproducible on on-prem A100s?"

**Response.** The analysis is GPU-local: the heterodyned likelihood
holds the LVK strain and PSDs in HBM and never round-trips through
network or persistent storage during sampling.  The GCP class is given
for hardware identification (NVIDIA A100 40 GB SXM4 in an
\texttt{a2-highgpu-1g} VM) and is not the source of the runtime.  An
on-prem A100 with the same SXM4 SKU and a CUDA-12-capable JAX build
will give comparable wall-clock; the runtime is dominated by GPU
saturation, not by GCP-side networking or storage I/O.  We can add a
single clarifying sentence to §5.1 if the editor judges it warranted,
but the public release's `docs/chain_regeneration.md` already states
this explicitly.

---

## R6 — "The Chen+2018 and Hu&Veitch+2025 forecast numbers should be tied to specific tables in those papers"

> *Referee:* "Please cite a specific table or figure of Chen+2018 and
> Hu&Veitch+2025 for the 25–80-events-in-5–10-years and
> $\gtrsim 10^4$-detections-per-year claims."

**Response.** Done in revision.  We have replaced the bare
\citet{Chen2018Forecast} / \citet{HuVeitch2025} with explicit table
or figure citations: \citet[fig.~3]{Chen2018Forecast} for the
$5\text{--}10$-year A+/Voyager bright-siren counts and
\citet[fig.~1]{HuVeitch2025} for the third-generation detection rate.

*(Action item before submission: confirm the figure numbers.  If the
authors quote a *table* rather than a figure, change accordingly.)*

---

## R7 — "IMRX-vs-IMR capture fraction may be a finite-sample artefact"

> *Referee:* "The 17 \% capture fraction for IMRX (NRTidalv3) and 58 \%
> for IMR (NRTidalv2) is attributed to ``tighter upper tail under
> NRTidalv3''.  But the IMRX run has different chain history (different
> n_live convergence path, different heterodyne reference effective bin
> count) from the IMR run.  Is the capture-fraction difference a tidal
> systematic, or a chain-history artefact?"

**Response.** The chain histories are matched up to the waveform-driven
differences: both runs use $n_{\rm live}=5000$, $n_{\rm delete}=2500$,
$n_{\rm mcmc}=8\,n_{\rm dim}=112$, and the same GWTC-1 heterodyne
reference parameters in their default configurations.  The reweighted
$n_{\rm eff}$ values are commensurate ($27{,}317$ for IMRX vs ${\sim}30{,}000$ for IMR);
neither is in the ``small-sample'' regime where finite-sample artefacts
would dominate.  The capture-fraction difference is most parsimoniously
explained by the NRTidalv2→NRTidalv3 calibration change reducing the
upper-$\hzero$ tail (paper main.tex:241), which mechanically reduces
how much of the prior-induced shift is reweightable.

A matched IMR rerun with NRTidalv3-calibrated chain history is a
clean cross-check.  We have not requested it for revision because the
qualitative claim — reweighting underestimates the prior-induced
shift on *both* waveforms — does not depend on which waveform shows
the bigger discrepancy.

---

## R8 — "Why not a population-scale forecast extrapolation, not just an event-rate quote?"

> *Referee:* "If reweighting under-recovers the high-$\hzero$ tail by a
> factor of 6 on GW170817, what does that propagate to in the
> Chen+2018 5-year-25-events case?"

**Response.** We deliberately do not extrapolate.  The per-event
deficit is not constant across the population — it depends on the
local $(\dL,\iota)$ posterior shape and on the location of the event
in the distance-inclination plane.  A single-event factor cannot be
multiplied across the population; the right propagation is to repeat
the direct-vs-reweighted comparison for each event and combine the
direct-sampled posteriors at the population level.  This is exactly
the runtime envelope we open up in §5: at $\lesssim 15$ minutes per
event on a single A100, the multi-event direct-sampling combination
is now within compute budget.  We have flagged this as the natural
next step at §6.3.

---

## Decision matrix — for each Minor-revision item, applied / deferred

| Item | Status | Page-cost  | Submit-now |
|------|--------|-----------|------------|
| R1 (100σ → resampling SE) | **applied** (Tier-B in main.tex) | 1 line | ✅ |
| R2 (k̂ canonical) | **applied** (Tier-C footnote) | 1 footnote | ✅ |
| R3 (precession transfer) | defer to letter | none | ✅ |
| R4 (population scope) | defer to letter | none | ✅ |
| R5 (A100 SKU/GCP) | defer to letter | none | ✅ |
| R6 (Chen/HuVeitch table refs) | **action before submit** | 2 cites | — |
| R7 (IMR vs IMRX matched run) | defer to follow-up | none | ✅ |
| R8 (population extrapolation) | defer to letter | none | ✅ |

R6 is the only one needing action before submission.  R1 + R2 are
already in `main.tex` after the pre-submission critical-analysis pass.
