#!/usr/bin/env bash
# Run all plotting scripts.
# Output: Results/gwtc1_phasemarg/plots/
set -e

cd "$(dirname "$0")/.."

echo "=== GW150914 corner ==="
python Plots/plot_GW150914.py

echo "=== H0: IMRPhenomD variants (baseline / flatZ / vp250) ==="
python Plots/plot_H0_IMRPhenomD_variants.py

echo "=== H0: TaylorF2 variants (baseline / flatZ / vp250) ==="
python Plots/plot_H0_TaylorF2_variants.py

echo "=== H0: IMRPhenomD reweighted (baseline / reweighted flatZ / vp250) ==="
python Plots/plot_H0_IMRPhenomD_reweighted.py

echo "=== H0: TaylorF2 reweighted (baseline / reweighted flatZ / vp250) ==="
python Plots/plot_H0_TaylorF2_reweighted.py

echo "=== Corner: IMRPhenomD heterodyned vs unheterodyned vs GWTC-1 ==="
python Plots/plot_corner_IMRPhenomD_hetero_vs_unhetero.py

echo "=== Corner: TaylorF2 heterodyned vs unheterodyned vs GWTC-1 ==="
python Plots/plot_corner_TaylorF2_hetero_vs_unhetero.py

echo "=== H0: baseline IMRPhenomD only ==="
python Plots/plot_H0_baseline_IMRPhenomD.py

echo "=== H0: baseline TaylorF2 only ==="
python Plots/plot_H0_baseline_TaylorF2.py

echo "=== Corner: IMRPhenomD + TaylorF2 + GWTC-1 ==="
python Plots/plot_corner_combined_waveforms.py

echo "=== H0: reweighted vs sampled flat-in-z comparison ==="
python Plots/plot_H0_reweight_comparison.py

echo "=== d_L posterior comparison ==="
python Plots/plot_dL_posterior.py

echo "=== H0: prior vs posterior ==="
python Plots/plot_prior_vs_posterior_H0.py

echo ""
echo "=== Computing analysis tables ==="

echo "--- Evidence table ---"
python Plots/compute_evidence_table.py

echo "--- Summary statistics ---"
python Plots/compute_summary_stats.py

echo "--- Waveform systematics ---"
python Plots/compute_waveform_systematics.py

echo ""
echo "All plots saved to Results/gwtc1_phasemarg/plots/"
echo "All tables saved to Results/gwtc1_phasemarg/"
