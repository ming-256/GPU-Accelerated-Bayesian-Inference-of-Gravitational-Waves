"""
GW170817 H_0 posterior — three-waveform comparison plus LVK actual posterior.

Overlays the three waveforms reported in Table~\\ref{tab:waveform-h0} plus
the LVK GW170817 GWTC-1 IMRPhenomPv2_NRTidal posterior mapped through this
work's standard-siren model:
  - IMRPhenomXAS_NRTidalv3   (s07 LVK-bounds baseline)               — primary
  - IMRPhenomD_NRTidalv2     (s07 LVK-bounds baseline)               — anchor
  - TaylorF2                 (gwtc1_phasemarg baseline, default mass) — family check
  - LVK GWTC-1 (Abbott+2017) — derived H_0 from d_L posterior

IMRPhenomPv2 (no tides) is reported inline only and stays out of this figure
(see s07__imrphenompv2__baseline_lvkbounds in the test_suite).

Output: Results/gwtc1_phasemarg/plots/H0_waveform_comparison.{pdf,png}
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _plot_utils import (
    OUT_DIR, RESULTS_DIR, COLORS, load_nested_csv,
    load_gwtc1_gw170817, derive_lvk_h0_samples, plot_h0,
)
import numpy as np

CSV_XAS_NRTV3   = 'Results/test_suite/s07__gw170817__imrphenomxas_nrtidalv3__baseline_lvkbounds__seed0000/samples.csv'
CSV_NRTV2       = 'Results/test_suite/s07__gw170817__imrphenomd_nrtidalv2__baseline_lvkbounds__seed0000/samples.csv'
# Prefer the LVK-bounds TF2 run (session_07b) once it exists; otherwise fall
# back to the default-mass TF2 baseline. The fallback's prior set differs from
# XAS/IMR — once session_07b finishes the figure becomes a like-for-like trio.
CSV_TF2_LVK     = 'Results/test_suite/s07__gw170817__taylorf2__baseline_lvkbounds__seed0000/samples.csv'
CSV_TF2_DEFAULT = 'Results/gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv'
CSV_TF2 = CSV_TF2_LVK if os.path.exists(CSV_TF2_LVK) else CSV_TF2_DEFAULT

runs = []
for csv, label, colour in [
    (CSV_XAS_NRTV3, 'this work (IMRPhenomXAS_NRTidalv3)',  COLORS['flatZ']),
    (CSV_NRTV2,     'this work (IMRPhenomD_NRTidalv2)',    COLORS['imr_baseline']),
    (CSV_TF2,       'this work (TaylorF2)',                COLORS['tf2_baseline']),
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
runs.append(((lvk_h0, lvk_w), 'GWTC-1 IMRPhenomPv2_NRTidal (mapped)', '0.25'))

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
