#!/usr/bin/env python

"""
    File name: montesearch.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 16/01/2010
    Date last modified: 17/01/2019
    Python Version: 3.5
"""

import sys
import math
import dataset
import warnings
from simulation import *

warnings.filterwarnings("error")


def set_param(pname, index, plas='Claire_noveto', prot='Letzkus'):
    """
    This function will either transform the given index to the corresponding parameter value or sample an index in the
    right parameter range to produce a randomly sampled value for the desired parameter.
    :param pname: Name of the parameter to set
    :param index: Index of the parameter value
    :param plas: Type of plasticity rule used
    :param prot: protocol that is being simulated
    :return: return the value for desired parameter to set
    """

    # Get optimal parameters that will be used as center to get the surrounding to grid search
    if prot == 'Letzkus':
        if plas == 'Claire_noveto':
            raise NotImplementedError
        elif plas == 'Claire_veto':
            cbest = {'A_LTD': 0.00017497, 'A_LTP': 0.0000392, 'Theta_low': 5.19687991 * b2.mV, 'b_theta': 9991.2109,
                     'Theta_high': 25.7159892 * b2.mV, 'tau_theta': 26.7646283 * b2.ms, 'tau_x': 21.8613168 * b2.ms,
                     'tau_lowpass1': 70.4876245 * b2.ms, 'tau_lowpass2': 2.00056053 * b2.ms}

        else:
            raise ValueError(plas)
    elif prot == 'Brandalise':
        if plas == 'Claire_noveto':
            raise NotImplementedError
        elif plas == 'Claire_veto':
            cbest = {'A_LTD': 0.099763602, 'A_LTP': 0.01505758, 'Theta_low': 2.927871397 * b2.mV,
                     'Theta_high': 12.12886953 * b2.mV, 'b_theta': 942.1754017, 'tau_theta': 114.6026989 * b2.ms,
                     'tau_lowpass1': 63.79366 * b2.ms, 'tau_lowpass2': 2.853035054 * b2.ms, 'tau_x': 4.990562943*b2.ms}
        else:
            raise ValueError(plas)
    elif prot == 'Brandaliseb':
        if plas == 'Claire_noveto':
            raise NotImplementedError
        elif plas == 'Claire_veto':
            cbest = {'A_LTD': 0.099761303, 'A_LTP': 0.013652842, 'Theta_low': 2.636491402 * b2.mV,
                     'Theta_high': 12.20124861 * b2.mV, 'b_theta': 2.114599383, 'tau_theta': 75.72422075 * b2.ms,
                     'tau_lowpass1': 74.55801316*b2.ms, 'tau_lowpass2': 2.786924509*b2.ms, 'tau_x': 5.12639093*b2.ms}
        else:
            raise ValueError(plas)
    else:
        raise ValueError(prot)

    # Compute parameter value from index
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
        if pname in ['Theta_high', 'Theta_low']:
            return cbest[pname] + 8 * index * b2.mV
        elif pname in ['A_LTP', 'A_LTD']:
            return cbest[pname] * 10 ** index
        elif pname in ['tau_lowpass1', 'tau_lowpass2', 'tau_x', 'tau_theta', 'b_theta']:
            return cbest[pname] * 4 ** index
        else:
            raise ValueError(pname)


def init_params(granularity, split, table_name, plasticity, veto, jid):
    """
    Initialize objects that will be necessary for the monte carlo parameter optimization and are specific to the desired
    specifics of the simulation.
    :param granularity: int describing how fine the param search will be (Note: the range is also decreased for that)
    :param split: bool whether or not to split the search grid dependening on the job id
    :param table_name: name of the database table, which also specifies the plasticity rule used
    :param plasticity: type of plasticity (Claire, Clopath)
    :param veto: whether or not to sue veto
    :param jid: id of the job on which this program is running (only useful in case of split)
    :return: list of names (keys) of the parameters to fit, dictionaries of the indexes and of the actual values of the
    parameters to start with, boundaries of the index grid to use for the search.
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

            # List of parameters to fit
            param_names = ['Theta_high', 'Theta_low', 'tau_lowpass1', 'tau_lowpass2', 'tau_x', 'b_theta', 'tau_theta']

            if granularity == 1:

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

            elif granularity == 3:

                # Compute set parameter indexes
                iap = (jid % 5) * 0.125 - 0.25
                iad = math.floor(float(jid) / 5.) * 0.125 - 0.25
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
        if table_name == 'Claire_veto':
            param_names += ['b_theta', 'tau_theta']

        # Initialize parameters not needing fitting
        parameters = {'PlasticityRule': plasticity, 'veto': veto, 'x_reset': 1., 'w_max': 1, 'w_init': 0.5}

        # Initialize dictionary for parameter indexes
        indexes = {}

    # Specifications of the search grid depending on the search granularity
    if table_name == 'Claire_noveto':
        if granularity == 0:
            grid_params = {'Theta_high': [1, 8], 'Theta_low': [1, 8], 'A_LTP': [1, 7], 'A_LTD': [1, 7],
                           'tau_lowpass1': [1, 6], 'tau_lowpass2': [1, 6], 'tau_x': [1, 6]}

        elif granularity == 1:
            grid_params = {'Theta_high': [3, 7], 'Theta_low': [2, 8], 'A_LTP': [-1, 7], 'A_LTD': [1, 7],
                           'tau_lowpass1': [1, 6], 'tau_lowpass2': [1, 4], 'tau_x': [1, 8]}
        else:
            raise NotImplementedError
    elif table_name == 'Claire_veto':

        if granularity == 1:
            grid_params = {'Theta_high': [-1.5, 1], 'Theta_low': [-0.5, 1.5], 'A_LTP': [-2, 2], 'A_LTD': [-2, 2],
                           'tau_lowpass1': [-1, 0.5], 'tau_lowpass2': [-0.5, 1], 'tau_x': [-1, 1],
                           'b_theta': [-1, 0.5], 'tau_theta': [-1, 0.5]}
        elif granularity == 3:
            grid_params = {'Theta_high': [-0.25, 0.25], 'Theta_low': [-0.25, 0.25], 'A_LTP': [-0.25, 0.25],
                           'A_LTD': [-0.25, 0.25], 'tau_lowpass1': [-0.25, 0.25], 'tau_lowpass2': [-0.25, 0.25],
                           'tau_x': [-0.25, 0.25], 'b_theta': [-0.25, 0.25], 'tau_theta': [-0.25, 0.25]}
        else:
            raise NotImplementedError
    else:
        raise ValueError(table_name)

    # Initialize parameter indices and values according to desired grid design and specfic granularity
    for param_name in param_names:
        indexes[param_name] = grid_params[param_name][0]
        parameters[param_name] = set_param(param_name, indexes[param_name], table_name)

    return param_names, indexes, parameters, grid_params


def gridrecursion(pi, pnames, indexes, grid_params, parameters, granularity, plas, nrp, table, database, nrtraces,
                  nrneurons, repets, prot, targets, nr, veto, catching_up):
    """
    Recursive function to loop each parameter to vary along it grid search values.
    :param pi: int describing which parameter of the variable parameter list we are currently varying
    :param pnames: list of variable parameters
    :param indexes: dictionary of indexes describing the position of the current parameters on the grid
    :param grid_params: dictionary of boundaries of the grid for each parameter
    :param parameters: dictionary of values of the parameters
    :param granularity: int describing how fine the param search will be (Note: the range is also decreased for that)
    :param plas: Type of plasticity rule used
    :param nrp: number of parameters that are varied in this program of grid search
    :param table: database table to update simulation results into
    :param database: database to commit simulation results into
    :param nrtraces: number of traces to simulate for that protocol
    :param nrneurons: number of neurons in this protocol
    :param repets: number of repetitions of the protocol we need to simulate to get the target plasticity
    :param prot: string describing the protocol to simulate
    :param targets: list of target plasticities to compute losses
    :param nr: The number of parameter configurations already simulated by the grid search
    :param veto: whether or not to use veto mechanism
    :param catching_up: whether or not the program is still catching up with precomputed configurations
    :return: The updated number of parameter configurations simulated by the grid search
    """

    # Copy dictionaries that will be modified
    pmts = dict(parameters)
    idxs = dict(indexes)

    # Loop through all indexes of the current parameter to vary in the search
    pname = pnames[pi]
    for i in range(int((grid_params[pname][1] - grid_params[pname][0]) * 2 ** granularity + 1)):

        # Update index and parameter
        idxs[pname] = grid_params[pname][0] + i * 0.5 ** granularity
        pmts[pname] = set_param(pname, idxs[pname], plas)

        ################################################################################################################
        #  Recurse into next parameter or simulate in case you arrived at the last parameter of the list
        ################################################################################################################
        if pi < nrp - 1:

            # Recurse into next parameter
            nr, catching_up = gridrecursion(pi + 1, pnames, idxs, grid_params, pmts, granularity, plas, nrp, table,
                                            database, nrtraces, nrneurons, repets, prot, targets, nr, veto, catching_up)

        else:

            # Check whether this parameter configuration was already simulated.
            if catching_up:
                if veto:
                    query = table.find_one(th=idxs['Theta_high'], tl=idxs['Theta_low'], ap=idxs['A_LTP'],
                                           ad=idxs['A_LTD'], t1=idxs['tau_lowpass1'], t2=idxs['tau_lowpass2'],
                                           tx=idxs['tau_x'], bt=idxs['b_theta'], tt=idxs['tau_theta'])
                else:
                    query = table.find_one(th=idxs['Theta_high'], tl=idxs['Theta_low'], ap=idxs['A_LTP'],
                                           ad=idxs['A_LTD'], t1=idxs['tau_lowpass1'], t2=idxs['tau_lowpass2'],
                                           tx=idxs['tau_x'])

                if query is None:
                    catching_up = False

            ############################################################################################################
            #  Simulate plasticities (We arrived at the last parameter to recurse into)
            ############################################################################################################

            if not catching_up:

                print('Configuration: {}'.format(nr))

                # Initialize plasticity array
                p = [0] * nrtraces

                # Iterate through all available traces to simulate
                for t in range(nrtraces):
                    # Simulate trace and store plasticity
                    p[t], _ = simulate(prot[:10], t, pmts)

                ########################################################################################################
                #  Compute losses and update database
                ########################################################################################################

                # If Brandalise weight supralinear and linear trace plasticity contributions
                if prot[:10] == 'Brandalise':
                    p = [p[0], 0.78 * p[1] + 0.22 * p[2], p[3], 0.8 * p[4] + 0.2 * p[5], p[6], p[7],
                         0.85 * p[8] + 0.15 * p[9], p[10], p[11], p[12], 0.81 * p[13] + 0.19 * p[14], p[15], p[16],
                         0.84 * p[17] + 0.16 * p[18], p[19], p[20], 0.85 * p[21] + 0.15 * p[22], p[23]]

                # Compute errors
                differences = [abs(targets[t] - 100 * (1 + repets * p[t])) for t in range(nrneurons)]

                # Update database
                table.insert(dict(th=idxs['Theta_high'], tl=idxs['Theta_low'], ap=idxs['A_LTP'], ad=idxs['A_LTD'],
                                  t1=idxs['tau_lowpass1'], t2=idxs['tau_lowpass2'], tx=idxs['tau_x'],
                                  bt=idxs['b_theta'], tt=idxs['tau_theta'], li=max(differences),
                                  l2=sum([d ** 2 for d in differences])))

                database.commit()

                print('        Max Error {}'.format(max(differences)))
                sys.stdout.flush()

            nr += 1

    return nr, catching_up


def main(protocol_type='Letzkus', plasticity='Claire', veto=False, granularity=0, split=True, jid=0):
    """

    :param protocol_type: Whether to fit on the 'Letzkus' or 'Brandalise' voltage traces.
    :param plasticity: plasticity rule to use; can be either of 'Claire' or 'Clopath'
    :param veto: bool whether or not to use a veto mechanism between LTP and LTD
    :param granularity: int describing how fine the param search will be (Note: the range is also decreased for that)
    :param split: bool whether or not to split the search grid dependening on the job id
    :param jid: id of the job running the montecarlo search. Necessary for splitting the grid search in case of split.
    """

    ####################################################################################################################
    # Define some variables depending on the protocol type
    ####################################################################################################################

    if protocol_type[:10] == 'Brandalise':
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

    db_name = '../Data/gridresults_' + protocol_type + '_g' + str(granularity) + '_j' + str(jid) + '.db'
    db = dataset.connect('sqlite:///' + db_name)
    table_name = plasticity + '_veto' if veto else plasticity + '_noveto'
    the_table = db.create_table(table_name)

    ####################################################################################################################
    # Plasticity parameters initializations
    ####################################################################################################################

    param_names, indexes, parameters, grid_params = init_params(granularity, split, table_name, plasticity, veto, jid)

    print('\nInitialization completed.')

    ####################################################################################################################
    # Grid search
    ####################################################################################################################

    print('\nStarting Grid Search:')
    sys.stdout.flush()

    _ = gridrecursion(0, param_names, indexes, grid_params, parameters, granularity, table_name, len(param_names),
                      the_table, db, nrtraces, nrneurons, repets, protocol_type, targets, 0, veto, True)

    print('\nFinished Grid search successfully!')

    return 0


if __name__ == "__main__":

    # Job ID
    j = int(sys.argv[1])

    # Resolution of the grid search
    if len(sys.argv) > 2:
        g = int(sys.argv[2])
    else:
        g = 3

    # Simulation choices
    ptype = 'Brandaliseb'  # Type of protocol to use for parameter fit
    rule_name = 'Claire'  # can be either of 'Claire' or 'Clopath'
    vetoing = True  # whether or not to use a veto mechanism between LTP and LTD

    # Run
    exi = main(ptype, rule_name, veto=vetoing, granularity=g, split=True, jid=j)

    if exi is 0:
        print('\nGrid search finished successfully!')
    else:
        print('\nAn error occured...')
