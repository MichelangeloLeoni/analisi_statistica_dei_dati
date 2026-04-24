'''
Script that generates a plot to illustrate the construction of Bayesian credible intervals 
using different ordering methods.
'''
import math
import numpy as np
import matplotlib.pyplot as plt
from asd import utils

# START SNIPPET
# Define parameters
PRIOR = 0.1 # Prior for Uniform(0, 10)
ALPHA = 0.10

def compute_posterior(mu, n):
    '''Compute the posterior for a Poisson distribution at given mu and observed count'''

    likelihood = np.exp(-mu) * mu**n / math.factorial(n)
    unnorm = PRIOR * likelihood
    norm = np.trapezoid(unnorm, mu)
    return unnorm / norm

def posterior_interval(mu, post, alpha=0.10):
    '''Compute the confidence interval using the posterior as the ordering function'''

    dmu = mu[1] - mu[0]
    idx = np.argsort(post)[::-1]
    mass = np.cumsum(post[idx] * dmu)

    keep = idx[mass <= (1 - alpha)]
    if len(keep) < len(idx):
        keep = np.append(keep, idx[len(keep)])
    keep = np.sort(keep)

    lower = mu[keep[0]]
    upper = mu[keep[-1]]

    return lower, upper

def lower_bound(mu, post, alpha=0.10):
    '''Compute the confidence interval using the lower bound ordering'''

    dmu = mu[1] - mu[0]
    cdf = np.cumsum(post * dmu)
    cdf /= cdf[-1]

    return np.interp(alpha, cdf, mu), mu[-1]

def upper_bound(mu, post, alpha=0.10):
    '''Compute the confidence interval using the upper bound ordering'''
    dmu = mu[1] - mu[0]
    cdf = np.cumsum(post * dmu)
    cdf /= cdf[-1]

    return mu[0], np.interp(1 - alpha, cdf, mu)
# END SNIPPET

k_values = [2, 5, 8]
m = np.linspace(0, 10, 1000)

# Generate first plot
fig, ax = utils.pgf_generator(figsize=(5.5, 3.5))

for k in k_values:
    posterior = compute_posterior(m, k)

    ax.plot(m, posterior, lw=2)

    peak_idx = np.argmax(posterior)
    peak_m = m[peak_idx]
    peak_y = posterior[peak_idx]

    ax.text(
        peak_m + 0.5,
        peak_y + 0.005,
        f"k = {k}",
        fontsize=9,
        va="center"
    )

ax.set_xlabel(r"$\mu$")
ax.set_ylabel("Posterior density")
ax.grid(True, alpha=0.3)

plt.savefig("images/bayes_posterior.pgf", bbox_inches='tight')
plt.close()

# Define ordering methods for interval calculation
ordering = ["Posterior", "Lower bound", "Upper bound"]
k = 5

posterior = compute_posterior(m, k)

lo_hpd, hi_hpd = posterior_interval(m, posterior, alpha=ALPHA)
lo_low, hi_low = lower_bound(m, posterior, alpha=ALPHA)
lo_high, hi_high = upper_bound(m, posterior, alpha=ALPHA)

# Generate LaTeX table
def fmt(a, b):
    '''Format the interval in LaTeX math mode'''
    return rf"${a:.2f} \leq \mu \leq {b:.2f}$" # format the interval in LaTeX math mode

utils.table_generator(
    n_columns=2,
    labels=(r"Method", r"90\% credible interval"),
    content=(ordering, [fmt(lo_hpd, hi_hpd), fmt(lo_low, hi_low), fmt(lo_high, hi_high)]),
    output_file_name="bayes_interval.tex"
    )

# Generate second plot
fig, ax = utils.pgf_generator(nrows=1, ncols=3, figsize=(5.5, 3.5), sharey=True)

for i, o in enumerate(ordering):

    lo, hi = None, None
    if o == "Posterior":
        lo, hi = lo_hpd, hi_hpd
    elif o == "Lower bound":
        lo, hi = lo_low, hi_low
    elif o == "Upper bound":
        lo, hi = lo_high, hi_high

    ax[i].plot(m, posterior, lw=2)

    mask = (m >= lo) & (m <= hi)
    ax[i].fill_between(m[mask], posterior[mask], alpha=0.25)

    peak_idx = np.argmax(posterior)
    peak_m = m[peak_idx]
    peak_y = posterior[peak_idx]

    ax[i].set_title(o, fontsize=10)

    ax[i].set_xlabel(r"$\mu$")
    ax[i].grid(True, alpha=0.3)
    ax[i].tick_params(axis='y', left=False, labelleft=False)

ax[0].set_ylabel("Posterior density")

plt.savefig("images/bayes_interval.pgf", bbox_inches='tight')
plt.close()

utils.code_snippet_generator(
    file=__file__,
    start_tag="# START SNIPPET",
    end_tag="# END SNIPPET",
    output_file_name="code_bayes_interval.tex"
)
