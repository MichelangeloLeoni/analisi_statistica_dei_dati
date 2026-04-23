import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar
from scipy.stats import chi2, poisson
import os

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

# LLR INTERVALS (Wilks)
def calculate_llr_intervals(n_values, cl=0.95):
    critical_value = chi2.ppf(cl, df=1)
    intervals = []

    for n in n_values:

        def f(mu):
            if n == 0:
                return 2 * mu - critical_value
            if mu <= 0:
                return 1e9
            return 2 * (mu - n + n * np.log(n / mu)) - critical_value

        try:
            if n == 0:
                low = 0.0
            else:
                low = root_scalar(f, bracket=[1e-12, n]).root

            upper_guess = max(n + 10*np.sqrt(n + 1), n + 10)
            high = root_scalar(f, bracket=[n, upper_guess]).root

            intervals.append((low, high))

        except ValueError:
            intervals.append((np.nan, np.nan))

    return intervals

# COVERAGE ERROR (LLR)
n_test = np.arange(0, 50)
intervals_cache = calculate_llr_intervals(n_test)

def coverage_error(mu):
    prob_covered = 0.0
    for n, (low, high) in zip(n_test, intervals_cache):
        if low <= mu <= high:
            prob_covered += poisson.pmf(n, mu)
    return 1 - prob_covered


# COMPUTE CURVE
mu_axis = np.linspace(0.1, 16, 1000)
errors = np.array([coverage_error(m) for m in mu_axis])


# PLOT
os.makedirs("images", exist_ok=True)

fig, ax = plt.subplots(figsize=(5.5, 3.5))

ax.plot(mu_axis, errors, lw=1.0, label=r"$1 - \mathcal{C}(\mu)$")

ax.axhline(0.05, ls="--", lw=1.0, label=r"Nominal level $0.05$")

ax.set_xlabel(r"$\mu$")
ax.set_ylabel(r"Coverage error")
ax.set_ylim(0, 0.2)

ax.legend()

plt.savefig("images/llr_poisson_coverage.pgf", bbox_inches="tight")
plt.close()


# LATEX TABLE GENERATION
n_table = np.arange(0, 10)
intervals_table = calculate_llr_intervals(n_table)

def fmt_interval(a, b):
    if np.isnan(a) or np.isnan(b):
        return r"$\text{--}$"
    return rf"${a:.5f} \leq \mu \leq {b:.5f}$"

# Build LaTeX table
table = r"""
\begin{center}
\begin{tabular}{|c|c|}
\hline
$n$ & LLR interval (95\% CL) \\
\hline
"""

for n, (low, high) in zip(n_table, intervals_table):
    table += f"{n} & {fmt_interval(low, high)} \\\\\n"

table += r"""\hline
\end{tabular}
\end{center}
"""

os.makedirs("tables", exist_ok=True)

with open("tables/llr_intervals.tex", "w") as f:
    f.write(table)