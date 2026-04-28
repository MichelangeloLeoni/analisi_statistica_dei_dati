from dataclasses import dataclass, field
from typing import Callable
import numpy as np
from asd.interval_estimation import neyman


@dataclass
class IntervalEstimator:

    prob_func: callable
    cl: float

    mu_hat_func: Callable | None = None
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

    def ratio(self, mu):
        pdf = self.pdf(mu)
        den = self.prob_func(self.x_range, self.mu_hat_func(self.x_range))
        return pdf / den

    def pdf(self, mu):
        return self.prob_func(self.x_range, mu)

    def coverage(self, intervals):

        cov = []

        for mu in self.mu_grid:
            total = 0.0

            for x in self.x_range:
                lo, hi = intervals[x]
                if lo <= mu <= hi:
                    total += self.prob_func(x, mu)

            cov.append(total)

        return np.array(cov)

def find_intervals_indices(mask):
    '''
    Find the start and end indices of contiguous True values in a boolean array.

    Parameters:
        mask: a boolean array
    '''

    starts = []
    ends = []
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
