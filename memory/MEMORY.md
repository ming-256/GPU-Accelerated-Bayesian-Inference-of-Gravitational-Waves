# Memory Index

- [Histograms over KDEs](feedback_kde_vs_histograms.md) — user wants weighted histograms + sample-HPDs for 1-D posteriors; KDE only OK for 2-D contours.
- [LVK posteriors as data](feedback_lvk_posteriors_as_data.md) — never plot LVK as HPD band/marker; always overlay actual samples from `Results/GW170817_GWTC-1.hdf5` or `EventData/GWOSC/GW150914/...XPHM...h5`.
- [MNRAS paper strategy](project_paper_strategy.md) — Abbott+2017 reproduction framing; locked waveform decisions (XPHM for GW150914 validation, XAS+IMR+TF2 for GW170817 primary, drop Pv2 from main).
- [Sky-prior naming pitfall](project_sky_prior_naming.md) — every heterodyned run is already full-sky; `_local_` in filenames means data source, not sky restriction. Don't call the hetero suite "host-localised" in writing.
- [Paper repo status](project_repo_status.md) — current submission state: paper compiles clean, reproducible repo at paper-reproduce/, remaining TODOs (Acknowledgements, Zenodo DOI, bib verification).
- [Abbott+2017 data files](project_abbott2017_data.md) — actual H0 posterior CSVs from LIGO-P1700296 are in the project root; used in Figures 2 and 4.
