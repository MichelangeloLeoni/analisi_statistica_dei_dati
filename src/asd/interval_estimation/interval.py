'''
Module conteining the class that function as an
interface for various interval estimation related
tasks.
'''
from dataclasses import dataclass, field
from typing import Callable
import numpy as np
from asd.interval_estimation import neyman
from asd import utils

@dataclass
class IntervalEstimator:
    '''
    High-level interface for confidence interval estimation.

    This class wraps:
    - the probability model
    - the Neyman construction
    - utilities for likelihood ratio, coverage, and interval extraction
    '''

    prob_func: callable
    cl: float

    mu_hat_func: Callable | None = None
    discrete: bool = True
    x_range: np.ndarray | None = None
    mu_grid: np.ndarray | None = None

    neyman: "neyman.NeymanConstruction" = field(init=False)

    def __post_init__(self):
        '''
        Post-initialization step.

        Computes grid spacing and builds the NeymanConstruction object.
        '''

        # Define grid spacing depending on discrete/continuous model
        self.dx = 1 if self.discrete else self.x_range[1] - self.x_range[0]

        # Initialize Neyman construction engine
        self.neyman = neyman.NeymanConstruction(
            model=self,
            mu_grid=self.mu_grid,
            x_range=self.x_range,
            discrete=self.discrete
        )

    def ratio(self, mu):
        '''
        Likelihood ratio used for Feldman–Cousins ordering.

        It compares the probability at a given mu with the maximum-likelihood
        estimate at each x.

        Parameters:
            mu : float
                Parameter value at which the ratio is evaluated.

        Output:
            ratio : array-like
                Likelihood ratio evaluated over x_range.
        '''

        pdf = self.pdf(mu)

        # Denominator: likelihood evaluated at the estimator mu_hat(x)
        den = self.prob_func(self.x_range, self.mu_hat_func(self.x_range))

        return pdf / den

    def pdf(self, mu):
        '''
        Evaluate the probability density (or mass) function at fixed mu.

        Parameters:
            mu : float
                Parameter value.

        Output:
            pdf : array-like
                Probability distribution over x_range.
        '''
        return self.prob_func(self.x_range, mu)

    # START SNIPPET
    def coverage(self, intervals):
        '''
        Compute coverage of confidence intervals over the parameter grid.

        For each true value of mu, integrates the probability of observing
        x values whose intervals contain mu.

        Parameters:
            intervals : dict or array-like
                Mapping from x to (lower, upper) confidence bounds.

        Output:
            cov : array-like
                Coverage probability as a function of mu.
        '''

        cov = []

        # Loop over true parameter values
        for mu in self.mu_grid:
            total = 0.0

            # Sum probability of all x that include mu in their interval
            for x in self.x_range:
                lo, hi = intervals[x]

                if lo <= mu <= hi:
                    total += self.prob_func(x, mu)

            cov.append(total)

        return np.array(cov)
    # END SNIPPET

    def masks_to_bounds(self, mask_list):
        '''
        Convert Neyman acceptance masks into interval bounds in x-space.

        Parameters:
            mask_list : list of boolean arrays
                Acceptance regions for each mu.

        Output:
            x_low : array-like
                Lower bounds of acceptance regions.
            x_high : array-like
                Upper bounds of acceptance regions.
        '''

        x_low = []
        x_high = []

        for mask in mask_list:

            # Extract indices where acceptance region is True
            idx = np.where(mask)[0]

            # Handle empty acceptance region
            if len(idx) == 0:
                x_low.append(np.nan)
                x_high.append(np.nan)
            else:
                # First and last accepted values define interval bounds
                x_low.append(self.x_range[idx[0]])
                x_high.append(self.x_range[idx[-1]])

        return np.array(x_low), np.array(x_high)


def find_intervals_indices(mask):
    '''
    Identify contiguous acceptance intervals in a boolean mask.

    This is useful when the acceptance region is not a single block
    but consists of multiple disjoint intervals.

    Parameters:
        mask : array-like (bool)
            Boolean array representing acceptance region.

    Output:
        starts : list of int
            Indices where True regions begin.
        ends : list of int
            Indices where True regions end.
    '''

    starts = []
    ends = []

    # Detect transitions between False -> True and True -> False
    for i in range(1, len(mask)):

        # Start of a new accepted region
        if not mask[i - 1] and mask[i]:
            starts.append(i)

        # End of an accepted region
        if mask[i - 1] and not mask[i]:
            ends.append(i - 1)

    # Edge cases: region starts at first element
    if mask[0]:
        starts.insert(0, 0)

    # Edge cases: region ends at last element
    if mask[-1]:
        ends.append(len(mask) - 1)

    return starts, ends

if __name__ == "__main__":
    utils.code_snippet_generator(
        start_tag="# START SNIPPET",
        end_tag="# END SNIPPET",
        output_file_name="coverage_code.tex",
        file=__file__
    )
