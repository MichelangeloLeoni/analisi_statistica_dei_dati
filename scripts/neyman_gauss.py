import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import norm

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

CL = 0.95
mu_grid = np.linspace(-3.0, 3.0, 400)

# 1.95996... known table value for 95% confidence intervals of a Gaussian with known variance
z = norm.ppf((1 + CL)/2)   

x_low = mu_grid - z
x_high = mu_grid + z

plt.figure(figsize=(5.5,3.5))

plt.fill_between(mu_grid, x_low, x_high, alpha=0.4)
plt.plot(mu_grid, x_low, color="black")
plt.plot(mu_grid, x_high, color="black")

plt.xlabel(r"$\mu$")
plt.ylabel(r"$x$")
plt.title(r"Probability ordering, all $\mu$ allowed")
plt.xlim(-3.0, 3.0)
plt.grid(alpha=0.25)
plt.savefig("images/neyman_gauss.pgf", bbox_inches='tight')
plt.close()