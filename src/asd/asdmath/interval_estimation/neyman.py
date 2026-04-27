from dataclasses import dataclass
import numpy as np

class NeymanConstruction:
    def __init__(self, model, ordering, mu_grid, x_range, discrete=True):
        self.model = model
        self.ordering = ordering
        self.mu_grid = mu_grid
        self.x_range = x_range
        self.discrete = discrete

    def get_slice(self, mu, method, ordering_type):
        pdf = self.model.pdf(mu)

        if ordering_type == "p":
            score = self.model.ratio(mu) if method == "fc" else pdf
            mask, thr = self.ordering.p_ordering(score, pdf)

        elif ordering_type == "upper":
            mask, thr = self.ordering.upper_ordering(pdf)

        elif ordering_type == "lower":
            mask, thr = self.ordering.lower_ordering(pdf)

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

    def coverage(self, mu_vals, x_vals, method, ordering_type):
        cov = []

        for mu in mu_vals:
            pdf = self.model.prob_func(x_vals, mu)
            total = 0.0

            for i, x in enumerate(x_vals):
                lo, hi = self.find_interval(x, method, ordering_type)

                if np.isnan(lo):
                    continue

                if lo <= mu <= hi:
                    total += pdf[i]

            cov.append(total)

        return np.array(cov)
