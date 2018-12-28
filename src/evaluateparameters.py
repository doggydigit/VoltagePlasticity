#!/usr/bin/env python

"""
    File name: evaluateparameters.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 27/12/2018
    Date last modified: 28/12/2018
    Python Version: 3.5
"""

from simulation import *

Bparams = {'PlasticityRule': 'Claire',
           'veto': True,
           'x_reset': 1.,  # spike trace reset value'
           'A_LTD': 0.099967,  # depression amplitude
           'A_LTP': 0.01795,  # potentiation amplitude
           'Theta_low': 3.315667 * b2.mV,  # depolarization threshold for plasticity
           'Theta_high': 11.96 * b2.mV,
           'b_theta': 1076.55 * b2.ms,
           'tau_theta': 114.91878 * b2.ms,
           'tau_lowpass1': 52.62584 * b2.ms,  # = tau_minus
           'tau_lowpass2': 3.041 * b2.ms,  # = tau_plus
           'tau_x': 4.8768 * b2.ms,
           'w_max': 1
           }

Lparams = {'PlasticityRule': 'Claire',
           'veto': True,
           'x_reset': 1.,  # spike trace reset value'
           'A_LTD': 0.000187,  # depression amplitude
           'A_LTP': 0.00003933,  # potentiation amplitude
           'Theta_low': 4.88578657 * b2.mV,  # depolarization threshold for plasticity
           'Theta_high': 26.04275 * b2.mV,
           'b_theta': 9998.87 * b2.ms,
           'tau_theta': 32.134 * b2.ms,
           'tau_lowpass1': 77.1748 * b2.ms,  # = tau_minus
           'tau_lowpass2': 2.00069 * b2.ms,  # = tau_plus
           'tau_x': 20.8914 * b2.ms,
           'w_max': 1
           }

if __name__ == "__main__":

    # Chose the simulation you want to test the parameters on
    protocol = 'Letzkus'

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
        # Initialize main class
        ex = PlasticityProtocol(protocol, t, parameters, debug=False)

        # Run simulation of trace
        m, p[t] = ex.run()

    if protocol is 'Brandalise':
        p = [p[0], 0.78 * p[1] + 0.22 * p[2], p[3], 0.8 * p[4] + 0.2 * p[5], p[6], p[7], 0.85 * p[8] + 0.15 * p[9],
             p[10], p[11],
             p[12], 0.81 * p[13] + 0.19 * p[14], p[15], p[16], 0.84 * p[17] + 0.16 * p[18], p[19], p[20],
             0.85 * p[21] + 0.15 * p[22], p[23]]
    for t in range(len(p)):
        print("Trace {} has plasticity: {}".format(t, int(100 * (1 + repets * p[t]))))
