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


def upper_ordering(pdf, cl, dx):
    order = np.argsort(pdf)[::-1]
    cum = 0.0

    threshold = None
    for i in order:
        cum += pdf[i] * dx
        if cum >= cl:
            threshold = pdf[i]
            break

    return pdf >= threshold, threshold


def lower_ordering(pdf, cl, dx):
    order = np.argsort(pdf)
    cum = 0.0

    threshold = None
    for i in order:
        cum += pdf[i] * dx
        if cum >= cl:
            threshold = pdf[i]
            break

    return pdf >= threshold, threshold