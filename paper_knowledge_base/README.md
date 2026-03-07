# Paper Knowledge Base

This folder contains the complete knowledge base for drafting the MNRAS paper on
GPU-accelerated nested sampling applied to GW170817 and H_0 inference.

## Index

| File | Contents |
|------|----------|
| `project_context.md` | Project overview, thesis summary, co-authored paper summary, relationship between them |
| `paper_strategy.md` | MNRAS targeting strategy, paper structure, narrative arc, what results are needed |
| `reviewer_response.md` | MNRAS rejection context for co-authored paper, how to address criticisms |
| `a100_run_data.md` | All A100 run timing data, parsed into tables with analysis |
| `hardware_platforms.md` | Hardware specs (A100, L4, CSD3), cost comparisons, Google Cloud pricing |
| `codebase_reference.md` | Key files, scripts, analysis configurations, output locations |
| `thesis_results_summary.md` | Key results from the master's thesis (Final_Report), superseded by new runs |
| `coauthored_paper_summary.md` | Summary of Prathaban et al. (2509.04336v1), the BBH-focused co-authored paper |
| `waveform_recommendation.md` | Waveform choice analysis: IMRPhenomD_NRTidalv2 recommended for pBilby comparison |

## Key Facts (Quick Reference)

- **Target journal:** MNRAS (Monthly Notices of the Royal Astronomical Society)
- **Paper focus:** GPU-accelerated nested sampling applied to GW170817 BNS, H_0 estimation, prior sensitivity
- **Co-authored paper:** Prathaban et al. 2025, "Gravitational-wave inference at GPU speed" (arXiv:2509.04336)
- **Hardware:** NVIDIA Tesla A100 (a2-highgpu-1g, Google Cloud)
- **Thesis hardware:** NVIDIA L4 (Google Cloud)
- **Framework:** JAX + BlackJAX nested sampling + Ripple waveforms
- **Key scientific result:** Prior reweighting critique — direct sampling under flat-in-z prior reveals materially different H_0 posterior vs reweighted result from Abbott et al. (2017b)
- **Key technical result:** Heterodyned likelihood at 5000 live points completes GW170817 H_0 inference in ~13-15 minutes (A100), a regime intractable on CPUs

## Author Information

- **Lead author:** Ming Yang (St. John's College, Cambridge)
- **Supervisor:** Will Handley (Institute of Astronomy / Kavli Institute for Cosmology, Cambridge)
- **Co-authors on Prathaban et al.:** Metha Prathaban, David Yallup, James Alvey, Will Templeton, Will Handley
