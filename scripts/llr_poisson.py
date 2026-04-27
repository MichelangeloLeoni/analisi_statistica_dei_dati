'''
Script that compute the confidence interval in the poissonian case using:
- llr method
- central interval
- feldman-cousins method
then populate a latex table to be put on the notes.
For the llr method is computed and plotted the coverage error.
'''
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar
from scipy.stats import chi2, poisson
from asd import utils, asdmath

# Define parameters
CL = 0.95

# START SNIPPET
def calculate_llr_intervals(n_values, cl=CL):
    '''Compute LLR (Wilks) interval at confidence level cl
    for a range of observed counts n_values.'''

    critical_value = chi2.ppf(cl, df=1)
    intervals = []

    for n in n_values:

        def lam(mu, n=n):
            '''Compute the log-likelihood-ratio for the poissonian case.'''
            if n == 0:
                return 2 * mu - critical_value
            if mu <= 0:
                return 1e9
            return 2 * (mu - n + n * np.log(n / mu)) - critical_value

        if n == 0:
            low = 0.0
        else:
            low = root_scalar(lam, bracket=[1e-12, n]).root

        upper_guess = max(n + 10*np.sqrt(n + 1), n + 10)
        high = root_scalar(lam, bracket=[n, upper_guess]).root

        intervals.append((low, high))

    return intervals

def calculate_central_interval_mu(n_obs, cl=0.95):
    '''
    Compute the central interval at confidence level cl
    for a given observed count n_obs.
    '''

    alpha = 1 - cl

    if n_obs == 0:
        low = 0.0
    else:
        def f_low(mu):
            return (1 - poisson.cdf(n_obs - 1, mu)) - alpha/2

        low = root_scalar(f_low, bracket=[1e-12, n_obs]).root

    def f_high(mu):
        return poisson.cdf(n_obs, mu) - alpha/2

    high_guess = n_obs + 10 * np.sqrt(n_obs + 1) + 20
    high = root_scalar(f_high, bracket=[n_obs, high_guess]).root

    return (low, high)

def coverage_error(mu, n_test, intervals):
    '''Calculate the coverage error for a given true mean mu.'''

    prob_covered = 0.0
    for n, (low, high) in zip(n_test, intervals):
        if low <= mu <= high:
            prob_covered += poisson.pmf(n, mu)

    return 1 - prob_covered

# Compute coverage error
mu_axis = np.linspace(0.001, 17, 1000)
mu_span = np.linspace(0.0001, 100, 1000)
n_grid = np.arange(0, 51)
intervals_cache = calculate_llr_intervals(n_grid)
errors = np.array([coverage_error(m, n_grid, intervals_cache) for m in mu_axis])

# Compute intervals for the table
n_table = np.concatenate([np.arange(0, 10), [50]])
lr_intervals = {n:
    asdmath.find_lr_intervals(
        x_obs=n,
        x_range=np.arange(0, 100),
        mu_grid=mu_span,
        mu_hat=np.arange(0, 100),
        prob_func=poisson.pmf,
        cl=CL
        ) for n in n_table}
central_intervals = {n: calculate_central_interval_mu(n) for n in n_table}
# END SNIPPET

# Generate plot
fig, ax = utils.pgf_generator(figsize=(5.5, 3.5))
ax.plot(mu_axis, errors, lw=1.0, label=r"$1 - \mathcal{C}(\mu)$")
ax.axhline(0.05, ls="--", lw=1.0, label=r"Nominal level $0.05$")

ax.set_xlim(-0.2, 16)
ax.set_xlabel(r"$\mu$")
ax.set_ylabel(r"Coverage error")
ax.set_ylim(0, 0.2)
ax.legend()

plt.savefig("images/llr_poisson_coverage.pgf", bbox_inches="tight")
plt.close()

# Format table content
def fmt_interval(a, b):
    '''Format an interval for LaTeX.'''
    if np.isnan(a) or np.isnan(b):
        return r"$\text{--}$"
    return rf"${a:.3f} \leq \mu \leq {b:.3f}$"

# Generate table
fmt_lr_intervals = [fmt_interval(*lr_intervals[n]) for n in n_table]
fmt_central_intervals = [fmt_interval(*central_intervals[n]) for n in n_table]
fmt_wisks = [fmt_interval(*intervals_cache[i]) for i in n_table]

utils.table_generator(
    n_columns=4,
    labels=("$n$", "Wilks", "Feldman-Cousins", "Central interval"),
    content=(n_table, fmt_wisks, fmt_lr_intervals, fmt_central_intervals),
    output_file_name="llr_poisson_intervals.tex"
    )

# Generate code snippet
utils.code_snippet_generator(
    start_tag="# START SNIPPET",
    end_tag="# END SNIPPET",
    output_file_name="code_llr_poisson.tex",
    file=__file__
)
