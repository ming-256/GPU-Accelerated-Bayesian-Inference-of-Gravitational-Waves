"""
GW170817 H_0 posterior — two-waveform comparison plus published LVK reference.

Overlays the two waveforms reported in Table~\\ref{tab:waveform-h0} and
references the published Abbott+2017 GW170817 H_0 = 70 +12/-8 km/s/Mpc
band as a vertical reference (no derived posterior).

  - IMRPhenomXAS_NRTidalv3   (s07 LVK-bounds baseline)  — primary
  - TaylorF2                 (s07 LVK-bounds baseline)  — family check
  - Abbott+2017 published H_0 band                       — literature reference

IMRPhenomD_NRTidalv2 (anchor) results are reported in Appendix~\\ref{app:robustness}
only and stay out of this figure.

Output: Results/gwtc1_phasemarg/plots/H0_waveform_comparison.{pdf,png}
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _plot_utils import (
    OUT_DIR, RESULTS_DIR, COLORS, load_nested_csv, plot_h0_hist,
)

CSV_XAS_NRTV3   = 'Results/test_suite/s07__gw170817__imrphenomxas_nrtidalv3__baseline_lvkbounds__seed0000/samples.csv'
CSV_TF2_LVK     = 'Results/test_suite/s07__gw170817__taylorf2__baseline_lvkbounds__seed0000/samples.csv'

runs = []
for csv, label, colour in [
    (CSV_XAS_NRTV3, 'this work (IMRPhenomXAS_NRTidalv3)', COLORS['imr_baseline']),
    (CSV_TF2_LVK,   'this work (TaylorF2)',               COLORS['tf2_baseline']),
]:
    if os.path.exists(csv):
        s = load_nested_csv(csv)
        runs.append((s, label, colour))
    else:
        print(f"  WARNING: missing {csv}")

if runs:
    plot_h0_hist(runs, 'H0_waveform_comparison', xlim=(40, 180), bins=140,
                 add_planck_shoes=True, lvk_band=True, hpd_lines=True)
print("\nDone.")
