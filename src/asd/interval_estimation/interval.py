from dataclasses import dataclass, field
import numpy as np
from asd.interval_estimation import neyman


@dataclass
class IntervalEstimator:
    mu_hat_func: callable
    prob_func: callable
    cl: float

    discrete: bool = True
    x_range: np.ndarray | None = None
    mu_grid: np.ndarray | None = None

    neyman: "neyman.NeymanConstruction" = field(init=False)

    def __post_init__(self):
        self.dx = 1 if self.discrete else self.x_range[1] - self.x_range[0]

        self.neyman = neyman.NeymanConstruction(
            model=self,
            mu_grid=self.mu_grid,
            x_range=self.x_range,
            discrete=self.discrete
        )

    def pdf(self, mu):
        return self.prob_func(self.x_range, mu)

    def ratio(self, mu):
        pdf = self.pdf(mu)
        den = self.prob_func(self.x_range, self.mu_hat_func(self.x_range))
        return pdf / den

    def get_interval(self, x_obs, method, ordering):
        return self.neyman.find_interval(x_obs, method, ordering)

    def compute_coverage(self, mu_vals, x_vals, method, ordering):
        return self.neyman.coverage(mu_vals, x_vals, method, ordering)
