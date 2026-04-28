'''
Script that builds the Neyman confidence belt for a Gaussian
with mean allowed to be any real number.
'''
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from asd import utils
from asd.interval_estimation import interval as asdinterval

# Define parameters
CL = 0.95

mu_grid = np.linspace(-3.0, 3.0, 400)
xx = np.linspace(-8.0, 8.0, 2000)

def gauss(x, mu):
    '''Wrapper for the gauss pdf'''
    return norm.pdf(x, loc=mu, scale=1)

estimator = asdinterval.IntervalEstimator(
    prob_func=gauss,
    cl=CL,
    mu_grid=mu_grid,
    x_range=xx,
    discrete=False
)

mask_list = estimator.neyman.build_belt(method="pdf", ordering_type="p")
x_low, x_high = estimator.masks_to_bounds(mask_list)

# Generate plot
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
