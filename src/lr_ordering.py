import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import norm

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

# START SNIPPET
CL = 0.95
mu = 0.5

x = np.linspace(-4, 5, 2000)
dx = x[1] - x[0]

# PDF under tested mu
pdf = norm.pdf(x, loc=mu, scale=1)

# constrained MLE: mu_hat = max(0,x)
mu_hat = np.maximum(0, x)

# denominator = best-fit likelihood
den = norm.pdf(x, loc=mu_hat, scale=1)

# LR ratio
R = pdf / den

# Find threshold c such that accepted region
# has probability CL
order = np.argsort(R)[::-1]

cum = 0
accepted = np.zeros_like(x, dtype=bool)

for i in order:
    accepted[i] = True
    cum += pdf[i] * dx
    if cum >= CL:
        c = R[i]
        break

# accepted region
mask = R >= c

# Find intersection points
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
# END SNIPPET

# Plot
fig, ax1 = plt.subplots(figsize=(5.5,3.5))

# PDF
ax1.plot(x, pdf, lw=2, label=r"$\mathcal{N}(x|\mu)$")
ax1.fill_between(x, 0, pdf, where=mask, alpha=0.35)

ax1.set_xlabel("x")
ax1.set_xlim(x[0], x[-1])
ax1.set_ylabel("pdf")
ax1.set_ylim(0, max(pdf)*1.2)

# second axis for LR
ax2 = ax1.twinx()
trasl = 0.5 # shift LR up for better visibility
ax2.plot(x, R, lw=2, ls="--", label=r"$LR(x)$")
ax2.axhline(c, ls=":", color="black", lw=1.0, label="Threshold")

# Vertical dotted lines at intersections
for idx in starts + ends:
    x_inter = x[idx]
    ax2.vlines(x_inter, -trasl, c, ls=":", color="black", lw=1.0)

ax2.set_ylabel("LR ratio")
ax2.set_ylim(-trasl, max(R)*1.1)
# cosmetics
ax1.set_title(r"Likelihood-ratio ordering for $\mu=0.5$")
ax1.grid(alpha=0.25)

# combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
plt.savefig("images/lr_ordering.pgf", bbox_inches='tight')
plt.close()

def extract_snippet(filename, start_tag, end_tag):
    with open(filename, "r") as f:
        lines = f.readlines()

    inside = False
    snippet = []

    for line in lines:
        if start_tag in line:
            inside = True
            continue
        if end_tag in line:
            break
        if inside:
            snippet.append(line)

    return "".join(snippet)


snippet_code = extract_snippet(
    __file__,
    "START SNIPPET",
    "END SNIPPET"
)

latex_code = r"""
\begin{minted}[fontsize=\small, linenos, breaklines]{python}
""" + snippet_code + r"""
\end{minted}
"""

with open("code/code_lr_ordering.tex", "w") as f:
    f.write(latex_code)