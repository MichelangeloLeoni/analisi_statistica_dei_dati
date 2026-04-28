'''
Script that generates two plots to illustrate the construction of Neyman confidence
belts for a binomial model using different ordering methods, 
and the corresponding coverage curves.
'''
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom
from asd import utils
from asd.interval_estimation import interval as asdinterval

# Define parameters
N = 20
ALPHA = 0.05
CL = 1 - ALPHA

prob_grid = np.linspace(0, 1, 100)
x_values = np.arange(N + 1)
order = [
    ("Probability ordering", "p"),
    ("Upper ordering", "upper"),
    ("Lower ordering", "lower")
]

def binomial(x, p):
    '''Wrapper for the binomial pmf'''
    return binom.pmf(x, N, p)

estimator = asdinterval.IntervalEstimator(
    prob_func=binomial,
    cl=CL,
    mu_grid=prob_grid,
    x_range=x_values
)

int_p_ordering  = []
int_upper = []
int_lower = []
for x_obs in x_values:
    int_p_ordering.append(estimator.neyman.find_interval(x_obs, method="pdf", ordering_type="p"))
    int_upper.append(estimator.neyman.find_interval(x_obs, method="pdf", ordering_type="upper"))
    int_lower.append(estimator.neyman.find_interval(x_obs, method="pdf", ordering_type="lower"))

cov_p_ordering  = estimator.coverage(int_p_ordering)
cov_upper       = estimator.coverage(int_upper)
cov_low         = estimator.coverage(int_lower)

titles = [
    "Probability ordering",
    "Upper ordering",
    "Lower ordering"
]
curves = [
    cov_p_ordering,
    cov_upper,
    cov_low
]

# Generate first plot
fig, axes = utils.pgf_generator(nrows=1, ncols=3, figsize=(5.5, 3.5), sharey=True)

for ax, (title, ordering_type) in zip(axes, order):
    mask_list = estimator.neyman.build_belt(method="pdf", ordering_type=ordering_type)
    x_low = []
    x_high = []

    for mask in mask_list:
        x_low.append(min(x_values[mask]))
        x_high.append(max(x_values[mask]))

    ax.fill_between(
        prob_grid,
        x_low,
        x_high,
        alpha=0.4
    )
    ax.plot(prob_grid, x_low, lw=1, color="black")
    ax.plot(prob_grid, x_high, lw=1, color="black")

    ax.set_title(title)
    ax.set_xlabel("p")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, N + 0.5)
    ax.grid(alpha=0.25)

axes[0].set_ylabel("x")

plt.savefig("images/binomial_Neyman_belts.pgf", bbox_inches="tight")
plt.close()

# Generate second plot
fig, axes = utils.pgf_generator(nrows=1, ncols=3, figsize=(5.5, 3.5), sharey=True)

for ax, title, curve in zip(axes, titles, curves):
    ax.plot(prob_grid, curve, lw=2)
    ax.axhline(CL, ls="--", lw=1.2, alpha=0.8)
    ax.set_title(title)
    ax.set_xlabel("p")
    ax.set_xlim(0, 1)
    ax.set_ylim(CL-0.03, 1.01)
    ax.grid(alpha=0.25)

axes[0].set_ylabel("Coverage probability")

plt.savefig("images/binomial_coverage.pgf", bbox_inches='tight')
plt.close()
