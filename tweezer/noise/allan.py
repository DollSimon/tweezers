#!/usr/bin/env python

import pandas as pd
import numpy as np


def allan_var(data):
    """
    Calculates the allan variance.
    """

    allanVariances = pd.DataFrame({'av': None, 'error': None}, index=pd.Index(range(1)))

    return allanVariances


#     function (values, freq)
# {
#     N = length(values)
#     tau = 1/freq
#     n = ceiling((N - 1)/2)
#     p = floor(log10(n)/log10(2))
#     av <- rep(0, p + 1)
#     time <- rep(0, p + 1)
#     error <- rep(0, p + 1)
#     print("Calculating...")
#     for (i in 0:(p)) {
#         omega = rep(0, floor(N/(2^i)))
#         T = (2^i) * tau
#         l <- 1
#         k <- 1
#         while (k <= floor(N/(2^i))) {
#             omega[k] = sum(values[l:(l + ((2^i) - 1))])/(2^i)
#             l <- l + (2^i)
#             k <- k + 1
#         }
#         sumvalue <- 0
#         for (k in 1:(length(omega) - 1)) {
#             sumvalue = sumvalue + (omega[k + 1] - omega[k])^2
#         }
#         av[i + 1] = sumvalue/(2 * (length(omega) - 1))
#         time[i + 1] = T
#         error[i + 1] = 1/sqrt(2 * ((N/(2^i)) - 1))
#     }
#     return(data.frame(time, av, error))
# }