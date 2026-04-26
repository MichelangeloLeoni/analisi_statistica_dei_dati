'''
Script that builds the Neyman confidence belt for a Gaussian with non-negative mean, 
using both probability ordering and likelihood ratio ordering.
'''
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from asd import utils

# Define parameters
CL = 0.95

mu_grid = np.linspace(0.0, 3.0, 200)
x_grid = np.linspace(-3.5, 5.0, 700)
dx = x_grid[1] - x_grid[0]

def acceptance_p_ordering(mu):
    '''
    Rank x by probability density f(x|mu).
    '''

    dens = norm.pdf(x_grid, loc=mu, scale=1.0)

    order = np.argsort(dens)[::-1]

    total = 0.0
    acc = set()

    for i in order:
        acc.add(i)
        total += dens[i] * dx
        if total >= CL:
            break

    return acc

def acceptance_lr(mu):
    '''
    Rank x by likelihood ratio f(x|mu) / f(x|mu_hat),
    where mu_hat is the MLE of mu given x.
    '''

    num = norm.pdf(x_grid, loc=mu, scale=1.0)

    mu_hat = np.maximum(0.0, x_grid)
    den = norm.pdf(x_grid, loc=mu_hat, scale=1.0)

    r = np.divide(num, den, out=np.zeros_like(num), where=den > 0)

    order = np.argsort(r)[::-1]

    total = 0.0
    acc = set()

    for i in order:
        acc.add(i)
        total += num[i] * dx
        if total >= CL:
            break

    return acc

def build_belt(acceptance_func):
    '''Build the confidence belt for a given acceptance function.'''

    x_low = []
    x_high = []

    for mu in mu_grid:
        acc = sorted(list(acceptance_func(mu)))
        x_low.append(x_grid[min(acc)])
        x_high.append(x_grid[max(acc)])

    return np.array(x_low), np.array(x_high)

xlow_p, xhigh_p = build_belt(acceptance_p_ordering)
xlow_lr, xhigh_lr = build_belt(acceptance_lr)

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

        starts = []
        ends = []
        for ind in range(1, len(mask)):
            if not mask[ind-1] and mask[ind]:
                starts.append(ind)
            if mask[ind-1] and not mask[ind]:
                ends.append(ind-1)
        if mask[0]:
            starts.insert(0, 0)
        if mask[-1]:
            ends.append(len(mask)-1)

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
