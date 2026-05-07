"""
GW170817 multi-waveform corner plot: M_c, q, chi_eff, d_L, iota, H_0.

Overlays our four-waveform suite against the GWTC-1 reference for context.
Output: Results/gwtc1_phasemarg/plots/corner_GW170817_waveform_comparison.{pdf,png}
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _plot_utils import *

PLOT_COLS = [r'$\mathcal{M}_c$', r'$q$', r'$\chi_{\rm eff}$',
             r'$d_L$', r'$\iota$']

def _to_chi_eff(s, has_inplane=False):
    Mc = s['M_c'].to_numpy(); q = s['q'].to_numpy()
    if has_inplane:
        s1z = s['a_1'].to_numpy() * s['cost_1'].to_numpy()
        s2z = s['a_2'].to_numpy() * s['cost_2'].to_numpy()
    else:
        s1z = s['s1_z'].to_numpy(); s2z = s['s2_z'].to_numpy()
    dL = s['d_L'].to_numpy(); iota = s['iota'].to_numpy()
    chi_eff = (s1z + q * s2z) / (1.0 + q)
    return MCMCSamples(
        np.column_stack([Mc, q, chi_eff, dL, iota]),
        columns=PLOT_COLS,
        weights=np.asarray(s.get_weights()),
    )

# GWTC-1 reference (PhenomPv2_NRTidal low-spin posterior)
gwtc1 = load_gwtc1_gw170817(columns=['M_c', 'q', 's1_z', 's2_z', 'd_L', 'iota'])
m1 = gwtc1['M_c'].to_numpy(); q_g = gwtc1['q'].to_numpy()
chi_eff_g = (gwtc1['s1_z'].to_numpy() + q_g * gwtc1['s2_z'].to_numpy()) / (1.0 + q_g)
gwtc1_5d = MCMCSamples(
    np.column_stack([m1, q_g, chi_eff_g,
                     gwtc1['d_L'].to_numpy(), gwtc1['iota'].to_numpy()]),
    columns=PLOT_COLS,
)

datasets = [(gwtc1_5d, 'GWTC-1 IMRPhenomPv2_NRTidal', COLORS['gwtc'])]

# Locked main set: IMRX (primary) + TF2 (family check). IMR (anchor) is
# reported in Appendix A only; IMRPhenomPv2 (no tides) is dropped from the
# paper -- BNS without tides is not a like-for-like model.
for csv, label, colour, has_inplane in [
    (os.path.join(RESULTS_DIR, 'test_suite',
                  's07__gw170817__imrphenomxas_nrtidalv3__baseline_lvkbounds__seed0000',
                  'samples.csv'),
     'this work (IMRPhenomXAS_NRTidalv3)', COLORS['imr_baseline'], False),
    (os.path.join(RESULTS_DIR, 'test_suite',
                  's07__gw170817__taylorf2__baseline_lvkbounds__seed0000',
                  'samples.csv'),
     'this work (TaylorF2)', COLORS['tf2_baseline'], False),
]:
    if os.path.exists(csv):
        s = load_nested_csv(csv)
        datasets.append((_to_chi_eff(s, has_inplane), label, colour))
    else:
        print(f"  WARNING: missing {csv}")

make_corner(datasets, PLOT_COLS, 'corner_GW170817_waveform_comparison',
            figsize=(13, 13))
print("\nDone.")
