#!/usr/bin/env python3
"""Generate all MNRAS-quality figures for the paper.

Run from the repo root:
    python3 mnras_paper/figures/plot_all.py

Outputs to mnras_paper/figures/output/ as PDF + 300-dpi PNG.
"""
import os
import sys
import json
import datetime as dt

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import corner

# ── paths ────────────────────────────────────────────────────────────────────
REPO  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "mnras_paper", "test_suite", "analysis"))
from _helpers import (
    RESULTS_ROOT, load_catalog, load_run,
    weighted_median, weighted_quantiles, weighted_tail_prob,
    read_log_evidence_from_log, read_nested_samples_csv,
)

OUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT, exist_ok=True)

# ── MNRAS rcParams ────────────────────────────────────────────────────────────
MNRAS_COL   = 3.32   # single column inches
MNRAS_2COL  = 6.97   # double column inches
GOLDEN      = (1 + 5**0.5) / 2

plt.rcParams.update({
    "text.usetex":        True,
    "font.family":        "serif",
    "font.serif":         ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size":          8,
    "axes.labelsize":     8,
    "axes.titlesize":     8,
    "xtick.labelsize":    7,
    "ytick.labelsize":    7,
    "legend.fontsize":    7,
    "legend.framealpha":  0.9,
    "lines.linewidth":    1.0,
    "axes.linewidth":     0.6,
    "xtick.major.width":  0.6,
    "ytick.major.width":  0.6,
    "xtick.minor.width":  0.4,
    "ytick.minor.width":  0.4,
    "xtick.direction":    "in",
    "ytick.direction":    "in",
    "xtick.top":          True,
    "ytick.right":        True,
    "figure.dpi":         300,
    "savefig.dpi":        300,
    "savefig.bbox":       "tight",
    "savefig.pad_inches": 0.02,
})

# ── colour palette (colourblind-safe) ────────────────────────────────────────
C0 = "#0072B2"   # blue
C1 = "#E69F00"   # orange
C2 = "#009E73"   # green
C3 = "#CC79A7"   # pink
C4 = "#56B4E9"   # sky blue
C5 = "#D55E00"   # vermillion
C6 = "#F0E442"   # yellow
GREY = "#888888"

# ── helper ───────────────────────────────────────────────────────────────────
def savefig(fig, name):
    for ext in ("pdf", "png"):
        path = os.path.join(OUT, f"{name}.{ext}")
        fig.savefig(path)
    plt.close(fig)
    print(f"  saved {name}")


def kde1d(x, w, xgrid, bw=None):
    """Weighted Gaussian KDE on a grid."""
    from scipy.stats import gaussian_kde
    w = np.asarray(w, float)
    w /= w.sum()
    kde = gaussian_kde(x, weights=w, bw_method=bw)
    return kde(xgrid)


def credible_interval(x, w, levels=(0.68, 0.95)):
    """Return list of (lo, hi) tuples for each credible level."""
    out = []
    for lv in levels:
        alpha = (1 - lv) / 2
        lo, hi = weighted_quantiles(x, w, [alpha, 1 - alpha])
        out.append((lo, hi))
    return out


def wallclock(run_id):
    cfg_p = os.path.join(RESULTS_ROOT, run_id, "config.json")
    fin_p = os.path.join(RESULTS_ROOT, run_id, "finish.json")
    if not (os.path.exists(cfg_p) and os.path.exists(fin_p)):
        return None
    cfg = json.load(open(cfg_p))
    fin_lines = [l.strip() for l in open(fin_p) if l.strip()]
    last = json.loads(fin_lines[-1])
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    try:
        s = dt.datetime.strptime(cfg["started"], fmt)
        e = dt.datetime.strptime(last["finished"], fmt)
        return (e - s).total_seconds()
    except Exception:
        return None


# ════════════════════════════════════════════════════════════════════════════
# Figure 1 — GW170817 main posteriors (corner, baseline NRTidalv2)
# ════════════════════════════════════════════════════════════════════════════
def fig_gw170817_corner():
    print("Fig 1: GW170817 corner …")
    run = load_run("s07__gw170817__imrphenomd_nrtidalv2__baseline_lvkbounds__seed0000")
    cols  = ["M_c", "q", "s1_z", "s2_z", "d_L", "iota", "lambda_1", "lambda_2"]
    labels = [r"$\mathcal{M}_c\,[M_\odot]$", r"$q$",
              r"$s_{1z}$", r"$s_{2z}$",
              r"$d_L\,[\mathrm{Mpc}]$", r"$\iota\,[\mathrm{rad}]$",
              r"$\Lambda_1$", r"$\Lambda_2$"]
    data = np.column_stack([run.param(c) for c in cols])
    w    = run.weights

    fig = corner.corner(
        data, weights=w, labels=labels,
        color=C0,
        levels=(0.68, 0.95),
        smooth=1.0, smooth1d=1.0,
        plot_datapoints=False,
        fill_contours=True,
        contourf_kwargs={"colors": [plt.cm.Blues(0.25), plt.cm.Blues(0.55), "white"],
                         "alpha": 0.9},
        contour_kwargs={"linewidths": 0.6},
        hist_kwargs={"linewidth": 0.8},
        label_kwargs={"fontsize": 7},
        title_kwargs={"fontsize": 7},
        show_titles=True, title_fmt=".3f",
        quantiles=[0.16, 0.5, 0.84],
        fig=plt.figure(figsize=(MNRAS_2COL, MNRAS_2COL)),
    )
    fig.suptitle(r"GW170817 — \texttt{IMRPhenomD\_NRTidalv2}, $n_\mathrm{live}=5000$",
                 fontsize=8, y=1.01)
    savefig(fig, "fig01_gw170817_corner")


# ════════════════════════════════════════════════════════════════════════════
# Figure 2 — H₀ posteriors: waveform comparison
# ════════════════════════════════════════════════════════════════════════════
def fig_h0_waveform():
    print("Fig 2: H₀ waveform comparison …")
    runs = [
        ("s07__gw170817__imrphenomd_nrtidalv2__baseline_lvkbounds__seed0000",
         r"\texttt{IMRPhenomD\_NRTidalv2}", C0, "-"),
        ("s07__gw170817__imrphenomxas_nrtidalv3__baseline_lvkbounds__seed0000",
         r"\texttt{IMRPhenomXAS\_NRTidalv3}", C1, "--"),
        ("s07__gw170817__imrphenompv2__baseline_lvkbounds__seed0000",
         r"\texttt{IMRPhenomPv2} (no tides)", C3, ":"),
    ]
    xgrid = np.linspace(30, 200, 800)

    fig, ax = plt.subplots(figsize=(MNRAS_COL * 1.5, MNRAS_COL))
    for rid, label, col, ls in runs:
        run = load_run(rid)
        x = run.param("H_0"); w = run.weights
        ax.plot(xgrid, kde1d(x, w, xgrid), color=col, ls=ls, lw=1.0, label=label)

    # LVK published result: H0 = 70 +13/-8 (Abbott+2017)
    h0_lvk, h0_lo, h0_hi = 70.0, 62.0, 83.0
    ax.axvline(h0_lvk, color=GREY, lw=0.7, ls="-.", zorder=0,
               label=r"LVK (Abbott et al.\ 2017)")
    ax.axvspan(h0_lo, h0_hi, color=GREY, alpha=0.12, zorder=0)
    ax.axvline(67.4, color="k", lw=0.5, ls=":", zorder=0,
               label=r"Planck CMB ($H_0=67.4$)")

    ax.set_xlabel(r"$H_0\;[\mathrm{km\,s^{-1}\,Mpc^{-1}}]$")
    ax.set_ylabel(r"Probability density")
    ax.set_xlim(30, 200)
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper right", fontsize=6)
    ax.set_title(r"GW170817 $H_0$ posterior — waveform comparison")
    fig.tight_layout()
    savefig(fig, "fig02_h0_waveform_comparison")


# ════════════════════════════════════════════════════════════════════════════
# Figure 3 — n_live convergence (3-panel)
# ════════════════════════════════════════════════════════════════════════════
def fig_nlive_convergence():
    print("Fig 3: n_live convergence …")
    nlive_runs = [
        (500,   "s13__gw170817__imrphenomd_nrtidalv2__baseline__nlive00500__seed0000"),
        (1000,  "s13__gw170817__imrphenomd_nrtidalv2__baseline__nlive01000__seed0000"),
        (2500,  "s13__gw170817__imrphenomd_nrtidalv2__baseline__nlive02500__seed0000"),
        (5000,  "s07__gw170817__imrphenomd_nrtidalv2__baseline_lvkbounds__seed0000"),
        (10000, "s13__gw170817__imrphenomd_nrtidalv2__baseline__nlive10000__seed0000"),
        (20000, "s13__gw170817__imrphenomd_nrtidalv2__baseline__nlive20000__seed0000"),
    ]
    nl, logz, sigz, med, q16, q84, wcs = [], [], [], [], [], [], []
    for n, rid in nlive_runs:
        run = load_run(rid)
        x = run.param("H_0"); w = run.weights
        lz, sz = read_log_evidence_from_log(os.path.join(RESULTS_ROOT, rid))
        lo, hi = weighted_quantiles(x, w, [0.15865, 0.84135])
        nl.append(n); logz.append(lz); sigz.append(sz if sz else 0)
        med.append(weighted_median(x, w)); q16.append(lo); q84.append(hi)
        wc = wallclock(rid)
        wcs.append(wc / 60.0 if wc else np.nan)

    nl = np.array(nl); logz = np.array(logz); sigz = np.array(sigz)
    med = np.array(med); q16 = np.array(q16); q84 = np.array(q84)
    wcs = np.array(wcs)

    fig, axes = plt.subplots(1, 3, figsize=(MNRAS_2COL, MNRAS_2COL / GOLDEN * 0.7))

    # Panel a: log Z
    ax = axes[0]
    ax.errorbar(nl, logz, yerr=sigz, fmt="o", color=C0, ms=3.5, lw=0.8, capsize=2)
    ax.set_xscale("log")
    ax.set_xlabel(r"$n_\mathrm{live}$")
    ax.set_ylabel(r"$\ln\mathcal{Z}$")
    ax.set_title(r"(a) Evidence")
    ax.set_xticks([500, 1000, 2500, 5000, 10000, 20000])
    ax.set_xticklabels(["500", "1k", "2.5k", "5k", "10k", "20k"], fontsize=6)

    # Panel b: H₀ median + 68% CI
    ax = axes[1]
    ax.fill_between(nl, q16, q84, alpha=0.25, color=C0, step=None)
    ax.plot(nl, med, "o-", color=C0, ms=3.5, lw=0.8)
    ax.set_xscale("log")
    ax.set_xlabel(r"$n_\mathrm{live}$")
    ax.set_ylabel(r"$H_0\;[\mathrm{km\,s^{-1}\,Mpc^{-1}}]$")
    ax.set_title(r"(b) $H_0$ convergence")
    ax.set_xticks([500, 1000, 2500, 5000, 10000, 20000])
    ax.set_xticklabels(["500", "1k", "2.5k", "5k", "10k", "20k"], fontsize=6)

    # Panel c: wall-clock
    ax = axes[2]
    ax.plot(nl, wcs, "s-", color=C2, ms=3.5, lw=0.8, label="heterodyned")
    # Add unheterodyned timing points from s04/s05
    unhet = [(500, 7317/60), (2500, 37240/60)]
    ax.scatter([u[0] for u in unhet], [u[1] for u in unhet],
               marker="^", color=C5, s=20, zorder=5, label="unheterodyned")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"$n_\mathrm{live}$")
    ax.set_ylabel(r"Wall-clock time [min]")
    ax.set_title(r"(c) Runtime scaling")
    ax.set_xticks([500, 1000, 2500, 5000, 10000, 20000])
    ax.set_xticklabels(["500", "1k", "2.5k", "5k", "10k", "20k"], fontsize=6)
    ax.legend(fontsize=6, loc="upper left")

    fig.tight_layout()
    savefig(fig, "fig03_nlive_convergence")


# ════════════════════════════════════════════════════════════════════════════
# Figure 4 — Sampler robustness (num_delete + n_bins, 2×2)
# ════════════════════════════════════════════════════════════════════════════
def fig_robustness():
    print("Fig 4: robustness sweep …")
    # num_delete
    nd_runs = [
        (500,  "s08__gw170817__imrphenomd_nrtidalv2__baseline__ndelete00500__seed0000"),
        (1250, "s08__gw170817__imrphenomd_nrtidalv2__baseline__ndelete01250__seed0000"),
        (2500, "s08__gw170817__imrphenomd_nrtidalv2__baseline__ndelete02500__seed0000"),
        (3750, "s08__gw170817__imrphenomd_nrtidalv2__baseline__ndelete03750__seed0000"),
    ]
    nb_runs = [
        (251,  "s09__gw170817__imrphenomd_nrtidalv2__baseline__nbins00251__seed0000"),
        (501,  "s09__gw170817__imrphenomd_nrtidalv2__baseline__nbins00501__seed0000"),
        (1001, "s09__gw170817__imrphenomd_nrtidalv2__baseline__nbins01001__seed0000"),
    ]

    def extract(runs):
        xs, lzs, szs, meds, los, his = [], [], [], [], [], []
        for val, rid in runs:
            run = load_run(rid)
            x = run.param("H_0"); w = run.weights
            lz, sz = read_log_evidence_from_log(os.path.join(RESULTS_ROOT, rid))
            lo, hi = weighted_quantiles(x, w, [0.15865, 0.84135])
            xs.append(val); lzs.append(lz); szs.append(sz if sz else 0)
            meds.append(weighted_median(x, w)); los.append(lo); his.append(hi)
        return map(np.array, (xs, lzs, szs, meds, los, his))

    nd = extract(nd_runs)
    nb = extract(nb_runs)

    fig, axes = plt.subplots(2, 2, figsize=(MNRAS_2COL, MNRAS_2COL * 0.65))

    for row, (xs, lzs, szs, meds, los, his), xlabel, ref_x in [
        (0, nd, r"$n_\mathrm{delete}$ (fraction of $n_\mathrm{live}$)", 2500),
        (1, nb, r"Number of heterodyne bins", 501),
    ]:
        fracs = xs / 5000 if row == 0 else xs

        ax = axes[row][0]
        ax.errorbar(fracs, lzs, yerr=szs, fmt="o", color=C0, ms=3.5, lw=0.8, capsize=2)
        ref_frac = ref_x / 5000 if row == 0 else ref_x
        ax.axvline(ref_frac, color=GREY, lw=0.6, ls="--")
        ax.set_xlabel(r"$n_\mathrm{delete}/n_\mathrm{live}$" if row == 0 else xlabel)
        ax.set_ylabel(r"$\ln\mathcal{Z}$")
        ax.set_title(r"(a) Evidence" if row == 0 else r"(c) Evidence")

        ax = axes[row][1]
        ax.fill_between(fracs, los, his, alpha=0.25, color=C0)
        ax.plot(fracs, meds, "o-", color=C0, ms=3.5, lw=0.8)
        ax.axvline(ref_frac, color=GREY, lw=0.6, ls="--", label="default")
        ax.set_xlabel(r"$n_\mathrm{delete}/n_\mathrm{live}$" if row == 0 else xlabel)
        ax.set_ylabel(r"$H_0\;[\mathrm{km\,s^{-1}\,Mpc^{-1}}]$")
        ax.set_title(r"(b) $H_0$ median $\pm 68\%$" if row == 0 else r"(d) $H_0$ median $\pm 68\%$")
        ax.legend(fontsize=6)

    fig.tight_layout()
    savefig(fig, "fig04_robustness")


# ════════════════════════════════════════════════════════════════════════════
# Figure 5 — d_L–ι bimodality (2D posterior + mode annotations)
# ════════════════════════════════════════════════════════════════════════════
def fig_bimodality():
    print("Fig 5: bimodality …")
    run_a = load_run("s10__gw170817__imrphenomd_nrtidalv2__flatz__dL30-75__refGWTC1__seed0000")
    run_b = load_run("s10__gw170817__imrphenomd_nrtidalv2__flatz__dL10-30__refGWTC1__seed0000")
    run_full = load_run("s10__gw170817__imrphenomd_nrtidalv2__flatz__dL10-75__refModeB__seed0000")

    fig, axes = plt.subplots(1, 2, figsize=(MNRAS_2COL, MNRAS_2COL / GOLDEN * 0.65))

    # Left: full posterior in d_L-iota plane
    ax = axes[0]
    dl = run_full.param("d_L"); iota = run_full.param("iota"); w = run_full.weights
    h, xe, ye = np.histogram2d(dl, iota, bins=80, weights=w, density=True)
    ax.contourf(0.5*(xe[:-1]+xe[1:]), 0.5*(ye[:-1]+ye[1:]), h.T,
                levels=10, cmap="Blues", alpha=0.85)
    ax.contour(0.5*(xe[:-1]+xe[1:]), 0.5*(ye[:-1]+ye[1:]), h.T,
               levels=5, colors="white", linewidths=0.4, alpha=0.6)
    ax.set_xlabel(r"$d_L\,[\mathrm{Mpc}]$")
    ax.set_ylabel(r"$\iota\,[\mathrm{rad}]$")
    ax.set_title(r"(a) Full posterior (flat-$z$, $d_L\in[10,75]$\,Mpc)")
    ax.text(16, 1.2, r"Mode B", fontsize=6, color="white", weight="bold")
    ax.text(35, 2.8, r"Mode A", fontsize=6, color="white", weight="bold")

    # Right: 1D d_L posteriors for each mode + combined
    ax = axes[1]
    xgrid = np.linspace(5, 80, 500)
    for run, label, col, ls in [
        (run_full, r"combined $[10,75]$\,Mpc",  C0, "-"),
        (run_a,    r"Mode A $[30,75]$\,Mpc",    C2, "--"),
        (run_b,    r"Mode B $[10,30]$\,Mpc",    C3, ":"),
    ]:
        dl = run.param("d_L"); w = run.weights
        ax.plot(xgrid, kde1d(dl, w, xgrid), color=col, ls=ls, lw=0.9, label=label)
    ax.set_xlabel(r"$d_L\,[\mathrm{Mpc}]$")
    ax.set_ylabel(r"Probability density")
    ax.set_title(r"(b) $d_L$ marginals by mode")
    ax.legend(fontsize=6)
    ax.set_xlim(5, 80)
    ax.set_ylim(bottom=0)

    fig.tight_layout()
    savefig(fig, "fig05_bimodality")


# ════════════════════════════════════════════════════════════════════════════
# Figure 6 — GW-only vs standard siren comparison
# ════════════════════════════════════════════════════════════════════════════
def fig_gw_only():
    print("Fig 6: GW-only vs siren …")
    pairs = [
        ("s12__gw170817__imrphenomd_nrtidalv2__gw_only__seed0000",
         "s07__gw170817__imrphenomd_nrtidalv2__baseline_lvkbounds__seed0000",
         r"\texttt{IMRPhenomD\_NRTidalv2}", C0),
        ("s12__gw170817__imrphenomxas_nrtidalv3__gw_only__seed0000",
         "s07__gw170817__imrphenomxas_nrtidalv3__baseline_lvkbounds__seed0000",
         r"\texttt{IMRPhenomXAS\_NRTidalv3}", C1),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(MNRAS_2COL, MNRAS_2COL / GOLDEN * 0.6))

    xd = np.linspace(5, 80, 500)
    xi = np.linspace(0, np.pi, 500)

    for gw_rid, si_rid, label, col in pairs:
        rg = load_run(gw_rid); rs = load_run(si_rid)
        axes[0].plot(xd, kde1d(rg.param("d_L"), rg.weights, xd),
                     color=col, ls="--", lw=0.9)
        axes[0].plot(xd, kde1d(rs.param("d_L"), rs.weights, xd),
                     color=col, ls="-",  lw=0.9)
        axes[1].plot(xi, kde1d(rg.param("iota"), rg.weights, xi),
                     color=col, ls="--", lw=0.9)
        axes[1].plot(xi, kde1d(rs.param("iota"), rs.weights, xi),
                     color=col, ls="-",  lw=0.9)

    axes[0].set_xlabel(r"$d_L\,[\mathrm{Mpc}]$")
    axes[0].set_ylabel("Probability density")
    axes[0].set_title(r"(a) Luminosity distance")
    axes[0].set_xlim(5, 75); axes[0].set_ylim(bottom=0)

    axes[1].set_xlabel(r"$\iota\,[\mathrm{rad}]$")
    axes[1].set_ylabel("Probability density")
    axes[1].set_title(r"(b) Inclination angle")
    axes[1].set_xlim(0, np.pi); axes[1].set_ylim(bottom=0)

    # legend
    handles = [
        Line2D([], [], color="k", ls="-",  lw=0.9, label="Standard siren"),
        Line2D([], [], color="k", ls="--", lw=0.9, label="GW-only"),
        Line2D([], [], color=C0,  ls="-",  lw=1.5, label=r"\texttt{IMRPhenomD\_NRTidalv2}"),
        Line2D([], [], color=C1,  ls="-",  lw=1.5, label=r"\texttt{IMRPhenomXAS\_NRTidalv3}"),
    ]
    axes[1].legend(handles=handles, fontsize=5.5, loc="upper right")
    fig.tight_layout()
    savefig(fig, "fig06_gw_only_vs_siren")


# ════════════════════════════════════════════════════════════════════════════
# Figure 7 — GW150914 posteriors corner
# ════════════════════════════════════════════════════════════════════════════
def fig_gw150914_corner():
    print("Fig 7: GW150914 corner …")
    run = load_run("s06__gw150914__imrphenomxphm__lvkbounds__seed0000")
    cols   = ["M_c", "q", "d_L", "iota"]
    labels = [r"$\mathcal{M}_c\,[M_\odot]$", r"$q$",
              r"$d_L\,[\mathrm{Mpc}]$", r"$\iota\,[\mathrm{rad}]$"]
    data = np.column_stack([run.param(c) for c in cols])

    fig = corner.corner(
        data, weights=run.weights, labels=labels,
        color=C2,
        levels=(0.68, 0.95),
        smooth=1.0, smooth1d=1.0,
        plot_datapoints=False, fill_contours=True,
        contourf_kwargs={"colors": [plt.cm.Greens(0.25), plt.cm.Greens(0.55), "white"],
                         "alpha": 0.9},
        contour_kwargs={"linewidths": 0.6},
        hist_kwargs={"linewidth": 0.8},
        label_kwargs={"fontsize": 7},
        title_kwargs={"fontsize": 7},
        show_titles=True, title_fmt=".2f",
        quantiles=[0.16, 0.5, 0.84],
        fig=plt.figure(figsize=(MNRAS_COL * 1.5, MNRAS_COL * 1.5)),
    )
    fig.suptitle(r"GW150914 — \texttt{IMRPhenomXPHM}, $n_\mathrm{live}=5000$",
                 fontsize=8, y=1.01)
    savefig(fig, "fig07_gw150914_corner")


# ════════════════════════════════════════════════════════════════════════════
# Figure 8 — PSD sensitivity + ref-params robustness
# ════════════════════════════════════════════════════════════════════════════
def fig_psd_refparams():
    print("Fig 8: PSD + ref-params …")
    xgrid = np.linspace(30, 180, 600)

    # Load gwtc1 TaylorF2 baseline
    baseline_csv = os.path.join(REPO, "Results", "gwtc1_phasemarg",
                                "PhaseMarg_Heterodyned_TaylorF2_local_psd-gwtc1_ref-gwtc1_baseline.csv")
    bl_df, bl_w = read_nested_samples_csv(baseline_csv)
    bl_x = bl_df["H_0"].to_numpy().astype(float)

    # gwtc1 IMR baseline for ref-params panel
    imr_csv = os.path.join(REPO, "Results", "gwtc1_phasemarg",
                           "PhaseMarg_Heterodyned_IMRPhenomD_NRTidalv2_local_psd-gwtc1_ref-gwtc1_baseline.csv")
    imr_df, imr_w = read_nested_samples_csv(imr_csv)
    imr_x = imr_df["H_0"].to_numpy().astype(float)

    fig, axes = plt.subplots(1, 2, figsize=(MNRAS_2COL, MNRAS_2COL / GOLDEN * 0.6))

    # Left: PSD sensitivity (TaylorF2)
    ax = axes[0]
    ax.plot(xgrid, kde1d(bl_x, bl_w, xgrid), color=C0, lw=0.9, label=r"GWTC-1 PSD (ref.)")
    for rid, label, col, ls in [
        ("s05__gw170817__taylorf2__baseline__psdKazewong__seed0000",
         r"Dax et al.\ PSD", C1, "--"),
        ("s05__gw170817__taylorf2__baseline__psdBilby__seed0000",
         r"Bilby PSD", C2, ":"),
    ]:
        run = load_run(rid)
        ax.plot(xgrid, kde1d(run.param("H_0"), run.weights, xgrid),
                color=col, ls=ls, lw=0.9, label=label)
    ax.set_xlabel(r"$H_0\;[\mathrm{km\,s^{-1}\,Mpc^{-1}}]$")
    ax.set_ylabel("Probability density")
    ax.set_title(r"(a) PSD sensitivity (\texttt{TaylorF2})")
    ax.set_xlim(30, 180); ax.set_ylim(bottom=0)
    ax.legend(fontsize=6)

    # Right: reference params (IMRPhenomD_NRTidalv2)
    ax = axes[1]
    ax.plot(xgrid, kde1d(imr_x, imr_w, xgrid), color=C0, lw=0.9, label=r"GWTC-1 ref.\ params")
    run_opt = load_run("s05__gw170817__imrphenomd_nrtidalv2__baseline__refOptimize__seed0000")
    ax.plot(xgrid, kde1d(run_opt.param("H_0"), run_opt.weights, xgrid),
            color=C3, ls="--", lw=0.9, label=r"Optimized ref.\ params")
    ax.set_xlabel(r"$H_0\;[\mathrm{km\,s^{-1}\,Mpc^{-1}}]$")
    ax.set_ylabel("Probability density")
    ax.set_title(r"(b) Heterodyne reference sensitivity")
    ax.set_xlim(30, 180); ax.set_ylim(bottom=0)
    ax.legend(fontsize=6)

    fig.tight_layout()
    savefig(fig, "fig08_psd_refparams")


# ════════════════════════════════════════════════════════════════════════════
# Figure 9 — Speedup: heterodyned vs unheterodyned
# ════════════════════════════════════════════════════════════════════════════
def fig_speedup():
    print("Fig 9: speedup …")
    # Heterodyned timing from s13
    het_nlive = [500, 1000, 2500, 5000, 10000, 20000]
    het_rids  = [
        "s13__gw170817__imrphenomd_nrtidalv2__baseline__nlive00500__seed0000",
        "s13__gw170817__imrphenomd_nrtidalv2__baseline__nlive01000__seed0000",
        "s13__gw170817__imrphenomd_nrtidalv2__baseline__nlive02500__seed0000",
        "s07__gw170817__imrphenomd_nrtidalv2__baseline_lvkbounds__seed0000",
        "s13__gw170817__imrphenomd_nrtidalv2__baseline__nlive10000__seed0000",
        "s13__gw170817__imrphenomd_nrtidalv2__baseline__nlive20000__seed0000",
    ]
    het_t = [wallclock(r) / 60.0 for r in het_rids]

    unhet_nlive = [500, 2500]
    unhet_t     = [7317 / 60.0, 37240 / 60.0]

    fig, ax = plt.subplots(figsize=(MNRAS_COL * 1.4, MNRAS_COL))
    ax.plot(het_nlive, het_t, "o-", color=C0, ms=4, lw=1.0,
            label=r"Heterodyned ($N_\mathrm{bins}=501$)")
    ax.scatter(unhet_nlive, unhet_t, marker="^", color=C5, s=25, zorder=5,
               label=r"Unheterodyned (full likelihood)")

    # Annotate speedup arrows at n_live=500 and 2500
    for nl, ht, ut in [(500, het_t[0], unhet_t[0]), (2500, het_t[2], unhet_t[1])]:
        speedup = ut / ht
        ax.annotate("", xy=(nl, ht), xytext=(nl, ut),
                    arrowprops=dict(arrowstyle="<->", color="k", lw=0.6))
        ax.text(nl * 1.12, np.sqrt(ht * ut),
                rf"${speedup:.0f}\times$", fontsize=6, va="center")

    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"$n_\mathrm{live}$")
    ax.set_ylabel(r"Wall-clock time [min]")
    ax.set_title(r"Heterodyning speedup — \texttt{IMRPhenomD\_NRTidalv2}")
    ax.legend(fontsize=6, loc="upper left")
    ax.set_xticks([500, 1000, 2500, 5000, 10000, 20000])
    ax.set_xticklabels(["500", "1k", "2.5k", "5k", "10k", "20k"], fontsize=6)
    fig.tight_layout()
    savefig(fig, "fig09_speedup")


# ════════════════════════════════════════════════════════════════════════════
# Figure 10 — Summary H₀ comparison table (all waveforms + GW-only)
# ════════════════════════════════════════════════════════════════════════════
def fig_h0_summary():
    print("Fig 10: H₀ summary …")
    entries = [
        # (label, run_id, color, marker)
        (r"\texttt{NRTidalv2} (siren)",   "s07__gw170817__imrphenomd_nrtidalv2__baseline_lvkbounds__seed0000",   C0, "o"),
        (r"\texttt{XAS\_NRTv3} (siren)",  "s07__gw170817__imrphenomxas_nrtidalv3__baseline_lvkbounds__seed0000", C1, "s"),
        (r"\texttt{Pv2} (no tides)",      "s07__gw170817__imrphenompv2__baseline_lvkbounds__seed0000",            C3, "^"),
        (r"\texttt{NRTidalv2} (GW-only)", "s12__gw170817__imrphenomd_nrtidalv2__gw_only__seed0000",              C4, "D"),
        (r"\texttt{XAS\_NRTv3} (GW-only)","s12__gw170817__imrphenomxas_nrtidalv3__gw_only__seed0000",            C2, "P"),
    ]

    # Recession velocity for GW170817 (corrected for peculiar motion, Abbott+2017)
    V_REC = 3017.0  # km/s

    fig, ax = plt.subplots(figsize=(MNRAS_COL * 1.5, MNRAS_COL * 0.9))
    y = np.arange(len(entries))
    for i, (label, rid, col, mk) in enumerate(entries):
        run = load_run(rid)
        if "H_0" in run.samples.columns:
            x = run.param("H_0")
        else:
            # GW-only run: derive effective H₀ = v_rec / d_L
            x = V_REC / run.param("d_L")
        w = run.weights
        med = weighted_median(x, w)
        lo, hi = weighted_quantiles(x, w, [0.15865, 0.84135])
        lo5, hi5 = weighted_quantiles(x, w, [0.025, 0.975])
        ax.plot([lo5, hi5], [i, i], color=col, lw=1.2, alpha=0.4)
        ax.plot([lo, hi],   [i, i], color=col, lw=2.5)
        ax.scatter([med], [i], color=col, marker=mk, s=22, zorder=5)
        ax.text(195, i, label, va="center", ha="right", fontsize=6.5)

    # LVK reference
    ax.axvspan(62, 83, color=GREY, alpha=0.15, label=r"LVK 68\% (Abbott 2017)")
    ax.axvline(70, color=GREY, lw=0.7, ls="-.")
    ax.axvline(67.4, color="k", lw=0.5, ls=":", label=r"Planck $H_0$")

    ax.set_xlabel(r"$H_0\;[\mathrm{km\,s^{-1}\,Mpc^{-1}}]$")
    ax.set_yticks([]); ax.set_xlim(40, 200)
    ax.set_title(r"GW170817 $H_0$ constraints — this work")
    handles = [
        Patch(color=GREY, alpha=0.3, label=r"LVK 68\% (Abbott+2017)"),
        Line2D([], [], color="k", ls=":", lw=0.7, label=r"Planck CMB"),
        Line2D([], [], color="k", lw=2.5, label=r"68\% CI"),
        Line2D([], [], color="k", lw=1.2, alpha=0.5, label=r"95\% CI"),
    ]
    ax.legend(handles=handles, fontsize=6, loc="upper left")
    fig.tight_layout()
    savefig(fig, "fig10_h0_summary")


# ════════════════════════════════════════════════════════════════════════════
# Run all
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"Writing figures to {OUT}/")
    fig_gw170817_corner()
    fig_h0_waveform()
    fig_nlive_convergence()
    fig_robustness()
    fig_bimodality()
    fig_gw_only()
    fig_gw150914_corner()
    fig_psd_refparams()
    fig_speedup()
    fig_h0_summary()
    print("Done.")
