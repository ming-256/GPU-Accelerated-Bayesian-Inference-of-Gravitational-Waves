"""
Comprehensive scaling-study plot: heterodyned vs unheterodyned, all available data.

Reads Results/scaling_study/scaling_summary_full.csv (built by build_scaling_table.py)
and produces a runtime-vs-n_live figure with all heterodyned and unheterodyned
points overlaid, in the existing Plots/ style.

Output: Results/gwtc1_phasemarg/plots/scaling_study_full.{pdf,png}
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _plot_utils import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

CSV = os.path.join(RESULTS_DIR, 'scaling_study', 'scaling_summary_full.csv')

df = pd.read_csv(CSV)

# Group keys: (waveform, kind, priors)
GROUPS = [
    # (mask, label, color, marker)
    (((df['kind']=='heterodyned') & (df['waveform']=='IMRPhenomD_NRTidalv2')
      & (df['priors']=='host-localised')),
     r'IMRPhenomD\_NRTidalv2 hetero (host-loc)',
     COLORS['imr_baseline'], 'o'),
    (((df['kind']=='heterodyned') & (df['waveform']=='IMRPhenomD_NRTidalv2')
      & (df['priors']=='lvk-bounds')),
     r'IMRPhenomD\_NRTidalv2 hetero (LVK-bounds)',
     COLORS['flatZ'], 's'),
    (((df['kind']=='unheterodyned') & (df['waveform']=='IMRPhenomD_NRTidalv2')
      & (df['priors']=='host-localised')),
     r'IMRPhenomD\_NRTidalv2 unhetero (host-loc)',
     'tab:red', '^'),
    (((df['kind']=='unheterodyned') & (df['waveform']=='IMRPhenomD_NRTidalv2')
      & (df['priors']=='full-sky')),
     r'IMRPhenomD\_NRTidalv2 unhetero (full-sky)',
     'tab:pink', 'v'),
    (((df['kind']=='unheterodyned') & (df['waveform']=='TaylorF2')),
     r'TaylorF2 unhetero',
     'tab:purple', 'D'),
]

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

# Panel A: Wall-clock total_s vs n_live (log-log)
ax = axes[0]
for mask, lab, col, mk in GROUPS:
    sub = df[mask].sort_values('n_live')
    if len(sub) == 0:
        continue
    ax.plot(sub['n_live'], sub['total_s'], color=col, lw=1.6,
            marker=mk, ms=8, label=lab, zorder=5)
# Linear-scaling reference through (5000, 858) for LVK-bounds heterodyned
n_ref = np.array([200, 200000])
rate = 858.0 / 5000.0  # s per live point
ax.plot(n_ref, rate * n_ref, 'k--', lw=1.0, alpha=0.4,
        label=r'Linear ref $\propto n_{\rm live}$')

ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel(r'$n_{\rm live}$', fontsize=13)
ax.set_ylabel('Total wall-clock (s)', fontsize=13)
ax.set_title('(a) Runtime scaling, all configurations')
ax.legend(frameon=False, fontsize=8, loc='upper left')
ax.grid(True, which='both', alpha=0.2)

# Panel B: speedup ratio at matched n_live
# Compute ratio unhet/hetero at n_live = 500, 1500-ish, 2500
ax = axes[1]
het_imr = df[(df['kind']=='heterodyned') & (df['waveform']=='IMRPhenomD_NRTidalv2')
             & (df['priors']=='host-localised')].set_index('n_live')['total_s']
het_imr_lvk = df[(df['kind']=='heterodyned') & (df['waveform']=='IMRPhenomD_NRTidalv2')
                 & (df['priors']=='lvk-bounds')].set_index('n_live')['total_s']
unhet_imr = df[(df['kind']=='unheterodyned') & (df['waveform']=='IMRPhenomD_NRTidalv2')
               & (df['priors']=='host-localised')].set_index('n_live')['total_s']

# Build matched pairs by interpolating the heterodyned baseline at the unhet n_live
xs, ys = [], []
for nl, t_un in unhet_imr.items():
    # Find closest hetero point with n_live ≤ nl, or interpolate
    if nl in het_imr.index:
        t_h = het_imr.loc[nl]
    else:
        # linear interp on log-log
        nl_arr = np.sort(het_imr.index.to_numpy())
        t_arr = het_imr.loc[nl_arr].to_numpy()
        t_h = np.exp(np.interp(np.log(nl), np.log(nl_arr), np.log(t_arr)))
    xs.append(nl); ys.append(t_un / t_h)
ax.plot(xs, ys, color='tab:red', marker='^', ms=10, lw=1.6,
        label=r'Unhetero / hetero (host-loc, IMR)')

# Annotate values
for nl, r in zip(xs, ys):
    ax.text(nl, r * 1.05, f'{r:.0f}$\\times$', ha='center', fontsize=9, color='tab:red')

ax.set_xscale('log')
ax.set_xlabel(r'$n_{\rm live}$', fontsize=13)
ax.set_ylabel('Wall-clock speedup factor', fontsize=13)
ax.set_title('(b) Heterodyne speedup vs $n_{\rm live}$')
ax.axhline(1.0, color='k', ls=':', alpha=0.4)
ax.grid(True, which='both', alpha=0.2)
ax.legend(frameon=False, fontsize=10, loc='lower right')

for a in axes:
    for spine in a.spines.values():
        spine.set_edgecolor('black'); spine.set_linewidth(1.5)

fig.tight_layout()
p = os.path.join(OUT_DIR, 'scaling_study_full')
plt.savefig(f'{p}.pdf', bbox_inches='tight')
plt.savefig(f'{p}.png', dpi=150, bbox_inches='tight')
print(f"  -> Saved {p}.pdf / .png")
plt.close(fig)

# Print the speedup table
print()
print("Speedup at matched n_live:")
print(f"  {'n_live':>8}  {'hetero (s)':>10}  {'unhetero (s)':>13}  {'speedup':>8}")
for nl, r in zip(xs, ys):
    if nl in het_imr.index:
        h = het_imr.loc[nl]
    else:
        nl_arr = np.sort(het_imr.index.to_numpy())
        t_arr = het_imr.loc[nl_arr].to_numpy()
        h = np.exp(np.interp(np.log(nl), np.log(nl_arr), np.log(t_arr)))
    u = unhet_imr.loc[nl]
    print(f"  {nl:>8}  {h:>10.0f}  {u:>13.0f}  {r:>7.1f}x")
