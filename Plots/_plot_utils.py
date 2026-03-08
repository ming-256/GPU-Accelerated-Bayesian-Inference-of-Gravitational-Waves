"""
Shared plotting utilities for GW paper figures.

Provides:
  - LaTeX rendering setup
  - Data loaders for nested sampling CSVs, reweighted CSVs, and GWTC reference
  - H_0 plotting with MAP, HPD credible intervals, and SHoES/Planck bands
  - Consistent color scheme across all plots
"""

import warnings
warnings.filterwarnings('ignore')

import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import h5py
import shutil
from anesthetic import MCMCSamples, read_chains, make_2d_axes
from scipy.stats import gaussian_kde
import pandas as pd

# --------------------------------------------------------------------------- #
# LaTeX rendering
# --------------------------------------------------------------------------- #
if shutil.which('pdflatex') or shutil.which('latex'):
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['Computer Modern']
else:
    mpl.rcParams['text.usetex'] = False
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['mathtext.fontset'] = 'cm'

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
RESULTS_DIR = 'Results'
OUT_DIR = 'Results/gwtc1_phasemarg/plots'
os.makedirs(OUT_DIR, exist_ok=True)

GWTC1_HDF5 = os.path.join(RESULTS_DIR, 'GW170817_GWTC-1.hdf5')
GWTC2P1_GW150914_HDF5 = 'EventData/GWOSC/GW150914/IGWN-GWTC2p1-v2-GW150914_095045_PEDataRelease_mixed_nocosmo.h5'

# --------------------------------------------------------------------------- #
# Consistent color scheme
# --------------------------------------------------------------------------- #
COLORS = {
    # Data lines — each source gets a unique, distinct color
    'gwtc':           'tab:blue',
    'imr_baseline':   'maroon',
    'tf2_baseline':   'tab:purple',
    'flatZ':          'teal',
    'vp250':          'tab:red',
    'reweighted':     'tab:cyan',
    'unhetero_imr':   '#555555',
    'unhetero_tf2':   '#888888',
    'small_h0_imr':   'tab:brown',
    'small_h0_tf2':   'tab:pink',
    # Planck / SHoES reference bands — traditional colors
    'planck_inner':   '#0CDE79',
    'planck_outer':   '#6DE6AC',
    'shoes_inner':    '#E87317',
    'shoes_outer':    '#F19851',
}

# --------------------------------------------------------------------------- #
# Data loaders
# --------------------------------------------------------------------------- #
def load_nested_csv(csv_path):
    """Load an anesthetic nested sampling CSV."""
    s = read_chains(csv_path)
    print(f"  Loaded {csv_path}  ({len(s)} samples)")
    return s


def load_reweighted_csv(csv_path):
    """Load a reweighted CSV (plain CSV with a 'weight' column)."""
    df = pd.read_csv(csv_path)
    weights = df['weight'].to_numpy()
    cols = [c for c in df.columns if c != 'weight']
    s = MCMCSamples(df[cols].to_numpy(), columns=cols, weights=weights)
    print(f"  Loaded {csv_path}  ({len(s)} samples, reweighted)")
    return s


def load_gwtc1_gw170817(columns=None):
    """Load GWTC-1 GW170817 posteriors, returning MCMCSamples.

    Default columns: M_c, q, s1_z, s2_z, d_L, iota
    """
    dataset = 'IMRPhenomPv2NRT_lowSpin_posterior'
    with h5py.File(GWTC1_HDF5, 'r') as f:
        data = f[dataset][:]

    m1 = data['m1_detector_frame_Msun']
    m2 = data['m2_detector_frame_Msun']
    M_c = (m1 * m2)**0.6 / (m1 + m2)**0.2
    q = m2 / m1
    d_L = data['luminosity_distance_Mpc']
    iota = np.arccos(data['costheta_jn'])
    s1_z = data['spin1'] * data['costilt1']
    s2_z = data['spin2'] * data['costilt2']

    if columns is None:
        columns = ['M_c', 'q', 's1_z', 's2_z', 'd_L', 'iota']
    col_map = {
        'M_c': M_c, 'q': q, 'd_L': d_L, 'iota': iota,
        's1_z': s1_z, 's2_z': s2_z,
    }
    arr = np.column_stack([col_map[c] for c in columns])
    return MCMCSamples(arr, columns=columns)


def load_gwtc2p1_gw150914():
    """Load GWTC-2p1 GW150914 posteriors for corner plot comparison."""
    dataset = 'C01:IMRPhenomXPHM/posterior_samples'
    with h5py.File(GWTC2P1_GW150914_HDF5, 'r') as f:
        data = f[dataset][:]

    M_c = data['chirp_mass']
    q = data['mass_ratio']
    d_L = data['luminosity_distance']
    iota = data['iota']
    chi_eff = data['chi_eff']

    cols = [r'$\mathcal{M}_c$', r'$q$', r'$\chi_{\rm eff}$', r'$d_L$', r'$\iota$']
    return MCMCSamples(
        np.column_stack([M_c, q, chi_eff, d_L, iota]), columns=cols,
    )


# --------------------------------------------------------------------------- #
# HPD interval computation
# --------------------------------------------------------------------------- #
def compute_hpd(x_eval, pdf_vals, cred_level):
    """Compute HPD (highest posterior density) interval boundaries."""
    dx = x_eval[1] - x_eval[0]
    total_area = np.sum(pdf_vals) * dx
    sorted_pdf = np.sort(pdf_vals)[::-1]
    cumarea = np.cumsum(sorted_pdf) * dx / total_area
    threshold = sorted_pdf[np.searchsorted(cumarea, cred_level)]
    above = pdf_vals >= threshold
    indices = np.where(above)[0]
    return x_eval[indices[0]], x_eval[indices[-1]]


# --------------------------------------------------------------------------- #
# H_0 plot with MAP, HPD, SHoES, Planck
# --------------------------------------------------------------------------- #
def plot_h0(runs, out_name, xlim=(20, 250), n_eval=2000):
    """Create an H_0 posterior plot using weighted KDE.

    Area-normalised KDE with MAP, HPD credible intervals, SHoES and Planck bands.

    Parameters
    ----------
    runs : list of (samples_or_dict, label, color)
        Each entry is (anesthetic samples object OR dict with 'H_0' and 'weights'), label, color.
    out_name : str
        Output filename stem (saved to OUT_DIR).
    xlim : tuple
        x-axis limits.
    n_eval : int
        Number of points for KDE evaluation grid.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    x_eval = np.linspace(xlim[0], xlim[1], n_eval)

    for samples, label, color in runs:
        # Extract H_0 values and weights
        if isinstance(samples, dict):
            h0_vals = samples['H_0']
            weights = samples['weights']
        else:
            h0_vals = samples['H_0'].to_numpy()
            weights = np.asarray(samples.get_weights())

        weights = weights / weights.sum()

        # Weighted KDE
        kde = gaussian_kde(h0_vals, weights=weights)
        pdf_vals = kde(x_eval)

        # Area-normalise
        pdf_vals = pdf_vals / np.trapezoid(pdf_vals, x_eval)

        # Plot
        ax.plot(x_eval, pdf_vals, color=color, lw=2, label=label)

        # MAP
        map_val = x_eval[np.argmax(pdf_vals)]
        print(f"  {label}: H_0 MAP = {map_val:.1f} km/s/Mpc")

        # HPD intervals
        for cred_level, sigma_label, ls in [(0.68269, r'1$\sigma$', '--'),
                                             (0.95450, r'2$\sigma$', ':')]:
            lo, hi = compute_hpd(x_eval, pdf_vals, cred_level)
            ax.axvline(lo, color=color, ls=ls, lw=1.2, alpha=0.7)
            ax.axvline(hi, color=color, ls=ls, lw=1.2, alpha=0.7)
            print(f"    {sigma_label} HPD: [{lo:.1f}, {hi:.1f}]")

    # Planck and SHoES reference bands
    ax.axvspan(65.7, 68.2, color=COLORS['planck_outer'], alpha=0.3, zorder=0)
    ax.axvspan(66.93 - 0.62, 66.93 + 0.62, color=COLORS['planck_inner'],
               alpha=0.3, zorder=0, label='Planck')
    ax.axvspan(69.76, 76.72, color=COLORS['shoes_outer'], alpha=0.3, zorder=0)
    ax.axvspan(73.24 - 1.74, 73.24 + 1.74, color=COLORS['shoes_inner'],
               alpha=0.3, zorder=0, label='SHoES')

    from matplotlib.ticker import MultipleLocator
    ax.yaxis.set_major_locator(MultipleLocator(0.01))
    ax.set_xlim(xlim)
    ax.set_ylim(bottom=0)
    ax.set_xlabel(r'$H_0$ (km s$^{-1}$ Mpc$^{-1}$)')
    ax.set_ylabel(r'$P(H_0)$ (km$^{-1}$ s Mpc)')

    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(1.5)

    ax.legend(frameon=False, fontsize=12)
    fig.tight_layout()

    path = os.path.join(OUT_DIR, out_name)
    plt.savefig(f'{path}.pdf', bbox_inches='tight')
    plt.savefig(f'{path}.png', dpi=150, bbox_inches='tight')
    print(f"  -> Saved {path}.pdf / .png")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# Corner plot helper
# --------------------------------------------------------------------------- #
def make_corner(datasets, params, out_name, figsize=(10, 10)):
    """Create a corner plot from multiple datasets.

    Parameters
    ----------
    datasets : list of (MCMCSamples, label, color)
    params : list of str — column names to plot
    out_name : str — output filename stem
    figsize : tuple
    """
    fig, axes = make_2d_axes(params=params, upper=False, figsize=figsize)

    for samples, label, color in datasets:
        samples.plot_2d(
            axes,
            kinds=dict(diagonal='hist_1d', lower='kde_2d'),
            diagonal_kwargs=dict(
                bins=35,
                histtype='step',
                linewidth=2.0,
                density=True,
            ),
            lower_kwargs=dict(levels=[0.99730, 0.95450, 0.68269]),
            color=color, alpha=0.75, label=label,
        )

    axes.iloc[-1, 0].legend(
        bbox_to_anchor=(len(axes) * 0.85, len(axes) * 0.8),
        loc='lower center',
        fontsize=14,
    )
    fig.tight_layout()
    axes.tick_params(grid_alpha=0)

    path = os.path.join(OUT_DIR, out_name)
    plt.savefig(f'{path}.pdf', bbox_inches='tight')
    plt.savefig(f'{path}.png', dpi=150, bbox_inches='tight')
    print(f"  -> Saved {path}.pdf / .png")
    plt.close(fig)
