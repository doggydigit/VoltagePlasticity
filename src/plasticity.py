#!/usr/bin/env python

"""
    File name: plasticity.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 21/12/2018
    Date last modified: 22/12/2018
    Python Version: 3.5
"""

import brian2 as b2

Clopath_parameters = {'PlasticityRule': 'Clopath',
                      'veto': True,
                      'x_reset': 1.,  # spike trace reset value'
                      'A_LTD': 2.7e-4,  # depression amplitude
                      'A_LTP': 1.2e-4,  # potentiation amplitude
                      'Theta_low': -55. * b2.mV,  # depolarization threshold for plasticity
                      'Theta_high': -45. * b2.mV,
                      'b_theta': 1077 * b2.ms,
                      'tau_theta': 114.9 * b2.ms,
                      'tau_x': 5. * b2.ms,
                      'tau_lowpass1': 10.5 * b2.ms,  # = tau_minus
                      'tau_lowpass2': 200 * b2.ms,  # = tau_plus
                      'w_max': 2
                      }

Claire_parameters = {'PlasticityRule': 'Claire',
                     'veto': True,
                     'x_reset': 1.,  # spike trace reset value'
                     'A_LTD': 1000,  # depression amplitude
                     'A_LTP': 1795,  # potentiation amplitude
                     'Theta_low': -55 * b2.mV,  # depolarization threshold for plasticity
                     'Theta_high': -45 * b2.mV,
                     'b_theta': 1077 * b2.ms,
                     'tau_theta': 114.9 * b2.ms,
                     'tau_lowpass1': 52.63 * b2.ms,  # = tau_minus
                     'tau_lowpass2': 3.04 * b2.ms,  # = tau_plus
                     'tau_x': 4.877 * b2.ms,
                     'w_max': 2
                     }


def get_plast(plasticity_parameters):
    """
    Produce some standard parameter values and equation to compute at presynaptic spike.
    :return: parameters and presynaptc spike trace update equation
    """
    # Parameter values that will be used in the equations
    params = {'x_reset': plasticity_parameters['x_reset'],
              'A_LTP': plasticity_parameters['A_LTP'],
              'A_LTD': plasticity_parameters['A_LTD'],
              'Theta_low': plasticity_parameters['Theta_low'],
              'Theta_high': plasticity_parameters['Theta_high'],
              'tau_x': plasticity_parameters['tau_x'],
              'w_max': plasticity_parameters['w_max']}

    # Presynaptic trace update
    pre_eqs = '''pre_x_trace += x_reset  # spike trace\n'''

    return params, pre_eqs


def get_clopath(plasticity_parameters, veto=False):
    """
    Function that produces all the necessary parameters and equations for the Clopath plasticity rule (Clopath, 2010).
    It also allows to use a veto mechanism between LTP and LTD mechanisms.
    :param plasticity_parameters: dictionary with parameter values to use
    :param veto: whether or not to use the veto mechanism
    :return: the parameter definitions, the presynaptic neuron equations and the synaptic equations
    """

    # Get parameter definitions for the equations and presynaptic trace equation
    params, pre_eqs = get_plast(plasticity_parameters)

    # Equations executed at every time step
    syn_eqs = '''dpre_x_trace/dt = -pre_x_trace/tau_x : 1 (clock-driven) # presynaptic spike\n'''
    syn_eqs += '''wLTP = A_LTP * pre_x_trace * (v/mV - Theta_high/mV) * (v_lowpass2/mV - Theta_low/mV)'''
    syn_eqs += ''' * int(v/mV - Theta_high/mV > 0) * int(v_lowpass2/mV - Theta_low/mV > 0) /ms'''
    syn_eqs += ''' * int(w_max > w_ampa)\n'''
    syn_eqs += '''dw_ampa/dt = wLTP: 1 (clock-driven)\n'''

    # Add veto equations if required
    if veto:
        params['Theta_low_zero'] = plasticity_parameters['Theta_low']
        params['b_theta'] = plasticity_parameters['b_theta']
        params['tau_theta'] = plasticity_parameters['tau_theta']
        syn_eqs += '''dtheta/dt = (wLTP - theta) / tau_theta : volt (clock-driven)\n'''
        syn_eqs += '''Theta_low = Theta_low_zero + b_theta * (wLTP - theta) / tau_theta: volt'''
    else:
        params['Theta_low'] = plasticity_parameters['Theta_low']

    # Equations executed only when a pre-synaptic spike occurs
    pre_eqs += '''w_ampa = clip(w_ampa - A_LTD * (v_lowpass1/mV - Theta_low/mV)'''
    pre_eqs += ''' * int(v_lowpass1_post/mV - Theta_low/mV > 0), 0, w_max)'''

    return params, pre_eqs, syn_eqs


def get_claire(plasticity_parameters, veto=False):
    """
    Function that produces all the necessary parameters and equations for the Claire Meissner's version of the Clopath
    plasticity rule (Clopath, 2010).

    :param plasticity_parameters: dictionary with parameter values to use
    :param veto: whether or not to use the veto mechanism
    :return: the parameter definitions, the presynaptic neuron equations and the synaptic equations
    """

    # Get parameter definitions for the equations and presynaptic trace equation
    params, pre_eqs = get_plast(plasticity_parameters)

    # Equations executed at every time step
    syn_eqs = '''dpre_x_trace/dt = -pre_x_trace/tau_x : 1 (clock-driven) # presynaptic spike\n'''
    syn_eqs += '''wLTD = A_LTD * pre_x_trace * (v_lowpass1 - Theta_low)'''
    syn_eqs += ''' * int(v_lowpass1/mV - Theta_low/mV > 0) * int(w_ampa > 0) : volt\n'''
    syn_eqs += '''wLTP = A_LTP * pre_x_trace * (v_lowpass2 - Theta_high)'''
    syn_eqs += ''' * int(v_lowpass2/mV - Theta_high/mV > 0) * int(w_max > w_ampa) : volt\n'''
    syn_eqs += '''dw_ampa/dt = (wLTP - wLTD)/(mV*ms) : 1 (clock-driven)\n'''

    # Add veto equations if required
    if veto:
        params['Theta_low_zero'] = plasticity_parameters['Theta_low']
        params['b_theta'] = plasticity_parameters['b_theta']
        params['tau_theta'] = plasticity_parameters['tau_theta']
        syn_eqs += '''dtheta/dt = (wLTP - theta) / tau_theta : volt (clock-driven)\n'''
        syn_eqs += '''Theta_low = Theta_low_zero + b_theta * (wLTP - theta) / tau_theta: volt'''
    else:
        params['Theta_low'] = plasticity_parameters['Theta_low']

    return params, pre_eqs, syn_eqs
