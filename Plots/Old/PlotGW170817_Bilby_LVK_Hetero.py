import anesthetic.read
import matplotlib.pyplot as plt
import h5py
import warnings
warnings.filterwarnings('ignore')
import logging
import pandas as pd
import bilby
from anesthetic import NestedSamples, read_chains, MCMCSamples
import anesthetic
import numpy as np
import matplotlib as mpl

# Prefer LaTeX-style font rendering if a LaTeX engine is available,
# otherwise fall back to matplotlib's mathtext (no external LaTeX required).
import shutil
if shutil.which('pdflatex') is not None or shutil.which('latex') is not None:
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = ['Computer Modern']
else:
    mpl.rcParams['text.usetex'] = False
    mpl.rcParams['font.family'] = 'serif'
    # Use Computer Modern look via mathtext if LaTeX isn't installed
    mpl.rcParams['mathtext.fontset'] = 'cm'
file_name = 'GW170817_GWTC-1.hdf5'
gwpath = '~/Desktop/CamProject/Paper/'
#with h5py.File(file_name, 'r') as f:
#    print('H5 datasets:')
 #   print(list(f))
    # Extract data into a dictionary
data_dict = {}
with h5py.File(file_name, "r") as hdf_file:
    dataset = hdf_file["IMRPhenomPv2NRT_lowSpin_posterior"]
    for name in dataset.dtype.names:
        data_dict[name] = np.array(dataset[name])  # Convert to NumPy array
#print(data_dict)
# Print first few values for verification
#for key, values in data_dict.items():
#    print(f"{key}: {values[:5]}")
# print('Found run labels:')
# print(data.labels)
#data.priors['analytic']['C01:IMRPhenomXPHM']['chirp_mass']

parameters = sorted(list(data_dict.keys()))
# print(parameters)
# print(parameters)
#GW170817_Uniform_Components_Short_Old.csv .csv
# GW170817_Heterodyned_Distance_Spin.csv
# GW170817_Heterodyned_NRTidal_32
'''
gwpath = '~/Desktop/CamProject/Paper/'
csv_file_path = gwpath + 'HPC_Outputs/PlotsData/GW170817_jim_IMRPhenomD_2.csv'
df = pd.read_csv(csv_file_path)
df.insert(0, '', range(len(df)))
modified_csv_file_path = gwpath + 'HPC_Outputs/PlotsData/GW170817_jim_IMRPhenomD_2_modified.csv'
df.to_csv(modified_csv_file_path, index=False)
'''
#blackjax_samples = anesthetic.read_chains(modified_csv_file_path)

#blackjax_samples = anesthetic.read_chains('Z_GW170817_Heterodyned_NRTidal_Constrained_Bilby_H0_50_140_2.csv')
eta_blackjax_samples = anesthetic.read_chains('GW170817_Canonical_H0_45_250.csv')
# GW170817_Heterodyned_NRTidal_128
# Final_UniformMass_Final.csv  
#GW170817_Heterodyned_Bad_Constraints.csv
#GW170817_Uniform_Components_Short
#GW170817_Uniform_Components_1
#blackjax_samples["M_c"] = (blackjax_samples["M_1"]*blackjax_samples["M_2"])**0.6 / (blackjax_samples["M_1"]+blackjax_samples["M_2"])**0.2
#blackjax_samples["q"] = blackjax_samples["M_2"] / blackjax_samples["M_1"]
#eta_blackjax_samples["q"] = eta_blackjax_samples["M_2"] / eta_blackjax_samples["M_1"]
#eta_blackjax_samples["M_c"] = (eta_blackjax_samples["M_1"]*eta_blackjax_samples["M_2"])**0.6 / (eta_blackjax_samples["M_1"]+eta_blackjax_samples["M_2"])**0.2
'''
eta_blackjax_samples.columns = pd.MultiIndex.from_tuples(
    [(col[0], col[1] if col[0] not in ['M_c', 'q'] else ('$M_c$' if col[0] == 'M_c' else '$q$')) for col in eta_blackjax_samples.columns],
    names=eta_blackjax_samples.columns.names
)

blackjax_samples.columns = pd.MultiIndex.from_tuples(
    [(col[0], col[1] if col[0] not in ['M_c', 'q'] else ('$M_c$' if col[0] == 'M_c' else '$q$')) for col in blackjax_samples.columns],
    names=blackjax_samples.columns.names
)
'''
columns = eta_blackjax_samples.columns
#print(f'Eta Columns: {columns}')
LVK_samples = MCMCSamples(columns=columns)
#GW150914_3.csv
david_blackjax_samples = anesthetic.read_chains('chains/GW170817Points1216')
david_blackjax_samples = david_blackjax_samples.iloc[:, 14:]
bilby_to_blackjax_conversion = {'chirp_mass':'M_c', 'mass_ratio':'q', 'chi_1':'s1_z', 'chi_2':'s2_z', 'luminosity_distance':'d_L', 'theta_jn':'iota', 'phase':'phase_c', 'geocent_time':'t_c', 'ra':'ra', 'dec':'dec', 'psi':'psi'}
david_blackjax_samples.rename(columns=bilby_to_blackjax_conversion, inplace=True)
#print(f'David: {david_blackjax_samples.columns}')
names = []
for col in david_blackjax_samples.columns:
    names.append(col[0])
names = list(names)
#print(f'names: {names}')
david_blackjax_samples.columns = pd.MultiIndex.from_arrays(
    [names]
)
#print(david_blackjax_samples.columns)
#david_blackjax_samples["M_c"] = (david_blackjax_samples["M_1"]*david_blackjax_samples["M_2"])**0.6 / (david_blackjax_samples["M_1"]+david_blackjax_samples["M_2"])**0.2
#david_blackjax_samples["q"] = david_blackjax_samples["M_2"] / david_blackjax_samples["M_1"]
david_blackjax_samples[("s1_z",)] = david_blackjax_samples[("a_1",)] * np.cos(david_blackjax_samples[("tilt_1",)])
david_blackjax_samples[("s2_z",)] = david_blackjax_samples[("a_2",)] * np.cos(david_blackjax_samples[("tilt_2",)])


param_conversion = {'M_1':'m1_detector_frame_Msun' , 'M_2':'m2_detector_frame_Msun', 'd_L':'luminosity_distance_Mpc', 'iota':'costheta_jn', 'ra':'right_ascension', 'dec':'declination', 'spin1':'spin1', 'spin2':'spin2', 'costilt1':'costilt1', 'costilt2':'costilt2'}
for param in param_conversion.keys():
    LVK_samples[param] = data_dict[param_conversion[param]]
LVK_samples["M_c"] = (LVK_samples["M_1"]*LVK_samples["M_2"])**0.6 / (LVK_samples["M_1"]+LVK_samples["M_2"])**0.2
LVK_samples["q"] = LVK_samples["M_2"] / LVK_samples["M_1"]
LVK_samples["iota"] = np.arccos(LVK_samples["iota"])
LVK_samples["s1_z"] = LVK_samples["spin1"] * LVK_samples["costilt1"] 
LVK_samples["s2_z"] = LVK_samples["spin2"] * LVK_samples["costilt2"]
bilby_samples_unprocessed = pd.read_csv(gwpath+'GW150914_Bilby.dat', sep='\s+')
bilby_to_blackjax_conversion = {'chirp_mass':'M_c', 'mass_ratio':'q', 'chi_1':'s1_z', 'chi_2':'s2_z', 'luminosity_distance':'d_L', 'iota':'iota', 'phase':'phase_c', 'geocent_time':'t_c', 'ra':'ra', 'dec':'dec', 'psi':'psi'}
#bilby_samples.rename(columns=bilby_to_blackjax_conversion, inplace=True)
bilby_samples_unprocessed = bilby.gw.conversion.generate_all_bbh_parameters(bilby_samples_unprocessed)
bilby_samples_unprocessed.rename(columns=bilby_to_blackjax_conversion, inplace=True)

bilby_samples = MCMCSamples(columns=LVK_samples.columns)
for param in bilby_to_blackjax_conversion.values():
    if param in bilby_samples_unprocessed.columns:
        bilby_samples[param] = bilby_samples_unprocessed[param]
bilby_samples


# Z_GW170817_NRTidal_Constrained_Bilby_1 
david_blackjax_samples = anesthetic.read_chains('chains/GW170817Points1216')
bilby_to_blackjax_conversion = {'chirp_mass':'M_c', 'mass_ratio':'q', 'luminosity_distance':'d_L', 'theta_jn':'iota', 'phase':'phase_c', 'geocent_time':'t_c', 'ra':'ra', 'dec':'dec', 'psi':'psi'}
david_blackjax_samples = david_blackjax_samples.iloc[:, 14:]
david_blackjax_samples.rename(columns=bilby_to_blackjax_conversion, inplace=True)
david_blackjax_samples["s1_z"] = david_blackjax_samples["a_1"] * np.cos(david_blackjax_samples["tilt_1"])
david_blackjax_samples["s2_z"] = david_blackjax_samples["a_2"] * np.cos(david_blackjax_samples["tilt_2"])

blackjax_samples = anesthetic.read_chains('GW170817_Wrapped_Components5.csv')

#eta_blackjax_samples = anesthetic.read_chains('GW170817_Canonical_40_200_4_reweighted.csv')
# david_blackjax_samples = david_blackjax_samples.replace([np.inf, -np.inf], np.nan).dropna()

label = 'Blackjax_LVK_Bilby_Comparison_kde_a'
label = 'Comparison_Flat_z_prior'
label = 'd_L_Comparison_Prior_Sensitivity_iota'
label = 'JAX_LVK_Bilby_Comparison'
#fig, axes = anesthetic.make_2d_axes(params=['M_c', 'q', 'd_L', 'iota', 'H_0', 'v_p'], upper=False, figsize=(10,10))
fig, axes = anesthetic.make_2d_axes(params=['M_c', 'q', 'd_L', 'iota'], upper=False, figsize=(10,10))
#fig, axes = anesthetic.make_2d_axes(params=['d_L', 'iota'], upper=False, figsize=(10,6))
#bilby_samples.plot_2d(axes, kinds=dict(diagonal='hist_1d', lower='kde_2d'), diagonal_kwargs=dict(bins=30, histtype='step', fill=False), lower_kwargs=dict(levels=[0.99730, 0.95450, 0.68269]), color='g', alpha=0.65, label='Uniform in M_c, q')
#blackjax_samples.plot_2d(axes, kinds=dict(diagonal='hist_1d', lower='kde_2d'), diagonal_kwargs=dict(bins=30, histtype='step', fill=False), lower_kwargs=dict(levels=[0.99730, 0.95450, 0.68269]), color='r', alpha=0.65, label='Blackjax no $H_0$')
#LVK_samples.plot_2d(axes, kinds=dict(diagonal='hist_1d', lower='kde_2d'), diagonal_kwargs=dict(bins=30, histtype='step', fill=False), lower_kwargs=dict(levels=[0.99730, 0.95450, 0.68269]), color='b', alpha=0.65, label='LVK (Ligo-Virgo-KAGRA)')
#eta_blackjax_samples.plot_2d(axes, kinds=dict(diagonal='hist_1d', lower='kde_2d'), diagonal_kwargs=dict(bins=30, histtype='step', fill=False), lower_kwargs=dict(levels=[0.99730, 0.95450, 0.68269]), color='m', alpha=0.65, label='Blackjax $H_0$')
#david_blackjax_samples.plot_2d(axes, kinds=dict(diagonal='hist_1d', lower='kde_2d'), diagonal_kwargs=dict(bins=30, histtype='step', fill=False), lower_kwargs=dict(levels=[0.99730, 0.95450, 0.68269]), color='y', alpha=0.65, label='Unconstrained')

LVK_samples.plot_2d(axes, kinds=dict(diagonal='kde_1d', lower='kde_2d'), lower_kwargs=dict(levels=[0.99730, 0.95450, 0.68269]), color='b', alpha=0.65, label='LVK (Ligo-Virgo-KAGRA)')
#david_blackjax_samples.plot_2d(axes, kinds=dict(diagonal='kde_1d', lower='kde_2d'), lower_kwargs=dict(levels=[0.99730, 0.95450, 0.68269]), color='g', alpha=0.65, label='Bilby')
blackjax_samples.plot_2d(axes, kinds=dict(diagonal='kde_1d', lower='kde_2d'), lower_kwargs=dict(levels=[0.99730, 0.95450, 0.68269]), color='purple', alpha=0.65, label='JAX')
#eta_blackjax_samples.plot_2d(axes, kinds=dict(diagonal='kde_1d', lower='kde_2d'), lower_kwargs=dict(levels=[0.99730, 0.95450, 0.68269]), color='m', alpha=0.65, label='Flat in z (reweighted)')
'''
axes['M_c']['iota'].set_xlabel('$M_c$', labelpad=10)
axes['M_c']['M_c'].set_ylabel('$M_c$')
axes['M_c']['iota'].set_ylabel('$\iota$')
axes['iota']['iota'].set_xlabel('$\iota$')
'''
# Label detector-frame chirp mass explicitly
axes['M_c']['M_c'].set_xlabel(r'$M_c^{\mathrm{det}}$', labelpad=10)
axes['M_c']['M_c'].set_ylabel(r'$M_c^{\mathrm{det}}$')
axes['d_L']['d_L'].set_xlabel('$d_L$ (Mpc)', labelpad=10)
axes['d_L']['d_L'].set_ylabel('$P(d_L)$ (Mpc$^{-1}$)')
axes['d_L']['d_L'].set_xlim(10,50)
axes['d_L']['d_L'].set_xticks(range(10, 51, 5))
axes.iloc[-1, 0].legend(bbox_to_anchor=(len(axes)*0.85,len(axes)*0.8), loc='lower center')
fig.tight_layout()
axes.tick_params(grid_alpha=0)
plt.savefig(f'{label}.pdf')
plt.show()


from anesthetic import read_chains, make_1d_axes
import numpy as np
from scipy.stats import gaussian_kde
from scipy import integrate
# Compatibility for SciPy removing `simps` in newer versions: prefer `simpson`, fallback to `trapz`
try:
    from scipy.integrate import simps
except Exception:
    try:
        from scipy.integrate import simpson as simps
    except Exception:
        def simps(y, x=None, dx=1.0, axis=-1, even='avg'):
            if x is None:
                return np.trapz(y, dx=dx, axis=axis)
            else:
                return np.trapz(y, x, axis=axis)

def test_plot_1d_histogram_eta_blackjax_samples(label, eta_blackjax_samples):
    import matplotlib.pyplot as plt

    fig, axes = make_1d_axes(params='H_0', figsize=(6, 6))
    ax = axes["H_0"]
    ax.set_ylabel('$P(H_0)$ (km s$^{-1}$ Mpc$^{-1}$)')
    axes.tick_params(grid_alpha=0)
    for ax in axes:
        ax.set_xlim(50,140)
        ax.set_xlabel('$H_0$ (km s$^{-1}$ Mpc$^{-1}$)')
        
    fig.tight_layout()

    eta_blackjax_samples.plot_1d(axes, kind='kde_1d', color='b', alpha=0.8, label='Heterodyned Blackjax Low')
    #blackjax_samples.plot_1d(axes, kind='kde_1d', color='r', alpha=0.8, label='Heterodyned Blackjax Mid')
    #david_blackjax_samples.plot_1d(axes, kind='kde_1d', color='y', alpha=0.8, label='Unconstrained')

    samples = eta_blackjax_samples['H_0']
    kde = gaussian_kde(samples)
    x_eval = np.linspace(min(samples) - 1, max(samples) + 1, 10000)
    pdf_values = kde(x_eval)
    map_value = x_eval[np.argmax(pdf_values)]
    print(f'MAP value: {map_value}')
    ax.legend()
    plt.savefig(f'{label}.pdf')
    plt.show()
    map_df = pd.DataFrame({'MAP_H_0': [map_value]})
    map_df.to_csv(f'{label}_MAP.csv', index=False)
# test_plot_1d_histogram_eta_blackjax_samples(label,eta_blackjax_samples)
