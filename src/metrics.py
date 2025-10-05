import numpy as np 


def MAE(target, reference):
    return np.mean(np.abs(target - reference))
