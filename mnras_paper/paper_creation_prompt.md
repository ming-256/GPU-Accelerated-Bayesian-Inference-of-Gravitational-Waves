# Prompt for Drafting the MNRAS Paper

Use this prompt to generate or expand the manuscript. It is written to prevent invented results and to keep the paper anchored to the repository.

---

## Prompt

You are drafting a **science-first MNRAS paper** on gravitational-wave cosmology from **GW170817**, using only the material and data available in this repository.

### Objective

Write a draft manuscript, or a section of it, for an MNRAS-style paper whose central scientific claim is:

- a GPU-accelerated nested-sampling pipeline makes it practical to perform **direct prior-sensitivity tests** for the GW170817 bright-siren measurement of the Hubble constant;
- the main science result is that **direct sampling under a flat-in-redshift prior produces a materially different H0 posterior than post-hoc reweighting**, implying that reweighting can understate prior sensitivity when the target prior up-weights poorly sampled regions.

The paper must be led by the astrophysics and cosmology. The acceleration and implementation details are enabling methods, not the main story.

### Hard Constraints

1. **Do not hallucinate any numbers, runs, figures, links, tables, or files.**
2. **Use only repository data for all numerical claims.**
3. **Do not import scientific results from outside papers into the Results section.**
4. External literature may be used only for:
   - motivation;
   - methodological context;
   - comparison of writing style and structure;
   - citations for background statements.
5. If a value is not explicitly available in the repository, write `TODO` rather than inventing it.
6. If a figure, table, or derived file has provenance caveats, preserve that caveat in the draft notes.
7. Do not claim any CPU-vs-GPU comparison beyond what is actually supported by repository files.

### Writing Style

Follow **MNRAS paper** conventions:

- concise abstract;
- numbered sections beginning with `Introduction` and ending with `Conclusions`;
- science-first framing;
- methods section kept compact unless required for reproducibility;
- results section built around figures and quantitative comparisons;
- restrained claims, especially for performance and model comparison.

Use these official MNRAS instructions for layout/style expectations:

- MNRAS Instructions to Authors: https://academic.oup.com/mnras/pages/general_instructions

Important MNRAS-relevant constraints visible there:

- the first numbered section should be `Introduction`;
- the last numbered section should present the authors’ conclusions;
- include a `Data availability` statement;
- make data/software provenance clear.

### Similar Papers to Emulate for Tone and Structure

Use the following papers only as **style and framing references**, not as sources of numerical results for this manuscript:

1. Debiasing cosmic gravitational wave sirens  
   https://academic.oup.com/mnras/article/491/3/3983/5645258

2. Standard siren speeds: improving velocities in gravitational-wave measurements of H0  
   https://academic.oup.com/mnras/article-abstract/492/3/3803/5700291

3. A dark siren measurement of the Hubble constant using gravitational wave events from the first three LIGO/Virgo observing runs and DELVE  
   https://academic.oup.com/mnras/article/528/2/3249/7513767

4. Directly inferring cosmology and the neutron-star equation of state from gravitational-wave mergers  
   https://academic.oup.com/mnras/article-abstract/543/4/3673/8269932

5. Bayesian inference for compact binary coalescences with bilby: validation and application to the first LIGO-Virgo gravitational-wave transient catalogue  
   https://academic.oup.com/mnras/article/499/3/3295/5909620

Use them to imitate:

- how the introduction moves from cosmology motivation to the specific event/problem;
- how methods are summarized without overwhelming the science;
- how results sections are organized around a small number of quantitative claims;
- how discussion sections separate robustness, limitations, and future use cases.

### Repository Sources of Truth

Use these files as the authoritative basis for the manuscript.

#### Narrative and project framing

- `Final_Report.pdf`
- `paper_knowledge_base/paper_strategy.md`
- `mnras_paper/main.tex`
- `mnras_paper/result_inventory.md`

#### Provenance map: which script created which output

- `paper_knowledge_base/result_link_index.md`

This file is the master guide for linking:

- result CSVs;
- plotting scripts;
- logs;
- summary tables;
- HDF5 references.

#### Primary numerical summary files

- `Results/gwtc1_phasemarg/summary_stats.csv`
- `Results/gwtc1_phasemarg/evidence_table.csv`
- `Results/gwtc1_phasemarg/waveform_systematics.csv`
- `Results/scaling_study/scaling_summary.csv`
- `paper_knowledge_base/a100_run_data.md`

#### Main posterior/result CSVs

- `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv`
- `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_flatZ.csv`
- `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv`
- `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_vp250.csv`
- `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv`
- `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_flatZ.csv`
- `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv`
- `Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_vp250.csv`
- `Results/gwtc1_phasemarg/PhaseMarg_Unheterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1.csv`
- `Results/gwtc1_phasemarg/PhaseMarg_Unheterodyned_TaylorF2_local_psd-gwtc1.csv`
- `Results/gwtc1_phasemarg/GW15_PhaseMarg_Heterodyned_IMRPhenomD_local_psd-gwtc2p1_ref-gwtc1.csv`

#### Reference posterior / strain data

- `Results/GW170817_GWTC-1.hdf5`
- `EventData/GWOSC/GW170817/*.hdf5`
- `EventData/GWOSC/GW150914/*.hdf5`

### Primary Figures to Build the Paper Around

Prefer these figures for the main text:

1. `Results/gwtc1_phasemarg/plots/H0_baseline_IMRPhenomD.pdf`
2. `Results/gwtc1_phasemarg/plots/H0_IMRPhenomD_reweighted.pdf`
3. `Results/gwtc1_phasemarg/plots/dL_reweight_comparison_IMRPhenomD_NRTidalv2.pdf`
4. `Results/gwtc1_phasemarg/plots/corner_combined_waveforms.pdf`
5. `Results/gwtc1_phasemarg/plots/corner_IMRPhenomD_hetero_vs_unhetero.pdf`
6. `Results/gwtc1_phasemarg/plots/scaling_study.pdf`
7. `Results/gwtc1_phasemarg/plots/corner_GW150914.pdf`

Use appendix/supporting figures only if needed:

- `Results/gwtc1_phasemarg/plots/H0_TaylorF2_reweighted.pdf`
- `Results/gwtc1_phasemarg/plots/corner_reweighted_vs_sampled_flatZ_IMRPhenomD.pdf`
- `Results/gwtc1_phasemarg/plots/prior_functions_IMRPhenomD_NRTidalv2.pdf`

### Result Priorities

The manuscript should emphasize these scientific points, in this order:

1. **Baseline GW170817 H0 inference** with the primary IMRPhenomD_NRTidalv2 analysis.
2. **Prior sensitivity**:
   - baseline volumetric-distance prior;
   - direct flat-in-redshift run;
   - reweighted flat-in-redshift comparison;
   - sigma_vp = 250 km/s variant.
3. **Mechanism of the prior effect** using the luminosity-distance posterior comparison.
4. **Waveform cross-check** using TaylorF2.
5. **Validation** against GW150914 and against unheterodyned GW170817 runs.
6. **Performance/scaling** only after the science case is established.

### What the Draft Must Explicitly Say

- GW170817 is the motivating bright siren.
- The paper is not claiming a new world-leading H0 measurement from one event.
- The scientific value is a **robustness study** enabled by fast direct inference.
- Reweighting is a useful diagnostic but is not always sufficient when the target prior changes support in poorly sampled regions.
- Waveform dependence appears smaller than the distance-prior effect for the current runs.
- Evidence differences among prior variants are modest and should not be oversold.

### What the Draft Must Not Say

- Do not say the pipeline “solves” the Hubble tension.
- Do not imply that GPU acceleration alone is the main scientific contribution.
- Do not compare against a single-core CPU baseline.
- Do not claim a final like-for-like `parallel_bilby` benchmark unless one is explicitly present in the repository output used.
- Do not claim precession is included if the chosen waveform does not include it.

### Known Caveats That Must Be Respected

Carry these caveats into notes/TODOs where relevant:

1. `Results/scaling_study/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv` is overwritten by different scaling runs; use `Results/scaling_study/scaling_summary.csv` and scaling logs for runtime provenance.
2. `Results/gwtc1_phasemarg/prior_sensitivity.csv`, `prior_sensitivity_full.json`, and `prior_sensitivity_pdfs.csv` can be overwritten when regenerated for a different waveform.
3. The thesis-era L4 results are background context only; use A100 repository outputs for current manuscript numbers.
4. The `20000` live-point scaling row should be treated cautiously until fully explained.

### Preferred Paper Structure

Write the paper using roughly this structure:

1. `Introduction`
   - H0 tension and why standard sirens matter
   - GW170817 as the key bright siren
   - why prior robustness matters scientifically
   - why repeated full inference is computationally hard
   - what this paper does

2. `Method`
   - Bayesian and nested-sampling setup
   - heterodyned likelihood / relative binning
   - GW170817 H0 likelihood with host-galaxy velocity treatment
   - priors and waveform choices

3. `Validation`
   - GW150914 check
   - GW170817 source-parameter comparison to reference posteriors
   - heterodyned versus unheterodyned consistency

4. `Results`
   - baseline H0 posterior
   - prior sensitivity
   - direct versus reweighted flat-in-z comparison
   - distance-posterior explanation
   - waveform cross-check
   - evidence summary with restrained interpretation

5. `Performance`
   - A100 runtime
   - scaling with live points
   - why runtime matters for scientific robustness studies

6. `Discussion`
   - implications for future bright sirens
   - limitations
   - where direct reruns are preferable to reweighting

7. `Conclusions`

8. `Acknowledgements`

9. `Data availability`

### Output Requirements

When generating manuscript text:

- cite exact repository files used for each quantitative statement in drafting notes;
- if producing prose only, add bracketed drafting notes like `[Source: Results/gwtc1_phasemarg/summary_stats.csv]`;
- if producing LaTeX, keep citation placeholders or `TODO` markers where bibliography entries still need verification;
- prefer exact filenames over vague references such as “the results file”;
- keep abstract and conclusion claims tightly matched to available evidence.

### Requested Deliverable

Produce one of the following, depending on the instruction given with this prompt:

- a full first manuscript draft;
- a revised abstract;
- a section-by-section outline;
- a results section draft;
- figure captions tied to actual files;
- a revision pass on `mnras_paper/main.tex`.

In all cases, stay inside the evidence available in this repository.

---

## Suggested First Use

“Using the prompt above, write a revised MNRAS-style outline plus abstract and Introduction for this paper. Base all scientific claims only on the repository files listed above, and attach `[Source: ...]` notes after each quantitative claim.”
