'''
Interval estimation mathematical utilities for the Analisi Statistica dei Dati notes.
'''
import numpy as np
from asd.utils import code_snippet_generator

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

# START SNIPPET
def p_ordering(p, pdf, x_range, cl, discrete=True):
    '''
    Compute the acceptance region for a given p ordering.

    Parameters:
        p: the ordering variable (e.g., likelihood ratio)
        pdf: the probability density/mass function values for the given x_range
        x_range: the range of x values to consider
        cl: the confidence level (e.g., 0.95)
        discrete: whether the x values are discrete (default: True)
            at the moment this only affects the use of dx,
            dx is computed supposing x_range is uniformly spaced
    '''

    order = np.argsort(p)[::-1]
    cum = 0
    dx = x_range[1] - x_range[0] if not discrete else 1

    for i in order:
        val = pdf[i] * dx
        cum += val
        if cum >= cl:
            threshold = p[i]
            break

    mask = p >= threshold

    return mask, threshold

def upper_ordering(p, pdf, x_range, cl, discrete=True):

    cum = 0
    dx = x_range[1] - x_range[0] if not discrete else 1

    for i in range(len(x_range)):
        val = pdf[i] * dx
        cum += val
        if cum >= cl:
            threshold = p[i]
            break

    mask = p >= threshold

    return mask, threshold

def lower_ordering(p, pdf, x_range, cl, discrete=True):

    cum = 0
    dx = x_range[1] - x_range[0] if not discrete else 1

    for i in reversed(range(len(x_range))):
        val = pdf[i] * dx
        cum += val
        if cum >= cl:
            threshold = p[i]
            break

    mask = p >= threshold

    return mask, threshold

def feldman_cousins_slice(mu, x_range, mu_hat_func, prob_func, cl, discrete=True):
    '''
    Compute the Feldman-Cousins acceptance region for a given mu.
    
    Parameters:
        mu: the parameter value for which to compute the acceptance region
        x_range: the range of x values to consider
        mu_hat_func: a function that computes the MLE for mu given x
        prob_func: a function that computes the probability density/mass for given x and mu
        cl: the confidence level (e.g., 0.95)
        discrete: whether the x values are discrete (default: True)
            at the moment this only affects the use of dx,
            dx is computed supposing x_range is uniformly spaced

    Example usage:
        For a guassian distribution with mean MU positive and unit variance:
            mask, threshold = asdmath.feldman_cousins_slice(
                x_range=x, # x = np.linspace(-4, 5, 2000)
                mu=MU,
                mu_hat_func=lambda x : np.maximum(0, x),
                prob_func=norm.pdf,
                cl=CL,
                discrete=False
            )
    '''

    pdf = prob_func(x_range, mu)
    den = prob_func(x_range, mu_hat_func(x_range))
    r = pdf / den

    return p_ordering(r, pdf, x_range, cl, discrete=discrete)

def lr_intervals(x_obs, x_range, mu_grid, mu_hat_func, prob_func, cl, discrete=True):
    '''
    Compute the confidence interval for a given observed x_obs using the likelihood-ratio ordering.
    
    Parameters:
        x_obs: the observed value of x
        x_range: the range of x values to consider for the ordering
        mu_grid: the grid of mu values to consider for the confidence interval
        mu_hat_func: a function that computes the MLE for mu given x
        prob_func: a function that computes the probability density/mass for given x and mu
        cl: the confidence level (e.g., 0.95)
        discrete: whether the x values are discrete (default: True)
            at the moment this only affects the use of dx,
            dx is computed supposing x_range is uniformly spaced
    
    Example usage:
        When observing n count from a poisson distribution:
            mu_interval = asdmath.lr_intervals(
                    x_obs=n,
                    x_range=np.arange(0, 300),
                    mu_grid=mu_span, # mu_span = np.linspace(0.0001, 100, 1000)
                    mu_hat_func=mu_hat_func, # mu_hat_func = lambda x: x
                    prob_func=poisson.pmf,
                    cl=0.95
                    )
    '''

    accepted_mu = []

    for mu in mu_grid:
        mask, _ = feldman_cousins_slice(
            x_range=x_range,
            mu=mu,
            mu_hat_func=mu_hat_func,
            prob_func=prob_func,
            cl=cl,
            discrete=discrete
        )

        if discrete:
            if x_obs < len(mask) and mask[x_obs]:
                accepted_mu.append(mu)
        else:
            idx = np.searchsorted(x_range, x_obs)
            if idx < len(mask) and mask[idx]:
                accepted_mu.append(mu)

    return (min(accepted_mu), max(accepted_mu))
# END SNIPPET

if __name__ == "__main__":
    code_snippet_generator(
        "# START SNIPPET",
        "# END SNIPPET",
        output_file_name="lr_intervals_function.tex",
        file=__file__
    )
