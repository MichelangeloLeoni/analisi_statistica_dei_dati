import numpy as np
from asd.interval_estimation import (
    ordering
)

class NeymanConstruction:

    def __init__(self, model, mu_grid, x_range, discrete=True):
        self.model = model
        self.mu_grid = mu_grid
        self.x_range = x_range
        self.discrete = discrete

    def get_slice(self, mu, method, ordering_type):
        pdf = self.model.pdf(mu)

        if ordering_type == "p":
            score = self.model.ratio(mu) if method == "fc" else pdf
            mask, thr = ordering.p_ordering(score, pdf, self.model.cl, self.model.dx)

        elif ordering_type == "upper":
            mask, thr = ordering.upper_ordering(pdf, self.model.cl, self.model.dx)

        elif ordering_type == "lower":
            mask, thr = ordering.lower_ordering(pdf, self.model.cl, self.model.dx)

        else:
            raise ValueError(ordering_type)

        return mask, thr

    def find_interval(self, x_obs, method, ordering_type):
        accepted_mu = []

        for mu in self.mu_grid:
            mask, _ = self.get_slice(mu, method, ordering_type)

            if self.discrete:
                if x_obs < len(mask) and mask[x_obs]:
                    accepted_mu.append(mu)
            else:
                idx = np.searchsorted(self.x_range, x_obs)
                if idx < len(mask) and mask[idx]:
                    accepted_mu.append(mu)

        if not accepted_mu:
            return (np.nan, np.nan)

        return (min(accepted_mu), max(accepted_mu))

    def coverage(self, mu_vals, x_vals, method="fc", ordering_type="p"):
        cov = []

        for mu in mu_vals:
            mask, _ = self.get_slice(mu, method, ordering_type)

            hits = 0
            total = 0

            for x in x_vals:
                total += 1
                idx = np.searchsorted(self.x_range, x)

                if idx < len(mask) and mask[idx]:
                    hits += 1

            cov.append(hits / total)

        return np.array(cov)
