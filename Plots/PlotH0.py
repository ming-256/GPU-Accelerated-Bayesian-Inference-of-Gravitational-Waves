
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
from pesummary.utils.utils import logger
import logging
logger.setLevel(logging.CRITICAL)
import anesthetic
import numpy as np
from anesthetic import make_2d_axes
from scipy.stats import gaussian_kde
import matplotlib as mpl

# Enable LaTeX-style font rendering
mpl.rcParams['text.usetex'] = True
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = ['Computer Modern']

file_name = 'GW170817_GWTC-1.hdf5'
label = 'H0Plot_SHoES_Planck_40_200'

Sample1 = anesthetic.read_chains('original_code_8000.csv')
Sample2 = anesthetic.read_chains('GW170817_Canonical_40_200_4.csv')
H0_1 = Sample1['H_0']

fig, axes = make_2d_axes(params=['H_0'], figsize=(10, 6))
ax = axes["H_0"]['H_0']

axes.tick_params(grid_alpha=0)
ax.set_xlim(50,140)
map_value = 69.84009427510232
fig.tight_layout()
ax.set_xticks(np.arange(50, 141, 10))
Sample1.plot_2d(axes, kind='kde_1d', color='b', alpha=0.8, label='$P(H_0 \ |$ GW170817) New')
Sample2.plot_2d(axes, kind='kde_1d', color='m', alpha=0.8, label='$P(H_0 \ |$ GW170817) Canonical')
axes.axlines({'H_0': [63.722832826195514, 87.65858205914093]}, ls='--', color='b')
axes.axlines({'H_0': [59.38955679392043, 119.48937712151974]}, ls=':', color='b')
axes.axspans({'H_0': [65.7, 68.2]}, edgecolor='none', alpha=0.3, upper=False, color='#6DE6AC')
axes.axspans({'H_0': [69.76, 76.72]}, edgecolor='none', alpha=0.3, upper=False, color='#F19851')
axes.axspans({'H_0': [66.93-0.62, 66.93+0.62]}, edgecolor='none', alpha=0.3, upper=False, color='#0CDE79', label = 'Planck')
axes.axspans({'H_0': [73.24-1.74, 73.24+1.74]}, edgecolor='none', alpha=0.3, upper=False, color='#E87317', label = 'SHoES')
ax.set_xlabel('$H_0$ (km s$^{-1}$ Mpc$^{-1}$)')
ax.set_ylabel('$P(H_0)$ (km$^{-1}$ s Mpc)')
for spine in ax.spines.values():
    spine.set_edgecolor('black')
    spine.set_linewidth(1.5)
kde = gaussian_kde(H0_1)
x_eval = np.linspace(min(H0_1) - 1, max(H0_1) + 1, 10000)
pdf_values = kde(x_eval)
map_value = x_eval[np.argmax(pdf_values)]
print(f'MAP value of H0_1: {map_value}')

ax.legend(frameon=False)
plt.savefig(f'{label}.pdf')
plt.show()
#map_df = pd.DataFrame({'MAP_H_0': [map_value]})
#map_df.to_csv(f'{label}_MAP.csv', index=False)
