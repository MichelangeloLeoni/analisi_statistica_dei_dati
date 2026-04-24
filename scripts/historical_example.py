import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from asd import utils

x = 2.5
sigma_1 = 0.5
sigma_2 = 3*sigma_1
f_1 = 0.001
f_2 = 0.002
f_3 = 0.05
xx = np.linspace(x-5, x+5, 1000)

gaussian_1 = norm.pdf(xx, loc=x, scale=sigma_1)
gaussian_2 = norm.pdf(xx, loc=x, scale=sigma_2)
prob_1 = (1-f_1)*gaussian_1 + f_1*gaussian_2
prob_2 = (1-f_2)*gaussian_1 + f_2*gaussian_2
prob_3 = (1-f_3)*gaussian_1 + f_3*gaussian_2

fig, ax = utils.pgf_generator(figsize=(5.5, 3.5))

ax.plot(xx, gaussian_1, label=r'$\mathcal{N}(x; \mu, \sigma_1)$', lw=1.0, linestyle=':')
ax.plot(xx, gaussian_2, label=r'$\mathcal{N}(x; \mu, 3\sigma_1)$', lw=1.0, linestyle='--')
#ax.plot(xx, prob_1, label=r'$L_1(m)$', color='#2ca02c', lw=1.5)
#ax.plot(xx, prob_2, label=r'$L_2(m)$', color='#d62728', lw=1.5)
ax.plot(xx, prob_3, label=r'$p(x; \mu, \sigma_1, f=0.05)$', lw=1.0)

ax.set_xticks([x])
ax.set_xticklabels([r'$\mu$'])
ax.set_yticks([0,1])
ax.set_yticklabels([0,1])   

ax.legend(loc='upper right', fontsize='small')
ax.grid(True, linestyle=':', alpha=0.3)

plt.savefig("images/historical_example.pgf", bbox_inches='tight')
plt.close()