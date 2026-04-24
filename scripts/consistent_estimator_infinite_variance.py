import numpy as np
import matplotlib.pyplot as plt
import os
from asd import utils

if not os.path.exists("images"):
    os.makedirs("images")

N_values = [2, 5, 10]
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

fig, ax = utils.pgf_generator(figsize=(5.5, 3.8))

for i, N in enumerate(N_values):
    x = np.array([-N**2, 0, N**2])
    probs = np.array([1/(2*N), 1 - (1/N), 1/(2*N)])
    
    # Usiamo 'o' come marker standard, il colore lo settiamo dopo
    markerline, stemlines, baseline = ax.stem(
        x, probs, 
        linefmt=colors[i], 
        markerfmt='o', 
        label=f'$N = {N}$',
        basefmt=" "
    )
    
    # Applichiamo il colore esadecimale e le proprietà ai marker e linee
    plt.setp(markerline, 'markerfacecolor', colors[i], 'markeredgecolor', colors[i], 'markersize', 4)
    plt.setp(stemlines, 'linewidth', 1.2, 'alpha', 0.7)

ax.axhline(0, color='black', linewidth=0.8, alpha=0.3)
ax.set_xlabel(r'$\hat{\mu}_N$')
ax.set_ylabel(r'$P(\hat{\mu}_N = x)$')
ax.set_ylim(-0.05, 1.05)

# Scala symlog per gestire N^2
ax.set_xscale('symlog', linthresh=1.0)

ax.grid(True, which="both", linestyle=':', alpha=0.4)
ax.legend(loc='upper right', fontsize='small')

plt.savefig("images/consistency_counterexample.pgf", bbox_inches='tight')
plt.close()