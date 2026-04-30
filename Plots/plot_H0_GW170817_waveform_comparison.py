"""
GW170817 H_0 posterior — slim two-waveform comparison plus LVK actual posterior.

Overlays the two NR-calibrated tidal waveforms used as primary/anchor
plus the LVK GW170817 GWTC-1 IMRPhenomPv2_NRTidal posterior mapped
through this work's standard-siren model:
  - IMRPhenomXAS_NRTidalv3   (s07 LVK-bounds baseline)  — primary
  - IMRPhenomD_NRTidalv2     (s07 LVK-bounds baseline)  — anchor
  - LVK GWTC-1 (Abbott+2017) — derived H_0 from d_L posterior

TaylorF2 and IMRPhenomPv2 are intentionally dropped from the main figure;
both stay in the open-source test_suite (TaylorF2 in gwtc1_phasemarg,
IMRPhenomPv2 in s07__imrphenompv2__baseline_lvkbounds).

Output: Results/gwtc1_phasemarg/plots/H0_waveform_comparison.{pdf,png}
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _plot_utils import (
    OUT_DIR, RESULTS_DIR, COLORS, load_nested_csv,
    load_gwtc1_gw170817, derive_lvk_h0_samples, plot_h0,
)
import numpy as np

CSV_NRTV2     = 'Results/test_suite/s07__gw170817__imrphenomd_nrtidalv2__baseline_lvkbounds__seed0000/samples.csv'
CSV_XAS_NRTV3 = 'Results/test_suite/s07__gw170817__imrphenomxas_nrtidalv3__baseline_lvkbounds__seed0000/samples.csv'

runs = []
for csv, label, colour in [
    (CSV_XAS_NRTV3, r'IMRPhenomXAS\_NRTidalv3 (Jim-based work)',  COLORS['flatZ']),
]:
    if os.path.exists(csv):
        s = load_nested_csv(csv)
        runs.append((s, label, colour))
    else:
        print(f"  WARNING: missing {csv}")

# Load LVK GWTC-1 GW170817 d_L posterior and derive H_0 under our standard-siren model.
print("  Loading LVK GWTC-1 GW170817 (IMRPhenomPv2_NRTidal lowSpin) posterior...")
lvk = load_gwtc1_gw170817(columns=['d_L'])
lvk_h0 = derive_lvk_h0_samples(lvk['d_L'].to_numpy(), rng=np.random.default_rng(170817))
lvk_w = np.ones(len(lvk_h0))
print(f"  Derived {len(lvk_h0)} LVK H_0 samples (median {float(np.median(lvk_h0)):.1f} km/s/Mpc)")
runs.append(((lvk_h0, lvk_w), r'IMRPhenomPv2\_NRTidal (LVK)', '0.25'))

if runs:
    # KDE variant per user request (overrides hist default for this figure).
    # plot_h0 expects dicts with 'H_0' and 'weights' keys.
    runs_kde = []
    for entry in runs:
        s, lab, col = entry
        if isinstance(s, tuple):
            d = {'H_0': np.asarray(s[0]), 'weights': np.asarray(s[1])}
        else:
            d = {'H_0': s['H_0'].to_numpy(), 'weights': np.asarray(s.get_weights())}
        runs_kde.append((d, lab, col))
    plot_h0(runs_kde, 'H0_waveform_comparison', xlim=(40, 180))
print("\nDone.")
