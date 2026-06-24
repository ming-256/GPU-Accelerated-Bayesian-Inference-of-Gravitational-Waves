# GW150914 mass-prior audit (DEFERRED_RUNS item 4)

**Status:** desk audit complete, 2026-05-23. Follow-up to M3 (GW170817
mass-prior mislabel). Looking for an analogous LVK-name vs LVK-bounds
mismatch on the GW150914 validation side.

## What the runs actually use

Both GW150914 runs reported in the manuscript carry a `lvkbounds` or
`nlive8000_mcmc160` tag but use **the same component-mass prior**, read
from their `config.json`:

| Run | Component-mass bounds (`--m-comp-lo / --m-comp-hi`) |
|---|---|
| `s06__gw150914__imrphenomxphm__lvkbounds__seed0000`   | `[5.0, 100.0] M_sun` |
| `s17a__gw150914__imrphenomxphm__nlive8000_mcmc160__seed0000` (production) | `[5.0, 100.0] M_sun` |

The bounds string in both `config.json`s is verbatim
`--m-comp-lo 5.0 --m-comp-hi 100.0`.

## What LVK actually used

The GWTC-2.1 IMRPhenomXPHM parameter estimation of GW150914 (which the
manuscript claims a "like-for-like reproduction" of) uses, per the
standard LALInference / `bilby` precessing-BBH default, component masses
uniform in detector frame on **`[10, 80] M_sun`** — narrower than our
`[5, 100]` window on both sides.

Source: GWTC-2.1 data release / `bilby_pipe` default for precessing BBH
PE. The GW150914 properties paper (Abbott et al. 2016, ApJL 818, L22)
also reports posteriors derived from this range.

## Is it a science problem?

No. GW150914 is a ≈30+30 M_sun binary; the posterior support sits well
inside `[10, 80] M_sun`, so the wider `[5, 100]` window adds no
posterior mass and the comparison numbers (M_c = 30.35 vs LVK 30.7;
d_L^med = 455 vs LVK 440 Mpc) carry over byte-for-byte. The "like-for-
like" claim is *quantitatively* fine in terms of recovered parameters.

## Is it a *labelling* problem?

Yes, in the same family as M3 (GW170817). Specifically:

1. The `s06` run carries the `lvkbounds` tag in its `run_id`. That tag
   implies "matching LVK". The actual bounds are not the LVK ones.
2. The manuscript claims a "like-for-like LVK reproduction" three times
   (§3.1 l.171, fig.1 caption l.188, §6 wall-clock paragraph l.320).
   A strict reading is incorrect — the prior is broader.

## Recommended fixes (no compute required)

Three coordinated edits. Pick (i) or (ii) — they are alternatives.

**(i) Soften the manuscript wording (zero-compute option, recommended).**
Replace the three "like-for-like LVK reproduction" instances with
"encompassing the LVK PE support" or "consistent with the LVK PE within
the recovered posterior support, on a component-mass prior wider than
LVK's [10, 80] M_sun but with no posterior mass near either boundary."
Add a one-line prior statement to §3.1: "Component masses are uniform
in the detector frame on [5, 100] M_sun, encompassing the LVK GWTC-2.1
[10, 80] M_sun range; the posterior has no support outside [25, 40]."

**(ii) Re-run at [10, 80] to literally match LVK.** Drop `--m-comp-lo`
and `--m-comp-hi` overrides and rerun s17a; expected wall-clock ≈5 h on
one A100. Result: indistinguishable from the existing posterior, plus
strict literalism on "like-for-like".

**(iii) Catalog hygiene (do regardless).** Rename `s06__gw150914__
imrphenomxphm__lvkbounds__seed0000` → `s06__gw150914__imrphenomxphm__
wide_mass__seed0000` (or similar) so the directory tag matches what was
actually run. Update `run_catalog.csv` and the build_paper_tables.py
GW150914_RUNS list.

## My recommendation

**Option (i) + (iii).** No re-run is needed; the science is unaffected;
the wording fix and the catalog rename make the labelling honest. This
matches the resolution path taken for M3 on the GW170817 side
(rename + accurate prior description). If the referee specifically
asks for [10, 80], option (ii) is cheap (one overnight run).

## Suggested response-letter line

> Following the M3 mass-prior audit on the GW170817 side, we
> independently audited the GW150914 validation prior. The s06 and
> s17a runs both use a component-mass prior uniform on [5, 100] M_sun,
> wider than the LVK GWTC-2.1 [10, 80] M_sun range; both posteriors sit
> well inside the LVK range, so the recovered parameters and the
> like-for-like comparison are unaffected. We have updated §3.1 and the
> figure caption to state the actual prior bounds explicitly.
