'''
Script that generates a plot to illustrate the construction of Bayesian credible intervals 
using different ordering methods.
'''
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson
from asd import utils
from asd.asdmath.interval_estimation import bayesian

# Define parameters
PRIOR = 0.1 # Prior for Uniform(0, 10)
CL = 0.9

k_values = [2, 5, 8]
m = np.linspace(0, 10, 1000)

# Generate first plot
fig, ax = utils.pgf_generator(figsize=(5.5, 3.5))

for k in k_values:
    posterior = bayesian.compute_posterior(
        x=k,
        mu=m,
        prob_func=poisson.pmf,
        prior_func=lambda mu: PRIOR
        )

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

posterior = bayesian.compute_posterior(
        x=k,
        mu=m,
        prob_func=poisson.pmf,
        prior_func=lambda mu: PRIOR
        )

lo_hpd, hi_hpd = bayesian.posterior_interval(k, m, poisson.pmf, lambda mu: PRIOR, cl=CL)
lo_low, hi_low = bayesian.lower_bound(k, m, poisson.pmf, lambda mu: PRIOR, cl=CL)
lo_high, hi_high = bayesian.upper_bound(k, m, poisson.pmf, lambda mu: PRIOR, cl=CL)

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
