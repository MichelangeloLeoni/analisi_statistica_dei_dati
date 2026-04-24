import numpy as np
import matplotlib.pyplot as plt
from scipy.special import comb
from asd import utils

k1 = 1
k2 = 0
n = 1
k3 = 25
xx = np.linspace(0, 1, 1000)

def binomial_pmf(k, n, p):
    return comb(n, k) * (p ** k) * ((1 - p) ** (n - k))

fig, ax = utils.pgf_generator(figsize=(5.5, 3.5))

ax.plot(xx, binomial_pmf(k1, n, xx), label=r'$L_{n=1,k=1}$', color='#1f77b4', lw=1.5)
ax.plot(xx, binomial_pmf(k2, n, xx), label=r'$L_{n=1,k=0}$', color='#ff7f0e', lw=1.5)
ax.plot(xx, binomial_pmf(k3, 50*n, xx), label=r'$L_{n=50,k=25}$', color='#2ca02c', lw=1.5)

ax.set_xticks([0,0.5,1])
ax.set_xticklabels([0,0.5,1])
ax.set_yticks([0,1])
ax.set_yticklabels([0,1])
ax.set_xlabel(r'$p$', fontsize=10)
ax.set_ylabel(r'$L(p)$', fontsize=10)

ax.legend(loc='upper center', fontsize='small')
ax.grid(True, linestyle=':', alpha=0.3)

plt.savefig("images/binomial_likelihood.pgf", bbox_inches='tight')
plt.close()