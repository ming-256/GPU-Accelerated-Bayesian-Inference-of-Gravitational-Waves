"""
Summary H_0 posterior plot: all available methods overlaid.

Provides an overview of how H_0 inference varies across:
  - heterodyned baseline
  - unheterodyned standard
  - unheterodyned small H_0 prior
  - sampled flat-in-z
  - reweighted flat-in-z

Only IMRPhenomD_NRTidalv2 is shown for clarity.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _plot_utils import *

RESULTS_PHASEMARG = os.path.join(RESULTS_DIR, 'gwtc1_phasemarg')

FILES = [
    (os.path.join(RESULTS_PHASEMARG,
        'PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv'),
     'Heterodyned baseline', 'tab:orange', 'nested'),
    (os.path.join(RESULTS_PHASEMARG,
        'PhaseMarg_Unheterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1.csv'),
     'Unheterodyned standard', '#555555', 'nested'),
    (os.path.join(RESULTS_PHASEMARG,
        'PhaseMarg_Unheterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_small_h0_prior.csv'),
     r'Unheterodyned narrow $H_0$', 'tab:red', 'nested'),
    (os.path.join(RESULTS_PHASEMARG,
        'PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_flatZ.csv'),
     r'Sampled flat-in-$z$', 'tab:green', 'nested'),
    (os.path.join(RESULTS_PHASEMARG,
        'PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv'),
     r'Reweighted flat-in-$z$', 'tab:cyan', 'reweighted'),
    (os.path.join(RESULTS_PHASEMARG,
        'PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_vp250.csv'),
     r'$\sigma_{v_p}=250$', 'tab:red', 'nested'),
]

runs = []
for csv_path, label, color, fmt in FILES:
    if not os.path.exists(csv_path):
        print(f"  WARNING: {csv_path} not found — skipping")
        continue
    if fmt == 'reweighted':
        s = load_reweighted_csv(csv_path)
    else:
        s = load_nested_csv(csv_path)
    try:
        cols = s.columns.get_level_values(0)
    except AttributeError:
        cols = s.columns
    if 'H_0' in cols:
        runs.append((s, label, color))
    else:
        print(f"  WARNING: {label} has no H_0 column — skipping")

if runs:
    plot_h0(runs, 'H0_summary_all_methods')
else:
    print("  No data found.")

print("\nDone.")
