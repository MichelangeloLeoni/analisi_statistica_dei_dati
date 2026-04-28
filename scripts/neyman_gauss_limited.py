'''
Script that builds the Neyman confidence belt for a Gaussian with non-negative mean, 
using both probability ordering and likelihood ratio ordering.
'''
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from asd import utils
from asd.interval_estimation import interval as asdinterval

# Define parameters
CL = 0.95

mu_grid = np.linspace(0.0, 3.0, 200)
x_grid = np.linspace(-3.5, 5.0, 700)
dx = x_grid[1] - x_grid[0]

def mu_hat(x):
    '''Wrapper for the MLE function'''
    return np.maximum(0.0, x)

estimator = asdinterval.IntervalEstimator(
    prob_func=norm.pdf,
    cl=CL,
    mu_hat_func=mu_hat,
    discrete=False,
    x_range=x_grid,
    mu_grid=mu_grid
)

mask_list_p = estimator.neyman.build_belt(method="pdf", ordering_type="p")
mask_list_lr = estimator.neyman.build_belt(method="fc", ordering_type="p")

xlow_p, xhigh_p = estimator.masks_to_bounds(mask_list_p)
xlow_lr, xhigh_lr = estimator.masks_to_bounds(mask_list_lr)

# Generate plot
fig, axes = utils.pgf_generator(nrows=1, ncols=2, figsize=(5.5, 3.5), sharey=True)

plots = [
    ("Probability ordering", xlow_p, xhigh_p),
    ("LR ordering", xlow_lr, xhigh_lr),
]

for ax, (title, low, high) in zip(axes, plots):

    ax.fill_between(mu_grid, low, high, alpha=0.4)
    ax.plot(mu_grid, low, lw=1.0, color="black")
    ax.plot(mu_grid, high, lw=1.0, color="black")

    min_x = np.min(low)
    max_x = np.min(high)
    ax.vlines(0, min_x, max_x, color="black", lw=1.0)
    ax.axhline(-2.5, ls=":", color="red", lw=1.0)

    mask = (low <= -2.5) & (-2.5 <= high)
    mu_over = mu_grid[mask]
    if len(mu_over) > 0:
        ax.plot(mu_over, -2.5 * np.ones(len(mu_over)), color="red", ls="-", lw=1.0)

        starts, ends = asdinterval.find_intervals_indices(mask)
        for idx in starts + ends:
            ax.scatter(mu_grid[idx], -2.5, color="red", s=10)

    ax.set_title(title)
    ax.set_xlabel(r"$\mu$")
    ax.set_xlim(-0.25, 3.0)
    ax.set_ylim(-3.5, 5)
    ax.grid(alpha=0.25)

axes[0].set_ylabel(r"$x$")

plt.tight_layout()
plt.savefig("images/neyman_gauss_limited.pgf", bbox_inches="tight")
plt.close()
