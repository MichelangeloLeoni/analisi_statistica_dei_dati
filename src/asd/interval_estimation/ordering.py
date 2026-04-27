import numpy as np

def p_ordering(score, pdf, cl, dx):
    order = np.argsort(score)[::-1]
    cum = 0.0

    threshold = None
    for i in order:
        cum += pdf[i] * dx
        if cum >= cl:
            threshold = score[i]
            break

    return score >= threshold, threshold

def upper_ordering(x_range, pdf, cl, dx):

    cum = 0
    for i in range(len(x_range)):
        cum += pdf[i] * dx
        if cum >= cl:
            threshold = x_range[i]
            break

    return x_range <= threshold, threshold

def lower_ordering(x_range, pdf, cl, dx):

    cum = 0
    for i in reversed(range(len(x_range))):
        cum += pdf[i] * dx
        if cum >= cl:
            threshold = x_range[i]
            break

    return x_range >= threshold, threshold
