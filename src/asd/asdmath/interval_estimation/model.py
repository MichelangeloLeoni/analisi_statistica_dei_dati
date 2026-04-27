from dataclasses import dataclass
import numpy as np

class LikelihoodModel:
    def __init__(self, x_range, mu_hat_func, prob_func):
        self.x_range = x_range
        self.mu_hat_func = mu_hat_func
        self.prob_func = prob_func

    def pdf(self, mu):
        return self.prob_func(self.x_range, mu)

    def ratio(self, mu):
        pdf = self.pdf(mu)
        den = self.prob_func(self.x_range, self.mu_hat_func(self.x_range))
        return pdf / den
