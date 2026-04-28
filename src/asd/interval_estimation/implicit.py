from scipy.stats import chi2
import numpy as np
from scipy.optimize import root_scalar

def lam(mu, x, prob_func, mu_hat_func, cl):

    critical_value = chi2.ppf(cl, df=1)

    if x == 0:
        return 2 * mu - critical_value
    if mu <= 0:
        return 1e9

    mle_pdf = prob_func(x, mu_hat_func(x))
    pdf = prob_func(x, mu)

    return 2 * np.log(mle_pdf/pdf) - critical_value

def wilks(mu, x, prob_func, mu_hat_func, cl):


    if x == 0:
        low = 0.0
    else:
        low = root_scalar(lam, bracket=[1e-12, x]).root

    upper_guess = max(n + 10*np.sqrt(x + 1), x + 10)
    high = root_scalar(lam, bracket=[x, upper_guess]).root

    return (low, high)

def central_interval():
    pass