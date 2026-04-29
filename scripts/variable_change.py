'''
Script that generates a plot to show why sometimes
you have to sum when performing variable change on pdfs.
Example: y = x^2
'''
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from asd import utils

# Define parameters
X0 = 0.75
Y0 = X0**2
EPS = 1e-10

x = np.linspace(-4, 4, 1000)
y = np.linspace(0.01, 16, 1000)  # Start from small positive to avoid division by zero

# Original pdf
f_x = norm.pdf(x)

# Transformation y = x^2
# For each y, there are two x values: +sqrt(y) and -sqrt(y)
sqrt_y = np.sqrt(y)
sqrt_y_safe = np.maximum(sqrt_y, EPS)  # More explicit than np.where

# f_Y(y) = [f_X(sqrt(y)) + f_X(-sqrt(y))] / (2*sqrt(y))
f_y = (norm.pdf(sqrt_y_safe) + norm.pdf(-sqrt_y_safe)) / (2 * sqrt_y_safe)

# Calculate PDF values at the highlighted points
f_X0 = norm.pdf(X0)
f_neg_X0 = norm.pdf(-X0)
f_Y0 = (norm.pdf(X0) + norm.pdf(-X0)) / (2 * X0)  # f_Y(Y0)

# Generate plot
fig, axs = utils.pgf_generator(nrows=1, ncols=2, figsize=(5.5, 3.5))

# --- LEFT: X space ---
ax = axs[0]
ax.plot(x, f_x, linewidth=1, color='blue')

# Highlight the two regions that map to the same y
# Points near X0 and -X0
mask_pos = (x > X0 - 0.15) & (x < X0 + 0.15)
mask_neg = (x > -X0 - 0.15) & (x < -X0 + 0.15)

ax.fill_between(x[mask_pos], f_x[mask_pos], alpha=0.4, color='blue', hatch='///')
ax.fill_between(x[mask_neg], f_x[mask_neg], alpha=0.4, color='blue', hatch='///')

ax.set_xlabel('$x$', fontsize=12)
ax.set_ylabel('$p_x(x)$', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_xlim(-4, 4)
ax.set_ylim(0, max(f_x)+0.025)
ax.set_xticks([])
ax.set_yticks([])

# --- RIGHT: Y space ---
ax = axs[1]
ax.plot(y, f_y, linewidth=1, color='green')

# Highlight the region around Y0
mask_y = (y > Y0 - 0.2) & (y < Y0 + 0.2)
ax.fill_between(y[mask_y], f_y[mask_y], alpha=0.4, color='green', hatch='xxx')

ax.set_xlabel('$y$', fontsize=12)
ax.set_ylabel('$p_y(y)$', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 8)
ax.set_ylim(0, max(f_y)-2)
ax.set_xticks([])
ax.set_yticks([])

plt.savefig("images/variable_change.pgf", bbox_inches='tight')
plt.close()
