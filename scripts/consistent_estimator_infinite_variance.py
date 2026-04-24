'''
Script that generate a plot of a particular pmf with distant peaks to be used in a counterexample
'''
import numpy as np
import matplotlib.pyplot as plt
from asd import utils

# Define parameters
N_VALUES = [2, 5, 10]
MARKERS = ['o', 's', '^']

# Generate plot
fig, ax = utils.pgf_generator(figsize=(5.5, 3.8))

for i, N in enumerate(N_VALUES):
    x = np.array([-N**2, 0, N**2])
    probs = np.array([1/(2*N), 1 - (1/N), 1/(2*N)])

    markerline, stemlines, baseline = ax.stem(
        x, probs,
        markerfmt=MARKERS[i],
        label=f'$N = {N}$',
        basefmt=" ",
    )

    plt.setp(markerline, 'markersize', 4)
    plt.setp(stemlines, 'linewidth', 1.2, 'alpha', 0.7)

ax.axhline(0, color='black', linewidth=0.8, alpha=0.3)
ax.set_xlabel(r'$\hat{\theta}_N$')
ax.set_ylabel(r'$P(\hat{\theta}_N = x)$')
ax.set_ylim(-0.05, 1.05)

ax.set_xscale('symlog', linthresh=1.0)

ax.grid(True, which="both", linestyle=':', alpha=0.4)
ax.legend(loc='upper right', fontsize='small')

plt.savefig("images/consistency_counterexample.pgf", bbox_inches='tight')
plt.close()
