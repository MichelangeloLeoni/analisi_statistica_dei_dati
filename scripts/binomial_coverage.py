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

# Acceptance rules for confidence belt construction
def acceptance_p_ordering(p, x_vals, cl=CL):
    '''Compute acceptance region following probability ordering.'''

    probs = binom.pmf(x_vals, N, p)
    order = np.argsort(probs)[::-1]

    total = 0.0
    acc = set()

    for i in order:
        acc.add(x_vals[i])
        total += probs[i]
        if total >= cl:
            break

    return acc

def acceptance_upper(p, x_vals, cl=CL):
    '''Compute acceptance region following upper ordering.'''

    probs = binom.pmf(x_vals, N, p)

    total = 0
    acc = set()

    for x in x_vals:
        acc.add(x)
        total += probs[x]
        if total >= cl:
            break

    return acc

def acceptance_lower(p, x_vals, cl=CL):
    '''Compute acceptance region following lower ordering.'''

    probs = binom.pmf(x_vals, N, p)

    total = 0
    acc = set()

    for x in reversed(x_vals):
        acc.add(x)
        total += probs[x]
        if total >= cl:
            break

    return acc

def build_belt(acceptance_func, p_grid, cl=CL):
    '''Compute Neyman confidence belt based on giveng acceptance function.'''

    temp_x_low = []
    temp_x_high = []

    for p in p_grid:
        acc = sorted(list(acceptance_func(p, x_values, cl=cl)))
        temp_x_low.append(min(acc))
        temp_x_high.append(max(acc))

    return np.array(temp_x_low), np.array(temp_x_high)

def invert_belt(acceptance_func, x_vals, p_grid, cl=CL):
    '''
    Compute confidence intervals for a given observed x based on
    giveng acceptance function and probability grid.
    '''

    intervals = {}
    for x_obs in x_vals:
        good_p = []

        for p in p_grid:
            acc = acceptance_func(p, x_vals, cl=cl)
            if x_obs in acc:
                good_p.append(p)

        if len(good_p) == 0:
            intervals[x_obs] = (np.nan, np.nan)
        else:
            intervals[x_obs] = (min(good_p), max(good_p))

    return intervals

def coverage_curve(intervals, p_grid, x_vals):
    '''
    Compute coverage curve for given confidence intervals, 
    probability grid and possible x values.
    '''

    cov = []

    for p in p_grid:
        total = 0.0

        for x in x_vals:
            lo, hi = intervals[x]
            if lo <= p <= hi:
                total += binom.pmf(x, N, p)

        cov.append(total)

    return np.array(cov)

prob_grid = np.linspace(0, 1, 100)
x_values = np.arange(N + 1)
order = [
    ("Probability ordering", "p"),
    ("Upper ordering", "upper"),
    ("Lower ordering", "lower")
]
def binomial(x, p):
    return binom.pmf(x, N, p)
estimator = asdinterval.IntervalEstimator(
    prob_func=binomial,
    cl=CL,
    mu_grid=prob_grid,
    x_range=x_values
)
int_p_ordering  = invert_belt(acceptance_p_ordering, x_values, prob_grid)
int_upper       = invert_belt(acceptance_upper, x_values, prob_grid)
int_lower       = invert_belt(acceptance_lower, x_values, prob_grid)

cov_p_ordering  = coverage_curve(int_p_ordering, prob_grid, x_values)
cov_upper       = coverage_curve(int_upper, prob_grid, x_values)
cov_low         = coverage_curve(int_lower, prob_grid, x_values)

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
