'''
Module conteining the main ordering functions to be
used in the various interval estimation algorithms
'''
import numpy as np
from asd import utils

# START SNIPPET
def score_ordering(score, pdf, cl, dx):
    '''
    Builds a Neyman acceptance region using probability (score-value) ordering.

    The function sorts observations by a given score (typically likelihood-ratio or
    probability), then accumulates probability mass until the desired
    confidence level is reached.

    Parameters:
        score : array-like
            Ordering statistic evaluated on each x (higher values are preferred).
        pdf : array-like
            Probability density (or mass) function evaluated on the same grid as score.
        cl : float
            Confidence level (e.g. 0.68, 0.95).
        dx : float
            Grid spacing used for numerical integration.

    Output:
        mask : array-like (bool)
            Boolean mask selecting the acceptance region.
        threshold : float
            Critical value of the ordering variable defining the cutoff.
    '''

    # Sort indices in descending order of the score (highest first)
    order = np.argsort(score)[::-1]

    # Initialize cumulative probability
    cum = 0.0

    threshold = None
    for i in order:
        # Increment cumulative probability
        # For discrete distributions, dx = 1
        cum += pdf[i] * dx

        # Stop once the desired confidence level is reached
        if cum >= cl:
            threshold = score[i]
            break

    return score >= threshold, threshold

def upper_ordering(x_range, pdf, cl, dx):
    '''
    Constructs a one-sided upper confidence interval (right tail).

    The acceptance region includes values from the lower end of the
    distribution up to a threshold such that the integrated probability
    equals the confidence level.

    Parameters:
        x_range : array-like
            Grid of observation values (assumed ordered).
        pdf : array-like
            Probability density (or mass) function on x_range.
        cl : float
            Confidence level (e.g. 0.95).
        dx : float
            Grid spacing used for numerical integration.

    Output:
        mask : array-like (bool)
            Boolean mask selecting values below the threshold.
        threshold : float
            Upper bound of the confidence interval.
    '''

    # Initialize cumulative probability
    cum = 0.0
    threshold = None

    # Scan from left to right accumulating probability mass
    for i, x in enumerate(x_range):
        cum += pdf[i] * dx

        # Stop once the desired confidence level is reached
        if cum >= cl:
            threshold = x
            break

    # Return acceptance region (left-sided interval) and the threshold value
    return x_range <= threshold, threshold

def lower_ordering(x_range, pdf, cl, dx):
    '''
    Constructs a one-sided lower confidence interval (left tail).

    The acceptance region includes values from the upper end of the
    distribution down to a threshold such that the integrated probability
    equals the confidence level.

    Parameters:
        x_range : array-like
            Grid of observation values (assumed ordered).
        pdf : array-like
            Probability density (or mass) function on x_range.
        cl : float
            Confidence level (e.g. 0.95).
        dx : float
            Grid spacing used for numerical integration.

    Output:
        mask : array-like (bool)
            Boolean mask selecting values above the threshold.
        threshold : float
            Lower bound of the confidence interval.
    '''

    # Initialize cumulative probability
    cum = 0.0
    threshold = None

    # Scan from right to left accumulating probability mass
    for i in reversed(range(len(x_range))):
        cum += pdf[i] * dx

        # Stop once the desired confidence level is reached
        if cum >= cl:
            threshold = x_range[i]
            break

    return x_range >= threshold, threshold
# END SNIPPET

if __name__ == "__main__":
    utils.code_snippet_generator(
        start_tag="# START SNIPPET",
        end_tag="# END SNIPPET",
        output_file_name="ordering_functions_code.tex",
        file=__file__
    )
