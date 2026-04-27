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

    # -----------------------
    # PDF & likelihood ratio
    # -----------------------

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

    # -----------------------
    # Ordering rules
    # -----------------------

    def p_ordering(self, score, pdf):
        order = np.argsort(score)[::-1]
        cum = 0.0

        for i in order:
            cum += pdf[i] * self.dx
            if cum >= self.cl:
                threshold = score[i]
                break

        return score >= threshold, threshold

    def upper_ordering(self, pdf):
        cum = 0.0

        for i in range(len(self.x_range)):
            cum += pdf[i] * self.dx
            if cum >= self.cl:
                threshold = pdf[i]
                break

        return pdf >= threshold, threshold

    def lower_ordering(self, pdf):
        cum = 0.0

        for i in reversed(range(len(self.x_range))):
            cum += pdf[i] * self.dx
            if cum >= self.cl:
                threshold = pdf[i]
                break

        return pdf >= threshold, threshold

    # -----------------------
    # Slice builders (cached)
    # -----------------------

    def get_slice(self, mu, method, ordering):
        key = (method, ordering, mu)

        if key in self._slice_cache:
            return self._slice_cache[key]

        pdf = self.get_pdf(mu)

        if ordering == "p":
            if method == "fc":
                score = self.get_ratio(mu)
            else:
                score = pdf
            mask, thr = self.p_ordering(score, pdf)

        elif ordering == "upper":
            mask, thr = self.upper_ordering(pdf)

        elif ordering == "lower":
            mask, thr = self.lower_ordering(pdf)

        else:
            raise ValueError(f"Unknown ordering: {ordering}")

        self._slice_cache[key] = (mask, thr)
        return mask, thr

    # -----------------------
    # Neyman construction
    # -----------------------

    def find_neyman_interval(self, x_obs, method, ordering):
        key = (method, ordering, x_obs)

        if key in self._interval_cache:
            return self._interval_cache[key]

        accepted_mu = []

        for mu in self.mu_grid:
            mask, _ = self.get_slice(mu, method, ordering)

            if self.discrete:
                if x_obs < len(mask) and mask[x_obs]:
                    accepted_mu.append(mu)
            else:
                idx = np.searchsorted(self.x_range, x_obs)
                if idx < len(mask) and mask[idx]:
                    accepted_mu.append(mu)

        if not accepted_mu:
            interval = (np.nan, np.nan)
        else:
            interval = (min(accepted_mu), max(accepted_mu))

        self._interval_cache[key] = interval
        return interval

    # -----------------------
    # Public API
    # -----------------------

    def get_interval(self, x_obs, method="fc", ordering="p"):
        return self.find_neyman_interval(x_obs, method, ordering)

    # -----------------------
    # Coverage
    # -----------------------

    def compute_coverage(self, mu_vals, x_vals, method="fc", ordering="p"):
        cov = []

        # cache intervalli per tutti gli x
        intervals = {
            x: self.get_interval(x, method, ordering)
            for x in x_vals
        }

        for mu in mu_vals:
            pdf = self.prob_func(x_vals, mu)
            total = 0.0

            for i, x in enumerate(x_vals):
                lo, hi = intervals[x]

                if np.isnan(lo):
                    continue

                if lo <= mu <= hi:
                    total += pdf[i] * self.dx

            cov.append(total)

        return np.array(cov)

# -----------------------
# Utility
# -----------------------

def find_intervals_indices(mask):
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