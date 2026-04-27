"""
GW170817 H_0 posterior — three-waveform comparison plus LVK actual posterior.

Overlays weighted-histogram H_0 posteriors (sample-derived HPDs, no KDE):
  - IMRPhenomXAS_NRTidalv3        (s07 LVK-bounds baseline) — primary
  - IMRPhenomD_NRTidalv2          (s07 LVK-bounds baseline) — anchor
  - TaylorF2  (host-localised, gwtc1_phasemarg)            — family check
  - LVK GW170817 GWTC-1 IMRPhenomPv2_NRTidal samples       — derived H_0

The LVK curve is *not* an HPD band — it is the LVK GWTC-1 d_L posterior
mapped through this work's standard-siren model
(v_obs ~ N(v_p + H_0 d_L, 72), v_p ~ N(310, 150)) so the comparison is
apples-to-apples. IMRPhenomPv2 (no tides) is intentionally dropped from the
main figure; the precession-only systematic stays in the open-source
test_suite (s07__imrphenompv2__baseline_lvkbounds).

Output: Results/gwtc1_phasemarg/plots/H0_waveform_comparison.{pdf,png}
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _plot_utils import (
    OUT_DIR, RESULTS_DIR, COLORS, load_nested_csv,
    load_gwtc1_gw170817, derive_lvk_h0_samples, plot_h0_hist,
)
import numpy as np

CSV_NRTV2     = 'Results/test_suite/s07__gw170817__imrphenomd_nrtidalv2__baseline_lvkbounds__seed0000/samples.csv'
CSV_XAS_NRTV3 = 'Results/test_suite/s07__gw170817__imrphenomxas_nrtidalv3__baseline_lvkbounds__seed0000/samples.csv'
CSV_TF2       = os.path.join(RESULTS_DIR,
    'gwtc1_phasemarg/PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv')

runs = []
for csv, label, colour in [
    (CSV_XAS_NRTV3, r'IMRPhenomXAS\_NRTidalv3 (this work)',  COLORS['flatZ']),
    (CSV_NRTV2,     r'IMRPhenomD\_NRTidalv2 (this work)',    COLORS['imr_baseline']),
    (CSV_TF2,       r'TaylorF2 (this work)',                  COLORS['tf2_baseline']),
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
runs.append(((lvk_h0, lvk_w), r'LVK GWTC-1 (Abbott+2017, this work\'s $v_p$ model)', '0.25'))

if runs:
    plot_h0_hist(runs, 'H0_waveform_comparison',
                 xlim=(40, 180), bins=80,
                 add_planck_shoes=True, lvk_band=False, hpd_lines=True)
print("\nDone.")
