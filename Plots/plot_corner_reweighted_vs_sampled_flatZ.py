"""
Corner plot: reweighted flat-in-z vs sampled flat-in-z posteriors.

This comparison identifies systematic differences between post-hoc
reweighting of the baseline posterior to a flat-in-z prior vs directly
sampling with the flat-in-z prior.  Both IMRPhenomD and TaylorF2
waveform models are shown.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _plot_utils import *

RESULTS_PHASEMARG = os.path.join(RESULTS_DIR, 'gwtc1_phasemarg')

# Sampled flat-in-z
IMR_SAMPLED_CSV = os.path.join(RESULTS_PHASEMARG,
    'PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_flatZ.csv')
TF2_SAMPLED_CSV = os.path.join(RESULTS_PHASEMARG,
    'PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_flatZ.csv')

# Reweighted flat-in-z
IMR_REWEIGHTED_CSV = os.path.join(RESULTS_PHASEMARG,
    'PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv')
TF2_REWEIGHTED_CSV = os.path.join(RESULTS_PHASEMARG,
    'PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv')

# ----------------------------------------------------------------------- #
# IMRPhenomD: reweighted vs sampled corner
# ----------------------------------------------------------------------- #
plot_params = ['M_c', 'q', 's1_z', 's2_z', 'd_L', 'iota', 'H_0']

datasets_imr = []
if os.path.exists(IMR_SAMPLED_CSV):
    datasets_imr.append((load_nested_csv(IMR_SAMPLED_CSV),
                         r'IMRPhenomD sampled flat-in-$z$', COLORS['flatZ']))
if os.path.exists(IMR_REWEIGHTED_CSV):
    datasets_imr.append((load_reweighted_csv(IMR_REWEIGHTED_CSV),
                         r'IMRPhenomD reweighted flat-in-$z$', COLORS['reweighted']))

if datasets_imr:
    make_corner(datasets_imr, plot_params,
                'corner_reweighted_vs_sampled_flatZ_IMRPhenomD',
                figsize=(14, 14))

# ----------------------------------------------------------------------- #
# TaylorF2: reweighted vs sampled corner
# ----------------------------------------------------------------------- #
datasets_tf2 = []
if os.path.exists(TF2_SAMPLED_CSV):
    datasets_tf2.append((load_nested_csv(TF2_SAMPLED_CSV),
                         r'TaylorF2 sampled flat-in-$z$', COLORS['flatZ']))
if os.path.exists(TF2_REWEIGHTED_CSV):
    datasets_tf2.append((load_reweighted_csv(TF2_REWEIGHTED_CSV),
                         r'TaylorF2 reweighted flat-in-$z$', COLORS['reweighted']))

if datasets_tf2:
    make_corner(datasets_tf2, plot_params,
                'corner_reweighted_vs_sampled_flatZ_TaylorF2',
                figsize=(14, 14))

# ----------------------------------------------------------------------- #
# H_0 comparison: all four overlaid
# ----------------------------------------------------------------------- #
h0_runs = []
for ds, label, color in datasets_imr + datasets_tf2:
    try:
        cols = ds.columns.get_level_values(0)
    except AttributeError:
        cols = ds.columns
    if 'H_0' in cols:
        h0_runs.append((ds, label, color))

if h0_runs:
    plot_h0(h0_runs, 'H0_reweighted_vs_sampled_flatZ')

print("\nDone.")
