#!/usr/bin/env python

"""
    File name: simulation.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 21/12/2018
    Date last modified: 22/12/2018
    Python Version: 3.5
"""

import numpy as np
import random as rnd
from plasticity import *


ProtocolParameters = {'integration_timestep': 0.1 * b2.ms,
                      'integration_method': 'euler',
                      'weight_initial': 0.5}


class PlasticityProtocol:
    def __init__(self, protocol_type='Letzkus', trace_id=1, plasticity_parameters=Clopath_parameters, debug=False):
        """
        A synaptic weight change simulation class, which calculates the weight change, when a synapse is exposed to the
        voltage trace defined by protocol_type and trace_id. This plasticity is computed using the plasticity rule
        defined by plasticity_parameters and veto.
        :param protocol_type:
        :param trace_id:
        :param plasticity_parameters: parameters of the pasticity rule (see plasticity.py for examples)
        :param debug: Set to true for verbose output and shorter simulation
        """

        # Fix random seeds to insure code reproducibility
        b2.seed(1)
        rnd.seed(321)
        np.random.seed(1002)

        # Initialize class variables
        b2.defaultclock.dt = ProtocolParameters['integration_timestep']
        self.plasticity_parameters = plasticity_parameters
        self.veto = plasticity_parameters['veto']
        self.debug = debug

        # Load voltage trace and create presynaptc input
        if protocol_type is 'Letzkus':
            voltage = np.load('../Data/L_{}.npy'.format(trace_id))
            if trace_id in [0, 2, 4, 6, 8, 9]:
                self.neuron_pre = b2.SpikeGeneratorGroup(1, [0], [0.0 * b2.ms])
            elif trace_id in [1, 3, 5, 7]:
                self.neuron_pre = b2.SpikeGeneratorGroup(1, [0], [10.0 * b2.ms])
            else:
                raise ValueError(trace_id)
        elif protocol_type is 'Brandalise':
            voltage = np.load('../Data/B_{}.npy'.format(trace_id))
            if trace_id in list(range(21)):
                self.neuron_pre = b2.SpikeGeneratorGroup(1, [0], [0.0 * b2.ms])
            elif trace_id in [21, 22, 23]:
                self.neuron_pre = b2.SpikeGeneratorGroup(1, [0], [40.0 * b2.ms])
            else:
                raise ValueError(trace_id)
        else:
            raise ValueError(protocol_type)
        print(np.max(voltage))
        vt = b2.TimedArray(voltage * b2.mV, ProtocolParameters['integration_timestep'])
        self.final_t = len(voltage) * ProtocolParameters['integration_timestep']

        # Build postsynaptic neuron
        self.neuron_post = self.make_neuron(vt)

        # Create synapse
        self.syn = self.make_synapse()

        if debug:
            print('\n\n\nInitialized Simulation with:')
            print('- Simulation time: {}'.format(self.final_t))
            print("- Stimulation protocol: {} and trace: {}".format(protocol_type, trace_id))
            print("- Plasticity model: {} and veto: {}\n".format(plasticity_parameters['PlasticityRule'], veto))

    def make_neuron(self, v_trace):
        """
        This function makes a postsynaptic neuron group based on the postsynaptic neuron parameters of the class object.
        :param v_trace: voltage trace of the neuron
        :return: the postsynaptic neuron group
        """

        # Define constants used in the equations
        neuronparams = {'v': v_trace,
                        'tau_lowpass1': self.plasticity_parameters['tau_lowpass1'],
                        'tau_lowpass2': self.plasticity_parameters['tau_lowpass2']}

        # Define equations
        eqs = '''dv_lowpass1/dt = (v(t)-v_lowpass1)/tau_lowpass1 : volt  # low-pass filter\n'''
        eqs += '''dv_lowpass2/dt = (v(t)-v_lowpass2)/tau_lowpass2 : volt  # low-pass filter'''

        # Create neuron group object according to the upper defined equations
        neuron_out = b2.NeuronGroup(N=1, model=eqs, namespace=neuronparams, name='postneuron',
                                    method=ProtocolParameters['integration_method'])

        # Initialize the values of the variables
        neuron_out.v_lowpass1 = 0
        neuron_out.v_lowpass1 = 0

        return neuron_out

    def make_synapse(self):
        """
        This function makes a synapse between the two neurons based on the plastictiy parameters

        :return: The synapse object
        """

        # Get the plasticity equations depending on the chosen plasticity rule
        if self.plasticity_parameters['PlasticityRule'] == 'Clopath':
            params, pre_eqs, syn_eqs = get_clopath(self.plasticity_parameters, self.veto)

        elif self.plasticity_parameters['PlasticityRule'] == 'Claire':
            params, pre_eqs, syn_eqs = get_claire(self.plasticity_parameters, self.veto)

        else:
            raise NotImplementedError(self.plasticity_parameters['PlasticityRule'])

        # Construct the synapses according to the equations
        syn = b2.Synapses(source=self.neuron_pre, target=self.neuron_post, model=syn_eqs, on_pre=pre_eqs,
                          multisynaptic_index='synapse_number', namespace=params,
                          method=ProtocolParameters['integration_method'])

        # Connect the neurons
        syn.connect(p=1)

        # Initialize synaptic variables
        syn.w_ampa = 0
        syn.pre_x_trace = 0
        if self.veto:
            syn.theta = 0

        if self.debug:
            print('synapse made according to ', self.plasticity_parameters['PlasticityRule'])

        return syn

    def run(self, syn_parameters=False, post_parameters=False):
        """
        :param syn_parameters: a list of the parameters that should be recorded from the synapse, e.g. ['w_ampa', 'r_1']
        :param post_parameters: a list of the parameters that should be recorded from the postsynaptic neuron.
        :return: parameters_out, a dictionary containing all the parameters that were recorded, with keys syn_monitor
        and post_monitor, if they were variables required respectively.
        """

        if self.debug:
            print('\nRunning Simulation:')

        neuron_pre = self.neuron_pre
        neuron_post = self.neuron_post
        syn = self.syn

        # Define monitors that will record the desired variables during simulation
        parameters_out = {}
        if syn_parameters:
            syn_monitor = b2.StateMonitor(syn, syn_parameters, record=True)
            parameters_out['syn_monitor'] = syn_monitor

        if post_parameters:
            post_monitor = b2.StateMonitor(neuron_post, post_parameters, record=True)
            parameters_out['post_monitor'] = post_monitor

        # Run simulation
        rep = 'text' if self.debug else None
        b2.run(self.final_t, report=rep)

        if self.debug:
            print('Simulation successfully terminated')

        # Compute final plasticity (Note how dependent this final value is on the initial weight)
        plasticity = self.syn.w_ampa / ProtocolParameters['weight_initial']

        return parameters_out, plasticity
