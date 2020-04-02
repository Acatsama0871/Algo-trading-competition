# Stationary strategy

import numpy as np
from statsmodels.tsa.stattools import adfuller


# Anxillury functions
# Sample mean
def sample_mean(data, num_py=True):
    result = []
    for i in data:
        result.append(i.mean())

    if num_py:
        result = np.array(result)

    return result


# Sample standard deviation
def sample_sd(data, num_py=True):
    result = []
    for i in data:
        result.append(i.std())

    if num_py:
        result = np.array(result)

    return result

# Trading width
def trading_width(trading_mean, trading_sd, sd_width_1, sd_width_2, num_py=True):
    result = []
    length = len(trading_mean)

    for i in range(0, length):
        upper_bound = trading_mean[i] + sd_width_1 * trading_sd[i]
        lower_bound = trading_mean[i] - sd_width_1 * trading_sd[i]
        super_upper_bound = trading_mean[i] + sd_width_2 * trading_sd[i]
        super_lower_bound = trading_mean[i] - sd_width_2 * trading_sd[i]
        temp = [upper_bound, lower_bound, super_upper_bound, super_lower_bound]
        result.append(temp)

    if num_py:
        result = np.array(result)

    return result


# Stationary test function
def stationary_test(data, significance_level=0.05, num_py=True):
    result = []
    for i in data:
        test_result = adfuller(i)[1]
        if test_result <= significance_level:
            result.append(True)
        else:
            result.append(False)

    if num_py:
        result = np.array(result)

    return result
