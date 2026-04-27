# qui metodi di implementazione neyman implicita come: centrale, wilks, ecc.
def calculate_llr_intervals(n_values, cl=CL):
    '''Compute LLR (Wilks) interval at confidence level cl
    for a range of observed counts n_values.'''

    critical_value = chi2.ppf(cl, df=1)
    intervals = []

    for n in n_values:

        def lam(mu, n=n):
            '''Compute the log-likelihood-ratio for the poissonian case.'''
            if n == 0:
                return 2 * mu - critical_value
            if mu <= 0:
                return 1e9
            return 2 * (mu - n + n * np.log(n / mu)) - critical_value

        if n == 0:
            low = 0.0
        else:
            low = root_scalar(lam, bracket=[1e-12, n]).root

        upper_guess = max(n + 10*np.sqrt(n + 1), n + 10)
        high = root_scalar(lam, bracket=[n, upper_guess]).root

        intervals.append((low, high))

    return intervals

def calculate_central_interval_mu(n_obs, cl=0.95):
    '''
    Compute the central interval at confidence level cl
    for a given observed count n_obs.
    '''

    alpha = 1 - cl

    if n_obs == 0:
        low = 0.0
    else:
        def f_low(mu):
            return (1 - poisson.cdf(n_obs - 1, mu)) - alpha/2

        low = root_scalar(f_low, bracket=[1e-12, n_obs]).root

    def f_high(mu):
        return poisson.cdf(n_obs, mu) - alpha/2

    high_guess = n_obs + 10 * np.sqrt(n_obs + 1) + 20
    high = root_scalar(f_high, bracket=[n_obs, high_guess]).root

    return (low, high)
