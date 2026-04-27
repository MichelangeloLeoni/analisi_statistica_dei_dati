'''
Script that generate the plot of the likelihood-ratio ordering for a gaussian
distribution with mean mu and unit variance, to be put on the notes.
'''
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from asd import utils, asdmath

# Define parameters
CL = 0.95
MU = 0.5
TRASL = 0.5

x = np.linspace(-4, 5, 2000)
dx = x[1] - x[0]

pdf = norm.pdf(x, loc=MU, scale=1)

mu_hat = np.maximum(0, x)

den = norm.pdf(x, loc=mu_hat, scale=1)

r = pdf / den

order = np.argsort(r)[::-1]

cum = 0
accepted = np.zeros_like(x, dtype=bool)

for i in order:
    accepted[i] = True
    cum += pdf[i] * dx
    if cum >= CL:
        c = r[i]
        break

mask = r >= c

starts, ends = asdmath.find_intervals(mask)

# Generate plot
fig, ax1 = utils.pgf_generator(figsize=(5.5,3.5))

ax1.plot(x, pdf, lw=2, label=r"$\mathcal{N}(x;\mu)$")
ax1.fill_between(x, 0, pdf, where=mask, alpha=0.35)

ax1.set_xlabel("x")
ax1.set_xlim(x[0], x[-1])
ax1.set_ylabel("pdf")
ax1.set_ylim(0, max(pdf)*1.2)

ax2 = ax1.twinx()
ax2.plot(x, r, lw=2, ls="--", label=r"$LR(x)$")
ax2.axhline(c, ls=":", color="black", lw=1.0, label="Threshold")

for idx in starts + ends:
    x_inter = x[idx]
    ax2.vlines(x_inter, -TRASL, c, ls=":", color="black", lw=1.0)

ax2.set_ylabel("LR ratio")
ax2.set_ylim(-TRASL, max(r)*1.1)
ax1.set_title(r"Likelihood-ratio ordering for $\mu=0.5$")
ax1.grid(alpha=0.25)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

plt.savefig("images/lr_ordering.pgf", bbox_inches='tight')
plt.close()
