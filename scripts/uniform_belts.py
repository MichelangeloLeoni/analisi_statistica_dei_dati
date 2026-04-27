'''
Script that builds the confidence belts for a uniform distribution
with unknown upper bound.
'''
import numpy as np
import matplotlib.pyplot as plt
from asd import utils
from asd.interval_estimation import interval as asdinterval

# Define parameters
CL = 0.9
X0 = 1
LO_UPPER = X0 / CL
LO_LR = X0
HI_LR = X0 / (1 - CL)

m_grid = np.linspace(0.0, 12, 500)
x_grid = np.linspace(0, 6, 500)

def upper_acceptance(m, x ,cl=CL):
    '''Upper ordering: accept x in [0, cl*m]'''

    lower = 0
    upper = cl * m

    return np.where((x >= lower) & (x <= upper))[0]

def lr_acceptance(m, x, cl=CL):
    '''LR/Central ordering: accept x in [m*(1-cl), m]'''

    lower = m * (1-cl)
    upper = m

    return np.where((x >= lower) & (x <= upper))[0]

def build_belt(acceptance_func, mu_grid, x, cl=CL):
    '''Build the confidence belt for a given acceptance function.'''

    x_low = []
    x_high = []

    for m in mu_grid:
        acc = sorted(list(acceptance_func(m, x, cl=cl)))
        x_low.append(x_grid[min(acc)])
        x_high.append(x_grid[max(acc)])

    return np.array(x_low), np.array(x_high)

xlow_upper, xhigh_upper = build_belt(upper_acceptance, m_grid, x_grid)
xlow_lr, xhigh_lr = build_belt(lr_acceptance, m_grid, x_grid)

# Generate table
def fmt(a, b):
    '''Format the confidence interval as a LaTeX string.'''

    return rf"${a:.2f} \leq m \leq {b:.2f}$"

utils.table_generator(
    n_columns=2,
    labels=("Method", r"90\% confidence interval"),
    content=(["Lower bound", "LR bound"], [rf"$ {LO_UPPER:.2f} \leq m$", fmt(LO_LR, HI_LR)]),
    output_file_name="uniform_belts.tex"
    )

# Generate plot
fig, axes = utils.pgf_generator(nrows=1, ncols=2, figsize=(5.5, 3.5), sharey=True)

plots = [
    ("Upper ordering", xlow_upper, xhigh_upper),
    ("LR ordering", xlow_lr, xhigh_lr),
]

for plot_idx, (ax, (title, low, high)) in enumerate(zip(axes, plots)):

    ax.fill_between(m_grid, low, high, alpha=0.4)
    ax.plot(m_grid, low, lw=1.0, color="black")
    ax.plot(m_grid, high, lw=1.0, color="black")

    ax.axhline(X0, ls=":", color="red", lw=1.0)

    mask = (low <= X0) & (X0 <= high)
    m_over = m_grid[mask]
    if len(m_over) > 0:
        if plot_idx == 0:
            x0_max = max(x_grid) / 2
            m_over_cut = m_over[m_over <= x0_max]
            if len(m_over_cut) > 0:
                ax.plot(m_over_cut, X0 * np.ones(len(m_over_cut)), color="red", ls="-", lw=1.0)
                ax.annotate("", xy=(m_over_cut[-1] + 0.3, X0), xytext=(m_over_cut[-1], X0),
                           arrowprops={"arrowstyle": "->", "color": "red", "lw": 1.0})
        else:
            ax.plot(m_over, X0 * np.ones(len(m_over)), color="red", ls="-", lw=1.0)

        starts, ends = asdinterval.find_intervals_indices(mask)

        for i in starts + ends:
            if plot_idx == 0:
                if m_grid[i] <= max(x_grid) / 2:
                    ax.scatter(m_grid[i], X0, color="red", s=10)
            else:
                ax.scatter(m_grid[i], X0, color="red", s=10)

    ax.set_title(title)
    ax.set_xlabel(r"$m$")
    ax.set_xlim(0, max(m_grid))
    ax.set_ylim(-0.5, max(x_grid))
    ax.grid(alpha=0.25)

axes[0].set_ylabel(r"$x$")

plt.tight_layout()
plt.savefig("images/uniform_belts.pgf", bbox_inches="tight")
plt.close()
