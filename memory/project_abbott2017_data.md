---
name: Abbott+2017 data files
description: Location and contents of Abbott+2017 public H0 posterior data (LIGO-P1700296) downloaded to project root
type: project
---

Abbott+2017 (LIGO-P1700296) public data release CSVs are in the project root:
- `Figure1.csv` — H0_samples: main H0 posterior (IMRPhenomPv2_NRTidal, host-galaxy prior), 131072 samples
- `Figure2.csv` — H0_samples, cosiota_samples: joint H0 / cos(iota) posterior
- `Figure3.csv` — cosiota_samples, planck_cosiota_samples, shoes_cosiota_samples: inclination comparison
- `ExtendedDataFigure2.csv` — H0_samples, flat_z_H0_samples, 250kms_uncert_H0_samples: prior variant comparison
- `LIGO-P1700296.pdf` — the paper itself

**Why:** Overlay actual posterior distributions in Figures 2 and 4 instead of a grey numerical band.
**How to apply:** Load with `pd.read_csv('Figure1.csv')['H0_samples']` using uniform weights. Shown as grey dashed curve in Figure 4 (H0_waveform_comparison) and Figure 2 panel (a). The Abbott+2017 posterior is narrower than our volumetric-prior runs because they used a host-galaxy-localised d_L prior.
