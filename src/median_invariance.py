import numpy as np
import matplotlib
import matplotlib.pyplot as plt

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

x = np.array([1, 2, 3, 4, 5, 6, 7])
exp_x = np.exp(x*0.5)

median_1 = np.median(x)
median_2 = np.median(exp_x)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5.5, 1.5))

ax1.errorbar(x, np.zeros_like(x), fmt=".")
ax1.axvline(median_1, linestyle='--')

ax1.set_title(r'$x$')
ax1.set_yticks([])
ax1.set_xticks([median_1])
ax1.set_xticklabels([r'm'])
ax1.grid(True, linestyle=':', alpha=0.3)

ax2.errorbar(exp_x, np.zeros_like(exp_x), fmt=".")
ax2.axvline(median_2, linestyle='--')

ax2.set_title(r'$\exp(x)$')
ax2.set_yticks([])
ax2.set_xticks([median_2])
ax2.set_xticklabels([r'exp(m)'])
ax2.grid(True, linestyle=':', alpha=0.3)

plt.tight_layout()
plt.savefig("images/median_invariance.pgf", bbox_inches='tight')
plt.close()