import numpy as np
import matplotlib.pyplot as plt
from scipy.special import comb
from asd import utils

x0 = 1
xx = np.linspace(0, 10, 1000)

likelihood = np.zeros_like(xx)
mask = (xx >= x0)
likelihood[mask] = 1 / xx[mask]

fig, ax = utils.pgf_generator(figsize=(5.5, 3.5))

ax.plot(xx, likelihood, label=r'$L_{x_0}(m)$', color='#1f77b4', lw=1.5)

ax.set_xticks([x0])
ax.set_xticklabels([r'$x_0$'])
ax.set_yticks([0,1])
ax.set_yticklabels([0,1])
ax.set_xlabel(r'$m$', fontsize=10)
ax.set_ylabel(r'$L(m)$', fontsize=10)

ax.legend(loc='upper right', fontsize='small')
ax.grid(True, linestyle=':', alpha=0.3)

plt.savefig("images/uniform_likelihood.pgf", bbox_inches='tight')
plt.close()