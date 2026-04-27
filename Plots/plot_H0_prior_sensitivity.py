"""
GW170817 H_0 prior-sensitivity comparison — weighted histograms (no KDE).

Overlays the four prior variants for the chosen primary waveform with
sample-derived HPDs and a real LVK posterior curve (no shaded band).

Default waveform: IMRPhenomXAS_NRTidalv3 (the locked primary). When the
s14 sensitivity-sweep CSVs are not yet available the script falls back to
IMRPhenomD_NRTidalv2 (host-loc) so REVIEW.md figures keep regenerating
during the GPU run.

Variants:
  - Baseline (volumetric d_L^2 prior)
  - Flat-in-redshift (direct sampling)
  - Flat-in-redshift (reweighted from baseline)
  - Enlarged peculiar velocity (sigma_vp = 250 km/s)

Output: Results/gwtc1_phasemarg/plots/H0_prior_sensitivity.{pdf,png}
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _plot_utils import (
    OUT_DIR, RESULTS_DIR, COLORS, load_nested_csv,
    load_gwtc1_gw170817, derive_lvk_h0_samples,
    compute_hpd_samples, plot_h0_hist,
)
import numpy as np
import pandas as pd


def load_h0_w(csv):
    """(H_0 array, normalised weight array) for both nested-sampling and reweighted CSVs."""
    if 'reweighted' in csv.lower() or 'reweight' in os.path.basename(csv).lower():
        df = pd.read_csv(csv, low_memory=False)
        x = df['H_0'].to_numpy().astype(float)
        w = df['weight'].to_numpy().astype(float)
    else:
        s = load_nested_csv(csv)
        x = s['H_0'].to_numpy().astype(float)
        w = np.asarray(s.get_weights(), dtype=float)
    w = w / w.sum()
    return x, w


# Try the s14 IMRPhenomXAS_NRTidalv3 sensitivity sweep first; fall back to IMR host-loc
# when those files have not yet been produced by the GPU run.
XAS_BASE = 'Results/test_suite/s14__gw170817__imrphenomxas_nrtidalv3'
XAS_CSVS = [
    f'{XAS_BASE}__baseline__seed0000/samples.csv',
    f'{XAS_BASE}__flatz__seed0000/samples.csv',
    f'{XAS_BASE}__reweighted_flatz__seed0000/samples.csv',
    f'{XAS_BASE}__vp250__seed0000/samples.csv',
]

if all(os.path.exists(c) for c in XAS_CSVS):
    PRIMARY_TAG = 'IMRPhenomXAS_NRTidalv3'
    VARIANTS = [
        (r'XAS\_NRTv3 baseline ($\pi(d_L)\propto d_L^2$)',
         XAS_CSVS[0], COLORS['imr_baseline']),
        (r'XAS\_NRTv3 flat-in-$z$ (direct)',
         XAS_CSVS[1], COLORS['flatZ']),
        (r'XAS\_NRTv3 flat-in-$z$ (reweighted)',
         XAS_CSVS[2], COLORS['reweighted']),
        (r'XAS\_NRTv3 $\sigma_{v_p}=250\,\rm km\,s^{-1}$',
         XAS_CSVS[3], COLORS['vp250']),
    ]
else:
    PRIMARY_TAG = 'IMRPhenomD_NRTidalv2 (host-loc) — XAS sweep not yet on disk'
    print(f"  NOTE: {XAS_BASE}__*/samples.csv not found; using IMR host-loc fallback.")
    VARIANTS = [
        (r'NRTv2 baseline ($\pi(d_L)\propto d_L^2$)',
         'Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv',
         COLORS['imr_baseline']),
        (r'NRTv2 flat-in-$z$ (direct)',
         'Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_flatZ.csv',
         COLORS['flatZ']),
        (r'NRTv2 flat-in-$z$ (reweighted)',
         'Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv',
         COLORS['reweighted']),
        (r'NRTv2 $\sigma_{v_p}=250\,\rm km\,s^{-1}$',
         'Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_vp250.csv',
         COLORS['vp250']),
    ]

print(f"  Primary waveform for prior sensitivity: {PRIMARY_TAG}\n")

runs = []
for label, csv, col in VARIANTS:
    if not os.path.exists(csv):
        print(f"  WARNING: missing {csv}"); continue
    x, w = load_h0_w(csv)
    p120 = float((w[x > 120]).sum())
    p150 = float((w[x > 150]).sum())
    print(f"  {label:55s}  P(>120)={p120:.3f}  P(>150)={p150:.3f}")
    runs.append(((x, w), label, col))

# LVK posterior — same standard-siren mapping as elsewhere; no shaded band.
print("  Loading LVK GWTC-1 GW170817 d_L posterior for the LVK overlay...")
lvk = load_gwtc1_gw170817(columns=['d_L'])
lvk_h0 = derive_lvk_h0_samples(lvk['d_L'].to_numpy(), rng=np.random.default_rng(170817))
lvk_w = np.ones(len(lvk_h0))
runs.append(((lvk_h0, lvk_w), r'LVK GWTC-1 (Abbott+2017)', '0.25'))

plot_h0_hist(runs, 'H0_prior_sensitivity',
             xlim=(40, 220), bins=110,
             add_planck_shoes=True, lvk_band=False, hpd_lines=False)
