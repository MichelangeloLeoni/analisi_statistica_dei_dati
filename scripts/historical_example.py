'''Script that generates a plot for a contaminated gaussian pdf'''
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from asd import utils

# Define parameters
MU = 2.5
SIGMA_1= 0.5
SIGMA_2 = 3*SIGMA_1
F = 0.05
xx = np.linspace(MU-5, MU+5, 1000)

gaussian_1 = norm.pdf(xx, loc=MU, scale=SIGMA_1)
gaussian_2 = norm.pdf(xx, loc=MU, scale=SIGMA_2)
prob = (1-F)*gaussian_1 + F*gaussian_2

# Generate plot
fig, ax = utils.pgf_generator(figsize=(5.5, 3.5))

ax.plot(xx, gaussian_1, label=r'$\mathcal{N}(x; \mu, \sigma_1)$', lw=1.0, linestyle=':')
ax.plot(xx, gaussian_2, label=r'$\mathcal{N}(x; \mu, 3\sigma_1)$', lw=1.0, linestyle='--')
ax.plot(xx, prob, label=r'$p(x; \mu, \sigma_1, f=0.05)$', lw=1.0)

ax.set_xticks([MU])
ax.set_xticklabels([r'$\mu$'])
ax.set_yticks([0,1])
ax.set_yticklabels([0,1])

ax.legend(loc='upper right', fontsize='small')
ax.grid(True, linestyle=':', alpha=0.3)

plt.savefig("images/historical_example.pgf", bbox_inches='tight')
plt.close()
