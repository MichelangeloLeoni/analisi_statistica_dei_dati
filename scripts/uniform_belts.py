import numpy as np
import matplotlib.pyplot as plt
from asd import utils

CL = 0.9
m_grid = np.linspace(0.0, 12, 500)

# observable x
x_grid = np.linspace(0, 6, 500)

def upper_acceptance(m):
    # Upper ordering: accept x in [0, CL*m]
    lower = 0
    upper = CL * m
    return np.where((x_grid >= lower) & (x_grid <= upper))[0]

def lr_acceptance(m):
    # LR/Central ordering: accept x in [m*(1-CL), m]
    lower = m * (1-CL)
    upper = m 
    return np.where((x_grid >= lower) & (x_grid <= upper))[0]


def build_belt(acceptance_func):
    x_low = []
    x_high = []

    for m in m_grid:
        acc = sorted(list(acceptance_func(m)))
        x_low.append(x_grid[min(acc)])
        x_high.append(x_grid[max(acc)])

    return np.array(x_low), np.array(x_high)

# Compute belts
xlow_upper, xhigh_upper = build_belt(upper_acceptance)
xlow_lr, xhigh_lr = build_belt(lr_acceptance)

# Compute intervals at x0=1
x0 = 1
lo_upper = x0 / CL
lo_lr = x0
hi_lr = x0 / (1 - CL)

# LaTeX table
def fmt(a, b):
    return rf"${a:.2f} \leq m \leq {b:.2f}$" # format the interval in LaTeX math mode

utils.table_generator(
    n_columns=2,
    labels=("Method", r"90\% confidence interval"),
    content=(["Lower bound", "LR bound"], [rf"$ {lo_upper:.2f} \leq m$", fmt(lo_lr, hi_lr)]),
    output_file_name="uniform_belts.tex"
    )

# Plot
fig, axes = utils.pgf_generator(nrows=1, ncols=2, figsize=(5.5, 3.5), sharey=True)

plots = [
    ("Upper ordering", xlow_upper, xhigh_upper),
    ("LR ordering", xlow_lr, xhigh_lr),
]

for plot_idx, (ax, (title, low, high)) in enumerate(zip(axes, plots)):

    ax.fill_between(m_grid, low, high, alpha=0.4)
    ax.plot(m_grid, low, lw=1.0, color="black")
    ax.plot(m_grid, high, lw=1.0, color="black")

    # Red dotted line at x=x0
    x0 = 1
    ax.axhline(x0, ls=":", color="red", lw=1.0)

    # Solid red line where it overlaps the belt
    mask = (low <= x0) & (x0 <= high)
    m_over = m_grid[mask]
    if len(m_over) > 0:
        if plot_idx == 0:  # Left plot: upper ordering - limit to half of max(x_grid)
            x0_max = max(x_grid) / 2
            m_over_cut = m_over[m_over <= x0_max]
            if len(m_over_cut) > 0:
                ax.plot(m_over_cut, x0 * np.ones(len(m_over_cut)), color="red", ls="-", lw=1.0)
                # Add right arrow at the end
                ax.annotate("", xy=(m_over_cut[-1] + 0.3, x0), xytext=(m_over_cut[-1], x0),
                           arrowprops=dict(arrowstyle='->', color='red', lw=1.0))
        else:  # Right plot: leave as is
            ax.plot(m_over, x0 * np.ones(len(m_over)), color="red", ls="-", lw=1.0)

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
        
        for i in starts + ends:
            if plot_idx == 0:
                if m_grid[i] <= max(x_grid) / 2:
                    ax.scatter(m_grid[i], x0, color="red", s=10)
            else:
                ax.scatter(m_grid[i], x0, color="red", s=10)
    ax.set_title(title)
    ax.set_xlabel(r"$m$")
    ax.set_xlim(0, max(m_grid))
    ax.set_ylim(-0.5, max(x_grid))
    ax.grid(alpha=0.25)

axes[0].set_ylabel(r"$x$")

plt.tight_layout()
plt.savefig("images/uniform_belts.pgf", bbox_inches="tight")
plt.close()