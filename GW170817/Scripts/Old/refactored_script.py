import os
os.environ['XLA_PYTHON_CLIENT_PREALLOCATE'] = 'false'
import jax
jax.config.update('jax_enable_x64', True)
import blackjax
import time 
import jax.scipy.stats as stats
import jax.numpy as jnp
import tqdm
from anesthetic import NestedSamples
from astropy.time import Time
from jimgw.single_event.detector import H1, L1, V1
from jimgw.single_event.likelihood import original_likelihood as likelihood_function
from jimgw.single_event.waveform import RippleIMRPhenomD_NRTidalv2

label = 'Results/Test'

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

@jax.jit
def loglikelihood_fn(params_array):
    # Convert array to dictionary
    params = dict(zip(parameter_names, params_array))
    params["eta"] = params["q"] / (1 + params["q"]) ** 2
    params["gmst"] = gmst

    # Defined as in Abbott et al. 2017 (https://arxiv.org/pdf/1710.05832.pdf)
    ll_vr = stats.norm.logpdf(3327, params["v_p"] + params["H_0"] * params["d_L"], 72)
    ll_vp = stats.norm.logpdf(310, params["v_p"], 150)

    waveform_sky = waveform(frequencies, params)
    align_time = jnp.exp(-1j * 2 * jnp.pi * frequencies * (epoch + params["t_c"]))
    
    return likelihood_function(
    params,
    waveform_sky,
    detectors,
    frequencies,
    align_time
    ) + ll_vr + ll_vp

# Define the Nested Sampling algorithm parameters
num_dims = len(parameter_names)
num_live = 1200
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