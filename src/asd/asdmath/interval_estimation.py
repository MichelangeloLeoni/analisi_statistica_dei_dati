from dataclasses import dataclass, field
import numpy as np

@dataclass
class IntervalEstimator:
    x_range: np.ndarray
    mu_hat_func: callable
    prob_func: callable
    cl: float
    discrete: bool = True
    mu_grid: np.ndarray | None = None

    # cache
    _pdf_cache: dict = field(default_factory=dict, init=False)
    _ratio_cache: dict = field(default_factory=dict, init=False)
    _slice_cache: dict = field(default_factory=dict, init=False)
    _interval_cache: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.dx = 1 if self.discrete else self.x_range[1] - self.x_range[0]

    def get_pdf(self, mu):
        if mu not in self._pdf_cache:
            self._pdf_cache[mu] = self.prob_func(self.x_range, mu)
        return self._pdf_cache[mu]

    def get_ratio(self, mu):
        if mu not in self._ratio_cache:
            pdf = self.get_pdf(mu)
            den = self.prob_func(self.x_range, self.mu_hat_func(self.x_range))
            self._ratio_cache[mu] = pdf / den
        return self._ratio_cache[mu]

    def find_intervals_indices(self, mask):
        starts, ends = [], []

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

    def p_ordering(self, p, pdf):
        order = np.argsort(p)[::-1]
        cum = 0

        for i in order:
            cum += pdf[i] * self.dx
            if cum >= self.cl:
                threshold = p[i]
                break

        return p >= threshold, threshold

    def upper_ordering(self, pdf):
        cum = 0
        for i in range(len(self.x_range)):
            cum += pdf[i] * self.dx
            if cum >= self.cl:
                threshold = pdf[i]
                break

        return pdf >= threshold, threshold

    def lower_ordering(self, pdf):
        cum = 0
        for i in reversed(range(len(self.x_range))):
            cum += pdf[i] * self.dx
            if cum >= self.cl:
                threshold = pdf[i]
                break

        return pdf >= threshold, threshold

    def build_neyman_belt(self, slice_func):
        return [slice_func(mu)[0] for mu in self.mu_grid]

    def find_neyman_interval(self, x_obs, slice_func):
        accepted_mu = []

        for mu in self.mu_grid:
            mask, _ = slice_func(mu)

            if self.discrete:
                if x_obs < len(mask) and mask[x_obs]:
                    accepted_mu.append(mu)
            else:
                idx = np.searchsorted(self.x_range, x_obs)
                if idx < len(mask) and mask[idx]:
                    accepted_mu.append(mu)

        if not accepted_mu:
            return (np.nan, np.nan)

        return min(accepted_mu), max(accepted_mu)

    def feldman_cousins_slice(self, mu):
        if mu in self._slice_cache:
            return self._slice_cache[mu]

        pdf = self.get_pdf(mu)
        r = self.get_ratio(mu)

        mask, thr = self.p_ordering(r, pdf)

        self._slice_cache[mu] = (mask, thr)
        return mask, thr

    def lr_interval(self, x_obs):
        if x_obs in self._interval_cache:
            return self._interval_cache[x_obs]

        interval = self.find_neyman_interval(
            x_obs,
            self.feldman_cousins_slice
        )

        self._interval_cache[x_obs] = interval
        return interval
