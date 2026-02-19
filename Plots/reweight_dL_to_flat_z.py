"""
Reweight d_L posterior samples from Beta(3,1) prior to flat-in-z prior.
========================================================================

Takes nested sampling CSV results (with Beta(3,1) ∝ d_L^2 prior on d_L)
and reweights them to a flat-in-redshift prior using importance sampling.

Derivation
----------
Old prior:  p_old(d_L) = Beta(3,1) on [lo, hi] = 3u^2 / (hi - lo),
            where u = (d_L - lo) / (hi - lo).

New prior:  flat in z, i.e. p_new(z) = const.

Using d_L = cz/H_0 (low-z Hubble law),  |dz/dd_L| = H_0/c,  |dd_L/dz| = c/H_0.

Importance reweighting (change of variable from d_L to z):

    w_new / w_old = p_new(z) / p_old(z)

where the old prior expressed in z-space is:

    p_old(z) = p_old(d_L) * |dd_L/dz| = p_old(d_L) * c / H_0

Therefore:

    w_new / w_old  = p_new(z) / [p_old(d_L) * (c / H_0)]
                   = const * H_0 / [c * p_old(d_L)]
                   ∝ H_0 / p_old(d_L)
                   = H_0 * (hi - lo) / (3 u^2)
                   = H_0 * (hi - lo)^3 / [3 * (d_L - lo)^2]

Since we normalise weights at the end, all multiplicative constants cancel:

    w_new ∝ w_old * H_0 / (d_L - d_L_lo)^2

Usage:
    python reweight_dL_to_flat_z.py <input_csv> [--output <output_csv>]
"""

import argparse
import numpy as np
from anesthetic import read_chains, NestedSamples

# Prior bounds for d_L (must match the sampling script)
D_L_LO = 1.0   # Mpc
D_L_HI = 75.0  # Mpc

parser = argparse.ArgumentParser(
    description='Reweight d_L samples from Beta(3,1) to flat-in-z prior')
parser.add_argument('input_csv', help='Path to input CSV (nested sampling results)')
parser.add_argument('--output', '-o', default=None,
                    help='Output CSV path (default: append _flatZ to input name)')
args = parser.parse_args()

# Load samples
samples = read_chains(args.input_csv)
print(f"Loaded {len(samples)} samples from {args.input_csv}")

# Extract needed columns
d_L = samples['d_L'].to_numpy()
H_0 = samples['H_0'].to_numpy()

# Original nested sampling weights (from evidence calculation)
weights_old = np.asarray(samples.get_weights())

# Reweighting factor: w_new ∝ w_old * H_0 / (d_L - d_L_lo)^2
# Guard against d_L == d_L_lo (u=0) which would give infinite weight
u = (d_L - D_L_LO) / (D_L_HI - D_L_LO)
reweight_factor = H_0 / (u**2 + 1e-30)

weights_new = weights_old * reweight_factor

# Normalise
weights_new /= weights_new.sum()

# Effective sample size (diagnostic)
n_eff = 1.0 / np.sum(weights_new**2)
print(f"Effective sample size after reweighting: {n_eff:.0f} / {len(samples)}")

# Build output: copy the samples DataFrame, overwrite the weights column
# For anesthetic NestedSamples, weights are derived from logL and logL_birth,
# so we save as a plain weighted CSV instead.
output_path = args.output
if output_path is None:
    output_path = args.input_csv.replace('.csv', '_reweighted_flatZ.csv')

# Safety: warn if the input filename suggests it already has a flat-in-z prior
if 'flatZ' in args.input_csv or 'flat_z' in args.input_csv.lower():
    print("  WARNING: Input filename contains 'flatZ' — are you sure this has a Beta(3,1) d_L prior?")
    print("           Reweighting a file that already has flat-in-z prior will give incorrect results.")

# Save as CSV with a weights column appended
import pandas as pd
df = pd.DataFrame(samples.to_numpy(), columns=samples.columns.get_level_values(0))
df['weight'] = weights_new
df.to_csv(output_path, index=False)
print(f"Saved reweighted samples to {output_path}")

# Print summary statistics for key parameters
print(f"\n{'='*50}")
print(f"Reweighted summary (flat-in-z prior)")
print(f"{'='*50}")
for param in ['d_L', 'H_0', 'M_c', 'q', 'iota']:
    if param in df.columns:
        vals = df[param].to_numpy()
        mean = np.average(vals, weights=weights_new)
        var = np.average((vals - mean)**2, weights=weights_new)
        lo, med, hi = np.interp(
            [0.05, 0.50, 0.95],
            np.cumsum(weights_new[np.argsort(vals)]),
            np.sort(vals),
        )
        print(f"  {param:8s}: mean={mean:.2f}, median={med:.2f}, 90% CI=[{lo:.2f}, {hi:.2f}]")
print(f"{'='*50}")
