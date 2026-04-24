import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from asd import utils

CL = 0.95
mu_grid = np.linspace(0.0, 3.0, 200)

# observable x
x_grid = np.linspace(-3.5, 5.0, 700)
dx = x_grid[1] - x_grid[0]


# Acceptance rules
def acceptance_p_ordering(mu):
    """
    Rank x by highest density f(x|mu)
    """
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
    """
    Likelihood-ratio ordering with constrained MLE:
        mu_hat(x) = max(0, x)
    Rank by:
        f(x|mu) / f(x|mu_hat)
    """
    num = norm.pdf(x_grid, loc=mu, scale=1.0)

    mu_hat = np.maximum(0.0, x_grid)
    den = norm.pdf(x_grid, loc=mu_hat, scale=1.0)

    R = np.divide(num, den, out=np.zeros_like(num), where=(den > 0))

    order = np.argsort(R)[::-1]

    total = 0.0
    acc = set()

    for i in order:
        acc.add(i)
        total += num[i] * dx
        if total >= CL:
            break

    return acc


# Build belt boundaries
def build_belt(acceptance_func):
    x_low = []
    x_high = []

    for mu in mu_grid:
        acc = sorted(list(acceptance_func(mu)))
        x_low.append(x_grid[min(acc)])
        x_high.append(x_grid[max(acc)])

    return np.array(x_low), np.array(x_high)


# Compute belts
xlow_p, xhigh_p = build_belt(acceptance_p_ordering)
xlow_lr, xhigh_lr = build_belt(acceptance_lr)


# Plot
fig, axes = utils.pgf_generator(nrows=1, ncols=2, figsize=(5.5, 3.5), sharey=True)

plots = [
    ("Probability ordering", xlow_p, xhigh_p),
    ("LR ordering", xlow_lr, xhigh_lr),
]

for ax, (title, low, high) in zip(axes, plots):

    ax.fill_between(mu_grid, low, high, alpha=0.4)
    ax.plot(mu_grid, low, lw=1.0, color="black")
    ax.plot(mu_grid, high, lw=1.0, color="black")

    # Vertical black line at mu=0 bounding min and max x
    min_x = np.min(low)
    max_x = np.min(high)
    ax.vlines(0, min_x, max_x, color="black", lw=1.0)
    # Red dotted line at x=-2.5
    ax.axhline(-2.5, ls=":", color="red", lw=1.0)

    # Solid red line where it overlaps the belt
    mask = (low <= -2.5) & (-2.5 <= high)
    mu_over = mu_grid[mask]
    if len(mu_over) > 0:
        ax.plot(mu_over, -2.5 * np.ones(len(mu_over)), color="red", ls="-", lw=1.0)

        # Red points at intersections
        starts = []
        ends = []
        for i in range(1, len(mask)):
            if not mask[i-1] and mask[i]:
                starts.append(i)
            if mask[i-1] and not mask[i]:
                ends.append(i-1)
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