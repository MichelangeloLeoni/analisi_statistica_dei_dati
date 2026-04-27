from dataclasses import dataclass
import numpy as np
from asd.asdmath.interval_estimation import (
    model,
    neyman,
    ordering,
    )

@dataclass
class IntervalEstimator:
    mu_hat_func: callable
    prob_func: callable
    cl: float

    discrete: bool = True
    x_range: np.ndarray | None = None
    mu_grid: np.ndarray | None = None

    def __post_init__(self):
        dx = 1 if self.discrete else self.x_range[1] - self.x_range[0]

        self.model = model.LikelihoodModel(
            self.x_range,
            self.mu_hat_func,
            self.prob_func
        )

        self.ordering = ordering.OrderingStrategy(
            self.x_range,
            self.cl,
            dx
        )

        self.neyman = neyman.NeymanConstruction(
            self.model,
            self.ordering,
            self.mu_grid,
            self.x_range,
            self.discrete
        )

    # -----------------------
    # API pubblica
    # -----------------------

    def get_interval(self, x_obs, method="fc", ordering="p"):
        return self.neyman.find_interval(x_obs, method, ordering)

    def compute_coverage(self, mu_vals, x_vals, method="fc", ordering="p"):
        return self.neyman.coverage(mu_vals, x_vals, method, ordering)
