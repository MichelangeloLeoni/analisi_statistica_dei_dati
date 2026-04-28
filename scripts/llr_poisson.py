'''
Script that computes confidence intervals in the Poisson case using:
- log-likelihood ratio (Wilks) method
- central intervals
- Feldman–Cousins construction

It also evaluates and plots the coverage error of the LLR method,
and generates a LaTeX table for comparison.
'''
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar
from scipy.stats import chi2, poisson
from asd import utils
from asd.interval_estimation import interval as asdinterval

# Define parameters
CL = 0.95

# START SNIPPET 1
def calculate_llr_intervals(n_values, cl=CL):
    '''
    Compute likelihood-ratio (Wilks) intervals for Poisson counts.

    For each observed count n, solves the likelihood ratio equation:
        -2 log lambda(mu) = chi2 quantile

    Parameters:
        n_values : array-like
            Observed counts.
        cl : float
            Confidence level.

    Output:
        intervals : list of tuples
            (lower, upper) bounds for each n.
    '''

    # Critical value from chi-square distribution (Wilks' theorem)
    critical_value = chi2.ppf(cl, df=1)
    intervals = []

    for n in n_values:

        def lam(mu, n=n):
            '''
            Likelihood ratio equation for Poisson model.

            Returns zero at the interval boundaries.
            '''
            if n == 0:
                return 2 * mu - critical_value
            if mu <= 0:
                return 1e9  # avoid invalid region
            return 2 * (mu - n + n * np.log(n / mu)) - critical_value

        # Lower bound
        if n == 0:
            low = 0.0
        else:
            low = root_scalar(lam, bracket=[1e-12, n]).root

        # Upper bound (use a wide bracket to ensure root is found)
        upper_guess = max(n + 10 * np.sqrt(n + 1), n + 10)
        high = root_scalar(lam, bracket=[n, upper_guess]).root

        intervals.append((low, high))

    return intervals
# END SNIPPET 1

# START SNIPPET 2
def calculate_central_interval_mu(n_obs, cl=CL):
    '''
    Compute central confidence interval for Poisson mean.

    The interval is defined by equal tail probabilities.

    Parameters:
        n_obs : int
            Observed count.
        cl : float
            Confidence level.

    Output:
        (low, high) : tuple
            Central confidence interval.
    '''

    alpha = 1 - cl

    # Lower bound
    if n_obs == 0:
        low = 0.0
    else:
        def f_low(mu):
            # Upper tail condition
            return (1 - poisson.cdf(n_obs - 1, mu)) - alpha / 2

        low = root_scalar(f_low, bracket=[1e-12, n_obs]).root

    # Upper bound
    def f_high(mu):
        # Lower tail condition
        return poisson.cdf(n_obs, mu) - alpha / 2

    high_guess = n_obs + 10 * np.sqrt(n_obs + 1) + 20
    high = root_scalar(f_high, bracket=[n_obs, high_guess]).root

    return (low, high)
# END SNIPPET 2

# Grids for coverage evaluation
mu_axis = np.linspace(0.001, 17, 1000)   # plotting range
mu_span = np.linspace(0.0001, 100, 1000) # wide range for belt construction

# Values of n used in the output table
n_table = np.concatenate([np.arange(0, 10), [50]])

# Estimator used for Feldman–Cousins intervals
estimator = asdinterval.IntervalEstimator(
    x_range=np.arange(0, 300),
    mu_grid=mu_span,
    mu_hat_func=lambda x: x,   # MLE for Poisson
    prob_func=poisson.pmf,
    cl=0.95,
    discrete=True
)

# Estimator used for coverage computation (restricted range)
cov_estimator = asdinterval.IntervalEstimator(
    x_range=np.arange(0, 51),
    mu_grid=mu_axis,
    mu_hat_func=lambda x: x,
    prob_func=poisson.pmf,
    cl=0.95,
    discrete=True
)

# Compute LLR intervals on discrete grid
n_grid = cov_estimator.x_range
intervals_cache = calculate_llr_intervals(n_grid)

# Evaluate coverage and corresponding error
coverage = cov_estimator.coverage(intervals_cache)
errors = 1 - coverage

# Feldman–Cousins intervals via Neyman construction
lr_intervals = {
    n: estimator.neyman.find_interval(
        x_obs=n,
        ordering_type="p",
        method="fc"
    )
    for n in n_table
}

# Central intervals
central_intervals = {
    n: calculate_central_interval_mu(n)
    for n in n_table
}

# Generate plot
fig, ax = utils.pgf_generator(figsize=(5.5, 3.5))

# Plot coverage error curve
ax.plot(mu_axis, errors, lw=1.0, label=r"$1 - \mathcal{C}(\mu)$")

# Reference line at nominal level
ax.axhline(0.05, ls="--", lw=1.0, label=r"Nominal level $0.05$")

ax.set_xlim(-0.2, 16)
ax.set_xlabel(r"$\mu$")
ax.set_ylabel(r"Coverage error")
ax.set_ylim(0, 0.2)
ax.legend()

plt.savefig("images/llr_poisson_coverage.pgf", bbox_inches="tight")
plt.close()

# Format intervals for LaTeX output
def fmt_interval(a, b):
    '''
    Format a confidence interval for LaTeX table.

    Adjusts precision depending on magnitude.
    '''
    if np.isnan(a) or np.isnan(b):
        return r"$\text{--}$"

    if a < 10 and b < 10:
        return rf"${a:.3f} \leq \mu \leq {b:.3f}$"
    if a < 10 and b >= 10:
        return rf"${a:.3f} \leq \mu \leq {b:.2f}$"
    if a >= 10 and b < 10:
        return rf"${a:.2f} \leq \mu \leq {b:.3f}$"

    return rf"${a:.2f} \leq \mu \leq {b:.2f}$"

# Prepare formatted table columns
fmt_lr_intervals = [fmt_interval(*lr_intervals[n]) for n in n_table]
fmt_central_intervals = [fmt_interval(*central_intervals[n]) for n in n_table]
fmt_wisks = [fmt_interval(*intervals_cache[i]) for i in n_table]

# Generate table
utils.table_generator(
    n_columns=4,
    labels=("$n$", "Wilks", "Feldman-Cousins", "Central interval"),
    content=(n_table, fmt_wisks, fmt_lr_intervals, fmt_central_intervals),
    output_file_name="llr_poisson_intervals.tex"
)

utils.code_snippet_generator(
    start_tag="# START SNIPPET 1",
    end_tag="# END SNIPPET 1",
    output_file_name="wilks_code.tex",
    file=__file__
)
utils.code_snippet_generator(
    start_tag="# START SNIPPET 2",
    end_tag="# END SNIPPET 2",
    output_file_name="central_code.tex",
    file=__file__
)
