#!/usr/bin/env python

"""
    File name: simulation.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 21/12/2018
    Date last modified: 04/01/2019
    Python Version: 3.5
"""

import numpy as np
import brian2 as b2

ProtocolParameters = {'integration_timestep': 0.1 * b2.msecond,
                      'integration_method': 'euler',
                      'weight_initial': 0.5}


def simulate(protocol_type='Letzkus', trace_id=1, plasticity_parameters=None,
             mon_parameters=False, debug=False):
    """
    A synaptic weight change simulation function, which calculates the weight change, when a synapse is exposed to the
    voltage trace defined by protocol_type and trace_id. This plasticity is computed using the plasticity rule
    defined by plasticity_parameters and veto.
    :param protocol_type: Specifies the study from which we use the voltage traces. Can be 'Brandalise' or 'Letzkus'
    :param trace_id: Identifies the voltage trace of the protocol.
    :param plasticity_parameters: parameters of the plasticity rule (see plasticity.py for examples)
    :param mon_parameters: Specifies the variables to monitor during the simulation
    :param debug: Set to true for verbose output and shorter simulation
    """

    ####################################################################################################################
    # Load voltage traces and get presynaptic input spike time
    ####################################################################################################################

    if protocol_type == 'Letzkus':
        voltage = np.load('../Data/L_{}.npy'.format(trace_id))
        if trace_id in [0, 2, 4, 6, 8, 9]:
            prespike = 0.0 * b2.ms
        elif trace_id in [1, 3, 5, 7]:
            prespike = 10.0 * b2.ms
        else:
            raise ValueError(trace_id)
    elif protocol_type == 'Brandalise':
        voltage = np.load('../Data/B_{}.npy'.format(trace_id))
        if trace_id in list(range(21)):
            prespike = 0.0 * b2.ms
        elif trace_id in [21, 22, 23]:
            prespike = 40.0 * b2.ms
        else:
            raise ValueError(trace_id)
    else:
        raise ValueError(protocol_type)

    # Get Simulation duration
    final_t = len(voltage) * ProtocolParameters['integration_timestep']

    ####################################################################################################################
    # Define neuron and synapse equations and bundle them into single neuron object for later simulation with Brian2
    ####################################################################################################################

    # Define constants used in the equations
    params = {'v': b2.TimedArray(voltage * b2.mV, ProtocolParameters['integration_timestep']),
              'tau_lowpass1': plasticity_parameters['tau_lowpass1'],
              'tau_lowpass2': plasticity_parameters['tau_lowpass2'],
              't_pre': prespike,
              'x_reset': plasticity_parameters['x_reset'],
              'A_LTP': plasticity_parameters['A_LTP'],
              'A_LTD': plasticity_parameters['A_LTD'],
              'Theta_low': plasticity_parameters['Theta_low'],
              'Theta_high': plasticity_parameters['Theta_high'],
              'tau_x': plasticity_parameters['tau_x'],
              'w_max': plasticity_parameters['w_max'] - plasticity_parameters['w_init'],
              'w_min': -plasticity_parameters['w_init']
              }

    # Define neuron equations
    eqs = b2.Equations('dv_lowpass1/dt = (v(t)-v_lowpass1)/tau_lowpass1 : volt')
    eqs += b2.Equations('dv_lowpass2/dt = (v(t)-v_lowpass2)/tau_lowpass2 : volt')
    eqs += b2.Equations('pre_x_trace = x_reset * exp((t_pre - t) / tau_x) * int(t >= t_pre) : 1')

    # Define plasticity equations depending on the chosen plasticity rule
    if plasticity_parameters['PlasticityRule'] == 'Clopath':
        eqs += b2.Equations('wLTD = A_LTD * pre_x_trace * (v_lowpass1 - Theta_low)'
                            ' * int(v_lowpass1/mV - Theta_low/mV > 0) : volt')
        eqs += b2.Equations('wLTP = A_LTP * pre_x_trace * (v - Theta_high) * (v_lowpass2 - Theta_low)'
                            ' * int(v - Theta_high > 0*mV) * int(v_lowpass2 - Theta_low > 0*mV)')
        eqs += b2.Equations('dw_ampa/dt = (wLTP - wLTD)/(mV*ms) : 1')

    elif plasticity_parameters['PlasticityRule'] == 'Claire':
        eqs += b2.Equations('wLTD = A_LTD * pre_x_trace * (v_lowpass1 - Theta_low)'
                            ' * int(v_lowpass1/mV - Theta_low/mV > 0) : volt')
        eqs += b2.Equations('wLTP = A_LTP * pre_x_trace * (v_lowpass2 - Theta_high)'
                            ' * int(v_lowpass2/mV - Theta_high/mV > 0) : volt')
        eqs += b2.Equations('dw_ampa/dt = (wLTP - wLTD)/(mV*ms) : 1')
    else:
        raise NotImplementedError(plasticity_parameters['PlasticityRule'])

    # Add veto equations if required
    if plasticity_parameters['veto']:
        params['Theta_low_zero'] = plasticity_parameters['Theta_low']
        params['b_theta'] = plasticity_parameters['b_theta']
        params['tau_theta'] = plasticity_parameters['tau_theta']
        eqs += b2.Equations('dtheta/dt = (wLTP - theta) / tau_theta : volt')
        eqs += b2.Equations('Theta_low = Theta_low_zero + b_theta * theta : volt')
    else:
        params['Theta_low'] = plasticity_parameters['Theta_low']

    # Create neuron group object according to the upper defined equations
    neuron = b2.NeuronGroup(N=1, model=eqs, namespace=params, name='postneuron',
                            method=ProtocolParameters['integration_method'])

    # Initialize variables
    neuron.v_lowpass1 = 0
    neuron.v_lowpass2 = 0
    neuron.w_ampa = 0
    if plasticity_parameters['veto']:
        neuron.theta = 0

    ####################################################################################################################
    # Finish Initialization
    ####################################################################################################################

    if debug:
        print('\nInitialized Simulation with:')
        print('- Simulation time: {}'.format(final_t))
        print("- Stimulation protocol: {} and trace: {}".format(protocol_type, trace_id))
        print("- Plasticity model: {} and veto: {}\n".format(plasticity_parameters['PlasticityRule'],
                                                             plasticity_parameters['veto']))

    ####################################################################################################################
    # Run Simulation
    ####################################################################################################################

    if debug:
        print('\nRunning Simulation:')

    # Define monitor that will record the desired variables during simulation
    monitor = None
    if mon_parameters:
        monitor = b2.StateMonitor(neuron, mon_parameters, record=True)

    # Run simulation
    rep = 'text' if debug else None
    b2.run(final_t, report=rep)

    if debug:
        print('Simulation successfully terminated.\n')

    ####################################################################################################################
    # Finished Simulation and prepare final output
    ####################################################################################################################

    # Compute final plasticity (Note how dependent this final value is on the initial weight)
    plasticity = neuron.w_ampa[0] / plasticity_parameters['w_init']

    return plasticity, monitor
