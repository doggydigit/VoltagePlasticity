#!/usr/bin/env python

"""
    File name: evaluateparameters.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 27/12/2018
    Date last modified: 04/01/2019
    Python Version: 3.5
"""

from simulation import *

Bparams = {'PlasticityRule': 'Claire',
           'veto': True,
           'x_reset': 1.,  # spike trace reset value'
           'A_LTD': 0.09997,  # depression amplitude
           'A_LTP': 0.01795,  # potentiation amplitude
           'Theta_low': 3.316 * b2.mV,  # depolarization threshold for plasticity
           'Theta_high': 11.96 * b2.mV,
           'b_theta': 1077.,
           'tau_theta': 114.9 * b2.ms,
           'tau_lowpass1': 52.63 * b2.ms,  # = tau_minus
           'tau_lowpass2': 3.041 * b2.ms,  # = tau_plus
           'tau_x': 4.877 * b2.ms,
           'w_max': 1,
           'w_init': 0.5
           }

Lparams = {'PlasticityRule': 'Claire',
           'veto': True,
           'x_reset': 1.,  # spike trace reset value'
           'A_LTD': 0.0001872,  # depression amplitude
           'A_LTP': 0.0000393,  # potentiation amplitude
           'Theta_low': 4.886 * b2.mV,  # depolarization threshold for plasticity
           'Theta_high': 26.04 * b2.mV,
           'b_theta': 9999,
           'tau_theta': 32.13 * b2.ms,
           'tau_lowpass1': 77.17 * b2.ms,  # = tau_minus
           'tau_lowpass2': 2.001 * b2.ms,  # = tau_plus
           'tau_x': 20.89 * b2.ms,
           'w_max': 1,
           'w_init': 0.5
           }

if __name__ == "__main__":

    # Chose the simulation you want to test the parameters on
    protocol = 'Brandalise'

    # Initialize some specifics
    if protocol is 'Brandalise':
        nrtraces = 24
        repets = 60
        parameters = Bparams
    elif protocol is 'Letzkus':
        nrtraces = 10
        repets = 150
        parameters = Lparams
    else:
        raise ValueError(protocol)
    p = [0] * nrtraces

    # Simulate for all available traces of the corresponding protocol
    for t in range(nrtraces):
        p[t], _ = simulate(protocol, t, parameters, debug=False)

    if protocol is 'Brandalise':
        p = [p[0], 0.78 * p[1] + 0.22 * p[2], p[3], 0.8 * p[4] + 0.2 * p[5], p[6], p[7], 0.85 * p[8] + 0.15 * p[9],
             p[10], p[11],
             p[12], 0.81 * p[13] + 0.19 * p[14], p[15], p[16], 0.84 * p[17] + 0.16 * p[18], p[19], p[20],
             0.85 * p[21] + 0.15 * p[22], p[23]]
    for t in range(len(p)):
        print("Trace {} has plasticity: {}".format(t, 100 * (1 + repets * p[t])))
