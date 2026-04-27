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
            mask, thr = ordering.upper_ordering(self.x_range, pdf, self.model.cl, self.model.dx)

        elif ordering_type == "lower":
            mask, thr = ordering.lower_ordering(self.x_range, pdf, self.model.cl, self.model.dx)

        else:
            raise ValueError(ordering_type)

        return mask, thr

    def build_belt(self, method, ordering_type):

        mask_list = []

        for mu in self.mu_grid:
            mask, _ = self.get_slice(mu, method, ordering_type)
            mask_list.append(mask)

        return mask_list

    def find_interval(self, x_obs, method, ordering_type):

        accepted_mu = []
        mask_list = self.build_belt(method, ordering_type)

        for mu, mask in zip(self.mu_grid, mask_list):
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
