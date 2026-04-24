import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar
from scipy.stats import chi2, poisson
from asd import utils

# START SNIPPET
def calculate_llr_intervals(n_values, cl=0.95):
    '''Compute LLR (Wilks) intervals for a range of observed counts n.'''
    critical_value = chi2.ppf(cl, df=1)
    intervals = []

    for n in n_values:

        def f(mu):
            if n == 0:
                return 2 * mu - critical_value
            if mu <= 0:
                return 1e9
            return 2 * (mu - n + n * np.log(n / mu)) - critical_value

        try:
            if n == 0:
                low = 0.0
            else:
                low = root_scalar(f, bracket=[1e-12, n]).root

            upper_guess = max(n + 10*np.sqrt(n + 1), n + 10)
            high = root_scalar(f, bracket=[n, upper_guess]).root

            intervals.append((low, high))

        except ValueError:
            intervals.append((np.nan, np.nan))

    return intervals

def calculate_lr_interval_mu(n_obs, mu_grid, cl=0.95, n_max=100):
    '''Compute the Feldman-Cousins interval for a given observed count n_obs.'''
    accepted_mu = []
    n_values = np.arange(0, n_max)

    for mu in mu_grid:
        pdf = poisson.pmf(n_values, mu)
        mu_hat = n_values
        den = poisson.pmf(n_values, mu_hat)
        R = pdf / den

        order = np.argsort(R)[::-1]

        cum = 0
        for i in order:
            cum += pdf[i]
            if cum >= cl:
                c = R[i]
                break

        mask = R >= c

        if n_obs < len(mask) and mask[n_obs]:
            accepted_mu.append(mu)

    if len(accepted_mu) == 0:
        return (np.nan, np.nan)

    return (min(accepted_mu), max(accepted_mu))

def calculate_central_interval_mu(n_obs, cl=0.95):
    '''Compute the central interval for a given observed count n_obs.'''
    alpha = 1 - cl
    
    try:
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

    except (ValueError, RuntimeError):
        return (np.nan, np.nan)

def coverage_error(mu, n_test, intervals_cache):
    '''Calculate the coverage error for a given true mean mu.'''
    prob_covered = 0.0
    for n, (low, high) in zip(n_test, intervals_cache):
        if low <= mu <= high:
            prob_covered += poisson.pmf(n, mu)
    return 1 - prob_covered
# END SNIPPET

# COMPUTE COVERAGE ERROR
mu_axis = np.linspace(0.001, 17, 1000)
mu_span = np.linspace(0.0001, 100, 1000)
n_test = np.arange(0, 51)
intervals_cache = calculate_llr_intervals(n_test)
errors = np.array([coverage_error(m, n_test, intervals_cache) for m in mu_axis])

# PLOT COVERAGE ERROR
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

# COMPUTE INTERVALS FOR TABLE
n_table = np.concatenate([np.arange(0, 10), [50]])
lr_intervals = {n: calculate_lr_interval_mu(n, mu_span) for n in n_table}
central_intervals = {n: calculate_central_interval_mu(n) for n in n_table}

# FORMAT TABLE
def fmt_interval(a, b):
    if np.isnan(a) or np.isnan(b):
        return r"$\text{--}$"
    return rf"${a:.3f} \leq \mu \leq {b:.3f}$"

# GENERATE LATEX TABLE
content = r"""
$n$ & Wilks & Feldman-Cousins & Central interval \\
\hline
"""
for n in n_table:
    content += (
        f"{n} & "
        f"{fmt_interval(intervals_cache[n][0], intervals_cache[n][1])} & "
        f"{fmt_interval(lr_intervals[n][0], lr_intervals[n][1])} & "
        f"{fmt_interval(central_intervals[n][0], central_intervals[n][1])} \\\\\n"
    )

utils.table_generator(4, content, "llr_poisson_intervals.tex")

# WRITE CODE SNIPPET TO FILE
def extract_snippet(filename, start_tag, end_tag):
    with open(filename, "r") as f:
        lines = f.readlines()

    inside = False
    snippet = []

    for line in lines:
        if start_tag in line:
            inside = True
            continue
        if end_tag in line:
            break
        if inside:
            snippet.append(line)

    return "".join(snippet)


snippet_code = extract_snippet(
    __file__,
    "START SNIPPET",
    "END SNIPPET"
)

latex_code = r"""
\begin{minted}[fontsize=\small, linenos, breaklines]{python}
""" + snippet_code + r"""
\end{minted}
"""

with open("code/code_llr_poisson.tex", "w") as f:
    f.write(latex_code)