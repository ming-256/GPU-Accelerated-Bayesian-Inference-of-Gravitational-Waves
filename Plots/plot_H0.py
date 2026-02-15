"""
H_0 posterior comparison plot for GW170817.

Auto-discovers all Results/*.csv files and overlays their H_0 posteriors.
"""

import warnings
warnings.filterwarnings('ignore')

import glob
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import shutil
from scipy.stats import gaussian_kde
from anesthetic import read_chains

# LaTeX rendering
if shutil.which('pdflatex') or shutil.which('latex'):
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['Computer Modern']
else:
    mpl.rcParams['text.usetex'] = False
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['mathtext.fontset'] = 'cm'


# ============================================================================
# Configuration
# ============================================================================
H0_MIN = 20
H0_MAX = 140

COLORS = ['b', 'r', 'g', 'm', 'darkorange', 'teal', 'brown', 'olive']

# Auto-discover all result CSVs
csv_files = sorted(glob.glob('Results/*.csv'))
if not csv_files:
    print("No CSV files found in Results/")
    exit()

print(f"Found {len(csv_files)} result file(s):")
for f in csv_files:
    print(f"  {f}")


# ============================================================================
# Plot
# ============================================================================
fig, ax = plt.subplots(figsize=(8, 5))

plotted = 0
for csv_path in csv_files:
    try:
        samples = read_chains(csv_path)
    except Exception as e:
        print(f"Skipping {csv_path}: {e}")
        continue

    if 'H_0' not in samples.columns.get_level_values(0):
        print(f"Skipping {csv_path}: no H_0 column")
        continue

    # Derive label from filename: Results/PhaseMarg_Heterodyned.csv -> PhaseMarg_Heterodyned
    label = os.path.splitext(os.path.basename(csv_path))[0]
    color = COLORS[plotted % len(COLORS)]

    h0 = samples['H_0'].to_numpy()
    weights = np.asarray(samples.get_weights())

    mask = (h0 >= H0_MIN) & (h0 <= H0_MAX)
    h0 = h0[mask]
    weights = weights[mask]
    weights = weights / weights.sum()

    # Weighted KDE
    kde = gaussian_kde(h0, weights=weights)
    x_eval = np.linspace(H0_MIN, H0_MAX, 1000)
    pdf = kde(x_eval)

    # MAP
    map_val = x_eval[np.argmax(pdf)]
    print(f"{label}: H_0 MAP = {map_val:.1f} km/s/Mpc, median = {np.median(h0):.1f}")

    ax.plot(x_eval, pdf, color=color, lw=2, label=label)
    ax.fill_between(x_eval, pdf, alpha=0.15, color=color)
    plotted += 1

if plotted == 0:
    print("No results with H_0 column found.")
    exit()

# Planck & SHoES reference bands
ax.axvspan(66.93 - 0.62, 66.93 + 0.62, alpha=0.3, color='#0CDE79', edgecolor='none', label='Planck')
ax.axvspan(73.24 - 1.74, 73.24 + 1.74, alpha=0.3, color='#E87317', edgecolor='none', label='SHoES')

ax.set_xlabel(r'$H_0$ (km s$^{-1}$ Mpc$^{-1}$)', fontsize=14)
ax.set_ylabel(r'$P(H_0)$', fontsize=14)
ax.set_xlim(H0_MIN, H0_MAX)
ax.set_ylim(bottom=0)  # Ensure y-axis starts at 0
ax.legend(fontsize=11)
ax.tick_params(labelsize=12)
fig.tight_layout()

out_label = 'Plots/Results/H0_comparison'
plt.savefig(f'{out_label}.pdf')
plt.savefig(f'{out_label}.png', dpi=150)
print(f"Saved to {out_label}.pdf and {out_label}.png")
plt.show()
