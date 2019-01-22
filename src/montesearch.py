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


def set_param(pname, index, plas='Claire_noveto'):
    """
    This function will either transform the given index to the corresponding parameter value or sample an index in the
    right parameter range to produce a randomly sampled value for the desired parameter.
    :param pname: Name of the parameter to set
    :param index: Index of the parameter value
    :param plas: Type of plasticity rule used
    :return: return the value for desired parameter to set
    """

    if plas == 'Claire_noveto':
        if pname in ['Theta_high', 'Theta_low']:
            return (-5 + 5 * index) * b2.mV
        elif pname in ['A_LTP', 'A_LTD']:
            return 10 ** (index - 6)
        elif pname in ['tau_lowpass1', 'tau_lowpass2', 'tau_x']:
            return 3 ** (index - 1) * b2.ms
        else:
            raise ValueError(pname)
    elif plas == 'Claire_veto':

        cbest = {'A_LTD': 0.0001872, 'A_LTP': 0.00003933, 'Theta_low': 4.886 * b2.mV, 'Theta_high': 26.04 * b2.mV,
                 'b_theta': 9999., 'tau_theta': 32.13 * b2.ms, 'tau_lowpass1': 77.17 * b2.ms,
                 'tau_lowpass2': 2.001 * b2.ms, 'tau_x': 20.89 * b2.ms}

        if pname in ['Theta_high', 'Theta_low']:
            return cbest[pname] + 8 * index * b2.mV
        elif pname in ['A_LTP', 'A_LTD']:
            return cbest[pname] * 10 ** index
        elif pname in ['tau_lowpass1', 'tau_lowpass2', 'tau_x', 'tau_theta', 'b_theta']:
            return cbest[pname] * 4 ** index
        else:
            raise ValueError(pname)
    else:
        raise ValueError(plas)


def init_params(granularity, split, table_name, plasticity, veto, jid, first_id, the_table, debug):
    """

    :param granularity: int describing how fine the param search will be (Note: the range is also decreased for that)
    :param split: bool whether or not to split the search grid dependening on the job id
    :param table_name: name of the database table, which also specifies the plasticity rule used
    :param plasticity: type of plasticity (Claire, Clopath)
    :param veto: whether or not to sue veto
    :param jid: id of the job on which this program is running (only useful in case of split)
    :param first_id: id of the first parameter configuration to use (can be none for random initialization)
    :param the_table: pointer to the database table used to store simulation results
    :param debug: debug mode or release mode
    :return: list of names (keys) of the parameters to fit, dictionaries of the indexes and of the actual values of the
    parameters to start with, boundaries of the index grid to use for the search, index increase step used for MC.
    """

    # Make list of parameters to fit and initialization of parameters object with those that don't need fitting
    if split:
        if table_name == 'Claire_noveto':
            if granularity == 0:
                # List of parameters to fit
                param_names = ['A_LTP', 'A_LTD', 'tau_lowpass1', 'tau_lowpass2', 'tau_x']

                # Compute set parameter indexes
                itl = jid % 9
                ith = int(math.floor(float(jid) / 9.))
                indexes = {'Theta_high': ith, 'Theta_low': itl}

                # Compute set parameter values
                tl = set_param('Theta_low', itl, table_name)
                th = set_param('Theta_high', ith, table_name)

                # Initialize parameters not needing fitting
                parameters = {'PlasticityRule': plasticity, 'veto': veto, 'x_reset': 1., 'w_max': 1, 'w_init': 0.5,
                              'Theta_high': th, 'Theta_low': tl}
            elif granularity == 1:
                # List of parameters to fit
                param_names = ['Theta_high', 'A_LTP', 'tau_lowpass1', 'tau_lowpass2', 'tau_x']

                # Compute set parameter indexes
                itl = (jid % 13) * 0.5 + 2
                iad = int(math.floor(float(jid) / 13.) + 1)
                indexes = {'Theta_low': itl, 'A_LTD': iad}

                # Compute set parameter values
                tl = set_param('Theta_low', itl, table_name)
                ad = set_param('A_LTD', iad, table_name)

                # Initialize parameters not needing fitting
                parameters = {'PlasticityRule': plasticity, 'veto': veto, 'x_reset': 1., 'w_max': 1, 'w_init': 0.5,
                              'Theta_low': tl, 'A_LTD': ad}
            else:
                raise ValueError(granularity)
        elif table_name == 'Claire_veto':
            if granularity == 1:
                # List of parameters to fit
                param_names = ['Theta_high', 'Theta_low', 'tau_lowpass1', 'tau_lowpass2', 'tau_x']

                # Compute set parameter indexes
                iap = (jid % 9) * 0.5 - 2
                iad = math.floor(float(jid) / 9.) * 0.5 - 2
                indexes = {'A_LTP': iap, 'A_LTD': iad}

                # Compute set parameter values
                ap = set_param('A_LTP', iap, table_name)
                ad = set_param('A_LTD', iad, table_name)

                # Initialize parameters not needing fitting
                parameters = {'PlasticityRule': plasticity, 'veto': veto, 'x_reset': 1., 'w_max': 1, 'w_init': 0.5,
                              'A_LTP': ap, 'A_LTD': ad}
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError(table_name)
    else:
        # List of parameters to fit
        param_names = ['Theta_high', 'Theta_low', 'A_LTP', 'A_LTD', 'tau_lowpass1', 'tau_lowpass2', 'tau_x']

        # Initialize parameters not needing fitting
        parameters = {'PlasticityRule': plasticity, 'veto': veto, 'x_reset': 1., 'w_max': 1, 'w_init': 0.5}

        # Initialize dictionary for parameter indexes
        indexes = {}

    # Specifications of the search grid depending on the search granularity
    increase = 0.5 ** granularity
    if table_name == 'Claire_noveto':
        if granularity == 0:
            grid_params = {'Theta_high': [0, 8], 'Theta_low': [0, 8], 'A_LTP': [1, 7], 'A_LTD': [1, 7],
                           'tau_lowpass1': [1, 6], 'tau_lowpass2': [1, 6], 'tau_x': [1, 6]}

        elif granularity == 1:
            grid_params = {'Theta_high': [3, 7], 'Theta_low': [2, 8], 'A_LTP': [-1, 7], 'A_LTD': [1, 7],
                           'tau_lowpass1': [1, 6], 'tau_lowpass2': [1, 4], 'tau_x': [1, 8]}
        else:
            raise NotImplementedError
    elif table_name == 'Claire_veto':
        param_names += ['b_theta', 'tau_theta']
        if granularity == 1:
            grid_params = {'Theta_high': [-1.5, 1], 'Theta_low': [-0.5, 1.5], 'A_LTP': [-2, 2], 'A_LTD': [-2, 2],
                           'tau_lowpass1': [-1, 0.5], 'tau_lowpass2': [-0.5, 1], 'tau_x': [-1, 1],
                           'b_theta': [-1, 0.5], 'tau_theta': [-1, 0.5]}
        else:
            raise NotImplementedError
    else:
        raise ValueError(table_name)

    # Initialize parameter indices
    if first_id is None:
        for param_name in param_names:
            nr_param_indexes = int(round((grid_params[param_name][1] - grid_params[param_name][0]) / increase + 1))
            indexes[param_name] = rnd.sample(range(nr_param_indexes), 1)[0] * increase + grid_params[param_name][0]
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
        parameters[param_name] = set_param(param_name, indexes[param_name], table_name)

    return param_names, indexes, parameters, grid_params, increase


def main(protocol_type='Letzkus', plasticity='Claire', veto=False, debug=False, granularity=0, first_id=None,
         split=True, jid=0):
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
        nrtraces = 9
        nrneurons = 9
        repets = 150
        targets = [92, 129, 90, 100, 118, 100, 137, 85, 100]
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

    param_names, indexes, parameters, grid_params, increase = init_params(granularity, split, table_name, plasticity,
                                                                          veto, jid, first_id, the_table, debug)

    print('\nInitialization completed.')

    ####################################################################################################################
    # Monte-Carlo iterations
    ####################################################################################################################

    # Initialize some variable
    maxint = 922337203685477
    current_score = maxint
    nr_iterations = 10000000
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
            if bool(rnd.getrandbits(1)):
                new_indexes[param_name] += increase
                if new_indexes[param_name] > grid_params[param_name][1]:
                    if current_score > 0:
                        print('Wall reached with parameter {} for index {}'.format(param_name, new_indexes[param_name]))
                    continue

            else:
                new_indexes[param_name] -= increase
                if new_indexes[param_name] < grid_params[param_name][0]:
                    if current_score > 0:
                        print('Wall reached with parameter {} for index {}'.format(param_name, new_indexes[param_name]))
                    continue

            # Index shift is accepted, thus update parameter value
            new_parameters[param_name] = set_param(param_name, new_indexes[param_name], table_name)

        else:
            # If the system is stuck in a region where it cannot explore new configurations, randomly reset parameters
            waiting = 0
            current_score = maxint

            for param_name in param_names:
                nr_param_indexes = int(round((grid_params[param_name][1] - grid_params[param_name][0]) / increase + 1))
                indexes[param_name] = rnd.sample(range(nr_param_indexes), 1)[0] * increase + grid_params[param_name][0]
                new_parameters[param_name] = set_param(param_name, indexes[param_name], table_name)

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
                                                 tt=new_indexes['tau_theta'], li=9999999999999999, l2=9999999999999999))

            else:
                query_id = the_table.insert(dict(th=new_indexes['Theta_high'], tl=new_indexes['Theta_low'],
                                                 ap=new_indexes['A_LTP'], ad=new_indexes['A_LTD'],
                                                 t1=new_indexes['tau_lowpass1'], t2=new_indexes['tau_lowpass2'],
                                                 tx=new_indexes['tau_x'], li=9999999999999999, l2=9999999999999999))
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
            if protocol_type == 'Brandalise':
                p = [p[0], 0.78 * p[1] + 0.22 * p[2], p[3], 0.8 * p[4] + 0.2 * p[5], p[6], p[7],
                     0.85 * p[8] + 0.15 * p[9], p[10], p[11], p[12], 0.81 * p[13] + 0.19 * p[14], p[15], p[16],
                     0.84 * p[17] + 0.16 * p[18], p[19], p[20], 0.85 * p[21] + 0.15 * p[22], p[23]]

            ############################################################################################################
            #  Compute score and update database
            ############################################################################################################

            # Compute score
            differences = [abs(targets[t] - 100 * (1 + repets * p[t])) for t in range(nrneurons)]
            new_score = sum([d ** 2 for d in differences])

            # Update database
            the_table.update(dict(id=query_id, li=max(differences), l2=new_score), ['id'])
            db.commit()

        else:

            waiting += 1

            # Get score that was already computed
            new_score = query['li']
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
