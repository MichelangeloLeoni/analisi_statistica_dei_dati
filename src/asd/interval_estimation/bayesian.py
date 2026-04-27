'''
Bayesian mathematical utilities for the Analisi Statistica dei Dati notes.
'''
import numpy as np

def compute_posterior(x, mu, prob_func, prior_func):
    '''
    Compute the posterior distribution for a given observed x and parameter mu,
    using the provided probability function and prior function.

    Parameters:
        x: the observed value
        mu: the parameter value for which to compute the posterior
        prob_func: a function that computes the probability density/mass for given x and mu
        prior_func: a function that computes the prior density/mass for given mu
    '''

    likelihood = prob_func(x, mu)
    unnorm = likelihood * prior_func(mu)
    norm = np.trapezoid(unnorm, mu)

    return unnorm / norm

def posterior_interval(x, mu, prob_func, prior_func, cl):
    '''
    Compute the Bayesian credible interval for a given observed x and parameter mu,
    using the provided probability function and prior function,
    and the specified confidence level (cl).

    Parameters:
        x: the observed value
        mu: the parameter values for which to compute the posterior interval
        prob_func: a function that computes the probability density/mass for given x and mu
        prior_func: a function that computes the prior density/mass for given mu
        cl: confidence level for the credible interval (e.g., 0.95 for 95% credible interval)
    '''

    post = compute_posterior(x, mu, prob_func, prior_func)
    dmu = mu[1] - mu[0]
    idx = np.argsort(post)[::-1]
    mass = np.cumsum(post[idx] * dmu)

    keep = idx[mass <= (cl)]
    if len(keep) < len(idx):
        keep = np.append(keep, idx[len(keep)])
    keep = np.sort(keep)

    lower = mu[keep[0]]
    upper = mu[keep[-1]]

    return lower, upper

def lower_bound(x, mu, prob_func, prior_func, cl):
    '''
    Compute the lower bound of the Bayesian credible interval
    for a given observed x and parameter mu,
    using the provided probability function and prior function,
    and the specified confidence level (cl).

    Parameters:
        x: the observed value
        mu: the parameter values for which to compute the posterior interval
        prob_func: a function that computes the probability density/mass for given x and mu
        prior_func: a function that computes the prior density/mass for given mu
        cl: confidence level for the credible interval (e.g., 0.95 for 95% credible interval)
    '''

    post = compute_posterior(x, mu, prob_func, prior_func)
    dmu = mu[1] - mu[0]
    cdf = np.cumsum(post * dmu)
    cdf /= cdf[-1]

    return np.interp(1-cl, cdf, mu), mu[-1]

def upper_bound(x, mu, prob_func, prior_func, cl):
    '''Compute the upper bound of the Bayesian credible interval
    for a given observed x and parameter mu,
    using the provided probability function and prior function,
    and the specified confidence level (cl).

    Parameters:
        x: the observed value
        mu: the parameter values for which to compute the posterior interval
        prob_func: a function that computes the probability density/mass for given x and mu
        prior_func: a function that computes the prior density/mass for given mu
        cl: confidence level for the credible interval (e.g., 0.95 for 95% credible interval)
    '''

    post = compute_posterior(x, mu, prob_func, prior_func)
    dmu = mu[1] - mu[0]
    cdf = np.cumsum(post * dmu)
    cdf /= cdf[-1]

    return mu[0], np.interp(cl, cdf, mu)
