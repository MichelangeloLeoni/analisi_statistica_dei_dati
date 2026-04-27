'''
Mathematical utilities for the Analisi Statistica dei Dati notes.
'''
import numpy as np

def find_intervals_indices(mask):
    '''
    Find the start and end indices of contiguous True values in a boolean array.

    Parameters:
        mask: a boolean array
    '''

    starts = []
    ends = []
    for i in range(1, len(mask)):
        if not mask[i-1] and mask[i]:
            starts.append(i)
        if mask[i-1] and not mask[i]:
            ends.append(i-1)
    if mask[0]:
        starts.insert(0, 0)
    if mask[-1]:
        ends.append(len(mask)-1)

    return starts, ends

def feldman_cousins_slice(x_range, mu, mu_hat_func, prob_func, cl, dx=None, discrete=True):

    # Compute Neyman belt slice
    pdf = prob_func(x_range, mu)
    den = prob_func(x_range, mu_hat_func(x_range))
    r = pdf / den

    order = np.argsort(r)[::-1]

    cum = 0
    for i in order:
        if discrete:
            cum += pdf[i]
        else:
            cum += pdf[i] * dx

        if cum >= cl:
            c = r[i]
            break

    mask = r >= c

    return mask

def lr_intervals(x_obs, x_range, mu_grid, mu_hat_func, prob_func, cl, dx=None, discrete=True):

    accepted_mu = []

    for mu in mu_grid:
        mask = feldman_cousins_slice(
            x_range=x_range,
            mu=mu,
            mu_hat_func=mu_hat_func,
            prob_func=prob_func,
            cl=cl,
            dx=dx,
            discrete=discrete
        )

        if x_obs < len(mask) and mask[x_obs]:
            accepted_mu.append(mu)

    return (min(accepted_mu), max(accepted_mu))
