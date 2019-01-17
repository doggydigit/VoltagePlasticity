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

Bparams2 = {'PlasticityRule': 'Claire',
            'veto': True,
            'x_reset': 1.,  # spike trace reset value'
            'A_LTD': 0.099761303,  # depression amplitude
            'A_LTP': 0.013652842,  # potentiation amplitude
            'Theta_low': 2.636491402 * b2.mV,  # depolarization threshold for plasticity
            'Theta_high': 12.20124861 * b2.mV,
            'b_theta': 2.114599383,
            'tau_theta': 75.72422075 * b2.ms,
            'tau_lowpass1': 74.55801316 * b2.ms,  # = tau_minus
            'tau_lowpass2': 2.786924509 * b2.ms,  # = tau_plus
            'tau_x': 5.12639093 * b2.ms,
            'w_max': 1,
            'w_init': 0.5
            }

Bparams3 = {'PlasticityRule': 'Claire',
            'veto': True,
            'x_reset': 1.,  # spike trace reset value'
            'A_LTD': 0.099763602,  # depression amplitude
            'A_LTP': 0.01505758,  # potentiation amplitude
            'Theta_low': 2.927871397 * b2.mV,  # depolarization threshold for plasticity
            'Theta_high': 12.12886953 * b2.mV,
            'b_theta': 942.1754017,
            'tau_theta': 114.6026989 * b2.ms,
            'tau_lowpass1': 63.79366 * b2.ms,  # = tau_minus
            'tau_lowpass2': 2.853035054 * b2.ms,  # = tau_plus
            'tau_x': 4.990562943 * b2.ms,
            'w_max': 1,
            'w_init': 0.5
            }

Lparams = {'PlasticityRule': 'Claire',
           'veto': True,
           'x_reset': 1.,  # spike trace reset value'
           'A_LTD': 0.0001872,  # depression amplitude
           'A_LTP': 0.00003933,  # potentiation amplitude
           'Theta_low': 4.886 * b2.mV,  # depolarization threshold for plasticity
           'Theta_high': 26.04 * b2.mV,
           'b_theta': 9999.,
           'tau_theta': 32.13 * b2.ms,
           'tau_lowpass1': 77.17 * b2.ms,  # = tau_minus
           'tau_lowpass2': 2.001 * b2.ms,  # = tau_plus
           'tau_x': 20.89 * b2.ms,
           'w_max': 1,
           'w_init': 0.5
           }

Lparams2 = {'PlasticityRule': 'Claire',
            'veto': True,
            'x_reset': 1.,  # spike trace reset value'
            'A_LTD': 0.000160328,  # depression amplitude
            'A_LTP': 0.0000385,  # potentiation amplitude
            'Theta_low': 5.6 * b2.mV,  # depolarization threshold for plasticity
            'Theta_high': 26.2 * b2.mV,
            'b_theta': 10000.98042,
            'tau_theta': 25.4 * b2.ms,
            'tau_lowpass1': 65.5 * b2.ms,  # = tau_minus
            'tau_lowpass2': 2.0 * b2.ms,  # = tau_plus
            'tau_x': 22.1 * b2.ms,
            'w_max': 1,
            'w_init': 0.5
            }


def set_param(pname, index, granu=0):
    """
    This function will either transform the given index to the corresponding parameter value or sample an index in the
    right parameter range to produce a randomly sampled value for the desired parameter.
    :param pname: Name of the parameter to set
    :param index: Index of the parameter value
    :param granu: Granularity of the parameter search, which determines what parameter search subspace
    :return: return the value for desired parameter to set
    """

    if granu == 0:
        if pname in ['Theta_high', 'Theta_low']:
            return (-5 + 5 * index) * b2.mV
        elif pname in ['A_LTP', 'A_LTD']:
            return 10 ** (index - 6)
        elif pname in ['tau_lowpass1', 'tau_lowpass2', 'tau_x']:
            return 3 ** (index - 1) * b2.ms
        elif pname is 'b_theta':
            return 0.4 * 5 ** index
        elif pname is 'tau_theta':
            return 0.2 * 5 ** index * b2.ms
        else:
            raise ValueError(pname)
    elif granu == 1:
        if pname is 'Theta_low':
            return (-5 + 5 * (index + 1)) * b2.mV
        elif pname is 'Theta_high':
            return (-5 + 5 * (float(index) / 2 + 1)) * b2.mV
        elif pname is 'A_LTP':
            if index > 4.5:
                i = float(index) / 2 + 2.5
            else:
                i = float(index) / 2 + 0.5
            return 10 ** (i - 9)
        elif pname is 'A_LTD':
            return 10 ** (index - 8)
        elif pname is 'tau_x':
            return 3 ** (float(index) / 2 + 2.5) * b2.ms
        elif pname is 'tau_lowpass1':
            return 3 ** (index - 1) * b2.ms
        elif pname is 'tau_lowpass2':
            return 3 ** (float(index) / 2 - 1) * b2.ms
        elif pname is 'b_theta':
            return 0.4 * 5 ** index
        elif pname is 'tau_theta':
            return 0.2 * 5 ** index * b2.ms
        else:
            raise ValueError(pname)
    else:
        raise NotImplementedError


if __name__ == "__main__":

    # Chose the simulation you want to test the parameters on
    protocol = 'Brandalise'

    # Initialize some specifics
    if protocol is 'Brandalise':
        nrtraces = 24
        repets = 60
        parameters = Bparams2
    elif protocol is 'Letzkus':
        nrtraces = 10
        repets = 150
        if True:
            parameters = Lparams2
        else:
            # List of parameters to fit
            param_names = ['Theta_high', 'Theta_low', 'A_LTP', 'A_LTD', 'tau_lowpass1', 'tau_lowpass2', 'tau_x']

            # Initialize parameters not needing fitting
            parameters = {'PlasticityRule': 'Claire', 'veto': False, 'x_reset': 1., 'w_max': 1, 'w_init': 0.5}

            # Initialize dictionary for parameter indexes
            indexes = {'A_LTD': 8, 'A_LTP': 4, 'Theta_low': 7, 'Theta_high': 1,
                       'tau_lowpass1': 6, 'tau_lowpass2': 1, 'tau_x': 4}

            # Initialize parameter values from indices according to desired grid design and specfic granularity
            for param_name in param_names:
                parameters[param_name] = set_param(param_name, indexes[param_name], 1)
    else:
        raise ValueError(protocol)
    p = [0] * nrtraces

    # Simulate for all available traces of the corresponding protocol
    for t in range(nrtraces):
        p[t], _ = simulate(protocol, t, parameters, debug=False)

    if protocol is 'Brandalise':
        p = [repets * p[0], 38 * p[1] + 22 * p[2], repets * p[3], 40 * p[4] + 20 * p[5], repets * p[6], repets * p[7],
             45 * p[8] + 15 * p[9], repets * p[10], repets * p[11], repets * p[12], 41 * p[13] + 19 * p[14],
             repets * p[15], repets * p[16], 44 * p[17] + 16 * p[18], repets * p[19], repets * p[20],
             45 * p[21] + 15 * p[22], repets * p[23]]
        target = [100, 144.8, 96.6, 122, 101.4, 95.5, 128.7, 101.1, 94.5,
                  100, 131, 96.6, 100, 119.3, 104.5, 104.3, 40, 40]
    else:
        p = [repets * pl for pl in p]
        target = [92, 129, 90, 100, 118, 100, 137, 85, 100, 78]

    d = [0] * len(target)
    for t in range(len(p)):
        plast = 100 * (1 + p[t])
        d[t] = abs(target[t] - plast)
        print("Trace {} has plasticity: {} and difference: {}".format(t, plast, d[t]))
    print("L-infinity is {}".format(max(d)))
    if protocol is 'Letzkus':
        print("L2 is {}".format(100 * sum([d[t] ** 2 for t in range(len(d) - 1)]) + 6.25 * d[-1] ** 2))
    elif protocol is 'Brandalise':
        print("L2 is {}".format(100 * sum([d[t] ** 2 for t in range(len(d) - 2)])
                                + 25 * sum([d[-t] ** 2 for t in range(1, 3)])))

    print(d)
