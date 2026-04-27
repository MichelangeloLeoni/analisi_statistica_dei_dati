from dataclasses import dataclass
import numpy as np

@dataclass
class IntervalEstimator:
    x_range: np.ndarray
    mu_hat_func: callable
    prob_func: callable
    cl: float
    discrete: bool = True
    mu_grid: np.ndarray | None = None
    mu: float | None = None

    def __post_init__(self):
        self.dx = 1 if self.discrete else self.x_range[1] - self.x_range[0]

    # -----------------------
    # PDF & likelihood ratio
    # -----------------------

    def get_pdf(self, mu):
        return self.prob_func(self.x_range, mu)

    def get_ratio(self, mu):
        pdf = self.get_pdf(mu)
        den = self.prob_func(self.x_range, self.mu_hat_func(self.x_range))
        return pdf / den

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
    # Slice builders
    # -----------------------

    def get_slice(self, mu, method, ordering):
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

        return mask, thr

    # -----------------------
    # Neyman construction
    # -----------------------

    def find_neyman_interval(self, x_obs, method, ordering):
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
            return (np.nan, np.nan)

        return (min(accepted_mu), max(accepted_mu))

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

        for mu in mu_vals:
            pdf = self.prob_func(x_vals, mu)
            total = 0.0

            for i, x in enumerate(x_vals):
                lo, hi = self.get_interval(x, method, ordering)

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
        if not mask[i - 1] and mask[i]:
            starts.append(i)
        if mask[i - 1] and not mask[i]:
            ends.append(i - 1)

    if mask[0]:
        starts.insert(0, 0)
    if mask[-1]:
        ends.append(len(mask) - 1)

    return starts, ends
