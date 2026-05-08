"""
GW170817 H_0 prior-sensitivity comparison — two-panel figure.

Panel (a): d_L prior-shape sensitivity — baseline vs flat-in-z (direct and
           reweighted) vs enlarged sigma_vp (sigma=250 km/s).
Panel (b): peculiar-velocity centre sweep — <v_p> in {215, 310, 405} km/s
           with sigma_vp=150 km/s (s18 runs).

Output: Results/gwtc1_phasemarg/plots/H0_prior_sensitivity.{pdf,png}
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _plot_utils import (
    OUT_DIR, RESULTS_DIR, COLORS, load_nested_csv,
    compute_hpd_samples,
)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


def load_h0_w(csv):
    """(H_0 array, weight array) — handles nested-sampling and reweighted CSVs."""
    if 'reweighted' in csv.lower() or 'reweight' in os.path.basename(csv).lower():
        df = pd.read_csv(csv, low_memory=False)
        x = df['H_0'].to_numpy().astype(float)
        w = df['weight'].to_numpy().astype(float)
    else:
        s = load_nested_csv(csv)
        x = s['H_0'].to_numpy().astype(float)
        w = np.asarray(s.get_weights(), dtype=float)
    finite = np.isfinite(x) & np.isfinite(w) & (w > 0)
    return x[finite], w[finite] / w[finite].sum()


def draw_panel(ax, runs, bins, xlim, add_planck_shoes=True, lvk_band=True, hpd_lines=True):
    """Draw a single H_0 histogram panel onto `ax`."""
    centres = 0.5 * (bins[:-1] + bins[1:])
    for x, w, label, color, ls in runs:
        counts, _ = np.histogram(x, bins=bins, weights=w, density=True)
        x_step = np.r_[bins[0], np.repeat(bins[1:-1], 2), bins[-1]]
        y_step = np.r_[np.repeat(counts, 2)]
        ax.plot(x_step, y_step, color=color, lw=2.0, label=label,
                linestyle=ls, drawstyle='default')
        if hpd_lines:
            lo68, hi68 = compute_hpd_samples(x, w, 0.68269)
            lo95, hi95 = compute_hpd_samples(x, w, 0.95450)
            map_ = float(centres[np.argmax(counts)])
            print(f"  {label}: MAP={map_:.1f}; 68%=[{lo68:.1f},{hi68:.1f}]; 95%=[{lo95:.1f},{hi95:.1f}]")
            for v, dls in [(lo68, '--'), (hi68, '--'), (lo95, ':'), (hi95, ':')]:
                ax.axvline(v, color=color, ls=dls, lw=0.8, alpha=0.55)

    if lvk_band:
        ax.axvspan(62, 82, color='0.55', alpha=0.18, zorder=0,
                   label=r'Abbott+2017 ($70^{+12}_{-8}$, 68\%)')
        ax.axvline(70.0, color='0.4', ls='-.', lw=1.0, zorder=0)

    if add_planck_shoes:
        ax.axvspan(65.7, 68.2, color=COLORS['planck_outer'], alpha=0.3, zorder=0)
        ax.axvspan(66.93 - 0.62, 66.93 + 0.62, color=COLORS['planck_inner'],
                   alpha=0.3, zorder=0, label='Planck')
        ax.axvspan(69.76, 76.72, color=COLORS['shoes_outer'], alpha=0.3, zorder=0)
        ax.axvspan(73.24 - 1.74, 73.24 + 1.74, color=COLORS['shoes_inner'],
                   alpha=0.3, zorder=0, label='SH0ES')

    ax.set_xlim(xlim)
    ax.set_ylim(bottom=0)
    ax.set_xlabel(r'$H_0\;(\mathrm{km\,s^{-1}\,Mpc^{-1}})$')
    ax.set_ylabel(r'$P(H_0)$')
    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(1.5)
    ax.legend(frameon=False, fontsize=9.5)


# ── data ──────────────────────────────────────────────────────────────────────
XAS = 'Results/test_suite/s14__gw170817__imrphenomxas_nrtidalv3'
S18 = 'Results/test_suite/s18__gw170817__imrphenomxas_nrtidalv3__baseline'

panel_a_specs = [
    (f'{XAS}__baseline__seed0000/samples.csv',
     r'Baseline ($\pi(d_L)\propto d_L^2$)',   COLORS['imr_baseline'], '-'),
    (f'{XAS}__flatz__seed0000/samples.csv',
     r'Flat-in-$z$ (direct)',                  COLORS['flatZ'],        '-'),
    (f'{XAS}__reweighted_flatz__seed0000/samples.csv',
     r'Flat-in-$z$ (reweighted)',              COLORS['reweighted'],   '--'),
    (f'{XAS}__vp250__seed0000/samples.csv',
     r'$\sigma_{v_p}=250\;\mathrm{km\,s^{-1}}$', COLORS['imr_baseline'], ':'),
]

panel_b_specs = [
    (f'{S18}__vpmean215__seed0000/samples.csv',
     r'$\langle v_p\rangle=215\;\mathrm{km\,s^{-1}}$',  '#e07b39', '-'),
    (f'{S18}__vpmean310__seed0000/samples.csv',
     r'$\langle v_p\rangle=310\;\mathrm{km\,s^{-1}}$ (baseline)', COLORS['imr_baseline'], '-'),
    (f'{S18}__vpmean405__seed0000/samples.csv',
     r'$\langle v_p\rangle=405\;\mathrm{km\,s^{-1}}$',  '#5b78b5', '-'),
]

XLIM = (40, 180)
BINS = np.linspace(XLIM[0], XLIM[1], 141)

def load_spec(csv, label, color, ls):
    if not os.path.exists(csv):
        raise SystemExit(f"Missing: {csv}")
    x, w = load_h0_w(csv)
    return (x, w, label, color, ls)

print("Panel (a) — d_L prior sensitivity")
runs_a = [load_spec(*s) for s in panel_a_specs]
print("Panel (b) — v_p centre sweep")
runs_b = [load_spec(*s) for s in panel_b_specs]

# ── plot ──────────────────────────────────────────────────────────────────────
fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(14, 5.5), sharey=False)

draw_panel(ax_a, runs_a, BINS, XLIM, add_planck_shoes=True, lvk_band=True)
ax_a.set_title(r'(a)\ $d_L$ prior sensitivity', fontsize=11, loc='left')

draw_panel(ax_b, runs_b, BINS, XLIM, add_planck_shoes=True, lvk_band=False)
ax_b.set_title(r'(b)\ $\langle v_p\rangle$ centre sweep', fontsize=11, loc='left')

fig.tight_layout(w_pad=3.0)
path = os.path.join(OUT_DIR, 'H0_prior_sensitivity')
plt.savefig(f'{path}.pdf', bbox_inches='tight')
plt.savefig(f'{path}.png', dpi=150, bbox_inches='tight')
print(f"\n-> Saved {path}.pdf / .png")
plt.close(fig)
