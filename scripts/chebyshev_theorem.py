'''Script that generate a plot to illustrate part of the Chebyshev's theorem dimonstration.'''
import numpy as np
import matplotlib.pyplot as plt
from asd import utils

# Define parameters
MU = 3
SI = 1.2
K = 1.5
Y_VALS = K * SI

def indicator_function(x, mu, threshold):
    '''Implement the indicator function'''

    return np.where(np.abs(x - mu) >= threshold, 1.0, 0.0)

xx = np.linspace(MU - 4, MU + 4, 1000)
y_ind = indicator_function(xx, MU, Y_VALS)

# Generate plot
fig, ax = utils.pgf_generator(figsize=(5.5, 3.5))

ax.hlines(Y_VALS, xx.min(), xx.max(), linestyles=":", color='gray', alpha=0.5, label=r'$k\sigma$')
ax.plot(xx, np.abs(xx - MU), label=r'$|x - \mu|$', color='#1f77b4', lw=1.5, linestyle='--')
ax.plot(xx, y_ind, label=r'$ \mathscr{F} (|x - \mu| \geq k\sigma)$', color='#d62728', linewidth=2)

ax.set_xticks([MU, MU - Y_VALS, MU + Y_VALS])
ax.set_xticklabels([r'$\mu$', r'$\mu-k\sigma$', r'$\mu+k\sigma$'])
ax.set_yticks([0, 1, Y_VALS])
ax.set_yticklabels(['0', '1', r'$k\sigma$'])

ax.legend(loc='upper right', fontsize='small')
ax.grid(True, linestyle=':', alpha=0.3)

plt.savefig("images/chebyshev_theorem.pgf", bbox_inches='tight')
plt.close()
