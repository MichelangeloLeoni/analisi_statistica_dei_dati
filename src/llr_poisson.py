import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar
from scipy.stats import chi2, poisson
import os

# ------------------ PLOT CONFIG ------------------
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

# ------------------ LLR INTERVALS (Wilks) ------------------
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

# ------------------ FELDMAN-COUSINS ------------------
def calculate_lr_interval_mu(n_obs, mu_grid, cl=0.95, n_max=100):
    accepted_mu = []
    n_values = np.arange(0, n_max)

    for mu in mu_grid:
        pdf = poisson.pmf(n_values, mu)
        mu_hat = n_values
        den = poisson.pmf(n_values, mu_hat)
        R = pdf / den

        order = np.argsort(R)[::-1]

        cum = 0
        for i in order:
            cum += pdf[i]
            if cum >= cl:
                c = R[i]
                break

        mask = R >= c

        if n_obs < len(mask) and mask[n_obs]:
            accepted_mu.append(mu)

    if len(accepted_mu) == 0:
        return (np.nan, np.nan)

    return (min(accepted_mu), max(accepted_mu))

# ------------------ ROBUST ROOT BRACKETING ------------------
def find_root_bracketed(f, a, b, expand_factor=2, max_iter=50):
    fa, fb = f(a), f(b)

    for _ in range(max_iter):
        if np.isnan(fa) or np.isnan(fb):
            return None

        if fa * fb < 0:
            return (a, b)

        a /= expand_factor
        b *= expand_factor
        fa, fb = f(a), f(b)

    return None

# ------------------ CENTRAL INTERVAL ------------------
def calculate_central_interval_mu(n_obs, cl=0.95):
    """
    Calcola l'intervallo di confidenza centrale (Neyman) per una media di Poisson.
    Utilizza la relazione tra Poisson e la distribuzione Gamma/Chi-quadro.
    """
    alpha = 1 - cl
    
    try:
        # LIMITE INFERIORE (Lower Limit)
        # Risolve P(N >= n_obs | mu_low) = alpha/2
        # Per n_obs = 0, il limite inferiore è strettamente 0.
        if n_obs == 0:
            low = 0.0
        else:
            # Relazione esatta con il quantile Chi-quadro: chi2.ppf(alpha/2, 2*n_obs) / 2
            def f_low(mu):
                # P(X >= n_obs) è 1 - P(X <= n_obs - 1)
                return (1 - poisson.cdf(n_obs - 1, mu)) - alpha/2

            # Bracket più sicuro: mu_low è sempre < n_obs (tranne casi degeneri)
            low = root_scalar(f_low, bracket=[1e-12, n_obs]).root

        # LIMITE SUPERIORE (Upper Limit)
        # Risolve P(N <= n_obs | mu_high) = alpha/2 (ovvero CDF = alpha/2)
        # O equivalentemente: P(X <= n_obs | mu_high) = 1 - alpha/2 non è corretto per il limite superiore centrale.
        # La definizione corretta è: P(N <= n_obs | mu_high) = alpha/2
        def f_high(mu):
            return poisson.cdf(n_obs, mu) - alpha/2

        # Bracket dinamico per l'upper bound
        # Il limite superiore per Poisson è circa n + 2*sqrt(n) + 2. 
        # Usiamo un margine molto ampio per il bracketing.
        high_guess = n_obs + 10 * np.sqrt(n_obs + 1) + 20
        high = root_scalar(f_high, bracket=[n_obs, high_guess]).root

        return (low, high)

    except (ValueError, RuntimeError):
        return (np.nan, np.nan)

# ------------------ COVERAGE ERROR (LLR) ------------------
n_test = np.arange(0, 50)
intervals_cache = calculate_llr_intervals(n_test)

def coverage_error(mu):
    prob_covered = 0.0
    for n, (low, high) in zip(n_test, intervals_cache):
        if low <= mu <= high:
            prob_covered += poisson.pmf(n, mu)
    return 1 - prob_covered

# ------------------ COMPUTE CURVE ------------------
mu_axis = np.linspace(0.0001, 20, 2000)
errors = np.array([coverage_error(m) for m in mu_axis])

# ------------------ PLOT ------------------
os.makedirs("images", exist_ok=True)

fig, ax = plt.subplots(figsize=(5.5, 3.5))
ax.plot(mu_axis, errors, lw=1.0, label=r"$1 - \mathcal{C}(\mu)$")
ax.axhline(0.05, ls="--", lw=1.0, label=r"Nominal level $0.05$")

ax.set_xlim(-0.2, 16)
ax.set_xlabel(r"$\mu$")
ax.set_ylabel(r"Coverage error")
ax.set_ylim(0, 0.2)
ax.legend()

plt.savefig("images/llr_poisson_coverage.pgf", bbox_inches="tight")
plt.close()

# ------------------ LATEX TABLE ------------------
n_table = np.arange(0, 10)

intervals_table = calculate_llr_intervals(n_table)

lr_intervals = [
    calculate_lr_interval_mu(n, mu_axis, cl=0.95)
    for n in n_table
]

central_intervals = [
    calculate_central_interval_mu(n, cl=0.95)
    for n in n_table
]

def fmt_interval(a, b):
    if np.isnan(a) or np.isnan(b):
        return r"$\text{--}$"
    return rf"${a:.3f} \leq \mu \leq {b:.3f}$"

table = r"""
\begin{center}
\begin{tabular}{|c|c|c|c|}
\hline
$n$ & Wilks & Feldman-Cousins & Central interval \\
\hline
"""

for n, (low, high) in zip(n_table, intervals_table):
    table += (
        f"{n} & "
        f"{fmt_interval(low, high)} & "
        f"{fmt_interval(lr_intervals[n][0], lr_intervals[n][1])} & "
        f"{fmt_interval(central_intervals[n][0], central_intervals[n][1])} \\\\\n"
    )

table += r"""\hline
\end{tabular}
\end{center}
"""

os.makedirs("tables", exist_ok=True)

with open("tables/llr_intervals.tex", "w") as f:
    f.write(table)