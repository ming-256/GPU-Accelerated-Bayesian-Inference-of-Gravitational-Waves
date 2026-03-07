# MNRAS Reviewer Response Strategy

## Context

The co-authored paper (Prathaban et al., arXiv:2509.04336) was submitted to MNRAS and
rejected. The reviewers suggested RASTI (Research and Applications of Scientific and
Technological Instruments) as a more appropriate venue.

## Reviewer Criticisms (Substantive)

### Criticism 1: Inaccurate description of CPU parallelisation

**The issue:** The introduction described existing CPU methods (pBilby/dynesty) inaccurately,
understating their parallelisation capabilities.

**How to address in this paper:**
- Accurately describe pBilby's parallelisation: it parallelises both likelihood evaluation (across frequency bins) and can run multiple parallel chains via MPI
- Cite the Bilby Zenodo record properly
- Frame our advantage as being about the *scaling regime* — when combining heterodyning with high live-point counts (thousands), the GPU enters a performance regime where each likelihood evaluation is so cheap that the bottleneck shifts entirely to the sampler, and massive inter-sample parallelism becomes the dominant factor
- Do NOT claim CPU methods are serial or poorly parallelised
- DO emphasise that CPU parallelism has practical limits (core counts, MPI overhead) while GPU parallelism scales with the hardware's native architecture

**Suggested introduction language (paraphrased):**
> Standard tools such as Bilby (Ashton et al. 2019; [Zenodo DOI]) with parallel_bilby
> can distribute inference across hundreds of CPU cores, achieving significant speedups
> through both intra-likelihood parallelisation and multi-chain nested sampling. These
> methods represent the current state of the art for production GW inference. However,
> the parallel architecture of GPUs offers a complementary scaling regime...

### Criticism 2: Speedup claims and cost accounting

**The issue:** The abstract compared GPU runtime against a single-core CPU baseline, which
is unrealistic. CPU-hours and GPU-hours were treated as equivalent, which is misleading
given the different hardware costs.

**How to address in this paper:**
- **NEVER compare against a single-core baseline.** Always compare against the realistic multi-core pBilby deployment (e.g., 532 MPI ranks on CSD3, or whatever the planned pBilby run uses).
- **Do NOT put dollar costs in the abstract.** The abstract should report wall-clock times on specific hardware.
- **Include a cost table in the results section** with proper qualifications:
  - Google Cloud on-demand rates (date-stamped, with caveat that prices fluctuate)
  - Academic HPC allocation equivalents (DiRAC rates if available)
  - Note that GPU costs are trending downward relative to CPU costs
- **Frame the cost discussion honestly:**
  - At comparable settings, GPU and CPU approaches achieve similar cost
  - The advantage is in the scaling regime: with heterodyning, high live-point GPU runs enter a regime where the equivalent CPU analysis would require impractical core counts
- **Use the CSD3 comparison point:** 4,256 cores is one CSD3 allocation. If GPU at 5000 live points with heterodyning completes in ~13 minutes, and the CPU equivalent would require >4,256 cores for comparable wall-clock time, that's a meaningful comparison.

**Our position (internal, not for the paper):**
- Runtime on specific hardware is a static, reproducible quantity; dollar costs fluctuate
- We are already more rigorous about cost accounting than most ML literature
- The reviewer's expectation of dollar costs in an abstract is unusual
- But: there is a middle ground on framing that satisfies reviewers without conceding entirely

**Suggested abstract framing:**
> "We perform a careful like-for-like comparison with standard CPU methods, achieving
> consistent posteriors and evidence estimates. At standard settings, the GPU analysis
> completes in [X] minutes wall-clock time on a single A100 GPU. When combined with
> the heterodyned likelihood at 5,000 live points, the full H_0 analysis completes in
> approximately 13 minutes — a performance regime that is complementary to, and in
> some configurations surpasses, current CPU cluster deployments."

### Implicit Criticism: Scope (methods vs science)

**The issue:** MNRAS reviewers saw the co-authored paper as a methods/software paper,
not an astrophysics paper.

**How this paper avoids the same fate:**
- Lead with H_0 inference (unambiguously MNRAS-scope cosmology)
- The prior sensitivity critique of Abbott et al. (2017b) is a scientific finding
- Waveform systematics are astrophysical
- Computational performance is presented as enabling, not as the primary contribution
- The paper's core claim is: "fast inference enables robust prior sensitivity analysis that
  was previously impractical, and this reveals that a key conclusion of the landmark
  GW170817 H_0 paper was an artifact of methodology"

## Additional Defensive Points

### On the reviewer potentially being a pBilby author
- The review focused disproportionately on the description of pBilby
- We should be scrupulously fair to pBilby in the introduction
- Frame GPU acceleration as complementary, not as replacing CPU methods
- Acknowledge pBilby's strengths: mature, well-validated, community standard

### On the scope question
- This paper has three layers of MNRAS-appropriate content:
  1. H_0 cosmology (bright siren measurement)
  2. Prior sensitivity analysis (methodological critique with astrophysical implications)
  3. Waveform systematics
- The computational performance section is shorter and positioned as supporting

### On reproducibility
- All code is public (GitHub repository)
- All data is from GWOSC (public)
- Hardware is commercially available (Google Cloud A100)
- Run configurations are specified (n_live, priors, waveforms)
