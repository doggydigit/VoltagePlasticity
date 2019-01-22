#!/usr/bin/env python

"""
    File name: build_space.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 22/01/2018
    Date last modified: 22/01/2019
    Python Version: 3.5
"""

import dataset
from sys import argv
from math import floor


def samplerecursion(pi, pnames, indexes, pgrid, gran, nrp, table, database, nr, vetoing):
    """
    Recursive function to loop each parameter to create a sample of each configuration.
    :param pi: int describing which parameter of the variable parameter list we are currently varying
    :param pnames: list of variable parameters
    :param indexes: dictionary of indexes describing the position of the current parameters on the grid
    :param pgrid: dictionary of boundaries of the grid for each parameter
    :param gran: int describing how fine the param search will be (Note: the range is also decreased for that)
    :param nrp: number of parameters that are varied in this program of grid search
    :param table: database table to update simulation results into
    :param database: database to commit simulation results into
    :param nr: The number of parameter configurations already simulated by the grid search
    :param vetoing: whether or not to use veto mechanism
    :return: The updated number of parameter configurations simulated by the grid search
    """

    # Copy index dictionariy, because it will be modified but must remain constant in the upper recursion
    idxs = dict(indexes)

    # Loop through all indexes of the current parameter to vary
    pname = pnames[pi]
    for i in range(int((pgrid[pname][1] - pgrid[pname][0]) * 2 ** (gran-1) + 1)):

        # Update index
        idxs[pname] = pgrid[pname][0] + i * 0.5 ** (gran - 1)

        ################################################################################################################
        #  Recurse into next parameter or add configuration in case you arrived at the last parameter of the list
        ################################################################################################################
        if pi < nrp - 1:

            # Recurse into next parameter
            nr = samplerecursion(pi + 1, pnames, idxs, pgrid, gran, nrp, table, database, nr, vetoing)

        else:
            ############################################################################################################
            #  Add configuration to database (We arrived at the last parameter to recurse into)
            ############################################################################################################

            if vetoing:
                table.insert(dict(th=idxs['Theta_high'], tl=idxs['Theta_low'], ap=idxs['A_LTP'], ad=idxs['A_LTD'],
                                  t1=idxs['tau_lowpass1'], t2=idxs['tau_lowpass2'], tx=idxs['tau_x'],
                                  bt=idxs['b_theta'], tt=idxs['tau_theta']))
            else:
                table.insert(dict(th=idxs['Theta_high'], tl=idxs['Theta_low'], ap=idxs['A_LTP'], ad=idxs['A_LTD'],
                                  t1=idxs['tau_lowpass1'], t2=idxs['tau_lowpass2'], tx=idxs['tau_x']))

            nr += 1

    if pi == 3:
        print(nr)
        database.commit()

    return nr


if __name__ == "__main__":

    if len(argv) != 2:
        raise ValueError("You must add a single integer argument to function call in order to define the job id.")
    else:
        j = int(argv[1])

    # Specifics of the run
    granularity = 1
    protocol_type = 'Letzkus'
    plasticity = 'Claire'
    veto = False

    # Predefine some specifics dependent stuff
    table_name = plasticity + '_veto' if veto else plasticity + '_noveto'
    if granularity == 1 and protocol_type is 'Letzkus' and plasticity is 'Claire' and not veto:
        if j > 63:
            raise ValueError("Job ID must be an integer between 0 and 63")
        param_names = ['Theta_high', 'Theta_low', 'tau_lowpass1', 'tau_lowpass2', 'tau_x']
        grid_params = {'Theta_high': [-0.5, 8.5], 'Theta_low': [-0.5, 8.5], 'tau_lowpass1': [0.5, 6.5],
                       'tau_lowpass2': [0.5, 6.5], 'tau_x': [0.5, 6.5]}
        indcs = {'A_LTP': 0.5 + j % 8, 'A_LTD': 0.5 + floor(float(j) / 8.)}
    else:
        raise NotImplementedError

    # Build ne database and table
    spacedb = dataset.connect("sqlite:///../Data/samplespace_"+protocol_type+"_g"+str(granularity)+"_j"+str(j)+".db")
    spacetab = spacedb.create_table(table_name)

    # Populate database recursively
    totnr = samplerecursion(0, param_names, indcs, grid_params, granularity, len(param_names), spacetab, spacedb, 0, veto)

    print('\nDone after creating a sample space with size {}'.format(totnr))
