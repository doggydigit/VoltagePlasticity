#!/usr/bin/env python

"""
    File name: montesearch.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 21/12/2018
    Date last modified: 04/01/2019
    Python Version: 3.5
"""

import sys
import math
import dataset
import warnings
import random as rnd
from simulation import *

warnings.filterwarnings("error")


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
            return (-15 - 7 * index) * b2.mV
        elif pname in ['A_LTP', 'A_LTD']:
            return 0.001 * 10 ** index
        elif pname in ['tau_lowpass1', 'tau_lowpass2']:
            return 2 ** index * b2.ms
        elif pname is 'tau_x':
            return 2 ** (index - 2) * b2.ms
        elif pname is 'b_theta':
            return 0.4 * 5 ** index
        elif pname is 'tau_theta':
            return 0.2 * 5 ** index * b2.ms
        else:
            raise ValueError(pname)
    else:
        raise NotImplementedError


def main(protocol_type='Letzkus', plasticity='Claire', veto=False, debug=False, granularity=0, first_id=None,
         split=True, jid=0,):
    """
    Simulate a stimulation protocol with the desired neuron model and plasticity rule to monitor the resulting synaptic
    weight dynamics. This can also plot or save some results of the simulation.
    :param protocol_type: Whether to fit on the 'Letzkus' or 'Brandalise' voltage traces.
    :param plasticity: plasticity rule to use; can be either of 'Claire' or 'Clopath'
    :param veto: bool whether or not to use a veto mechanism between LTP and LTD
    :param debug: bool whether or not to have a more verbose output and simplified simulation
    :param granularity: int describing how fine the param search will be (Note: the range is also decreased for that)
    :param first_id: ID of the parameter configuration to start with. If None, a random configuration is used.
    :param split: bool whether or not to split the search grid dependening on the job id
    :param jid: id of the job running the montecarlo search. Necessary for splitting the grid search in case of split.
    """

    # Set random seed to current time to have different seeds for each of the many jobs
    rnd.seed()

    ####################################################################################################################
    # Define some variables depending on the protocol type
    ####################################################################################################################

    if protocol_type is 'Brandalise':
        nrtraces = 24
        nrneurons = 18
        repets = 60
        targets = [100, 144.8, 96.6, 122, 101.4, 95.5, 128.7, 101.1, 94.5,
                   100, 131, 96.6, 100, 119.3, 104.5, 104.3, 40, 40]
    elif protocol_type is 'Letzkus':
        nrtraces = 10
        nrneurons = 10
        repets = 150
        targets = [92, 129, 90, 100, 118, 100, 137, 85, 100, 78]
    else:
        raise ValueError(protocol_type)

    ####################################################################################################################
    # Connect to database (Sqlite database corresponding to the plasticity model used)
    ####################################################################################################################

    db_name = '../Data/monteresults_' + protocol_type + '_g' + str(granularity) + '_j' + str(jid) + '.db'
    db = dataset.connect('sqlite:///' + db_name)
    table_name = plasticity + '_veto' if veto else plasticity + '_noveto'
    the_table = db.create_table(table_name)

    ####################################################################################################################
    # Plasticity parameters initializations
    ####################################################################################################################

    # List of parameters to fit and initialization of parameters object with those that don't need fitting
    if split:
        # List of parameters to fit
        param_names = ['A_LTP', 'A_LTD', 'tau_lowpass1', 'tau_lowpass2', 'tau_x']

        # Compute set parameter indexes
        itl = jid % 9
        ith = int(math.floor(float(jid) / 9.))
        indexes = {'Theta_high': ith, 'Theta_low': itl}

        # Compute set parameter values
        tl = set_param('Theta_low', itl, g)
        th = set_param('Theta_high', ith, g)

        # Initialize parameters not needing fitting
        parameters = {'PlasticityRule': plasticity, 'veto': veto, 'x_reset': 1., 'w_max': 1, 'w_init': 0.5,
                      'Theta_high': th, 'Theta_low': tl}
    else:
        # List of parameters to fit
        param_names = ['Theta_high', 'Theta_low', 'A_LTP', 'A_LTD', 'tau_lowpass1', 'tau_lowpass2', 'tau_x']

        # Initialize parameters not needing fitting
        parameters = {'PlasticityRule': plasticity, 'veto': veto, 'x_reset': 1., 'w_max': 1, 'w_init': 0.5}

        # Initialize dictionary for parameter indexes
        indexes = {}

    # Specifications of the search grid depending on the search granularity
    if granularity == 0:
        grid_params = {'Theta_high': 8, 'Theta_low': 8, 'A_LTP': 8, 'A_LTD': 8, 'tau_lowpass1': 7,
                       'tau_lowpass2': 7, 'tau_x': 7}
    elif granularity == 1:
        grid_params = {'Theta_high': 8, 'Theta_low': 8, 'A_LTP': 8, 'A_LTD': 8, 'tau_lowpass1': 7,
                       'tau_lowpass2': 7, 'tau_x': 7, 'b_theta': 5, 'tau_theta': 5}
    else:
        raise NotImplementedError

    # Add veto parameters if required
    if veto:
        param_names += ['b_theta', 'tau_theta']
        grid_params['b_theta'] = 5
        grid_params['tau_theta'] = 5

    # Initialize parameter indices
    if first_id is None:
        for param_name in param_names:
            indexes[param_name] = rnd.sample(range(grid_params[param_name]), 1)[0] + 1
    else:
        translator = {'Theta_high': 'th', 'Theta_low': 'tl', 'A_LTP': 'ap', 'A_LTD': 'ad', 'tau_lowpass1': 't1',
                      'tau_lowpass2': 't2', 'tau_x': 'tx', 'b_theta': 'bt', 'tau_theta': 'tt'}
        first_indices = the_table.find_one(id=first_id)
        for param_name in param_names:
            indexes[param_name] = first_indices[translator[param_name]]

        if debug:
            print('First indices are:\n{}'.format(first_indices))

    # Initialize parameter values from indices according to desired grid design and specfic granularity
    for param_name in param_names:
        parameters[param_name] = set_param(param_name, indexes[param_name], granularity)

    print('\nInitialization completed.')

    ################################################################################################################
    # Monte-Carlo iterations
    ################################################################################################################

    # Initialize some variable
    current_score = sys.maxsize
    nr_iterations = 100000000
    patience = 3*len(param_names)
    waiting = 0

    print('\nStarting Monte-Carlo optimization:')

    for i in range(nr_iterations):

        print('Iteration: {}'.format(i))
        sys.stdout.flush()

        if waiting < patience:

            ############################################################################################################
            #        Modify one parameter and only accept new configuration if it remains within the allowed bounds
            ############################################################################################################

            # Select parameter to modify and make copy of all parameters to work with
            new_parameters = dict(parameters)
            new_indexes = dict(indexes)
            param_name = rnd.sample(param_names, 1)[0]

            # Shift index of selected parameter and check whether it remains in accepted bounds. Else skip iteration.
            direction = bool(rnd.getrandbits(1))
            if direction:
                new_indexes[param_name] += 1
                if new_indexes[param_name] > grid_params[param_name]:
                    if current_score > 0:
                        print('Wall reached with parameter {} for index {}'.format(param_name, new_indexes[param_name]))
                    continue

            else:
                new_indexes[param_name] -= 1
                if new_indexes[param_name] < 1:
                    if current_score > 0:
                        print('Wall reached with parameter {} for index {}'.format(param_name, new_indexes[param_name]))
                    continue

            # Index shift is accepted, thus update parameter value
            new_parameters[param_name] = set_param(param_name, new_indexes[param_name])

        else:
            # If the system is stuck in a region where it cannot explore new configurations, randomly reset parameters
            waiting = 0
            current_score = sys.maxsize

            for param_name in param_names:
                new_indexes[param_name] = rnd.sample(range(grid_params[param_name]), 1)[0] + 1
                new_parameters[param_name] = set_param(param_name, indexes[param_name], granularity)

            print('\n>>>> Random Parameter Reset\n')

        ################################################################################################################
        # If parameter configuration was already simulated, move on to accept or reject it. Otherwise, run simulations.
        ################################################################################################################

        # Check whether this parameter configuration was already simulated.
        if veto:
            query = the_table.find_one(th=new_indexes['Theta_high'], tl=new_indexes['Theta_low'],
                                       ap=new_indexes['A_LTP'], ad=new_indexes['A_LTD'], t1=new_indexes['tau_lowpass1'],
                                       t2=new_indexes['tau_lowpass2'], tx=new_indexes['tau_x'],
                                       bt=new_indexes['b_theta'], tt=new_indexes['tau_theta'])
        else:
            query = the_table.find_one(th=new_indexes['Theta_high'], tl=new_indexes['Theta_low'],
                                       ap=new_indexes['A_LTP'], ad=new_indexes['A_LTD'], t1=new_indexes['tau_lowpass1'],
                                       t2=new_indexes['tau_lowpass2'], tx=new_indexes['tau_x'])

        if query is None:

            waiting = 0

            # Create that row and temporarily put a score of zero to prevent other processors to compute it again
            if veto:
                query_id = the_table.insert(dict(th=new_indexes['Theta_high'], tl=new_indexes['Theta_low'],
                                                 ap=new_indexes['A_LTP'], ad=new_indexes['A_LTD'],
                                                 t1=new_indexes['tau_lowpass1'], t2=new_indexes['tau_lowpass2'],
                                                 tx=new_indexes['tau_x'], bt=new_indexes['b_theta'],
                                                 tt=new_indexes['tau_theta'], score=9999999999999999))

            else:
                query_id = the_table.insert(dict(th=new_indexes['Theta_high'], tl=new_indexes['Theta_low'],
                                                 ap=new_indexes['A_LTP'], ad=new_indexes['A_LTD'],
                                                 t1=new_indexes['tau_lowpass1'], t2=new_indexes['tau_lowpass2'],
                                                 tx=new_indexes['tau_x'], score=9999999999999999))
            db.commit()

            ############################################################################################################
            #            Run Simulations of all traces with new parameters and get plasticity
            ############################################################################################################

            # Initialize plasticity array
            p = [0] * nrtraces

            # Iterate through all available traces
            for t in range(nrtraces):

                # Simulate traces and store plasticities
                p[t], _ = simulate(protocol_type, t, new_parameters)

            # If Brandalise weight supralinear and linear trace plasticity contributions
            if protocol_type is 'Brandalise':
                p = [p[0], 0.78 * p[1] + 0.22 * p[2], p[3], 0.8 * p[4] + 0.2 * p[5], p[6], p[7],
                     0.85 * p[8] + 0.15 * p[9], p[10], p[11], p[12], 0.81 * p[13] + 0.19 * p[14], p[15], p[16],
                     0.84 * p[17] + 0.16 * p[18], p[19], p[20], 0.85 * p[21] + 0.15 * p[22], p[23]]

            ############################################################################################################
            #  Compute score and update database
            ############################################################################################################

            # Compute score
            differences = [abs(targets[t] - 100 * (1 + repets * p[t])) for t in range(nrneurons)]
            new_score = max(differences)

            # Update database
            the_table.update(dict(id=query_id, score=new_score), ['id'])
            db.commit()

        else:

            waiting += 1

            # Get score that was already computed
            new_score = query['score']
            print('    Was already simulated')

        # Given appropriate probability, update current state with the new state
        if new_score < current_score:
            parameters = new_parameters
            indexes = new_indexes
            current_score = new_score
        else:
            try:
                accept_prob = current_score / new_score
            except ZeroDivisionError or RuntimeWarning:
                accept_prob = 1

            if rnd.uniform(0, 1) < accept_prob:
                parameters = new_parameters
                indexes = new_indexes
                current_score = new_score

        print('    Score = {}'.format(current_score))

    return 0


if __name__ == "__main__":

    # Job ID
    j = int(sys.argv[1])

    # Resolution of the grid search
    if len(sys.argv) > 2:
        g = int(sys.argv[2])
    else:
        g = 0

    # Starting Configuration
    if len(sys.argv) == 4:
        fid = int(sys.argv[3])
    else:
        fid = None

    # Simulation choices
    ptype = 'Letzkus'  # Type of protocol to use for parameter fit
    rule_name = 'Claire'  # can be either of 'Claire' or 'Clopath'
    vetoing = False  # whether or not to use a veto mechanism between LTP and LTD

    # Run
    exi = main(ptype, rule_name, veto=vetoing, debug=False, granularity=g, first_id=fid, split=True, jid=j)

    if exi is 0:
        print('\nMonte-Carlo search finished successfully!')
    else:
        print('\nAn error occured...')
