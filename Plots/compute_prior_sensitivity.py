#!/usr/bin/env python
"""
Prior Sensitivity Analysis for H_0 Inference
=============================================

Quantifies the impact of prior choices on the H_0 posterior from GW170817:
  1. KL divergence between baseline and alternative-prior posteriors
  2. Jensen-Shannon divergence (symmetric)
  3. MAP shift and credible interval changes
  4. Effective sample size of reweighted vs directly sampled posteriors
  5. Bayes factors from evidence ratios
  6. Comparison of reweighted vs directly-sampled flat-in-z posteriors

Outputs:
  - Console summary table (LaTeX-ready)
  - Results/gwtc1_phasemarg/prior_sensitivity.csv
  - Plots: prior_sensitivity_H0.pdf, prior_functions.pdf, dL_reweight_comparison.pdf
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Plots'))

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, entropy
from scipy.special import rel_entr
from anesthetic import read_chains, MCMCSamples
import pandas as pd

# Import shared utilities
from _plot_utils import (COLORS, OUT_DIR, RESULTS_DIR, load_nested_csv,
                         load_reweighted_csv, compute_hpd, plot_h0)

import matplotlib as mpl
import shutil
if shutil.which('pdflatex') or shutil.which('latex'):
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['Computer Modern']
else:
    mpl.rcParams['text.usetex'] = False
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['mathtext.fontset'] = 'cm'

PHASEMARG_DIR = os.path.join(RESULTS_DIR, 'gwtc1_phasemarg')

# ============================================================================
# Configuration — which waveform to focus on
# ============================================================================
WAVEFORM = os.environ.get('WAVEFORM', 'IMRPhenomD_NRTidalv2')
print(f"Waveform: {WAVEFORM}")
print(f"(Set WAVEFORM env var to change, e.g. WAVEFORM=TaylorF2)")
print()

# ============================================================================
# Helper functions
# ============================================================================

def weighted_kde(values, weights, x_eval):
    """Compute area-normalised weighted KDE."""
    w = weights / weights.sum()
    kde = gaussian_kde(values, weights=w)
    pdf = kde(x_eval)
    pdf = pdf / np.trapezoid(pdf, x_eval)
    return pdf


def kl_divergence(p, q, x_eval):
    """KL(P || Q) in nats, computed from discretised PDFs."""
    dx = x_eval[1] - x_eval[0]
    # Avoid division by zero
    mask = (p > 1e-30) & (q > 1e-30)
    return np.sum(p[mask] * np.log(p[mask] / q[mask])) * dx


def js_divergence(p, q, x_eval):
    """Jensen-Shannon divergence (symmetric) in nats."""
    m = 0.5 * (p + q)
    return 0.5 * kl_divergence(p, m, x_eval) + 0.5 * kl_divergence(q, m, x_eval)


def effective_sample_size(weights):
    """ESS = 1 / sum(w_i^2) where w_i are normalised weights."""
    w = weights / weights.sum()
    return 1.0 / np.sum(w**2)


def map_and_hpd(x_eval, pdf_vals):
    """Return MAP, 68% HPD interval, 95% HPD interval."""
    map_val = x_eval[np.argmax(pdf_vals)]
    lo68, hi68 = compute_hpd(x_eval, pdf_vals, 0.68269)
    lo95, hi95 = compute_hpd(x_eval, pdf_vals, 0.95450)
    return map_val, (lo68, hi68), (lo95, hi95)


# ============================================================================
# 1. Load all relevant posteriors
# ============================================================================
print("=" * 70)
print("LOADING POSTERIORS")
print("=" * 70)

tag = 'IMRPhenomD_NRTidalv2' if WAVEFORM == 'IMRPhenomD_NRTidalv2' else 'TaylorF2'

files = {
    'baseline': f'PhaseMarg_Heterodyned_{tag}_local_psd-gwtc1_ref-gwtc1_baseline.csv',
    'flatZ':    f'PhaseMarg_Heterodyned_{tag}_local_psd-gwtc1_ref-gwtc1_flatZ.csv',
    'vp250':    f'PhaseMarg_Heterodyned_{tag}_local_psd-gwtc1_ref-gwtc1_vp250.csv',
}

# Check for reweighted file
reweighted_file = f'PhaseMarg_Heterodyned_{tag}_local_psd-gwtc1_ref-gwtc1_reweighted_flatZ.csv'

samples = {}
for name, fname in files.items():
    path = os.path.join(PHASEMARG_DIR, fname)
    if not os.path.exists(path):
        # Try Results/ directly
        path = os.path.join(RESULTS_DIR, fname)
    if os.path.exists(path):
        samples[name] = load_nested_csv(path)
    else:
        print(f"  WARNING: {fname} not found, skipping {name}")

reweighted_path = os.path.join(PHASEMARG_DIR, reweighted_file)
if not os.path.exists(reweighted_path):
    reweighted_path = os.path.join(RESULTS_DIR, reweighted_file)
if os.path.exists(reweighted_path):
    samples['reweighted_flatZ'] = load_reweighted_csv(reweighted_path)
    print(f"  Loaded reweighted flat-in-z samples")
else:
    print(f"  No reweighted flat-in-z file found (run reweight_dL_to_flat_z.py first)")

print()

# ============================================================================
# 2. Compute H_0 PDFs via KDE
# ============================================================================
print("=" * 70)
print("COMPUTING H_0 POSTERIORS (KDE)")
print("=" * 70)

x_eval = np.linspace(20, 250, 1000)
pdfs = {}

for name, s in samples.items():
    h0 = s['H_0'].to_numpy()
    w = np.asarray(s.get_weights())
    pdfs[name] = weighted_kde(h0, w, x_eval)
    map_val, (lo68, hi68), (lo95, hi95) = map_and_hpd(x_eval, pdfs[name])
    print(f"  {name:20s}: MAP={map_val:6.1f}, "
          f"68% HPD=[{lo68:.1f}, {hi68:.1f}], "
          f"95% HPD=[{lo95:.1f}, {hi95:.1f}]")

print()

# ============================================================================
# 3. KL and JS divergences
# ============================================================================
print("=" * 70)
print("DIVERGENCE METRICS (relative to baseline)")
print("=" * 70)

results_rows = []

if 'baseline' in pdfs:
    p_base = pdfs['baseline']

    for name in ['flatZ', 'vp250', 'reweighted_flatZ']:
        if name not in pdfs:
            continue
        q = pdfs[name]

        kl_pq = kl_divergence(p_base, q, x_eval)  # KL(baseline || alt)
        kl_qp = kl_divergence(q, p_base, x_eval)   # KL(alt || baseline)
        jsd = js_divergence(p_base, q, x_eval)

        # MAP shift
        map_base = x_eval[np.argmax(p_base)]
        map_alt = x_eval[np.argmax(q)]
        map_shift = map_alt - map_base

        # 68% CI width comparison
        _, (lo_b, hi_b), _ = map_and_hpd(x_eval, p_base)
        _, (lo_a, hi_a), _ = map_and_hpd(x_eval, q)
        ci_width_base = hi_b - lo_b
        ci_width_alt = hi_a - lo_a

        row = {
            'comparison': f'baseline vs {name}',
            'KL(base||alt)': kl_pq,
            'KL(alt||base)': kl_qp,
            'JSD': jsd,
            'MAP_shift': map_shift,
            'CI68_width_base': ci_width_base,
            'CI68_width_alt': ci_width_alt,
            'CI68_ratio': ci_width_alt / ci_width_base,
        }
        results_rows.append(row)

        print(f"  {name:20s}: KL(base||alt)={kl_pq:.4f} nats, "
              f"KL(alt||base)={kl_qp:.4f} nats, "
              f"JSD={jsd:.4f} nats")
        print(f"    MAP shift: {map_shift:+.1f} km/s/Mpc, "
              f"68% CI width: {ci_width_base:.1f} -> {ci_width_alt:.1f} "
              f"(ratio: {ci_width_alt/ci_width_base:.2f})")

    # Special comparison: reweighted vs directly sampled flat-in-z
    if 'flatZ' in pdfs and 'reweighted_flatZ' in pdfs:
        p_sampled = pdfs['flatZ']
        q_reweight = pdfs['reweighted_flatZ']
        kl_sr = kl_divergence(p_sampled, q_reweight, x_eval)
        kl_rs = kl_divergence(q_reweight, p_sampled, x_eval)
        jsd_sr = js_divergence(p_sampled, q_reweight, x_eval)

        print()
        print(f"  REWEIGHTING vs DIRECT SAMPLING (flat-in-z):")
        print(f"    KL(sampled||reweighted) = {kl_sr:.4f} nats")
        print(f"    KL(reweighted||sampled) = {kl_rs:.4f} nats")
        print(f"    JSD = {jsd_sr:.4f} nats")

        map_s = x_eval[np.argmax(p_sampled)]
        map_r = x_eval[np.argmax(q_reweight)]
        print(f"    MAP (sampled): {map_s:.1f}, MAP (reweighted): {map_r:.1f}, "
              f"shift: {map_s - map_r:+.1f} km/s/Mpc")

        results_rows.append({
            'comparison': 'flatZ_sampled vs flatZ_reweighted',
            'KL(base||alt)': kl_sr,
            'KL(alt||base)': kl_rs,
            'JSD': jsd_sr,
            'MAP_shift': map_s - map_r,
            'CI68_width_base': 0,
            'CI68_width_alt': 0,
            'CI68_ratio': 0,
        })

print()

# ============================================================================
# 4. Effective sample sizes
# ============================================================================
print("=" * 70)
print("EFFECTIVE SAMPLE SIZES")
print("=" * 70)

for name, s in samples.items():
    w = np.asarray(s.get_weights())
    ess = effective_sample_size(w)
    n_total = len(s)
    print(f"  {name:20s}: N_total={n_total:,}, N_eff={ess:,.0f}, "
          f"efficiency={ess/n_total:.3f}")

print()

# ============================================================================
# 5. Bayesian evidence and Bayes factors
# ============================================================================
print("=" * 70)
print("BAYESIAN EVIDENCE & BAYES FACTORS")
print("=" * 70)

evidences = {}
for name, s in samples.items():
    if hasattr(s, 'logZ'):
        logZ = float(s.logZ())
        logZ_err = float(s.logZ(100).std())  # bootstrap error
        evidences[name] = (logZ, logZ_err)
        print(f"  {name:20s}: ln Z = {logZ:.2f} +/- {logZ_err:.2f}")

if 'baseline' in evidences:
    logZ_base, _ = evidences['baseline']
    for name in ['flatZ', 'vp250']:
        if name in evidences:
            logZ_alt, _ = evidences[name]
            delta_logZ = logZ_alt - logZ_base
            bayes_factor = np.exp(delta_logZ)
            print(f"    B({name}/baseline) = exp({delta_logZ:.2f}) = {bayes_factor:.2f}")

print()

# ============================================================================
# 6. Save results
# ============================================================================
if results_rows:
    df = pd.DataFrame(results_rows)
    out_csv = os.path.join(PHASEMARG_DIR, 'prior_sensitivity.csv')
    df.to_csv(out_csv, index=False)
    print(f"Saved: {out_csv}")

    # LaTeX table
    print()
    print("LaTeX table:")
    print(r"\begin{tabular}{lcccccc}")
    print(r"\hline")
    print(r"Comparison & KL(base$\|$alt) & KL(alt$\|$base) & JSD & MAP shift & "
          r"68\% CI ratio \\")
    print(r"\hline")
    for _, row in df.iterrows():
        print(f"  {row['comparison']} & {row['KL(base||alt)']:.4f} & "
              f"{row['KL(alt||base)']:.4f} & {row['JSD']:.4f} & "
              f"{row['MAP_shift']:+.1f} & {row['CI68_ratio']:.2f} \\\\")
    print(r"\hline")
    print(r"\end{tabular}")

print()

# ============================================================================
# 7. Plots
# ============================================================================
print("=" * 70)
print("GENERATING PLOTS")
print("=" * 70)

# --- Plot A: H_0 prior sensitivity comparison ---
runs_for_plot = []
color_map = {
    'baseline': COLORS['imr_baseline'] if 'IMRPhenomD' in WAVEFORM else COLORS['tf2_baseline'],
    'flatZ': COLORS['flatZ'],
    'vp250': COLORS['vp250'],
    'reweighted_flatZ': COLORS['reweighted'],
}
label_map = {
    'baseline': r'Baseline ($\pi(d_L) \propto d_L^2$, $\sigma_{v_p}=150$)',
    'flatZ': r'Flat-in-$z$ (sampled)',
    'vp250': r'$\sigma_{v_p} = 250$ km/s',
    'reweighted_flatZ': r'Flat-in-$z$ (reweighted)',
}

for name in ['baseline', 'flatZ', 'vp250', 'reweighted_flatZ']:
    if name in samples:
        runs_for_plot.append((samples[name], label_map[name], color_map[name]))

if runs_for_plot:
    plot_h0(runs_for_plot, f'prior_sensitivity_H0_{WAVEFORM}', xlim=(20, 200))

# --- Plot B: Prior functions themselves ---
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Panel 1: d_L prior
d_L = np.linspace(1, 75, 500)
# Volumetric: p(d_L) ∝ d_L^2
p_vol = d_L**2
p_vol = p_vol / np.trapezoid(p_vol, d_L)
# Flat-in-z: p(d_L) ~ const / d_L^2 (inverse of Jacobian), but more precisely
# p(z) = const => p(d_L) = p(z) * |dz/dd_L| ∝ 1/d_L^2 at low z (H_0*d_L ~ cz)
# At low z: d_L ~ cz/H_0, so dz/dd_L = H_0/c, giving p(d_L) = const
# More accurately: flat in z means uniform in z, which maps to roughly uniform in d_L at low z
p_flat = np.ones_like(d_L)
p_flat = p_flat / np.trapezoid(p_flat, d_L)

axes[0].plot(d_L, p_vol, color=COLORS['imr_baseline'], lw=2, label=r'Volumetric: $\pi(d_L) \propto d_L^2$')
axes[0].plot(d_L, p_flat, color=COLORS['flatZ'], lw=2, ls='--', label=r'Flat-in-$z$: $\pi(z) = \mathrm{const}$')
axes[0].set_xlabel(r'$d_L$ (Mpc)')
axes[0].set_ylabel(r'$\pi(d_L)$')
axes[0].set_title('Distance Prior')
axes[0].legend(fontsize=9)

# Panel 2: H_0 prior
H0 = np.linspace(20, 250, 500)
p_h0 = 1.0 / H0  # flat-in-log
p_h0 = p_h0 / np.trapezoid(p_h0, H0)
axes[1].plot(H0, p_h0, color='black', lw=2, label=r'$\pi(H_0) \propto 1/H_0$')
axes[1].set_xlabel(r'$H_0$ (km s$^{-1}$ Mpc$^{-1}$)')
axes[1].set_ylabel(r'$\pi(H_0)$')
axes[1].set_title(r'$H_0$ Prior (log-uniform)')
axes[1].legend(fontsize=9)

# Panel 3: Peculiar velocity prior
v_p = np.linspace(-1000, 1000, 500)
p_vp_150 = np.exp(-0.5 * ((v_p - 310) / 150)**2)
p_vp_150 = p_vp_150 / np.trapezoid(p_vp_150, v_p)
p_vp_250 = np.exp(-0.5 * ((v_p - 310) / 250)**2)
p_vp_250 = p_vp_250 / np.trapezoid(p_vp_250, v_p)
axes[2].plot(v_p, p_vp_150, color=COLORS['imr_baseline'], lw=2,
             label=r'$\sigma_{v_p} = 150$ km/s')
axes[2].plot(v_p, p_vp_250, color=COLORS['vp250'], lw=2, ls='--',
             label=r'$\sigma_{v_p} = 250$ km/s')
axes[2].set_xlabel(r'$v_p$ (km/s)')
axes[2].set_ylabel(r'$\mathcal{L}(\langle v_p \rangle | v_p)$')
axes[2].set_title('Peculiar Velocity Likelihood')
axes[2].legend(fontsize=9)

for ax in axes:
    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(1.0)

fig.tight_layout()
path = os.path.join(OUT_DIR, f'prior_functions_{WAVEFORM}')
plt.savefig(f'{path}.pdf', bbox_inches='tight')
plt.savefig(f'{path}.png', dpi=150, bbox_inches='tight')
print(f"  -> Saved {path}.pdf / .png")
plt.close(fig)

# --- Plot C: d_L posterior comparison (sampled vs reweighted flat-in-z) ---
if 'flatZ' in samples and 'reweighted_flatZ' in samples:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax_idx, (param, xlabel) in enumerate([('d_L', r'$d_L$ (Mpc)'),
                                                ('iota', r'$\iota$ (rad)')]):
        ax = axes[ax_idx]

        for name, label, color, ls in [
            ('baseline', 'Baseline (volumetric)', COLORS['imr_baseline'], '-'),
            ('flatZ', 'Flat-in-z (sampled)', COLORS['flatZ'], '-'),
            ('reweighted_flatZ', 'Flat-in-z (reweighted)', COLORS['reweighted'], '--'),
        ]:
            if name not in samples:
                continue
            s = samples[name]
            vals = s[param].to_numpy()
            w = np.asarray(s.get_weights())
            w = w / w.sum()

            if param == 'd_L':
                x_grid = np.linspace(0, 80, 500)
            else:
                x_grid = np.linspace(0, np.pi, 500)

            kde = gaussian_kde(vals, weights=w)
            pdf = kde(x_grid)
            pdf = pdf / np.trapezoid(pdf, x_grid)
            ax.plot(x_grid, pdf, color=color, ls=ls, lw=2, label=label)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(f'$P({param})$')
        ax.legend(fontsize=9)
        for spine in ax.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(1.0)

    fig.suptitle(f'Reweighted vs Directly Sampled: {WAVEFORM}', fontsize=14)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, f'dL_reweight_comparison_{WAVEFORM}')
    plt.savefig(f'{path}.pdf', bbox_inches='tight')
    plt.savefig(f'{path}.png', dpi=150, bbox_inches='tight')
    print(f"  -> Saved {path}.pdf / .png")
    plt.close(fig)

# --- Plot D: H_0 posterior with KL annotations ---
if 'baseline' in pdfs and ('flatZ' in pdfs or 'vp250' in pdfs):
    fig, ax = plt.subplots(figsize=(10, 6))

    for name, label, color in [
        ('baseline', 'Baseline', COLORS['imr_baseline']),
        ('flatZ', 'Flat-in-z (sampled)', COLORS['flatZ']),
        ('vp250', r'$\sigma_{v_p}=250$', COLORS['vp250']),
        ('reweighted_flatZ', 'Flat-in-z (reweighted)', COLORS['reweighted']),
    ]:
        if name not in pdfs:
            continue
        ax.plot(x_eval, pdfs[name], color=color, lw=2, label=label)

    # Annotate with JSD values
    y_pos = 0.95
    for name in ['flatZ', 'vp250', 'reweighted_flatZ']:
        if name not in pdfs or 'baseline' not in pdfs:
            continue
        jsd = js_divergence(pdfs['baseline'], pdfs[name], x_eval)
        label_short = {'flatZ': 'flat-z', 'vp250': 'vp250',
                       'reweighted_flatZ': 'reweight'}[name]
        ax.text(0.98, y_pos, f'JSD(base, {label_short}) = {jsd:.4f} nats',
                transform=ax.transAxes, ha='right', va='top', fontsize=10)
        y_pos -= 0.05

    ax.set_xlim(20, 200)
    ax.set_ylim(bottom=0)
    ax.set_xlabel(r'$H_0$ (km s$^{-1}$ Mpc$^{-1}$)')
    ax.set_ylabel(r'$P(H_0)$')
    ax.set_title(f'Prior Sensitivity: {WAVEFORM}')
    ax.legend(frameon=False, fontsize=11)
    fig.tight_layout()

    path = os.path.join(OUT_DIR, f'prior_sensitivity_annotated_{WAVEFORM}')
    plt.savefig(f'{path}.pdf', bbox_inches='tight')
    plt.savefig(f'{path}.png', dpi=150, bbox_inches='tight')
    print(f"  -> Saved {path}.pdf / .png")
    plt.close(fig)

print()
print("Done.")
