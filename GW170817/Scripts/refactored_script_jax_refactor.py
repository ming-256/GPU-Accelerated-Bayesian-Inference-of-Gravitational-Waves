import os
os.environ['XLA_PYTHON_CLIENT_PREALLOCATE'] = 'false'
import jax
jax.config.update('jax_enable_x64', True)
import blackjax
import time
import jax.scipy.stats as stats
import jax.numpy as jnp
import tqdm
from functools import partial
from anesthetic import NestedSamples
from astropy.time import Time
from jimgw.single_event.detector import H1, L1, V1
from jimgw.single_event.likelihood import original_likelihood as likelihood_function
from jimgw.single_event.waveform import RippleIMRPhenomD_NRTidalv2

label = 'Results/Test_jax_refactor'

# Define the parameters class
class ParameterPrior:
    def __init__(self, name: str, label: str, prior_fn: callable, *args):
        self.name = name
        self.label = label
        self.prior_fn = prior_fn
        self.args = args

    def logprob(self, value: float) -> float:
        return self.prior_fn(value, *self.args)

# Define the prior functions (kept for completeness; we use codes for sampling/eval)
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
    ParameterPrior("lambda_2", r"$\Lambda_2$", UniformPrior, 0.0, 5000.0)
]

parameter_names = [param.name for param in parameters]
labels = [param.label for param in parameters]

# Map prior types to integer codes and build argument arrays (for JIT-friendly priors)
PRIOR_UNIFORM = 0
PRIOR_SIN = 1
PRIOR_COS = 2
PRIOR_BETA = 3
PRIOR_FLATLOG = 4

_prior_code_list = []
_prior_arg1 = []
_prior_arg2 = []
for p in parameters:
    if p.prior_fn == UniformPrior:
        _prior_code_list.append(PRIOR_UNIFORM)
        _prior_arg1.append(p.args[0])
        _prior_arg2.append(p.args[1])
    elif p.prior_fn == SinPrior:
        _prior_code_list.append(PRIOR_SIN)
        _prior_arg1.append(0.0)
        _prior_arg2.append(0.0)
    elif p.prior_fn == CosPrior:
        _prior_code_list.append(PRIOR_COS)
        _prior_arg1.append(0.0)
        _prior_arg2.append(0.0)
    elif p.prior_fn == BetaPrior:
        _prior_code_list.append(PRIOR_BETA)
        _prior_arg1.append(p.args[0])
        _prior_arg2.append(p.args[1])
    elif p.prior_fn == FlatInLogPrior:
        _prior_code_list.append(PRIOR_FLATLOG)
        _prior_arg1.append(p.args[0])
        _prior_arg2.append(p.args[1])
    else:
        _prior_code_list.append(PRIOR_UNIFORM)
        _prior_arg1.append(0.0)
        _prior_arg2.append(1.0)

prior_codes = jnp.array(_prior_code_list)
prior_arg1 = jnp.array(_prior_arg1)
prior_arg2 = jnp.array(_prior_arg2)

# Ensure frequencies is a JAX array and precompute frequency-dependent factors
frequencies = jnp.array(frequencies)
# Precompute alignment factor component that is independent of t_c
_base_align = jnp.exp(-1j * 2 * jnp.pi * frequencies * epoch)

# Create an example parameter pytree and an unravel function so we can convert
# a flat parameter vector to the dict/pytree expected by the waveform and likelihood
# without constructing Python dicts on every call (prevents heavy Python overhead).
_example_params = {name: jnp.array(0.0) for name in parameter_names}
_, _unravel_fn = jax.flatten_util.ravel_pytree(_example_params)


# Vectorized prior evaluator (kept JIT'd)
def _logprior_per_param(v, code, a1, a2):
    def _u(operand):
        vv, a1o, a2o = operand
        return stats.uniform.logpdf(vv, a1o, a2o - a1o)

    def _s(operand):
        vv, _, _ = operand
        return jnp.where((vv < 0.0) | (vv > jnp.pi), -jnp.inf, jnp.log(jnp.sin(vv) / 2.0))

    def _c(operand):
        vv, _, _ = operand
        return jnp.where(
            (vv < -jnp.pi / 2.0) | (vv > jnp.pi / 2.0), -jnp.inf, jnp.log(jnp.cos(vv) / 2.0)
        )

    def _b(operand):
        vv, a1o, a2o = operand
        return stats.beta.logpdf(vv, 3.0, 1.0, a1o, a2o - a1o)

    def _fl(operand):
        vv, a1o, a2o = operand
        return jnp.where((vv < a1o) | (vv > a2o), -jnp.inf, (-jnp.log(jnp.log(a2o / a1o)) - jnp.log(vv)))

    branches = (_u, _s, _c, _b, _fl)
    return jax.lax.switch(code, branches, (v, a1, a2))


@jax.jit
def logprior_fn(params_array):
    vals = jax.vmap(_logprior_per_param)(params_array, prior_codes, prior_arg1, prior_arg2)
    return jnp.sum(vals)


@jax.jit
def loglikelihood_fn(params_array):
    # Convert flat array to the parameter pytree using a precomputed unravel function
    params = _unravel_fn(params_array)
    # Derived parameters
    params["eta"] = params["q"] / (1 + params["q"]) ** 2
    params["gmst"] = gmst

    # Defined as in Abbott et al. 2017 (https://arxiv.org/pdf/1710.05832.pdf)
    # ll_vr = stats.norm.logpdf(3327, params["v_p"] + params["H_0"] * params["d_L"], 72)
    # ll_vp = stats.norm.logpdf(310, params["v_p"], 150)

    waveform_sky = waveform(frequencies, params)
    # Use precomputed base align and multiply by the small t_c-dependent factor
    align_time = _base_align * jnp.exp(-1j * 2 * jnp.pi * frequencies * params["t_c"])

    return likelihood_function(
        params,
        waveform_sky,
        detectors,
        frequencies,
        align_time
    ) #+ ll_vr + ll_vp


# Define the Nested Sampling algorithm parameters
num_dims = len(parameter_names)
num_live = 1000
num_delete = int(num_live * 0.5)
num_mcmc_steps = int(num_dims * 5)

# Make batch size a module-level constant so it is static for JIT
BATCH_SIZE = 8

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


# Batch-run N steps on-device using lax.scan to reduce Python loop overhead.
@partial(jax.jit, static_argnums=(2,))
def run_n_steps(state, rng_key, n_steps):
    xs = jnp.arange(n_steps)

    def body(carry, _):
        state, key = carry
        key, subk = jax.random.split(key)
        state, dead_point = nested_sampler.step(subk, state)
        return (state, key), dead_point

    (state, key), deads = jax.lax.scan(body, (state, rng_key), xs)
    return state, key, deads


# Vectorized sampling of prior for initial live points (A + B)
@partial(jax.jit, static_argnums=(3,))
def sample_prior_vectorized(prior_codes, a1, a2, n_live, rng_key):
    """Return array of shape (n_dims, n_live) with samples per prior code.

    Uses a separate key per dimension obtained from rng_key.
    """
    n_dims = prior_codes.shape[0]
    keys = jax.random.split(rng_key, n_dims)

    def _sample_for_dim(code, aa, bb, key):
        # returns (n_live,) array for this dim
        def _u(inp):
            _, a, b, k = inp
            return a + jax.random.uniform(k, (n_live,)) * (b - a)

        def _s(inp):
            _, a, b, k = inp
            return 2 * jnp.arcsin(jax.random.uniform(k, (n_live,)) ** 0.5)

        def _c(inp):
            _, a, b, k = inp
            return 2 * jnp.arcsin(jax.random.uniform(k, (n_live,)) ** 0.5) - jnp.pi / 2.0

        def _b(inp):
            _, a, b, k = inp
            return jax.random.beta(k, 3.0, 1.0, (n_live,)) * (b - a) + a

        def _fl(inp):
            _, a, b, k = inp
            return a * (b / a) ** jax.random.uniform(k, (n_live,))

        branches = (_u, _s, _c, _b, _fl)
        return jax.lax.switch(code, branches, (None, aa, bb, key))

    sampled = jax.vmap(_sample_for_dim)(prior_codes, a1, a2, keys)
    return sampled


# RNG + initial particle generation (vectorized)
# Provide a small JIT'd wrapper to produce the initial particle matrix (num_live, num_dims)
@partial(jax.jit, static_argnums=(3,))
def generate_initial_particles(prior_codes, prior_arg1, prior_arg2, num_live, rng_key):
    sampled = sample_prior_vectorized(prior_codes, prior_arg1, prior_arg2, num_live, rng_key)
    return jnp.transpose(sampled)

rng_key = jax.random.PRNGKey(0)
rng_key, init_key = jax.random.split(rng_key, 2)
initial_particles = generate_initial_particles(prior_codes, prior_arg1, prior_arg2, num_live, init_key)

state = nested_sampler.init(initial_particles)

# Run nested sampling
def main():
    print("Running nested sampling (refactor_jax_refactor)...")
    ns_start = time.time()
    dead = []

    # Use module-level `state` and `rng_key` variables (they are initialized at module scope).
    # Declare as global so assignments in this function update the module-level objects
    # instead of creating new local variables (avoids UnboundLocalError).
    global state, rng_key

    import numpy as _np

    # Use batched on-device stepping to reduce Python-level loop overhead.
    batch_size = BATCH_SIZE  # number of nested_sampler.step calls to run per Python iteration
    with tqdm.tqdm(desc="Dead points", unit=" dead points") as pbar:
        while True:
            # Run batch_size steps on-device
            state, rng_key, deads = run_n_steps(state, rng_key, batch_size)
            # Move batch of dead points to host and collect
            deads_host = jax.device_get(deads)
            # `deads_host` is a pytree where each leaf has leading axis batch_size
            for i in range(batch_size):
                dead.append(jax.tree_map(lambda x: x[i], deads_host))
            pbar.update(num_delete * batch_size)

            # Check termination condition on host to decide whether to continue
            diff = float(jax.device_get(state.logZ_live - state.logZ))
            if diff < -3:
                break

    # Finalise using blackjax utility (it will operate on host arrays we collected)
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
    try:
        print(f"Log Evidence: {samples.logZ():.2f} ± {samples.logZ(100).std():.2f}")
    except Exception:
        print("Could not compute evidence summary")

    samples.to_csv(f'{label}.csv')
    print(f"Samples saved to {label}.csv")


if __name__ == '__main__':
    main()
