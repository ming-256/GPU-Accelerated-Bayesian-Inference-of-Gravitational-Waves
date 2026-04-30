"""
GW170817 d_L–iota bimodality figure (existing Plots/ style).

Two panels:
  (a) The unrestricted flat-in-redshift run shown in (d_L, iota) plane,
      with the prior-restricted Mode-A and Mode-B contours overlaid.
  (b) 1D H_0 marginal under each variant (showing why direct flat-z
      sampling places ~28 per cent of the posterior mass at H_0 > 120,
      which the volumetric prior suppresses).

Output: Results/gwtc1_phasemarg/plots/bimodality.{pdf,png}
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _plot_utils import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

CSV_A    = 'Results/test_suite/s10__gw170817__imrphenomd_nrtidalv2__flatz__dL30-75__refGWTC1__seed0000/samples.csv'
CSV_B    = 'Results/test_suite/s10__gw170817__imrphenomd_nrtidalv2__flatz__dL10-30__refGWTC1__seed0000/samples.csv'
CSV_FULL = 'Results/test_suite/s10__gw170817__imrphenomd_nrtidalv2__flatz__dL10-75__refModeB__seed0000/samples.csv'

def load_dl_iota_h0(csv):
    s = load_nested_csv(csv)
    return (s['d_L'].to_numpy(), s['iota'].to_numpy(),
            s['H_0'].to_numpy() if 'H_0' in s.columns else None,
            np.asarray(s.get_weights()))

dlA, iA, h0A, wA = load_dl_iota_h0(CSV_A)
dlB, iB, h0B, wB = load_dl_iota_h0(CSV_B)
dlF, iF, h0F, wF = load_dl_iota_h0(CSV_FULL)

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# ----- Panel (a): d_L vs iota -----
ax = axes[0]
xi = np.linspace(8, 80, 200)
yi = np.linspace(0, np.pi, 200)
XX, YY = np.meshgrid(xi, yi)
kde_full = gaussian_kde(np.vstack([dlF, iF]), weights=wF/wF.sum())
ZZ = kde_full(np.vstack([XX.ravel(), YY.ravel()])).reshape(XX.shape)
ax.contourf(XX, YY, ZZ, levels=15, cmap='Blues', alpha=0.6)
# Mode A contour
ZA = gaussian_kde(np.vstack([dlA, iA]), weights=wA/wA.sum())(
    np.vstack([XX.ravel(), YY.ravel()])).reshape(XX.shape)
ax.contour(XX, YY, ZA, levels=6, colors='tab:orange', linewidths=1.2)
# Mode B contour
ZB = gaussian_kde(np.vstack([dlB, iB]), weights=wB/wB.sum())(
    np.vstack([XX.ravel(), YY.ravel()])).reshape(XX.shape)
ax.contour(XX, YY, ZB, levels=6, colors=COLORS['small_h0_imr'], linewidths=1.2)
ax.set_xlim(10, 60); ax.set_ylim(1.5, np.pi)
ax.set_xlabel(r'$d_L$ (Mpc)', fontsize=13)
ax.set_ylabel(r'$\iota$ (rad)', fontsize=13)
ax.set_title(r'(a) Joint $(d_L,\iota)$ posterior, flat-in-$z$')
# Annotate modes
ax.text(23, 1.80, 'Mode B', color=COLORS['small_h0_imr'], fontsize=12,
        weight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=1))
ax.text(42, 2.75, 'Mode A', color='tab:orange', fontsize=12,
        weight='bold', ha='center', bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=1))

# ----- Panel (b): H_0 1D marginals -----
ax = axes[1]
xg = np.linspace(40, 230, 4000)
for x, w, label, col, ls in [
    (h0A, wA, r'Mode A ($d_L\in[30,75]\,\rm Mpc$)', 'tab:orange', '--'),
    (h0B, wB, r'Mode B ($d_L\in[10,30]\,\rm Mpc$)', COLORS['small_h0_imr'],   ':'),
    (h0F, wF, r'Combined ($d_L\in[10,75]\,\rm Mpc$)', COLORS['imr_baseline'], '-'),
]:
    if x is None: continue
    w = w / w.sum()
    pdf = gaussian_kde(x, weights=w)(xg); pdf /= np.trapezoid(pdf, xg)
    ax.plot(xg, pdf, color=col, lw=2.0, ls=ls, label=label)
# Cosmological reference bands — Planck CMB and SH0ES distance-ladder.
# (LVK GW170817 band intentionally dropped: this work is itself a
# GW170817 reanalysis, so the LVK band is uninformative here.)
ax.axvspan(65.7, 68.2, color=COLORS['planck_outer'], alpha=0.3, zorder=0)
ax.axvspan(66.93 - 0.62, 66.93 + 0.62, color=COLORS['planck_inner'],
           alpha=0.3, zorder=0, label='Planck')
ax.axvspan(69.76, 76.72, color=COLORS['shoes_outer'], alpha=0.3, zorder=0)
ax.axvspan(73.24 - 1.74, 73.24 + 1.74, color=COLORS['shoes_inner'],
           alpha=0.3, zorder=0, label='SH0ES')
ax.set_xlim(40, 230); ax.set_ylim(bottom=0)
ax.set_xlabel(r'$H_0$ (km s$^{-1}$ Mpc$^{-1}$)', fontsize=13)
ax.set_ylabel(r'$P(H_0)$ (km$^{-1}$ s Mpc)', fontsize=13)
ax.set_title(r'(b) $H_0$ marginal by mode')
ax.legend(frameon=False, fontsize=10, loc='upper right')

for a in axes:
    for sp in a.spines.values():
        sp.set_edgecolor('black'); sp.set_linewidth(1.5)

fig.tight_layout()
p = os.path.join(OUT_DIR, 'bimodality')
plt.savefig(f'{p}.pdf', bbox_inches='tight')
plt.savefig(f'{p}.png', dpi=150, bbox_inches='tight')
print(f"  -> Saved {p}.pdf / .png")
plt.close(fig)
