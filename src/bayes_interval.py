import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math

matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    "text.usetex": True,
    "pgf.rcfonts": False,
    "font.family": "serif", 
    "font.size": 10,  
    "pgf.preamble": r"""
        \usepackage{amsmath}
        \usepackage{mathrsfs}
    """
})


# Grid for mu
m = np.linspace(0, 10, 1000)

# Prior: Uniform(0,10)
prior = 0.1

# Posterior for observed k
def posterior(m, k):
    unnorm = prior * np.exp(-m) * m**k / math.factorial(k)
    norm = np.trapezoid(unnorm, m)   # updated integration
    return unnorm / norm


def posterior_interval(m, post, alpha=0.10):
    # local grid widths for integration weights
    w = np.empty_like(m)
    w[1:-1] = 0.5 * (m[2:] - m[:-2])
    w[0] = 0.5 * (m[1] - m[0])
    w[-1] = 0.5 * (m[-1] - m[-2])

    # sort posterior heights descending
    idx = np.argsort(post)[::-1]

    # cumulative posterior mass in that ordering
    mass = np.cumsum(post[idx] * w[idx])

    # keep enough points to reach target probability
    keep = idx[mass <= (1 - alpha)]

    # include first point exceeding threshold
    if len(keep) < len(idx):
        keep = np.append(keep, idx[len(keep)])

    keep = np.sort(keep)

    lower = m[keep[0]]
    upper = m[keep[-1]]

    return lower, upper

# Lower limit 90% credible interval
def lower_limit(m, post, alpha=0.10):
    dx = m[1] - m[0]
    cdf = np.cumsum(post) * dx
    cdf /= cdf[-1]

    return np.interp(alpha, cdf, m), m[-1]


# Upper limit 90% credible interval
def upper_limit(m, post, alpha=0.10):
    dx = m[1] - m[0]
    cdf = np.cumsum(post) * dx
    cdf /= cdf[-1]

    return m[0], np.interp(1 - alpha, cdf, m)

# Values of k to plot
k_values = [2, 5, 8]


# Plot
fig, ax = plt.subplots(figsize=(5.5, 3.5))

for k in k_values:
    post = posterior(m, k)

    # Plot posterior curve
    ax.plot(m, post, lw=2)

    # Peak location for label
    peak_idx = np.argmax(post)
    peak_m = m[peak_idx]
    peak_y = post[peak_idx]

    # Put label near peak
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

### Different intervals:

# Ordering methods for interval calculation
ordering = ["Posterior", "Lower limit", "Upper limit"]

k = 5  # fixed observed count

post = posterior(m, k)

# Calculate the intervals
lo_hpd, hi_hpd = posterior_interval(m, post, alpha=0.10)
lo_low, hi_low = lower_limit(m, post, alpha=0.10)
lo_high, hi_high = upper_limit(m, post, alpha=0.10)

# LaTeX table
def fmt(a, b):
    return rf"${a:.2f} < \mu < {b:.2f}$" # format the interval in LaTeX math mode

table = rf"""
\begin{{center}}
\begin{{tabular}}{{l|c}}
\hline
Method & 90\% credible interval \\
\hline
Posterior & {fmt(lo_hpd, hi_hpd)} \\
Lower bound & {fmt(lo_low, hi_low)} \\
Upper bound & {fmt(lo_high, hi_high)} \\
\hline
\end{{tabular}}
\end{{center}}
"""

with open("tables/bayes_interval.tex", "w") as f:
    f.write(table)

# Plot
fig, ax = plt.subplots(1, 3, figsize=(5.5, 3.5), sharey=True)

for i, o in enumerate(ordering):

    # Select interval rule
    if o == "Posterior":
        lo, hi = lo_hpd, hi_hpd
    elif o == "Lower limit":
        lo, hi = lo_low, hi_low
    elif o == "Upper limit":
        lo, hi = lo_high, hi_high

    # Plot posterior curve
    ax[i].plot(m, post, lw=2)

    # Shade interval
    mask = (m >= lo) & (m <= hi)
    ax[i].fill_between(m[mask], post[mask], alpha=0.25)

    # Peak location
    peak_idx = np.argmax(post)
    peak_m = m[peak_idx]
    peak_y = post[peak_idx]

    # Title
    ax[i].set_title(o, fontsize=10)

    # Axes formatting
    ax[i].set_xlabel(r"$\mu$")
    ax[i].grid(True, alpha=0.3)
    ax[i].tick_params(axis='y', left=False, labelleft=False)
# Shared y-label
ax[0].set_ylabel("Posterior density")

plt.savefig("images/bayes_interval.pgf", bbox_inches='tight')
plt.close()