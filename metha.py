# Converted from `metha_latest_version.ipynb`
# Minimal script version — execution block placed under `main()`.

# Memory configuration should be consistent and optimized
import os
os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"] = "0.8"  # More conservative than 1.0
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"  # Enable for better memory management

import jax
import jax.numpy as jnp
import numpy as np
import blackjax
import matplotlib.pyplot as plt
from astropy.time import Time
import tqdm

# Enable 64-bit precision early
jax.config.update("jax_enable_x64", True)

# Import detector and likelihood functions
from jimgw.single_event.detector import H1, L1, V1
from jimgw.single_event.likelihood import original_likelihood as likelihood_function
from jimgw.single_event.likelihood import phase_marginalized_likelihood as likelihood_function_phase_marginalized
from jimgw.single_event.waveform import RippleIMRPhenomD

# Initialize waveform once
waveform = RippleIMRPhenomD(f_ref=50)

# Constants for noise curves
ASD_PATHS = {
    "H1": "/mnt/data/myp23/env/lib/python3.10/site-packages/bilby/gw/detector/noise_curves/aLIGO_O4_high_asd.txt",
    "L1": "/mnt/data/myp23/env/lib/python3.10/site-packages/bilby/gw/detector/noise_curves/aLIGO_O4_high_asd.txt", 
    "V1": "/mnt/data/myp23/env/lib/python3.10/site-packages/bilby/gw/detector/noise_curves/AdV_asd.txt",
}

# Pre-compute injection parameters as JAX arrays
INJECTION_PARAMS = {
    "M_c": jnp.array(28.588),  # Pre-computed chirp mass
    "q": jnp.array(0.806),     # Pre-computed mass ratio
    "s1_z": jnp.array(0.4),
    "s2_z": jnp.array(-0.3),   # Negative due to tilt_2=π
    "d_L": jnp.array(2000.0),
    "iota": jnp.array(0.4),
    "t_c": jnp.array(0.0),
    "phase_c": jnp.array(1.3),
    "ra": jnp.array(1.375),
    "dec": jnp.array(-1.2108),
    "psi": jnp.array(2.659),
    #"gmst": jnp.array(1.7539),  # Pre-computed GMST
    "eta": jnp.array(0.246),    # Pre-computed symmetric mass ratio
}

# Load detector data efficiently as JAX arrays
DETECTOR_DATA = {
    'frequencies': jnp.array(np.load('debug_frequency_array.npy')),
    'H1': jnp.array(np.load('debug_H1_data.npy')),
    'L1': jnp.array(np.load('debug_L1_data.npy')),
    'V1': jnp.array(np.load('debug_V1_data.npy'))
}

print(f"Loaded detector data as JAX arrays: {type(DETECTOR_DATA['frequencies'])}")

# Configure detector frequency range efficiently
FREQ_RANGE = {'min': 20.0, 'max': 2048.0}

# Vectorized frequency mask calculation
freq_mask = (DETECTOR_DATA['frequencies'] >= FREQ_RANGE['min']) & (DETECTOR_DATA['frequencies'] <= FREQ_RANGE['max'])
filtered_frequencies = DETECTOR_DATA['frequencies'][freq_mask]

# Configure detectors using vectorized operations
detectors = [H1, L1, V1]
detector_names = ['H1', 'L1', 'V1']

# Vectorized detector configuration
for det, name in zip(detectors, detector_names):
    det.frequencies = filtered_frequencies  
    det.data = DETECTOR_DATA[name][freq_mask]

print(f"Configured {len(detectors)} detectors with {len(filtered_frequencies)} frequency points")

# Verify JAX arrays are preserved
print(f"H1.frequencies type: {type(H1.frequencies)}")
print(f"H1.data type: {type(H1.data)}")

# Pre-load and vectorize PSD data for all detectors
def load_psd_data(asd_paths):
    """Load ASD data for all detectors and convert to PSD."""
    psd_data = {}
    for name, path in asd_paths.items():
        f_np, asd_vals_np = np.loadtxt(path, unpack=True)
        psd_data[name] = {
            'frequencies': jnp.array(f_np),
            'psd': jnp.array(asd_vals_np**2)  # Convert ASD to PSD
        }
    return psd_data

# Load all PSD data once
PSD_DATA = load_psd_data(ASD_PATHS)

# Vectorized PSD interpolation for all detectors
@jax.jit
def interpolate_psd(det_frequencies, psd_frequencies, psd_values):
    """JAX-compiled PSD interpolation."""
    return jnp.interp(det_frequencies, psd_frequencies, psd_values)

# Configure detector PSDs using vectorized operations
for det in detectors:
    det.psd = interpolate_psd(
        det.frequencies,
        PSD_DATA[det.name]['frequencies'],
        PSD_DATA[det.name]['psd']
    )

# Verify PSD arrays are JAX arrays
print(f"H1.psd type: {type(H1.psd)}")
print(f"PSD shape: {H1.psd.shape}")

# Define which parameters to sample over - ALL EXCEPT phase_c for phase marginalization
SAMPLE_KEYS = ["M_c", "q", "s1_z", "s2_z", "iota", "d_L", "t_c", "psi", "ra", "dec"]  # Exclude phase_c

# All possible parameters and their properties
ALL_PARAM_CONFIG = {
    "M_c": {"min": 20.0, "max": 40.0, "prior": "uniform", "wraparound": False, "angle": 1.0},
    "q": {"min": 0.25, "max": 1.0, "prior": "uniform", "wraparound": False, "angle": 1.0},
    "s1_z": {"min": -1.0, "max": 1.0, "prior": "uniform", "wraparound": False, "angle": 1.0},
    "s2_z": {"min": -1.0, "max": 1.0, "prior": "uniform", "wraparound": False, "angle": 1.0},
    "iota": {"min": 0.0, "max": jnp.pi, "prior": "sine", "wraparound": False, "angle": 1.0},
    "d_L": {"min": 100.0, "max": 5000.0, "prior": "beta", "wraparound": False, "angle": 1.0},
    "t_c": {"min": -0.1, "max": 0.1, "prior": "uniform", "wraparound": False, "angle": 1.0},
    "phase_c": {"min": 0.0, "max": 2*jnp.pi, "prior": "uniform", "wraparound": True, "angle": 2*jnp.pi},
    "psi": {"min": 0.0, "max": jnp.pi, "prior": "uniform", "wraparound": True, "angle": jnp.pi},
    "ra": {"min": 0.0, "max": 2*jnp.pi, "prior": "uniform", "wraparound": True, "angle": 2*jnp.pi},
    "dec": {"min": -jnp.pi/2, "max": jnp.pi/2, "prior": "cosine", "wraparound": False, "angle": 1.0},
}

# Extract configuration for sampled parameters only
SAMPLED_CONFIG = {key: ALL_PARAM_CONFIG[key] for key in SAMPLE_KEYS}
n_dims = len(SAMPLE_KEYS)

# Pre-compute vectorized arrays for GPU efficiency
PARAM_MINS = jnp.array([SAMPLED_CONFIG[key]["min"] for key in SAMPLE_KEYS])
PARAM_MAXS = jnp.array([SAMPLED_CONFIG[key]["max"] for key in SAMPLE_KEYS])
PARAM_PRIOR_TYPES = jnp.array([
    0 if SAMPLED_CONFIG[key]["prior"] == "uniform" else
    1 if SAMPLED_CONFIG[key]["prior"] == "sine" else
    2 if SAMPLED_CONFIG[key]["prior"] == "cosine" else
    3 for key in SAMPLE_KEYS  # beta
])

# CRITICAL Fix: Use SAMPLE_KEYS order consistently
wraparound = jnp.array([SAMPLED_CONFIG[key]["wraparound"] for key in SAMPLE_KEYS])
wraparound_angle = jnp.array([SAMPLED_CONFIG[key]["angle"] for key in SAMPLE_KEYS])

print(f"Sampling over {n_dims} parameters: {SAMPLE_KEYS}")
print(f"Wraparound parameters: {[key for key in SAMPLE_KEYS if SAMPLED_CONFIG[key]['wraparound']]}")
print(f"Wraparound array: {wraparound}")
print(f"Wraparound angles: {wraparound_angle}")
print("Using PHASE MARGINALIZED LIKELIHOOD - phase_c excluded from sampling")

# Set up constants for likelihood computation
post_trigger_duration = 2
duration = 8
epoch = duration - post_trigger_duration
gmst = Time(1126259642.413, format="gps").sidereal_time("apparent", "greenwich").rad
frequencies = H1.frequencies

# Column labels for plotting
column_to_label = {
    "M_c": r"$M_c$",
    "q": r"$q$",
    "d_L": r"$d_L$",
    "iota": r"$\\iota$",
    "ra": r"$\\alpha$",
    "dec": r"$\\delta$",
    "s1_z": r"$s_{1z}$",
    "s2_z": r"$s_{2z}$",
    "t_c": r"$t_c$",
    "psi": r"$\\psi$",
    "phase_c": r"$\\phi_c$",
}

# Vectorized prior functions
@jax.jit
def vectorized_uniform_logprob(x, a, b):
    return jnp.where((x >= a) & (x <= b), -jnp.log(b - a), -jnp.inf)

@jax.jit
def vectorized_sine_logprob(x):
    return jnp.where((x >= 0.0) & (x <= jnp.pi), jnp.log(jnp.sin(x) / 2.0), -jnp.inf)

@jax.jit
def vectorized_cosine_logprob(x):
    return jnp.where(jnp.abs(x) < jnp.pi / 2, jnp.log(jnp.cos(x) / 2.0), -jnp.inf)

@jax.jit
def vectorized_beta_logprob(x, a, b):
    u = (x - a) / (b - a)
    logpdf = (2.0 * jnp.log(u) + 0.0 * jnp.log(1 - u) - jax.scipy.special.betaln(3.0, 1.0) - jnp.log(b - a))
    return jnp.where((x >= a) & (x <= b), logpdf, -jnp.inf)

@jax.jit
def loglikelihood_fn(params):
    """Phase marginalized likelihood function - sets phase_c=0."""
    # Start with injection parameters and update with sampled parameters
    p = INJECTION_PARAMS.copy()
    p.update(params)  # JAX-compatible dictionary update

    # CRITICAL: Set phase_c = 0 for phase marginalized likelihood
    p["phase_c"] = 0.0

    # Use dynamically calculated gmst instead of hardcoded value
    p["gmst"] = gmst

    # Always calculate this
    p["eta"] = p["q"] / (1 + p["q"]) ** 2

    waveform_sky = waveform(filtered_frequencies, p)
    align_time = jnp.exp(-1j * 2 * jnp.pi * filtered_frequencies * (epoch + p["t_c"]))

    # Use phase marginalized likelihood function
    return likelihood_function_phase_marginalized(p, waveform_sky, detectors, filtered_frequencies, align_time)

@jax.jit
def logprior_fn(params):
    """Fully vectorized prior function - no loops."""
    # Extract parameter values in consistent order
    param_values = jnp.array([params[key] for key in SAMPLE_KEYS])

    # Compute all prior types vectorially
    uniform_priors = vectorized_uniform_logprob(param_values, PARAM_MINS, PARAM_MAXS)
    sine_priors = vectorized_sine_logprob(param_values)
    cosine_priors = vectorized_cosine_logprob(param_values)
    beta_priors = vectorized_beta_logprob(param_values, PARAM_MINS, PARAM_MAXS)

    # Select appropriate prior for each parameter using vectorized operations
    priors = jnp.where(
        PARAM_PRIOR_TYPES == 0, uniform_priors,
        jnp.where(
            PARAM_PRIOR_TYPES == 1, sine_priors,
            jnp.where(
                PARAM_PRIOR_TYPES == 2, cosine_priors,
                beta_priors
            )
        )
    )

    return jnp.sum(priors)

# Nested sampling configuration
n_live = 1000
n_delete = int(n_live * 0.5)
num_mcmc_steps = n_dims * 5

# Sample live points only for parameters we're fitting
rng_key = jax.random.PRNGKey(0)
rng_key, init_key = jax.random.split(rng_key, 2)
init_keys = jax.random.split(init_key, len(SAMPLE_KEYS))

particles = {}
for i, key in enumerate(SAMPLE_KEYS):
    config = SAMPLED_CONFIG[key]

    if config["prior"] == "uniform":
        particles[key] = jax.random.uniform(
            init_keys[i], (n_live,), minval=config["min"], maxval=config["max"]
        )
    elif config["prior"] == "sine":
        particles[key] = jnp.arccos(1 - 2 * jax.random.uniform(init_keys[i], (n_live,)))
    elif config["prior"] == "cosine":
        particles[key] = jnp.arcsin(2 * jax.random.uniform(init_keys[i], (n_live,)) - 1)
    elif config["prior"] == "beta":
        particles[key] = (jax.random.beta(init_keys[i], 3.0, 1.0, shape=(n_live,)) * 
                         (config["max"] - config["min"]) + config["min"])

print(f"Initialized {n_live} particles for parameters: {list(particles.keys())}")

# Create unravel function once - fixes recompilation issue
example_particle = jax.tree_util.tree_map(lambda x: x[0], particles)
_, unravel_fn = jax.flatten_util.ravel_pytree(example_particle)
print("Created unravel function once (prevents recompilation)")

# Determine ravel order and matching wraparound arrays
def get_ravel_order(particles_dict):
    """Determine the order that ravel_pytree uses for flattening."""
    example = jax.tree_util.tree_map(lambda x: x[0], particles_dict)
    flat, _ = jax.flatten_util.ravel_pytree(example)

    # Create a test dict with unique values to identify the order
    test_dict = {key: float(i) for i, key in enumerate(particles_dict.keys())}
    test_flat, _ = jax.flatten_util.ravel_pytree(test_dict)

    # The order is determined by the positions in the flattened array
    order = []
    for val in test_flat:
        for key, test_val in test_dict.items():
            if abs(val - test_val) < 1e-10:
                order.append(key)
                break
    return order

ravel_order = get_ravel_order(particles)
print(f"Ravel order: {ravel_order}")

# Create wraparound arrays in the SAME order as ravel_pytree uses
wraparound_ravel_order = jnp.array([SAMPLED_CONFIG[key]["wraparound"] for key in ravel_order])
wraparound_angle_ravel_order = jnp.array([SAMPLED_CONFIG[key]["angle"] for key in ravel_order])

print(f"Wraparound array (ravel order): {wraparound_ravel_order}")
print(f"Wraparound angles (ravel order): {wraparound_angle_ravel_order}")

# Generic stepper factory
def make_generic_stepper(wraparound_config):
    """Factory that creates a generic stepper function."""

    @jax.jit
    def stepper_fn(x, d, t):
        # 1. Perform the standard linear step for all parameters
        y_proposed = jax.tree_util.tree_map(lambda val, direction: val + t * direction, x, d)

        # 2. Define the logic to apply wrapping conditionally
        def wrap_leaf(path, leaf_val):
            # For a dict, path will be a tuple like (KeyPath(key='psi'),)
            key = path[0].key 
            if key in wraparound_config:
                return jnp.mod(leaf_val, wraparound_config[key])
            else:
                return leaf_val

        # 3. Apply the wrapping logic to the proposed tree
        y_wrapped = jax.tree_util.tree_map_with_path(wrap_leaf, y_proposed)

        return y_wrapped

    return stepper_fn

# Create wraparound configuration from SAMPLED_CONFIG
wraparound_config = {
    key: SAMPLED_CONFIG[key]["angle"] 
    for key in SAMPLE_KEYS 
    if SAMPLED_CONFIG[key]["wraparound"]
}
print(f"Wraparound config: {wraparound_config}")

# Create the generic stepper once
generic_stepper = make_generic_stepper(wraparound_config)

# Factory function for covariance calculation
def make_calc_covmat_jax(unravel_fn, wraparound, wraparound_angle):
    """Factory function that creates the adaptation function with fixed unravel_fn."""

    @jax.jit
    def calc_covmat_jax_inner(state, info, inner_kernel_params):
        """Fast covariance calculation using ravel_pytree (efficient and standard)."""
        x = jax.vmap(lambda p: jax.flatten_util.ravel_pytree(p)[0])(state.particles)
        x = x / wraparound_angle  # Scale by angles - now in correct ravel order

        x = x.T
        nDims, n = x.shape

        # Circular statistics only for wraparound parameters
        sinpart = jnp.sum(jnp.sin(x * 2*jnp.pi), axis=1)
        cospart = jnp.sum(jnp.cos(x * 2*jnp.pi), axis=1)
        circle_mu_angular_part = jnp.atan2(sinpart, cospart) / (2*jnp.pi)

        circle_mu = jnp.where(wraparound, circle_mu_angular_part, 0.0)
        circle_diff = x - circle_mu[:, jnp.newaxis]
        circle_diff = circle_diff - jnp.round(circle_diff)

        circle_mu_refined = jnp.mod(jnp.sum(circle_diff, axis=1) / n + circle_mu, 1.0)
        normal_diff = x - jnp.sum(x, axis=1)[:, jnp.newaxis] / n
        circle_diff_refined = x - circle_mu_refined[:, jnp.newaxis]
        wraparound_broadcast = wraparound[:, jnp.newaxis]
        dx = jnp.where(wraparound_broadcast, circle_diff_refined - jnp.round(circle_diff_refined), normal_diff)
        dx = dx * wraparound_angle[:, jnp.newaxis]

        cov_matrix = (dx @ dx.T) / (n - 1.0)

        cov_pytree = jax.vmap(unravel_fn)(cov_matrix)
        return {"cov": cov_pytree}

    return calc_covmat_jax_inner

# Create the adaptation function with ravel-order wraparound arrays
my_calc_covmat_fn = make_calc_covmat_jax(unravel_fn, wraparound_ravel_order, wraparound_angle_ravel_order)

# Initialize the Nested Sampling algorithm
nested_sampler = blackjax.nss(
    logprior_fn=logprior_fn,
    loglikelihood_fn=loglikelihood_fn,
    num_delete=n_delete,
    num_inner_steps=num_mcmc_steps,
    stepper_fn=generic_stepper,  # Use the generic stepper
    adapt_direction_params_fn=my_calc_covmat_fn,  # Use the pre-created function
)

state = nested_sampler.init(particles, logprior_fn=logprior_fn, loglikelihood_fn=loglikelihood_fn)

@jax.jit
def one_step(carry, xs):
    state, k = carry
    k, subk = jax.random.split(k, 2)
    state, dead_point = nested_sampler.step(subk, state)
    return (state, k), dead_point

print("✅ Nested sampler initialized with recompilation-free, generic functions")
print("✅ FIXED: Wraparound arrays now match ravel_pytree order exactly")
print("✅ FIXED: Using efficient ravel_pytree with matching unravel_fn")


def main():
    # Run Nested Sampling
    dead = []
    try:
        with tqdm.tqdm(desc="Dead points", unit=" dead points") as pbar:
            while not state.logZ_live - state.logZ < -3:
                (state, rng_key), dead_info = one_step((state, rng_key), None)
                dead.append(dead_info)
                pbar.update(n_delete)  # Update progress bar
    except KeyboardInterrupt:
        print("Interrupted by user; proceeding to save results")

    # Save nested sampling results using anesthetic
    from anesthetic import NestedSamples

    # Process dead points structure
    dead = jax.tree.map(
        lambda *args: jnp.reshape(
            jnp.stack(args, axis=0), (-1,) + args[0].shape[1:]
        ),
        *dead,
    )
    live = state

    # Combine log-likelihoods
    logL = np.concatenate((dead.loglikelihood, live.loglikelihood), dtype=float)
    logL_birth = np.concatenate((dead.loglikelihood_birth, live.loglikelihood_birth), dtype=float)
    # Where logL_birth is nan, set to -inf
    logL_birth = np.where(np.isnan(logL_birth), -np.inf, logL_birth)

    # Extract parameter data for ONLY the sampled parameters (in correct order)
    dead_data = np.column_stack([dead.particles[key] for key in SAMPLE_KEYS])
    live_data = np.column_stack([live.particles[key] for key in SAMPLE_KEYS])

    # Combine dead and live data
    data = np.concatenate([dead_data, live_data], axis=0)

    sampled_labels = {key: column_to_label[key] for key in SAMPLE_KEYS}

    print(f"Creating NestedSamples with {len(SAMPLE_KEYS)} parameters: {SAMPLE_KEYS}")
    print(f"Data shape: {data.shape}")
    print(f"LogL shape: {logL.shape}")

    # Create NestedSamples object
    samples = NestedSamples(
        data, 
        logL=logL, 
        logL_birth=logL_birth, 
        columns=SAMPLE_KEYS,  # Only sampled parameters
        labels=sampled_labels  # Only sampled parameter labels
    )

    # Save to CSV
    output_filename = "test_refactor_v2.csv"
    samples.to_csv(output_filename)
    print(f"✅ Saved nested samples to: {output_filename}")

    print("📊 Summary:")
    print(f"   - Sampled {len(SAMPLE_KEYS)} parameters (phase_c marginalized)")
    print(f"   - Total samples: {data.shape[0]}")
    try:
        print(f"   - Evidence: logZ = {samples.logZ():.2f}")
    except Exception:
        print("   - Evidence: could not compute `samples.logZ()`")
    print(f"   - Output file: {output_filename}")


if __name__ == '__main__':
    main()
