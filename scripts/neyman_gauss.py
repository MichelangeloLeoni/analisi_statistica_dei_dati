import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from asd import utils

CL = 0.95
mu_grid = np.linspace(-3.0, 3.0, 400)

# 1.95996... known table value for 95% confidence intervals of a Gaussian with known variance
z = norm.ppf((1 + CL)/2)   

x_low = mu_grid - z
x_high = mu_grid + z

fig, ax = utils.pgf_generator(figsize=(5.5,3.5))

ax.fill_between(mu_grid, x_low, x_high, alpha=0.4)
ax.plot(mu_grid, x_low, color="black")
ax.plot(mu_grid, x_high, color="black")

ax.set_xlabel(r"$\mu$")
ax.set_ylabel(r"$x$")
ax.set_title(r"Probability ordering, all $\mu$ allowed")
ax.set_xlim(-3.0, 3.0)
ax.grid(alpha=0.25)

plt.savefig("images/neyman_gauss.pgf", bbox_inches='tight')
plt.close()