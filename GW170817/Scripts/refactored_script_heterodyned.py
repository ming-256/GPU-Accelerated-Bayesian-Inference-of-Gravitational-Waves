import os
os.environ['XLA_PYTHON_CLIENT_PREALLOCATE'] = 'false'
import jax
jax.config.update('jax_enable_x64', True)
import blackjax
import blackjax.ns.adaptive
import matplotlib.pyplot as pltw
import time 
import jax.scipy.stats as stats
import jax.numpy as jnp
import numpy as np
import pandas as pd
import tqdm
import anesthetic
from anesthetic import NestedSamples
from astropy.time import Time
from jimgw.single_event.detector import Detector, H1, L1, V1
from jimgw.single_event.likelihood import original_relative_binning_likelihood as relative_binning_likelihood_function
from jimgw.single_event.waveform import RippleIMRPhenomD_NRTidalv2
import optax
from jaxtyping import Array, Float
import numpy.typing as npt
from scipy.interpolate import interp1d


# Minimal in-file Adam optimizer to replace external `flowMC` optimizer.
# This follows the API used in this repo: `.optimize(key, loss_fn, initial_position)`
class optimization_Adam:
    """FlowMC-like population Adam optimizer wrapper using optax.

    Implements a minimal `.optimize(key, loss_fn, initial_position)` API compatible
    with the rest of the codebase while using the same optax chain as flowMC's
    `Optimizer` (clip_by_global_norm + adamw).
    """

    def __init__(self, n_steps: int = 1000, learning_rate: float = 1e-3, noise_level: float = 0.0, momentum: float = 0.9, clip_norm: float = 1.0):
        self.n_steps = int(n_steps)
        self.learning_rate = float(learning_rate)
        self.noise_level = float(noise_level)
        self.momentum = float(momentum)
        self.clip_norm = float(clip_norm)
        # Build the same chain as flowMC's Optimizer
        self._optim = optax.chain(
            optax.clip_by_global_norm(self.clip_norm),
            optax.adamw(learning_rate=self.learning_rate, b1=self.momentum),
        )

    def optimize(self, key, loss_fn, initial_position):
        """Optimize a population of parameter vectors.

        Args:
            key: JAX PRNGKey
            loss_fn: callable(params_vector) -> scalar loss (to minimize)
            initial_position: array shape (popsize, n_dims)

        Returns:
            (key, optimized_positions, summary)
        """
        popsize = int(initial_position.shape[0])
        params = initial_position.copy()

        # init per-particle opt state
        opt_states = [self._optim.init(params[i]) for i in range(popsize)]

        for step in range(self.n_steps):
            losses, grads = jax.vmap(jax.value_and_grad(loss_fn))(params)

            # apply updates per particle
            for i in range(popsize):
                updates, opt_states[i] = self._optim.update(grads[i], opt_states[i], params[i])
                params = params.at[i].set(optax.apply_updates(params[i], updates))

            if self.noise_level > 0.0:
                key, subk = jax.random.split(key)
                params = params + self.noise_level * jax.random.normal(subk, params.shape)

        final_losses = jax.vmap(loss_fn)(params)
        summary = {"final_log_prob": final_losses}
        return key, params, summary


label = 'Results/Test_Heterodyned'

# Define the parameters class
class ParameterPrior:
    def __init__(self, name: str, label: str, prior_fn: callable, *args):
        self.name = name
        self.label = label
        self.prior_fn = prior_fn
        self.args = args

    def logprob(self, value: float) -> float:
        return self.prior_fn(value, *self.args)

# Define the prior functions
@jax.jit
def UniformPrior(x: float, min: float, max: float) -> float:    
    return stats.uniform.logpdf(x, min, max-min)

@jax.jit
def SinPrior(x):
    return jnp.where((x < 0.0) | (x > jnp.pi), -jnp.inf, jnp.log(jnp.sin(x) / 2.0))

@jax.jit
def CosPrior(x):
    return jnp.where((x < -jnp.pi / 2.0) | (x > jnp.pi / 2.0), -jnp.inf, jnp.log(jnp.cos(x) / 2.0))

@jax.jit
def BetaPrior(x, min, max):
    return stats.beta.logpdf(x, 3.0, 1.0, min, max-min)

@jax.jit
def FlatInLogPrior(x: float, min: float, max: float) -> float:
    return jnp.where((x < min) | (x > max), -jnp.inf, (-jnp.log(jnp.log(max / min)) - jnp.log(x)))

# Define LIGO event data, detectors, and waveform model
gps = 1187008882.43 # GW170817 event time
fmin = 23.0
fmax = 2048.0
duration = 128
post_trigger_duration = 2
end_time = gps + post_trigger_duration
start_time = end_time - duration
roll_off = 0.4
tukey_alpha = 2 * roll_off / duration
psd_pad = 16
psd_duration = 1024

detectors = [H1, L1, V1]

for det in detectors:
    det.load_data(
        gps, 
        duration - post_trigger_duration,
        post_trigger_duration,
        fmin,
        fmax,
        psd_pad=psd_pad,
        psd_duration=psd_duration,
        tukey_alpha=tukey_alpha,
        gwpy_kwargs={"cache": True, "version": 2}
        )

waveform = RippleIMRPhenomD_NRTidalv2(
    f_ref=fmin,
    use_lambda_tildes=False,
    no_taper=False
    )

frequencies = H1.frequencies
epoch = duration - post_trigger_duration
gmst = Time(gps, format="gps").sidereal_time("apparent", "greenwich").rad

# Define the priors
# GW170817 defined as per https://arxiv.org/pdf/1805.11579
parameters = [
    ParameterPrior("M_c", r"$M_c$", UniformPrior, 1.184, 2.168),
    ParameterPrior("q", r"$q$", UniformPrior, 0.125, 1.00),  
    ParameterPrior("s1_z", r"$s_{1z}$", UniformPrior, -0.05, 0.05),
    ParameterPrior("s2_z", r"$s_{2z}$", UniformPrior, -0.05, 0.05),
    ParameterPrior("iota", r"$\iota$", SinPrior),
    ParameterPrior("d_L", r"$d_L$", BetaPrior, 10.0, 75.0),
    ParameterPrior("t_c", r"$t_c$", UniformPrior, -0.1, 0.1),
    ParameterPrior("phase_c", r"$\phi_c$", UniformPrior, 0.0, 2 * jnp.pi),
    ParameterPrior("psi", r"$\psi$", UniformPrior, 0.0, jnp.pi),
    ParameterPrior("ra", r"$\alpha$", UniformPrior, 3.44, 3.45),
    ParameterPrior("dec", r"$\delta$", UniformPrior, -0.41, -0.40),
    ParameterPrior("lambda_1", r"$\Lambda_1$", UniformPrior, 0.0, 5000.0),
    ParameterPrior("lambda_2", r"$\Lambda_2$", UniformPrior, 0.0, 5000.0),
    ParameterPrior("H_0", r"$H_0$", FlatInLogPrior, 20.0, 140.0),
    ParameterPrior("v_p", r"$v_p$", UniformPrior, -1000.0, 1000.0)
]

parameter_names = [param.name for param in parameters]
labels = [param.label for param in parameters]

# Define the log prior function
@jax.jit
def logprior_fn(params_array):
    # Convert array to dictionary
    params_dict = dict(zip(parameter_names, params_array))
    return jnp.sum(jnp.array([param.logprob(params_dict[param.name]) for param in parameters]))

# Heterodyning implementation
def max_phase_diff(
    f: npt.NDArray[np.floating],
    f_low: float,
    f_high: float,
    chi: Float = 1.0,
    ):

    gamma = np.arange(-5, 6, 1) / 3.0
    f = np.repeat(f[:, None], len(gamma), axis=1)
    f_star = np.repeat(f_low, len(gamma))
    f_star[gamma >= 0] = f_high
    return 2 * np.pi * chi * np.sum((f / f_star) ** gamma * np.sign(gamma), axis=1)

def compute_coefficients(data, h_ref, psd, freqs, f_bins, f_bins_center):
    A0_array = []
    A1_array = []
    B0_array = []
    B1_array = []

    df = freqs[1] - freqs[0]
    data_prod = np.array(data * h_ref.conj())
    self_prod = np.array(h_ref * h_ref.conj())
    for i in range(len(f_bins) - 1):
        f_index = np.where((freqs >= f_bins[i]) & (freqs < f_bins[i + 1]))[0]
        A0_array.append(4 * np.sum(data_prod[f_index] / psd[f_index]) * df)
        A1_array.append(
            4
            * np.sum(
                data_prod[f_index]
                / psd[f_index]
                * (freqs[f_index] - f_bins_center[i])
            )
            * df
        )
        B0_array.append(4 * np.sum(self_prod[f_index] / psd[f_index]) * df)
        B1_array.append(
            4
            * np.sum(
                self_prod[f_index]
                / psd[f_index]
                * (freqs[f_index] - f_bins_center[i])
            )
            * df
        )

    A0_array = jnp.array(A0_array)
    A1_array = jnp.array(A1_array)
    B0_array = jnp.array(B0_array)
    B1_array = jnp.array(B1_array)
    return A0_array, A1_array, B0_array, B1_array

def original_likelihood(
    params: dict[str, Float],
    h_sky: dict[str, Float[Array, " n_dim"]],
    detectors: list[Detector],
    freqs: Float[Array, " n_dim"],
    align_time: Float,
    **kwargs,
) -> Float:
    log_likelihood = 0.0
    df = freqs[1] - freqs[0]
    for detector in detectors:
        h_dec = detector.fd_response(freqs, h_sky, params) * align_time
        match_filter_SNR = (
            4 * jnp.sum((jnp.conj(h_dec) * detector.data) / detector.psd * df).real
        )
        optimal_SNR = 4 * jnp.sum(jnp.conj(h_dec) * h_dec / detector.psd * df).real
        log_likelihood += match_filter_SNR - optimal_SNR / 2

    return log_likelihood

class HeterodynedLikelihood():
    def __init__(self, detectors: list[Detector], waveform, frequencies, epoch, gmst):
        self.detectors = detectors
        self.waveform = waveform
        self.frequencies = frequencies
        self.epoch = epoch
        self.gmst = gmst
        self.n_bins = 100
        self.A0_array = {}
        self.A1_array = {}
        self.B0_array = {}
        self.B1_array = {}
        self.waveform_low_ref = {}
        self.waveform_center_ref = {}

    def make_binning_scheme(
        self, freqs: npt.NDArray[np.floating], n_bins: int, chi: float = 1
    ) -> tuple[Float[Array, " n_bins+1"], Float[Array, " n_bins"]]:

        phase_diff_array = max_phase_diff(freqs, freqs[0], freqs[-1], chi=chi)
        bin_f = interp1d(phase_diff_array, freqs)
        f_bins = np.array([])
        for i in np.linspace(phase_diff_array[0], phase_diff_array[-1], n_bins + 1):
            f_bins = np.append(f_bins, bin_f(i))
        f_bins_center = (f_bins[:-1] + f_bins[1:]) / 2
        return jnp.array(f_bins), jnp.array(f_bins_center)

    def maximize_likelihood(
        self,
        popsize: int = 100,
        n_steps: int = 500,
        ):
        # Optimize only parameters that matter for the waveform reference state
        opt_parameters = [p for p in parameters if p.name not in ("H_0", "v_p")]
        opt_param_names = [p.name for p in opt_parameters]

        def y_opt(x):
            named_params = dict(zip(opt_param_names, x))
            return -self.evaluate_original(named_params)

        print("Starting the optimizer (excluding H_0 and v_p)")

        optimizer = optimization_Adam(n_steps=n_steps, learning_rate=0.001, noise_level=1)

        initial_position = jnp.zeros((popsize, len(opt_param_names))) + jnp.nan
        while not jax.tree.reduce(
            jnp.logical_and, jax.tree.map(lambda x: jnp.isfinite(x), initial_position)
        ).all():
            non_finite_index = jnp.where(
                jnp.any(
                    ~jax.tree.reduce(
                        jnp.logical_and,
                        jax.tree.map(lambda x: jnp.isfinite(x), initial_position),
                    ),
                    axis=1,
                )
            )[0]

            init_key = jax.random.PRNGKey(0)
            init_key, subkey = jax.random.split(init_key, 2)
            # Sample from prior for the optimization parameters only
            prior_keys = jax.random.split(subkey, len(opt_parameters))
            guess_dict = {}
            for param, key in zip(opt_parameters, prior_keys):
                guess_dict[param.name] = sample_prior(param, key, popsize)

            # Convert to array format for only the optimized parameters
            guess = jnp.array(jax.tree.leaves({k: guess_dict[k] for k in opt_param_names})).T

            finite_guess = jnp.where(
                jnp.all(jax.tree.map(lambda x: jnp.isfinite(x), guess), axis=1)
            )[0]
            common_length = min(len(finite_guess), len(non_finite_index))
            initial_position = initial_position.at[
                non_finite_index[:common_length]
            ].set(guess[:common_length])

        rng_key, optimized_positions, summary = optimizer.optimize(
            jax.random.PRNGKey(12094), y_opt, initial_position
        )

        best_fit = optimized_positions[jnp.argmin(summary["final_log_prob"])]

        # Return only the optimized parameters (do NOT include H_0 or v_p)
        named_params = dict(zip(opt_param_names, best_fit))
        # Ensure derived 'eta' exists for waveform evaluation
        try:
            qval = float(named_params.get("q", 1.0))
            named_params["eta"] = qval / ((1.0 + qval) ** 2)
        except Exception:
            named_params["eta"] = 0.249

        return named_params

    def evaluate_original(
        self, params: dict[str, Float]
    ) -> (
        Float
    ):
        log_likelihood = 0
        frequencies = self.frequencies
        params["gmst"] = self.gmst
        params["eta"] = params["q"] / ((1 + params["q"]) ** 2)
        # evaluate the waveform as usual
        waveform_sky = self.waveform(frequencies, params)
        align_time = jnp.exp(
            -1j * 2 * jnp.pi * frequencies * (self.epoch + params["t_c"])
        )
        log_likelihood = original_likelihood(
            params,
            waveform_sky,
            self.detectors,
            frequencies,
            align_time
        )
        
        return log_likelihood
        # guard final losses
        final_losses = jnp.where(jnp.isfinite(final_losses), final_losses, 1e20)
        best_idx = int(jnp.argmin(final_losses))
        best_fit = params[best_idx]
        
        named_params = dict(zip(parameter_names, best_fit))
        # Add derived parameter 'eta' required by waveform code
        try:
            qval = float(named_params.get("q"))
            named_params["eta"] = qval / ((1.0 + qval) ** 2)
        except Exception:
            # fallback: set eta to a default small value
            named_params["eta"] = 0.249
        
        return named_params

    def reference_state(self):
        popsize = 100
        n_steps = 2000
        params = self.maximize_likelihood(
            popsize=popsize,
            n_steps=n_steps,
        )
        params = {key: float(value) for key, value in params.items()}           
        print(f'Optimized reference parameters: {params}')
        params["gmst"] = self.gmst
        if "eta" in params:
            if jnp.isclose(params["eta"], 0.25):
                params["eta"] = 0.249995

        h_sky = waveform(self.frequencies, params)
        # Get the grid of the relative binning scheme (contains the final endpoint)
        # and the center points
        freq_grid, self.freq_grid_center = self.make_binning_scheme(
            np.array(self.frequencies), self.n_bins
            )
        self.freq_grid_low = freq_grid[:-1]
        # Get frequency masks to be applied, for both original
        # and heterodyne frequency grid
        h_amp = jnp.sum(
            jnp.array([jnp.abs(h_sky[key]) for key in h_sky.keys()]), axis=0
        )
        f_valid = self.frequencies[jnp.where(h_amp > 0)[0]]
        f_max = jnp.max(f_valid)
        f_min = jnp.min(f_valid)

        mask_heterodyne_grid = jnp.where((freq_grid <= f_max) & (freq_grid >= f_min))[0]
        mask_heterodyne_low = jnp.where(
            (self.freq_grid_low <= f_max) & (self.freq_grid_low >= f_min)
        )[0]
        mask_heterodyne_center = jnp.where(
            (self.freq_grid_center <= f_max) & (self.freq_grid_center >= f_min)
        )[0]
        freq_grid = freq_grid[mask_heterodyne_grid]
        self.freq_grid_low = self.freq_grid_low[mask_heterodyne_low]
        self.freq_grid_center = self.freq_grid_center[mask_heterodyne_center]

        # Assure frequency grids have same length
        if len(self.freq_grid_low) > len(self.freq_grid_center):
            self.freq_grid_low = self.freq_grid_low[: len(self.freq_grid_center)]

        h_sky_low = self.waveform(self.freq_grid_low, params)
        h_sky_center = self.waveform(self.freq_grid_center, params)
        # Get phase shifts to align time of coalescence
        align_time = jnp.exp(
            -1j
            * 2
            * jnp.pi
            * self.frequencies
            * (self.epoch + params["t_c"])
        )
        align_time_low = jnp.exp(
            -1j
            * 2
            * jnp.pi
            * self.freq_grid_low
            * (self.epoch + params["t_c"])
        )
        align_time_center = jnp.exp(
            -1j
            * 2
            * jnp.pi
            * self.freq_grid_center
            * (self.epoch + params["t_c"])
        )

        for detector in self.detectors:
            waveform_ref = (
                detector.fd_response(self.frequencies, h_sky, params)
                * align_time
            )
            self.waveform_low_ref[detector.name] = (
                detector.fd_response(self.freq_grid_low, h_sky_low, params)
                * align_time_low
            )
            self.waveform_center_ref[detector.name] = (
                detector.fd_response(
                    self.freq_grid_center, h_sky_center, params
                )
                * align_time_center
            )
            A0, A1, B0, B1 = compute_coefficients(
                detector.data,
                waveform_ref,
                detector.psd,
                self.frequencies,
                freq_grid,
                self.freq_grid_center,
            )
            self.A0_array[detector.name] = A0[mask_heterodyne_center]
            self.A1_array[detector.name] = A1[mask_heterodyne_center]
            self.B0_array[detector.name] = B0[mask_heterodyne_center]
            self.B1_array[detector.name] = B1[mask_heterodyne_center]

    def evaluate(self, params: dict[str, Float]) -> Float:
        frequencies_low = self.freq_grid_low
        frequencies_center = self.freq_grid_center
        params["gmst"] = self.gmst
        params["eta"] = params["q"] / ((1 + params["q"]) ** 2)
        # evaluate the waveforms as usual
        waveform_sky_low = self.waveform(frequencies_low, params)
        waveform_sky_center = self.waveform(frequencies_center, params)
        align_time_low = jnp.exp(
            -1j * 2 * jnp.pi * frequencies_low * (self.epoch + params["t_c"])
        )
        align_time_center = jnp.exp(
            -1j * 2 * jnp.pi * frequencies_center * (self.epoch + params["t_c"])
        )
        return relative_binning_likelihood_function(
            params,
            self.A0_array,
            self.A1_array,
            self.B0_array,
            self.B1_array,
            waveform_sky_low,
            waveform_sky_center,
            self.waveform_low_ref,
            self.waveform_center_ref,
            self.detectors,
            frequencies_low,
            frequencies_center,
            align_time_low,
            align_time_center
        )

# | Define the likelihood function
likelihood_function = HeterodynedLikelihood(
    detectors,
    waveform,
    frequencies,
    epoch,
    gmst)

@jax.jit
def loglikelihood_fn(params_array):
    # Convert array to dictionary
    params = dict(zip(parameter_names, params_array))
    params["eta"] = params["q"] / (1 + params["q"]) ** 2

    # Defined as in Abbott et al. 2017 (https://arxiv.org/pdf/1710.05832.pdf)
    ll_vr = stats.norm.logpdf(3327, params["v_p"] + params["H_0"] * params["d_L"], 72)
    ll_vp = stats.norm.logpdf(310, params["v_p"], 150)

    return likelihood_function.evaluate(params) + ll_vr + ll_vp

# Define the Nested Sampling algorithm parameters
num_dims = len(parameter_names)
num_live = 5000
num_delete = int(num_live * 0.5)
num_mcmc_steps = int(num_dims * 5)

# Initialize the Nested Sampling algorithm
nested_sampler = blackjax.nss(
    logprior_fn=logprior_fn,
    loglikelihood_fn=loglikelihood_fn,
    num_delete=num_delete,
    num_inner_steps=num_mcmc_steps,
)

@jax.jit
def one_step(carry, xs):
    state, k = carry
    k, subk = jax.random.split(k, 2)
    state, dead_point = nested_sampler.step(subk, state)
    return (state, k), dead_point

# | Sample live points from the prior
def sample_prior(parameter, key, n_live):
    if parameter.prior_fn == UniformPrior:
        return jax.random.uniform(key, (n_live,), minval=parameter.args[0], maxval=parameter.args[1])
    elif parameter.prior_fn == SinPrior:
        return 2 * jnp.arcsin(jax.random.uniform(key, (n_live,)) ** 0.5)
    elif parameter.prior_fn == CosPrior:
        return 2 * jnp.arcsin(jax.random.uniform(key, (n_live,)) ** 0.5) - jnp.pi / 2.0
    elif parameter.prior_fn == BetaPrior:
        return jax.random.beta(key, 3.0, 1.0, (n_live,)) * (parameter.args[1] - parameter.args[0]) + parameter.args[0]
    elif parameter.prior_fn == FlatInLogPrior:
        return parameter.args[0] * (parameter.args[1] / parameter.args[0]) ** jax.random.uniform(key, (n_live,))

rng_key = jax.random.PRNGKey(0)
rng_key, init_key = jax.random.split(rng_key, 2)
init_keys = jax.random.split(init_key, len(parameters))
initial_particles = jnp.vstack([sample_prior(param, key, num_live) for param, key in zip(parameters, init_keys)]).T
likelihood_function.reference_state()

state = nested_sampler.init(initial_particles)

# Run nested sampling
print("Running nested sampling...")
ns_start = time.time()
dead = []

with tqdm.tqdm(desc="Dead points", unit=" dead points") as pbar:
    while (not state.logZ_live - state.logZ < -3):
        (state, rng_key), dead_info = one_step((state, rng_key), None)
        dead.append(dead_info)
        pbar.update(num_delete)

dead = blackjax.ns.utils.finalise(state, dead)
ns_time = time.time() - ns_start

# Post processing
data = jnp.vstack([dead.particles[name] for name in parameter_names]).T
samples = NestedSamples(
    data,
    logL=dead.loglikelihood,
    logL_birth=dead.loglikelihood_birth,
    columns=parameter_names,
    labels=labels,
    logzero=jnp.nan,
)

print(f"Sampler runtime: {ns_time:.2f} seconds")
print(f"Log Evidence: {samples.logZ():.2f} ± {samples.logZ(100).std():.2f}")

samples.to_csv(f'{label}.csv')
print(f"Samples saved to {label}.csv")