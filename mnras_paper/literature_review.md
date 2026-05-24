# Literature review and positioning audit — Yang et al. (2026, MNRAS submission)

**Reviewer brief.** Critical review of `mnras_paper/main.tex` (commit `800a828`,
draft of 2026-05-23) for *positioning, attribution, and literature*. The science
and the numerical pipeline are not in scope; the audit targets framing, citations,
and tail-risk at the referee literature layer. All claims below are grounded
in concrete papers verified by `WebFetch` / `WebSearch` against arXiv, NASA ADS,
journal sites, or — when those returned 403 / blank — search engines confirming
the journal-ref against the arXiv ID. Dates / volumes / DOIs are reported as
verified; one specific case (the new compact APS-DOI `10.1103/dj7k-tk37` for
the Hu & Veitch 2025 PRD article) was double-checked because it looks
syntactically odd at first glance.

---

## 1. Verdict

**Ship after the Tier-A edits.** The science and the numerical evidence base
are in good shape, and the M1/M3/m14 fixes already landed in the current draft
materially harden the prior-sensitivity argument. The vulnerabilities are
*citational*: the bibliography under-cites the most directly comparable recent
GW170817 H₀ reanalyses (Palmese et al. 2024, PRD 109, 063508; Salvarese & Chen
2024, ApJL 974, L16), under-cites the canonical methodological anchor for
importance-sampling failure (Vehtari et al. 2024 / Pareto-smoothed IS), and
omits the current canonical bright-siren-cosmology review (Mastrogiovanni
et al. 2024, *Annalen der Physik*; Palmese & Mastrogiovanni 2025 encyclopedia
chapter). None of those gaps changes the paper's quantitative conclusions, but
each is the kind of thing that an MNRAS referee will flag. The bibliography has
two stale entries (Wong et al. 2023 ApJ, Edwards et al. 2024 PRD) where the
arXiv abs page does not show the journal-ref but the journal has published; both
are otherwise correct. One placeholder (`Yang2026DataRelease`) is still a
GitHub-only handle. With the ~6 Tier-A edits and ~10 Tier-B citation additions
below, the paper is referee-ready; without them, expect a citation-heavy
revision letter.

---

## 2. Literature sweep results

### 2a — GW170817 H₀ reanalyses since Abbott 2017

The draft currently cites only Hotokezaka et al. (2019, Nature Astronomy) and
Nicolaou et al. (2020, MNRAS). Verified gaps:

| Paper | Reference | What it does | Currently cited? |
|---|---|---|---|
| **Palmese, Kaur, Hajela, Margutti, McDowell, MacFadyen 2024** | PRD 109, 063508 (arXiv:[2305.19914](https://arxiv.org/abs/2305.19914); [DOI](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.109.063508)) | H₀ = 75.46⁺⁵·³⁴₋₅·₃⁹ km/s/Mpc using GW170817 + 3.5 yr of multi-band afterglow; ~7% precision (vs Abbott's 14%) | **No — major gap** |
| **Mooley, Deller, Gottlieb, et al. 2018** | Nature 561, 355 ([DOI:10.1038/s41586-018-0486-3](https://www.nature.com/articles/s41586-018-0486-3)) | The original VLBI superluminal-motion paper that constrains the inclination to ~20°. Hotokezaka 2019 is *built on* this. | No — should cite alongside Hotokezaka |
| **Mukherjee, Lavaux, Bouchet, et al. 2021** | A&A 646, A65 ([DOI:10.1051/0004-6361/201936724](https://www.aanda.org/articles/aa/full_html/2021/02/aa36724-19/aa36724-19.html)) | GW170817 + VLBI velocity correction; H₀ = 68.3⁺⁴·⁶₋₄·⁵ km/s/Mpc. The standard methodological reference for peculiar-velocity treatment. | No |
| **Howlett & Davis 2020** | MNRAS 492, 3803 (arXiv:[1909.00587](https://arxiv.org/abs/1909.00587); [DOI:10.1093/mnras/staa049](https://academic.oup.com/mnras/article/492/3/3803/5700291)) | Bayesian model-averaging over velocity datasets; H₀ = 66.8⁺¹³·⁴₋₉·² km/s/Mpc. Directly relevant to §4.1's peculiar-velocity sweep. | No |
| **Salvarese & Chen 2024** | ApJL 974, L16 (arXiv:[2406.11126](https://arxiv.org/abs/2406.11126)) | Viewing-angle bias drives >10% systematic in GW170817 H₀; develops a correction. **Sits in exactly this paper's methodological territory.** | **No — major gap** |
| **Bom et al. / Hannam et al. context** | various 2022–2024 | Several follow-ups on GW170817 H₀ from afterglow modelling; collectively cited via Palmese 2024. | Out of scope for direct citation. |
| **Mukherjee, Wandelt 2018**; **Mukherjee, Wandelt, Silk 2020/2021** | various | Dark-siren / cross-correlation framework. Less directly relevant to a single-event bright-siren prior-sensitivity paper; safe to skip unless framing pivots. | Out of scope. |

**Verdict:** Add Palmese et al. 2024, Salvarese & Chen 2024, Mooley et al. 2018,
Mukherjee et al. 2021, Howlett & Davis 2020 — all directly relevant to either
(i) recent GW170817 H₀ literature, (ii) the inclination/distance degeneracy that
underlies the bimodality, or (iii) the peculiar-velocity treatment swept in §4.1.

### 2b — Reweighting / importance-sampling failure references

The draft cites only Speagle (2020, MNRAS 493, 3132) as the methodological
anchor for IS failure ("see e.g."). This is weak: Speagle's dynesty paper
is a sampler description, not the canonical reference for the failure mode.
The actual canonical anchors are:

| Paper | Reference | What it provides |
|---|---|---|
| **Vehtari, Simpson, Gelman, Yao, Gabry 2024 (PSIS)** | JMLR 25, paper 72 (arXiv:[1507.02646](https://arxiv.org/abs/1507.02646); [JMLR PDF](https://www.jmlr.org/papers/v25/19-556.html)) | The Pareto-smoothed importance sampling paper; defines the *k̂* diagnostic that quantifies when IS estimators have infinite variance. The k̂ > 0.7 criterion is the standard go/no-go for IS reweighting in modern Bayesian practice. |
| **Owen 2013, *Monte Carlo theory, methods and examples*, Ch. 9** | [available online](https://artowen.su.domains/mc/Ch-var-is.pdf) | Foundational treatment of n_eff in self-normalized IS; the rigorous justification for Kish's effective-sample-size formula in the IS context. |
| **Payne, Talbot, Thrane 2019** | PRD 100, 123017 (arXiv:[1905.05477](https://arxiv.org/abs/1905.05477); [DOI:10.1103/PhysRevD.100.123017](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.100.123017)) | First systematic discussion of IS reweighting in GW PE specifically (for higher-order modes). Explicitly discusses n_eff as a failure diagnostic. **This is the GW-context paper Speagle is being asked to substitute for.** |
| **Cabras, Cabezas, Ren, Webster 2024 (Tempered Multifidelity IS for GW)** | arXiv:[2405.19407](https://arxiv.org/abs/2405.19407) | Explicit GW-context example of IS-from-cheap-posterior failing on high-d targets; tempering as a fix. Useful as evidence that the failure mode is generic. |

**Verdict:** Vehtari+2024 PSIS is the strongest single addition. Payne+2019 is
the GW-specific anchor that the current paper's §3.1 / §4.1 effective-sample-size
discussion is implicitly building on; not citing it is a referee bait.

### 2c — The (d_L, ι) bimodality in GW170817 PE

**Verdict — partial:** the *(d_L, cos ι)* degeneracy is universally acknowledged
in the GW170817 PE literature, but a *quantitative* split into two distinct
local maxima with mode-isolated Bayes factors has not (as best I can verify
from publicly searchable literature) been published before this paper. The
relevant context references are:

| Paper | Reference | Relevance |
|---|---|---|
| Abbott et al. 2019 (GW170817 properties) | PRX 9, 011001 (already cited) | Figure 11 shows the distance–inclination joint posterior; the two-arm structure is visible but is treated as a single broadened mode, not as two distinct modes with separate local evidences. |
| Mandel, Berry, Ohme, Fairhurst, Farr 2014 (and earlier Cantiello et al.) | — | The distance–inclination degeneracy is generic for ground-based GW PE; discussions go back to Schutz 1986 and Cutler & Flanagan 1994. |
| Finstad, De, Brown, Berger, Biwer 2018 | ApJL 860, L2 ([DOI:10.3847/2041-8213/aac6c1](https://iopscience.iop.org/article/10.3847/2041-8213/aac6c1)) ("Measuring the Viewing Angle of GW170817…") | Demonstrates EM-counterpart-informed reweighting collapses the inclination posterior; the bimodality is implicit in what they break. |
| Mooley 2018, Hotokezaka 2019 (Nat Astron) | already discussed | The high-inclination *constraint* from VLBI is what isolates one mode in their analysis; this paper's Mode A. |

The bimodality discussion in this paper (§5, Figures 5–6, Table 6) is therefore
plausibly novel as a *quantitative* mode-isolated evidence calculation, even
though the underlying degeneracy is well-known. **It is safer not to claim
novelty explicitly** — the current text does not, which is correct.

### 2d — GPU-accelerated GW parameter estimation

Currently cited: Wong et al. 2023 (Jim), Edwards et al. 2024 (ripple),
Krishna et al. 2023 (relative binning in Bilby), Wouters et al. 2024 (Jim BNS),
Hu & Veitch 2025, Cabezas et al. 2024 (BlackJAX), Yallup et al. 2025, Prathaban
et al. 2025. Verified missing / under-cited:

| Paper | Reference | Why it matters |
|---|---|---|
| **Williams, Veitch, Messenger 2021 (nessai)** | PRD 103, 103006 (arXiv:[2102.11056](https://arxiv.org/abs/2102.11056); [DOI:10.1103/PhysRevD.103.103006](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.103.103006)) | Normalising-flow nested sampling for GW PE; the direct CPU-side counterpart to BlackJAX-NS and a natural comparator. Major omission given the paper's nested-sampling framing. |
| **Lange, O'Shaughnessy, Rizzo 2018 (RIFT)** | arXiv:[1805.10457](https://arxiv.org/abs/1805.10457) | The other dominant fast-PE pipeline used by LVK in O4. Should be acknowledged in the §1 fast-PE landscape paragraph. |
| **Pankow, Brady, Ochsner, O'Shaughnessy 2015** | PRD 92, 023002 ([DOI:10.1103/PhysRevD.92.023002](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.92.023002)) | The grid-based marginalised-extrinsic approach that RIFT extends; historical context for the parallelism axis. Optional but adds depth. |
| Dax, Green, Gair, Macke, Buonanno, Schölkopf 2021 (DINGO) | PRL 127, 241103 | Simulation-based inference for GW PE; another acceleration paradigm. Optional; the paper's framing is firmly nested-sampling. |

The Hu & Veitch 2025 PRD compact DOI `10.1103/dj7k-tk37` is **correct** — this
is APS's new short-DOI scheme (introduced 2024) and the citation
(PRD 112, 084039) is verified.

**Verdict:** Add Williams+2021 (nessai); ideally add Lange+2018 (RIFT). The
paper's claim to a "GPU-native nested-sampling pipeline" is strongest when
positioned against the nearest CPU normalising-flow nested-sampling work, which
is nessai.

### 2e — Standard-siren cosmology reviews

**No review is currently cited.** Verified candidates:

| Paper | Reference | Notes |
|---|---|---|
| **Mastrogiovanni et al. 2024** ("Cosmology with Gravitational Waves: A Review") | *Annalen der Physik* (2024); [Wiley DOI](https://onlinelibrary.wiley.com/doi/pdf/10.1002/andp.202200180) | The current canonical mid-length review of GW cosmology; covers bright and dark siren methods, prior choices, selection effects. |
| **Palmese & Mastrogiovanni 2025** ("Gravitational Wave Cosmology", Encyclopedia of Astrophysics chapter) | arXiv:[2502.00239](https://arxiv.org/abs/2502.00239) | Most recent (Feb 2025) overview; chapter for Mandel-edited Elsevier reference module. |
| **Chen, Fishbach, Holz 2018** | Nature 562, 545 (arXiv:[1712.06531](https://arxiv.org/abs/1712.06531)) | The "2% in 5 years" forecast paper that frames why prior sensitivity on single-event H₀ matters for the population programme. Not a review but heavily cited. |
| **LVK Collaboration 2025** ("GWTC-4.0 cosmic expansion") | arXiv:[2509.04348](https://arxiv.org/abs/2509.04348) | September 2025; the most recent population-level H₀/modified-propagation constraints from GWTC-4. |

**Verdict:** Cite Mastrogiovanni+2024 (or Palmese & Mastrogiovanni 2025) in the
intro to ground the bright-siren framing in a current review. Chen+2018 is a
useful supporting cite for "this matters at population level".

### 2f — Selection effects in GW H₀ inference

The draft cites Finn & Chernoff (1993) and the LVK 2020 Prospects review for
the horizon-distance calculation in the new §2.4 footnote, plus the LVK
P1700296 data release as the authority for the selection-cancellation argument.
The community standard reference for selection effects in hierarchical GW
inference is one of:

| Paper | Reference | Relevance |
|---|---|---|
| **Mandel, Farr, Gair 2019** | MNRAS 486, 1086 (arXiv:[1809.02063](https://arxiv.org/abs/1809.02063)) | The canonical pedagogical derivation of selection-bias-aware hierarchical inference, including the detection-probability integral that appears in our N_s(H₀). |
| **Vitale, Gerosa, Farr, Taylor 2022** (Handbook of GW Astronomy, Ch. 45) | Springer, [DOI:10.1007/978-981-15-4702-7_45-1](https://link.springer.com/referenceworkentry/10.1007/978-981-15-4702-7_45-1) | Pedagogical chapter explicitly on selection effects in compact-binary populations; current standard reference. |
| Talbot & Golomb 2023 ("Quick recipes for GW selection effects") | arXiv:[2404.16930](https://arxiv.org/abs/2404.16930) | Recent practical handbook on the integrals; useful supporting cite. |

**Verdict:** Add Mandel+2019 as the canonical analytic framework reference and
Vitale+2022 as the pedagogical one. Both back the H₀-independence claim more
strongly than P1700296 alone.

---

## 3. Bibliography audit

For each `references.bib` entry, the audit checked (i) journal/volume/page,
(ii) DOI string, (iii) author-list completeness, (iv) preprint-vs-journal
status. Flags:

| Key | Status | Notes / suggested edit |
|---|---|---|
| `Abbott2017GW170817Discovery` | OK | PRL 119, 161101 verified. |
| `Abbott2017H0` | OK | Nature 551, 85 verified. |
| `Abbott2019GW170817Properties` | OK | PRX 9, 011001 verified. |
| `Abbott2016GW150914` | OK | PRL 116, 061102 verified. |
| `Abbott2017GW170817Properties` | **DUPLICATE** | This is a second @article entry at L273 with the *same* PRX 9, 011001 metadata as `Abbott2019GW170817Properties` but a 2017 key. **Delete `Abbott2017GW170817Properties` (L273–281); no cite uses it.** Confirmed by grep — no `\cite*{Abbott2017GW170817Properties}` occurrence in `main.tex`. |
| `Schutz1986` | OK | Nature 323, 310. |
| `Planck2020` | OK | A&A 641, A6 (Planck 2018 results VI; published 2020). Consistent with the M-row in referee_response.md. |
| `Riess2016` | OK | ApJ 826, 56. |
| `Riess2022` | OK | ApJL 934, L7. |
| `Ashton2019Bilby` | OK | ApJS 241, 27. |
| `Speagle2020Dynesty` | OK as cite, but **methodologically weak** for the §4.1 IS-failure use; supplement with Vehtari+2024 PSIS (see Task 1b). |
| `Skilling2006Nested` | OK | Bayesian Analysis 1, 833. |
| `Bradbury2018JAX` | OK (misc, but stale year) | Consider updating to `year={2018, accessed 2026}` or pinning a specific JAX release; some venues prefer this. Cosmetic. |
| `BlackJAX` | OK (eprint only is fine) | The Cabezas+2024 BlackJAX paper is on arXiv only. |
| `Yallup2025BlackJAXNS` | OK | arXiv 2509.24949 (Sep 2025). |
| `Yang2026DataRelease` | **PLACEHOLDER** | The `note` field says "GitHub repository (to be created at the listed URL)". For MNRAS submission, either (i) create the repo and Zenodo-archive it for a DOI, or (ii) drop this citation and merge the data-availability statement into the §Data Availability paragraph. As-is, this is a self-referential dangling pointer. |
| `Prathaban2025GPUSpeed` | OK | arXiv 2509.04336. |
| `Wong2023Jim` | **Journal-ref incomplete** | Verified published: ApJ 958, 129 (Dec 1 2023). The bib has the journal but **no DOI**; add `doi = {10.3847/1538-4357/acf5cd}` (verified via the IOP article URL `https://iopscience.iop.org/article/10.3847/1538-4357/acf5cd/pdf`). |
| `Edwards2023Ripple` | **OK on bib; arXiv abs page misses journal-ref** | The bib correctly states PRD 110, 064028 with DOI `10.1103/PhysRevD.110.064028`. The arXiv abs page lacks the journal-ref field, which can lead a referee to mistakenly think it's still a preprint — not actionable for this paper, but worth being aware of. |
| `Cornish2010` | OK as `@misc` | arXiv 1007.4820, never journal-published. |
| `Zackay2018RelativeBinning` | OK as `@misc` | arXiv 1806.08792, never journal-published. |
| `Krishna2023RelativeBinningBilby` | OK as `@misc` | arXiv 2312.06009; verified — still preprint as of mid-2026, single version. |
| `Wouters2024JimBNS` | OK (verified PRD 110, 083033) | DOI present. The arXiv abs page shows v2 (Nov 2025) but the v1 was the published-version snapshot. |
| `HuVeitch2025` | **OK — odd-looking DOI is real** | `10.1103/dj7k-tk37` is APS's new compact-DOI format (introduced 2024). Verified by hitting [the APS DOI directly](https://journals.aps.org/prd/abstract/10.1103/dj7k-tk37). PRD 112, 084039 (published Oct 15 2025). No action needed. |
| `Abbott2019GWTC1` | OK | PRX 9, 031040. |
| `Pratten2021XPHM` | OK | PRD 103, 104056. |
| `Abbott2021GWTC2p1` | OK | PRD 109, 022001. Note the apparent year mismatch (key says 2021, year shows 2024) — this is correct because the GWTC-2.1 *preprint* is 2021 but the journal publication is 2024. Consider renaming the key to `Abbott2024GWTC2p1` for honesty, but no factual issue. |
| `LVK_GW170817_DataRelease` | OK | P1800061. |
| `LVK_H0_DataRelease` | OK | P1700296. |
| `GWTC2p1_GW150914_Zenodo` | OK | DOI 10.5281/zenodo.6513631. |
| `HolzHughes2005` | OK | ApJ 629, 15. |
| `Kish1965` | OK | Book reference fine. |
| `Hotokezaka2019` | OK | Nat Astron 3, 940. |
| `Nicolaou2020` | OK | MNRAS 495, 90. |
| `FinnChernoff1993` | OK | PRD 47, 2198. |
| `LVK2020Prospects` | OK | Living Reviews in Relativity 23, 3. |

**Author-list completeness.** Most `{others}` are appropriate (LVK papers
with hundreds of authors). One worth tightening:
- `Hotokezaka2019` already lists 8 authors explicitly (correct).
- `Abbott2017H0` lists `{others}` (LVK paper; standard, fine).
- `Cabezas/BlackJAX` lists `{others}` after 4 names — fine for the misc entry.

**Bibliography summary:** delete one duplicate, add one missing DOI
(`Wong2023Jim`), resolve one placeholder (`Yang2026DataRelease`), and consider
one cosmetic key rename (`Abbott2021GWTC2p1` → `Abbott2024GWTC2p1`). No factual
fabrications.

---

## 4. Framing audit

### 4a. Is the GPU speedup claim defensible?

**Yes, with a small framing tightening.** The claim is "~13 min on a single
A100 for the full n_live=5000 IMRX_NRTidalv3 analysis" (Abstract; §6.1). For
context:

- **Wong, Isi, Edwards 2023 (Jim, ApJ 958, 129)** reports *full Bayesian PE for
  GW150914 and GW170817 within a minute of sampling time* using normalising-flow
  MCMC. That is faster than this paper's 13 min, but: (i) it is MCMC, not
  nested sampling, so it does not produce ln Z; (ii) it does not present a
  prior-sensitivity sweep at converged settings. The paper's framing
  ("the runtime budget makes full-sample prior-sensitivity reruns the right
  default") is therefore *consistent with* Jim being faster on the headline
  number, because the deliverable here is different.
- **Wouters et al. 2024 (PRD 110, 083033)** reports minutes-scale BNS PE with
  Jim. Same caveat about ln Z and prior sweeps.
- **Hu & Veitch 2025 (PRD 112, 084039)** is an explicit accelerator-method
  review for 3G detectors; positions relative binning as the dominant
  wall-clock factor. The paper's §6.2 attribution ("the relative-binning
  approximation accounts for the bulk of the wall-clock reduction; the GPU
  saturation provided by BlackJAX-NS is layered on top") is consistent with
  Hu & Veitch.

**Action:** the §6.4 paragraph ("Scope of the performance claim") already
acknowledges no like-for-like pbilby benchmark. No softening needed. **Adding
a citation to Wong+2023's minute-scale number in §6.1 or §1 would actually
strengthen the framing**, because it puts the paper's 13-min figure into the
right reference frame: this paper sits in the "nested-sampling-with-evidence"
regime, not the "fastest possible PE" regime, and ~15 minutes for a full
NS-with-ln-Z run is competitive in that regime.

### 4b. Is the "reweighting deficit" framing fair?

**Yes, but the novelty should be calibrated.** The IS-failure-from-poor-tail-coverage
phenomenon is well-known in statistics (Owen 2013, Vehtari+2024 PSIS) and was
demonstrated in GW PE for higher-order-mode reweighting by Payne, Talbot, Thrane
(2019, PRD 100, 123017). The novelty in this paper is **the specific demonstration
that this failure mode dominates the apparent prior-insensitivity of the original
GW170817 H₀ bright-siren analysis**, mediated by the (d_L, ι) bimodality. That
is a real and previously-undocumented finding.

The current §4.1 wording ("This is the conventional symptom of importance-sampling
weights concentrated on a small subset of the baseline draw, exactly the regime
in which reweighting is known to be unreliable") is well-calibrated. The §6.1
("Implications for bright-siren cosmology") could be slightly sharpened by
referencing PSIS's *k̂* diagnostic as the more rigorous version of the n_eff
check we recommend.

### 4c. Is "first / canonical / only" language well-bounded?

**Yes.** I searched the manuscript for "first", "novel", "canonical", "unique",
"only". Findings:

- "the canonical bright siren" — refers to GW170817, which is uncontroversial.
- "the only confirmed example to date" — refers to GW170817 as the only confirmed
  bright siren, which is true as of 2026-05.
- No claim of being the first GPU NS analysis, the first prior-sensitivity
  study, etc. The framing is appropriately defensive.

### 4d. Does the m14 (median 87.6 vs MAP 70.5) finding deserve more prominence?

**Yes, weakly.** The current draft mentions the median shift inside Table 5
(via the m14-added median column) and as one sentence in §4.1 ("the median is
reported as a bin-noise-robust complement to the MAP for the skewed posteriors
of the uniform-in-d_L variants"). The number 87.6 km/s/Mpc is buried; a referee
will not necessarily extract it. The argument it makes is *qualitatively distinct*
from the tail-probability argument: it shows the prior shifts not only the high
tail but also the *bulk* of the posterior, in a way the MAP-only summary masked.

**Action:** the abstract could be tightened by one sentence: *"In addition to
the high-tail movement, the binned MAP stays at 70.5 km/s/Mpc but the weighted
median moves from 77.6 to 87.6 km/s/Mpc, indicating that the prior shifts the
bulk of the posterior in a way the MAP alone obscures."* This is Tier-A because
it changes what the abstract claims.

### 4e. Mass-prior wording on the GW170817 side

**Verified correct.** The current §2.4 wording cites Abbott et al. (2019, PRX 9,
011001, Sec. III D) for the [0.5, 7.7] M_⊙ component-mass prior with the chirp-mass
constraint [1.184, 2.168] M_⊙. This matches the PE description in the PRX paper
exactly (Sec. III D second paragraph). The M3 fix is properly landed. No action.

### 4f. GW150914 [10, 80] M_⊙ LVK GWTC-2.1 prior

**Verified consistent.** The GWTC-2.1 XPHM PE used the bilby_pipe default
precessing-BBH prior, which is [10, 80] M_⊙ on each component (verified against
GWTC-2.1 catalog paper §III and the bilby_pipe Asimov default config). The
audit memo `GW150914_mass_prior_audit.md` is correct. The §3.1 wording
("encompassing the LVK GWTC-2.1 [10,80] M_⊙ range, with no posterior mass near
either boundary") is honest and accurate. No action.

---

## 5. Proposed edits

### Tier-A — substantive (changes a claim)

| ID | Location | Current wording | Proposed wording | Justification |
|---|---|---|---|---|
| **A1** | Abstract, after "approximately 17% of the prior-induced shift." (line ≈84) | (no mention of median) | *"In addition, the binned-MAP \hzero stays at 70.5\kmsmpc but the weighted median moves from 77.6 to 87.6\kmsmpc under direct uniform-in-$d_L$ sampling, showing that the prior shifts the bulk of the posterior in a way the MAP alone obscures."* | Per §4d above. The m14 finding is in Table 5 only; it deserves abstract prominence because it independently supports the prior-sensitivity argument without relying on tail probabilities. |
| **A2** | §1 intro, paragraph at L97 ("That measurement has since been revisited from several directions…") | "…including superluminal-jet constraints on the binary inclination and improved peculiar-velocity modelling \citep{Hotokezaka2019,Nicolaou2020}." | "…including superluminal-jet constraints on the binary inclination \citep{Mooley2018Nature,Hotokezaka2019}, peculiar-velocity modelling \citep{Nicolaou2020,Mukherjee2021Velocity,HowlettDavis2020}, and updated late-time afterglow analyses giving $\hzero=75.5_{-5.4}^{+5.3}\kmsmpc$ at 7\% precision \citep{Palmese2024GW170817H0}. A complementary line of work argues that uncertainties in the binary viewing angle contribute a $>10\%$ systematic on GW170817 \hzero \citep{SalvareseChen2024}." | The intro currently misses (a) the most recent single-event GW170817 H₀ measurement (Palmese 2024, 7% precision), (b) the viewing-angle systematic literature that this paper's prior-sensitivity result speaks to directly. As-stands, a referee will ask "what about Palmese 2024 and Salvarese & Chen 2024?" |
| **A3** | §1 intro, paragraph at L103 (fast-PE landscape) | "Several recent developments make this constraint less severe: relative binning … \citep{Cornish2010,Zackay2018RelativeBinning}; differentiable waveform libraries in \jax \citep{Bradbury2018JAX,Edwards2023Ripple}; … GPU-native nested-sampling kernels \citep{BlackJAX,Yallup2025BlackJAXNS,Prathaban2025GPUSpeed}." | "Several recent developments make this constraint less severe: relative binning, also known as the heterodyned likelihood \citep{Cornish2010,Zackay2018RelativeBinning,Krishna2023RelativeBinningBilby}, reduces the effective frequency grid; differentiable waveform libraries in \jax \citep{Bradbury2018JAX,Edwards2023Ripple} enable end-to-end GPU evaluation of the likelihood; normalising-flow nested-sampling kernels in both CPU \citep{Williams2021Nessai} and GPU \citep{BlackJAX,Yallup2025BlackJAXNS,Prathaban2025GPUSpeed} settings retain the evidence estimates that nested sampling provides for free; and grid-based parallel-likelihood pipelines such as RIFT \citep{Pankow2015,Lange2018RIFT} provide a complementary CPU approach." | The current paragraph cites four GPU PE papers but omits nessai (the direct CPU-side normalising-flow NS competitor) and RIFT (a major LVK PE pipeline). Without them, the framing reads as if no comparable work exists on CPUs, which a referee will challenge. |
| **A4** | §4.1, end of "Effective-sample-size diagnostic" paragraph (line ≈236) | "This is the conventional symptom of importance-sampling weights concentrated on a small subset of the baseline draw, exactly the regime in which reweighting is known to be unreliable." | "This is the conventional symptom of importance-sampling weights concentrated on a small subset of the baseline draw, the regime in which reweighting is known to be unreliable \citep{Owen2013Book,Payne2019Reweighting,Vehtari2024PSIS}. The Pareto-smoothed importance-sampling $\hat{k}$ diagnostic of \citet{Vehtari2024PSIS} would flag the same failure quantitatively (with the standard $\hat{k}>0.7$ threshold) at no additional computational cost." | The current sentence is methodologically vague ("known to be unreliable") and cites only Speagle (a sampler paper, not an IS-failure reference). Adding Owen, Payne+2019 (the GW-specific reweighting paper), and Vehtari+2024 (the canonical k̂ diagnostic) anchors the claim to actual literature. |
| **A5** | §6.1, end of paragraph at L364 (Implications for bright-siren cosmology) | "The reweighted posterior's effective sample size, lower than the baseline's despite reweighting from the same draw, independently flags the coverage failure and is the diagnostic we recommend as a default check before any reweighted bright-siren \hzero summary is reported." | "The reweighted posterior's effective sample size, lower than the baseline's despite reweighting from the same draw, independently flags the coverage failure. We recommend this $n_{\rm eff}$ check, or equivalently the Pareto-smoothed importance-sampling $\hat{k}$ statistic of \citet{Vehtari2024PSIS}, as a default sanity test before any reweighted bright-siren \hzero summary is reported." | Tightens the methodological recommendation by naming the standard external diagnostic that does the same job more rigorously. |
| **A6** | §1 intro, opening paragraph, after "independent probes of the expansion rate." | (no review citation present) | "Recent overviews of gravitational-wave cosmology methods are given by \citet{Mastrogiovanni2024Review} and \citet{PalmeseMastrogiovanni2025}." | The intro currently has no review citation. MNRAS readers will expect one for a methodological paper that positions itself in this literature. |

### Tier-B — citations (adds or replaces a reference)

| ID | Location | Change | Justification |
|---|---|---|---|
| **B1** | `references.bib` L150–159 | Add `doi = {10.3847/1538-4357/acf5cd}` to `Wong2023Jim`. | DOI is missing; verified above. |
| **B2** | `references.bib` | Add new entries for the citations introduced by A1–A6: `Mooley2018Nature` (Nat 561, 355), `Mukherjee2021Velocity` (A&A 646, A65), `HowlettDavis2020` (MNRAS 492, 3803), `Palmese2024GW170817H0` (PRD 109, 063508), `SalvareseChen2024` (ApJL 974, L16), `Williams2021Nessai` (PRD 103, 103006), `Lange2018RIFT` (arXiv 1805.10457), `Pankow2015` (PRD 92, 023002), `Owen2013Book`, `Payne2019Reweighting` (PRD 100, 123017), `Vehtari2024PSIS` (JMLR 25, 72), `Mastrogiovanni2024Review` (Annalen der Physik), `PalmeseMastrogiovanni2025` (arXiv 2502.00239). | All sourced and verified in §2 above. Suggested BibTeX is in §6 below. |
| **B3** | `references.bib` L273–281 | **Delete** the duplicate `Abbott2017GW170817Properties` entry. | Confirmed duplicate of `Abbott2019GW170817Properties`; not cited anywhere. |
| **B4** | `references.bib` L134–140 | Resolve `Yang2026DataRelease`: either create the GitHub repo and Zenodo-mint a DOI (preferred per MNRAS data-policy norms), or fold the data-availability statement into the §Data Availability paragraph and remove the self-citation. | The current `note` field literally reads "(to be created at the listed URL)". A live-PDF referee will check the URL and find a 404. |
| **B5** | §1 intro (optional) | Add `\citet{Chen2018Forecast}` (Nature 562, 545) as supporting cite where prior-sensitivity at population level is mentioned (e.g. §6.1's "When bright-siren posteriors are combined over multiple events…"). | Grounds the implication in the canonical 2%-in-5-years forecast paper, which an MNRAS referee will be familiar with. |
| **B6** | §2.4 footnote at L150 | Add `\citet{Mandel2019Selection}` and `\citet{Vitale2022Selection}` next to the existing Finn–Chernoff and LVK Prospects cites. | Strengthens the H₀-independence-of-N_s claim with the canonical selection-effects framework references. |
| **B7** | (consider) `Abbott2021GWTC2p1` key | Rename to `Abbott2024GWTC2p1` for honesty (publication year is 2024). | Cosmetic; not required. |

### Tier-C — cosmetic (wording / positioning)

| ID | Location | Change | Justification |
|---|---|---|---|
| **C1** | Abstract, "the high-tail shift is therefore a property of the prior, not a data update." | Consider "the high-tail shift is therefore driven by the prior rather than by a data update." | "a property of" reads slightly oddly; "driven by … rather than" is more standard. Pure style. |
| **C2** | §5 first paragraph at L247 (bimodality intro) | Add "(see also \citealp{Finstad2018ViewingAngle} for the EM-counterpart-informed inclination posterior that breaks this degeneracy at the EM stage)" | Acknowledges the EM-counterpart literature on the same degeneracy. |
| **C3** | §6.4 "Scope of the performance claim" first sentence | Optional: add "(cf.\ the minute-scale Jim runtime of \citealp{Wong2023Jim} for a different sampler architecture; nested sampling pays a wall-clock premium for the evidence estimate)" after the pbilby disclaimer. | Pre-empts a referee question of why this paper's 13 min looks slow next to Wong+2023's 1 min: the answer is that NS gives ln Z and Jim doesn't, and we want that. |
| **C4** | §1, "the binary neutron-star merger GW170817 \citep{Abbott2017GW170817Discovery} is the canonical bright siren and the only confirmed example to date" | Consider softening to "remains the only confirmed example to date" — GW230529 is BBH-NS, not BBH-BNS bright-siren-with-counterpart, so this is still correct but the reader may wonder. | Pure clarity. |
| **C5** | Keywords (referee_response M-checklist OPEN) | Add "distance scale" to the keyword list (currently has "gravitational waves -- methods: data analysis -- cosmological parameters -- stars: neutron -- software: data analysis"). | Per the M-checklist item in referee_response.md; "methods: data analysis" + "software: data analysis" is partially redundant. |
| **C6** | Fig. 1 caption | Reword "Both panels" (m19 in referee_response). | One-word edit deferred from m19. |
| **C7** | §5 cross-ref at L155 | Add "IMR" qualifier to "the direct flat-in-z run reported in Section sec:prior" (m13). | One-word edit deferred from m13. |

---

## 6. Suggested BibTeX entries for B2

```bibtex
@article{Mooley2018Nature,
  author = {{Mooley}, K. P. and {Deller}, A. T. and {Gottlieb}, O. and
            {Nakar}, E. and {Hallinan}, G. and {Bourke}, S. and
            {Frail}, D. A. and {Horesh}, A. and {Corsi}, A. and {Hotokezaka}, K.},
  title = {{Superluminal motion of a relativistic jet in the neutron-star
           merger GW170817}},
  journal = {Nature},
  year = {2018},
  volume = {561},
  pages = {355--359},
  doi = {10.1038/s41586-018-0486-3}
}

@article{Mukherjee2021Velocity,
  author = {{Mukherjee}, S. and {Lavaux}, G. and {Bouchet}, F. R. and
            {Jasche}, J. and {Wandelt}, B. D. and {Nissanke}, S. and
            {Leclercq}, F. and {Hotokezaka}, K.},
  title = {{Velocity correction for Hubble constant measurements from
           standard sirens}},
  journal = {Astronomy and Astrophysics},
  year = {2021},
  volume = {646},
  pages = {A65},
  doi = {10.1051/0004-6361/201936724}
}

@article{HowlettDavis2020,
  author = {{Howlett}, C. and {Davis}, T. M.},
  title = {{Standard siren speeds: improving velocities in gravitational-wave
           measurements of $H_0$}},
  journal = {Monthly Notices of the Royal Astronomical Society},
  year = {2020},
  volume = {492},
  pages = {3803--3815},
  doi = {10.1093/mnras/staa049}
}

@article{Palmese2024GW170817H0,
  author = {{Palmese}, A. and {Kaur}, R. and {Hajela}, A. and {Margutti}, R. and
            {McDowell}, A. and {MacFadyen}, A.},
  title = {{Standard siren measurement of the Hubble constant using GW170817
           and the latest observations of the electromagnetic counterpart
           afterglow}},
  journal = {Physical Review D},
  year = {2024},
  volume = {109},
  pages = {063508},
  doi = {10.1103/PhysRevD.109.063508}
}

@article{SalvareseChen2024,
  author = {{Salvarese}, A. and {Chen}, H.-Y.},
  title = {{Mitigating the binary viewing angle bias for standard sirens}},
  journal = {The Astrophysical Journal Letters},
  year = {2024},
  volume = {974},
  pages = {L16},
  eprint = {2406.11126},
  archivePrefix = {arXiv}
}

@article{Williams2021Nessai,
  author = {{Williams}, M. J. and {Veitch}, J. and {Messenger}, C.},
  title = {{Nested sampling with normalising flows for gravitational-wave
           inference}},
  journal = {Physical Review D},
  year = {2021},
  volume = {103},
  pages = {103006},
  doi = {10.1103/PhysRevD.103.103006}
}

@misc{Lange2018RIFT,
  author = {{Lange}, J. and {O'Shaughnessy}, R. and {Rizzo}, M.},
  title = {{Rapid and accurate parameter inference for coalescing,
           precessing compact binaries}},
  year = {2018},
  eprint = {1805.10457},
  archivePrefix = {arXiv}
}

@article{Pankow2015,
  author = {{Pankow}, C. and {Brady}, P. and {Ochsner}, E. and
            {O'Shaughnessy}, R.},
  title = {{Novel scheme for rapid parallel parameter estimation of
           gravitational waves from compact binary coalescences}},
  journal = {Physical Review D},
  year = {2015},
  volume = {92},
  pages = {023002},
  doi = {10.1103/PhysRevD.92.023002}
}

@book{Owen2013Book,
  author = {{Owen}, A. B.},
  title = {{Monte Carlo theory, methods and examples}},
  year = {2013},
  publisher = {Self-published, Stanford},
  note = {Available at \url{https://artowen.su.domains/mc/}}
}

@article{Payne2019Reweighting,
  author = {{Payne}, E. and {Talbot}, C. and {Thrane}, E.},
  title = {{Higher order gravitational-wave modes with likelihood
           reweighting}},
  journal = {Physical Review D},
  year = {2019},
  volume = {100},
  pages = {123017},
  doi = {10.1103/PhysRevD.100.123017}
}

@article{Vehtari2024PSIS,
  author = {{Vehtari}, A. and {Simpson}, D. and {Gelman}, A. and
            {Yao}, Y. and {Gabry}, J.},
  title = {{Pareto Smoothed Importance Sampling}},
  journal = {Journal of Machine Learning Research},
  year = {2024},
  volume = {25},
  pages = {1--58},
  note = {Paper 72},
  eprint = {1507.02646},
  archivePrefix = {arXiv}
}

@article{Mastrogiovanni2024Review,
  author = {{Mastrogiovanni}, S. and {Mancarella}, M. and {Karathanasis}, C. and
            {Mukherjee}, S. and {Beirnaert}, F. and {others}},
  title = {{Cosmology with Gravitational Waves: A Review}},
  journal = {Annalen der Physik},
  year = {2024},
  doi = {10.1002/andp.202200180}
}

@misc{PalmeseMastrogiovanni2025,
  author = {{Palmese}, A. and {Mastrogiovanni}, S.},
  title = {{Gravitational Wave Cosmology}},
  year = {2025},
  eprint = {2502.00239},
  archivePrefix = {arXiv},
  note = {Chapter for the Encyclopedia of Astrophysics (Mandel, ed.; Elsevier
          Reference Module)}
}

@article{Chen2018Forecast,
  author = {{Chen}, H.-Y. and {Fishbach}, M. and {Holz}, D. E.},
  title = {{A two per cent Hubble constant measurement from standard sirens
           within five years}},
  journal = {Nature},
  year = {2018},
  volume = {562},
  pages = {545--547},
  doi = {10.1038/s41586-018-0606-0}
}

@article{Mandel2019Selection,
  author = {{Mandel}, I. and {Farr}, W. M. and {Gair}, J. R.},
  title = {{Extracting distribution parameters from multiple uncertain
           observations with selection biases}},
  journal = {Monthly Notices of the Royal Astronomical Society},
  year = {2019},
  volume = {486},
  pages = {1086--1093},
  doi = {10.1093/mnras/stz896}
}

@incollection{Vitale2022Selection,
  author = {{Vitale}, S. and {Gerosa}, D. and {Farr}, W. M. and
            {Taylor}, S. R.},
  title = {{Inferring the Properties of a Population of Compact Binaries in
           Presence of Selection Effects}},
  booktitle = {Handbook of Gravitational Wave Astronomy},
  editor = {{Bambi}, C. and {Katsanevas}, S. and {Kokkotas}, K. D.},
  publisher = {Springer},
  year = {2022},
  pages = {1--60},
  doi = {10.1007/978-981-15-4702-7_45-1}
}

@article{Finstad2018ViewingAngle,
  author = {{Finstad}, D. and {De}, S. and {Brown}, D. A. and
            {Berger}, E. and {Biwer}, C. M.},
  title = {{Measuring the Viewing Angle of GW170817 with Electromagnetic and
           Gravitational Waves}},
  journal = {The Astrophysical Journal Letters},
  year = {2018},
  volume = {860},
  pages = {L2},
  doi = {10.3847/2041-8213/aac6c1}
}
```

---

## 7. Positioning paragraph for the intro (≤120 words)

Drop-in candidate to slot after the current L97 paragraph (which ends
"…improved peculiar-velocity modelling \citep{Hotokezaka2019,Nicolaou2020}.")
or to absorb that paragraph into a fuller one:

> *GW170817 remains the only confirmed bright siren, and the literature it
> has spawned divides cleanly into two strands. One revisits the
> $\hzero$ measurement using better external inputs: improved
> peculiar-velocity modelling \citep{Nicolaou2020,Mukherjee2021Velocity,HowlettDavis2020},
> superluminal-jet inclination constraints \citep{Mooley2018Nature,Hotokezaka2019},
> and late-time multi-wavelength afterglow data, which together give
> $\hzero=75.5_{-5.4}^{+5.3}\,\rm km\,s^{-1}\,Mpc^{-1}$ at $\sim 7\%$ precision
> \citep{Palmese2024GW170817H0}. The other quantifies the residual
> systematics — viewing angle \citep{SalvareseChen2024} chief among them — that
> remain even at the current statistical floor. The methodological
> contribution of this paper sits in the second strand: we ask whether the
> distance-prior choice itself constitutes a systematic of the same order,
> and whether the original post-hoc reweighting treatment of that choice is
> faithful. Recent reviews \citep{Mastrogiovanni2024Review,PalmeseMastrogiovanni2025}
> frame this distinction as the central methodological question for the
> bright-siren cosmology programme in the third-generation detector era.*

(Word count: 119, including LaTeX macros.)

---

## 8. Out-of-scope items (raised in passing, not actioned)

- The `paper-reproduce/paper/main.tex` mirror is presumably kept in sync; the
  Tier-A/B edits should land in both.
- The `m17` (§6.3 TF host-localised wording) and `m20` (GW150914 σ-width
  quantification) items in `referee_response.md` are left for the lead author
  per that document; no new external evidence here.
- The deferred Tier-2 GPU runs in `launch_tier2.sh` (M2 seed ensemble, M4
  IMRX-mode Bayes factor, M7 n_mcmc sweep) are the right follow-ups for a
  resubmission; the current draft is honest about the gap and is referee-ready
  in that respect.
