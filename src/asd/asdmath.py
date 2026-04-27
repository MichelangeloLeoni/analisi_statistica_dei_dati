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

def find_lr_intervals(x_obs, x_range, mu_grid, mu_hat, prob_func, cl):
    '''
    Compute the likelihood-ratio intervals at confidence level cl for a given observed value x_obs,
    using the probability function prob_func and building the neyman belt for parameter values
    mu_grid (could be used, for example, in poissonian or gaussian cases).

    Parameters:
        x_obs: the observed value for which to compute the interval
        x_range: the range of possible observed values to consider when building the neyman belt
        mu_grid: the range of parameter values to consider when building the neyman belt
        mu_hat: the function that computes the best-fit parameter value for a given observed value
        prob_func: the probability function that takes x_range and mu as 
            arguments and returns the pdf values
        cl: the confidence level for the interval
    '''

    # Initialize list to store mu values that generate intervals
    # contatining n_obs at confidence level cl
    accepted_mu = []

    # Compute Neyman belt
    for mu in mu_grid:
        pdf = prob_func(x_range, mu)
        den = prob_func(x_range, mu_hat)
        r = pdf / den

        order = np.argsort(r)[::-1]

        cum = 0
        for i in order:
            cum += pdf[i]
            if cum >= cl:
                c = r[i]
                break

        mask = r >= c

        if x_obs < len(mask) and mask[x_obs]:
            accepted_mu.append(mu)

    return (min(accepted_mu), max(accepted_mu))
