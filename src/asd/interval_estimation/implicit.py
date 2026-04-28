from scipy.stats import chi2
import numpy as np
from scipy.optimize import root_scalar

def lam(mu, x, prob_func, mu_hat_func, cl):

    critical_value = chi2.ppf(cl, df=1)

    if mu <= 0:
        return 1e9

    mu_hat = mu_hat_func(x)

    # usa log invece dei pdf
    log_mle = np.log(prob_func(x, mu_hat))
    log_pdf = np.log(prob_func(x, mu))

    return 2 * (log_mle - log_pdf) - critical_value

def wilks(x, prob_func, mu_hat_func, cl):

    # funzione in una sola variabile (mu)
    f = lambda m: lam(m, x, prob_func, mu_hat_func, cl)

    # lower bound
    if x == 0:
        low = 0.0
    else:
        try:
            low = root_scalar(f, bracket=[1e-12, x]).root
        except ValueError:
            # fallback se non trova cambio di segno
            low = 0.0

    # upper bound
    upper_guess = max(x + 10*np.sqrt(x + 1), x + 10)

    try:
        high = root_scalar(f, bracket=[x, upper_guess]).root
    except ValueError:
        # se il bracket non funziona, espandilo dinamicamente
        factor = 2
        while True:
            new_upper = upper_guess * factor
            try:
                high = root_scalar(f, bracket=[x, new_upper]).root
                break
            except ValueError:
                factor *= 2

    return (low, high)

def central_interval():
    pass