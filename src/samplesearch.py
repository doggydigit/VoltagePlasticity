#!/usr/bin/env python

"""
    File name: samplesearch.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 22/01/2018
    Date last modified: 22/01/2019
    Python Version: 3.5
"""

import sys
import dataset
import warnings
import random as rnd
from simulation import *
from os.path import isfile


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


def main(protocol_type='Letzkus', plasticity='Claire', veto=False, granularity=0, jid=0):
    """
    Parameter search script that randomly samples parameter configurations to test through simulation according to a
    distribution determined by a loss expectation evaluated by a previous parameter search run with lower granularity.
    :param protocol_type: Whether to fit on the 'Letzkus' or 'Brandalise' voltage traces.
    :param plasticity: plasticity rule to use; can be either of 'Claire' or 'Clopath'
    :param veto: bool whether or not to use a veto mechanism between LTP and LTD
    :param granularity: int describing how fine the param search will be (Note: the range is also decreased for that)
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

    if not isfile('../Data/sampleresults_' + protocol_type + '_g' + str(granularity) + '_j' + str(jid) + '.db'):
        raise EnvironmentError("You must call model_distrbution.py (with correct specs) before this.")
    db_name = '../Data/sampleresults_' + protocol_type + '_g' + str(granularity) + '_j' + str(jid) + '.db'
    db = dataset.connect('sqlite:///' + db_name)
    table_name = plasticity + '_veto' if veto else plasticity + '_noveto'
    the_table = db.create_table(table_name)

    ####################################################################################################################
    # Plasticity parameters initializations
    ####################################################################################################################

    # Initialize parameters that are constant throughout
    parameters = {'PlasticityRule': plasticity, 'veto': veto, 'x_reset': 1., 'w_max': 1, 'w_init': 0.5}

    # List of parameters
    if veto:
        param_names = ['A_LTP', 'A_LTD', 'Theta_high', 'Theta_low', 'tau_lowpass1', 'tau_lowpass2', 'tau_x',
                       'b_theta', 'tau_theta']
    else:
        param_names = ['A_LTP', 'A_LTD', 'Theta_high', 'Theta_low', 'tau_lowpass1', 'tau_lowpass2', 'tau_x']

    translate = {'A_LTP': 'ap', 'A_LTD': 'ad', 'Theta_high': 'th', 'Theta_low': 'tl', 'tau_lowpass1': 't1',
                 'tau_lowpass2': 't2', 'tau_x': 'tx', 'b_theta': 'bt', 'tau_theta': 'tt'}

    print('\nInitialization completed.')

    ####################################################################################################################
    # Simulation iterations with sampled configurations
    ####################################################################################################################

    # Initialize some variables
    nr_iterations = 10000000
    nrs = 0

    print('\nStarting Sample Search:')

    for i in range(nr_iterations):

        print('Iteration: {}'.format(i))
        sys.stdout.flush()

        # Draw a conifguration according to the estimated loss distribution
        draw = rnd.uniform(0, 1)
        query = the_table.find_one(the_table.table.columns.crp >= draw)
        if query is None:
            query = the_table.find_one(id=the_table.count())

        if query['l2'] == 9999999999999999:

            nrs += 1
            print(nrs)
            sys.stdout.flush()

            for p in param_names:
                parameters[p] = set_param(p, query[translate[p]], table_name)

            ############################################################################################################
            #            Run Simulations of all traces with new parameters and get plasticity
            ############################################################################################################

            # Initialize plasticity array
            p = [0] * nrtraces

            # Iterate through all available traces
            for t in range(nrtraces):

                # Simulate traces and store plasticities
                p[t], _ = simulate(protocol_type, t, parameters)

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
            the_table.update(dict(id=query['id'], li=max(differences), l2=new_score), ['id'])

            db.commit()

    return 0


if __name__ == "__main__":

    # Job ID
    j = int(sys.argv[1])

    # Resolution of the grid search
    if len(sys.argv) > 2:
        g = int(sys.argv[2])
    else:
        g = 0

    # Simulation choices
    ptype = 'Letzkus'
    rule_name = 'Claire'
    vetoing = False

    # Run
    exi = main(ptype, rule_name, veto=vetoing, granularity=g, jid=j)

    if exi is 0:
        print('\nSample search finished successfully!')
    else:
        print('\nAn error occured...')
