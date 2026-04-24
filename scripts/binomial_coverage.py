import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom
from asd import utils

n = 20                 # sample size
alpha = 0.05           # 95% confidence intervals
CL = 1 - alpha

p_grid = np.linspace(0, 1, 100)
x_vals = np.arange(n + 1)

# Acceptance rules for confidence belt construction
def acceptance_p_ordering(p):
    probs = binom.pmf(x_vals, n, p)

    # order x by decreasing probability P(x|p)
    order = np.argsort(probs)[::-1]

    total = 0.0
    acc = set()

    for i in order:
        acc.add(x_vals[i])
        total += probs[i]
        if total >= CL:
            break

    return acc

def acceptance_upper(p):
    probs = binom.pmf(x_vals, n, p)

    total = 0
    acc = set()

    for x in x_vals:
        acc.add(x)
        total += probs[x]
        if total >= CL:
            break

    return acc

def acceptance_lower(p):
    probs = binom.pmf(x_vals, n, p)

    total = 0
    acc = set()

    for x in reversed(x_vals):
        acc.add(x)
        total += probs[x]
        if total >= CL:
            break

    return acc


# Build confidence belt
def build_belt(acceptance_func):
    x_low = []
    x_high = []

    for p in p_grid:
        acc = sorted(list(acceptance_func(p)))
        x_low.append(min(acc))
        x_high.append(max(acc))

    return np.array(x_low), np.array(x_high)

fig, axes = utils.pgf_generator(nrows=1, ncols=3, figsize=(5.5, 3.5), sharey=True)

methods = [
    ("Probability ordering", acceptance_p_ordering),
    ("Upper ordering", acceptance_upper),
    ("Lower ordering", acceptance_lower),

]

# Plot Neyman belts
for ax, (title, func) in zip(axes, methods):

    x_low, x_high = build_belt(func)

    ax.fill_between(
        p_grid,
        x_low,
        x_high,
        alpha=0.4
    )
    ax.plot(p_grid, x_low, lw=1, color="black")
    ax.plot(p_grid, x_high, lw=1, color="black")

    ax.set_title(title)
    ax.set_xlabel("p")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, n + 0.5)
    ax.grid(alpha=0.25)

axes[0].set_ylabel("x")

plt.savefig("images/binomial_Neyman_belts.pgf", bbox_inches="tight")
plt.close()

# Build confidence intervals by inversion
def invert_belt(acceptance_func):
    """
    For each observed x, confidence interval in p obtained by inversion.
    """
    intervals = {}
    for x_obs in x_vals:
        good_p = []

        for p in p_grid:
            acc = acceptance_func(p)
            if x_obs in acc:
                good_p.append(p)

        if len(good_p) == 0:
            intervals[x_obs] = (np.nan, np.nan)
        else:
            intervals[x_obs] = (min(good_p), max(good_p))

    return intervals


# Coverage calculator
def coverage_curve(intervals):
    cov = []

    for p in p_grid:
        total = 0.0

        for x in x_vals:
            lo, hi = intervals[x]
            if lo <= p <= hi:
                total += binom.pmf(x, n, p)

        cov.append(total)

    return np.array(cov)


# Compute intervals
int_p_ordering  = invert_belt(acceptance_p_ordering)
int_upper       = invert_belt(acceptance_upper)
int_lower       = invert_belt(acceptance_lower)

# Coverage curves
cov_p_ordering  = coverage_curve(int_p_ordering)
cov_upper       = coverage_curve(int_upper)
cov_low         = coverage_curve(int_lower)

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

# Plot coverage curves
fig, axes = plt.subplots(1, 3, figsize=(5.5, 3.5), sharey=True)

for ax, title, curve in zip(axes, titles, curves):
    ax.plot(p_grid, curve, lw=2)
    ax.axhline(CL, ls="--", lw=1.2, alpha=0.8)
    ax.set_title(title)
    ax.set_xlabel("p")
    ax.set_xlim(0, 1)
    ax.set_ylim(CL-0.03, 1.01)
    ax.grid(alpha=0.25)

# Shared y-label
axes[0].set_ylabel("Coverage probability")

plt.savefig("images/binomial_coverage.pgf", bbox_inches='tight')
plt.close()