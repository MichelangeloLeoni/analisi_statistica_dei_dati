import numpy as np
import matplotlib.pyplot as plt
from asd import utils

mu = 3
sigma = 1.2
k = 1.5
y_val = k * sigma
xx = np.linspace(mu - 4, mu + 4, 1000)

def indicator_function(x, mu, threshold):
    return np.where(np.abs(x - mu) >= threshold, 1.0, 0.0)

fig, ax = utils.pgf_generator(figsize=(5.5, 3.5))

ax.hlines(y_val, xx.min(), xx.max(), linestyles=":", color='gray', alpha=0.5, label=r'$k\sigma$')

ax.plot(xx, np.abs(xx - mu), label=r'$|x - \mu|$', color='#1f77b4', lw=1.5, linestyle='--')

y_ind = indicator_function(xx, mu, y_val)
ax.plot(xx, y_ind, label=r'$ \mathscr{F} (|x - \mu| \geq k\sigma)$', color='#d62728', linewidth=2)

ax.set_xticks([mu, mu - y_val, mu + y_val])
ax.set_xticklabels([r'$\mu$', r'$\mu-k\sigma$', r'$\mu+k\sigma$'])
ax.set_yticks([0, 1, y_val])
ax.set_yticklabels(['0', '1', r'$k\sigma$'])

ax.legend(loc='upper right', fontsize='small')
ax.grid(True, linestyle=':', alpha=0.3)

plt.savefig("images/chebyshev_theorem.pgf", bbox_inches='tight')
plt.close()