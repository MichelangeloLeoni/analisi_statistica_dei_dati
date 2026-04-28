'''
Module containing the class NeymanConstruction that
implements the Neyman construction for confidence intervals.

The class builds acceptance regions (Neyman belts) for different
parameter values and extracts confidence intervals from observed data.
'''
import numpy as np
from asd import utils
from asd.interval_estimation import (
    ordering
)

# START SNIPPET
class NeymanConstruction:
    '''
    Class that implements the Neyman construction for confidence intervals.
    '''

    def __init__(self, model, mu_grid, x_range, discrete=True):
        '''
        Initialize the Neyman construction framework.

        Parameters:
            model : object
                Statistical model providing pdf(mu), ratio(mu), cl, and dx.
            mu_grid : array-like
                Grid of parameter values over which the belt is constructed.
            x_range : array-like
                Grid of observable values.
            discrete : bool
                Whether the observable space is discrete or continuous.
        '''
        self.model = model
        self.mu_grid = mu_grid
        self.x_range = x_range
        self.discrete = discrete

    def get_slice(self, mu, method, ordering_type):
        '''
        Construct the acceptance region (slice of the Neyman belt)
        for a fixed parameter value mu.

        Parameters:
            mu : float
                Parameter value at which the slice is evaluated.
            method : str
                Method used for ordering (e.g. "fc" for Feldman-Cousins).
            ordering_type : str
                Type of ordering ("p", "upper", "lower").

        Output:
            mask : array-like (bool)
                Acceptance region mask over x_range.
            thr : float
                Threshold value defining the boundary of the region.
        '''

        # Compute probability distribution for fixed parameter mu
        pdf = self.model.pdf(mu)

        if ordering_type == "p":
            # Define ordering score:
            # - Feldman-Cousins uses likelihood ratio
            # - Otherwise use the pdf directly
            score = self.model.ratio(mu) if method == "fc" else pdf

            # Build acceptance region using probability ordering
            mask, thr = ordering.score_ordering(
                score,
                pdf,
                self.model.cl,
                self.model.dx
            )

        elif ordering_type == "upper":
            # One-sided upper confidence construction
            mask, thr = ordering.upper_ordering(
                self.x_range,
                pdf,
                self.model.cl,
                self.model.dx
            )

        elif ordering_type == "lower":
            # One-sided lower confidence construction
            mask, thr = ordering.lower_ordering(
                self.x_range,
                pdf,
                self.model.cl,
                self.model.dx
            )

        else:
            raise ValueError(ordering_type)

        return mask, thr

    def build_belt(self, method, ordering_type):
        '''
        Construct the full Neyman confidence belt.

        For each value of mu in the grid, compute the corresponding
        acceptance region over the observable space.

        Output:
            mask_list : list of boolean arrays
                Each element is the acceptance region for a given mu.
        '''

        mask_list = []

        # Loop over all parameter values
        for mu in self.mu_grid:
            mask, _ = self.get_slice(mu, method, ordering_type)
            mask_list.append(mask)

        return mask_list

    def find_interval(self, x_obs, method, ordering_type):
        '''
        Extract confidence interval for a given observed value.

        The interval is obtained by inverting the Neyman construction:
        selecting all mu values whose acceptance region includes x_obs.

        Parameters:
            x_obs : float or int
                Observed data point.
            method : str
                Ordering method used in construction.
            ordering_type : str
                Type of ordering ("p", "upper", "lower").

        Output:
            interval : tuple (mu_min, mu_max)
                Confidence interval for the parameter.
                Returns (nan, nan) if no mu is accepted.
        '''

        accepted_mu = []

        # Build full Neyman belt
        mask_list = self.build_belt(method, ordering_type)

        # Check which mu values accept the observation
        for mu, mask in zip(self.mu_grid, mask_list):

            if self.discrete:
                # Discrete case: direct indexing
                if x_obs < len(mask) and mask[x_obs]:
                    accepted_mu.append(mu)
            else:
                # Continuous case: map observation to grid index
                idx = np.searchsorted(self.x_range, x_obs)
                if idx < len(mask) and mask[idx]:
                    accepted_mu.append(mu)

        # No accepted values -> empty confidence interval
        if not accepted_mu:
            return (np.nan, np.nan)

        # Return full accepted mu range
        return (min(accepted_mu), max(accepted_mu))
# END SNIPPET

if __name__ == "__main__":
    utils.code_snippet_generator(
        start_tag="# START SNIPPET",
        end_tag="# END SNIPPET",
        output_file_name="neyman_intervals_code.tex",
        file=__file__
    )
