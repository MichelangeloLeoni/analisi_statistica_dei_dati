from dataclasses import dataclass
import numpy as np

class OrderingStrategy:
    def __init__(self, x_range, cl, dx):
        self.x_range = x_range
        self.cl = cl
        self.dx = dx

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
