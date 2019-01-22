#!/usr/bin/env python

"""
    File name: model_distribution.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 21/01/2018
    Date last modified: 22/01/2019
    Python Version: 3.5
"""

import dataset
import random
from sys import argv
from os.path import isfile


if __name__ == "__main__":

    ####################################################################################################################
    #  Initialize variables specfic to the current run
    ####################################################################################################################

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
        threshold = 3000
        prealgo = "monte"
        totnr = 2195200
        nrsplits = 64
        if totnr % nrsplits != 0:
            raise ValueError("{} rows cannot be equally split between {} nodes.".format(totnr, nrsplits))
    else:
        raise NotImplementedError

    if not isfile("../Data/samplespace_" + protocol_type + "_g" + str(granularity) + ".db"):
        raise EnvironmentError("You must call build_space.py (with correct specs) and merge databases before this.")

    ####################################################################################################################
    #  Connect to all 3 databases that will be used for this script (old, new and sample space data base)
    ####################################################################################################################

    # Database containing the results from the simulations of the configurations with granularity - 1
    oldb = dataset.connect("sqlite:///../Data/"+prealgo+"results_"+protocol_type+"_g"+str(granularity-1)+".db")
    oldtab = oldb.create_table(table_name)

    # Database that will contain the new results
    newdb = dataset.connect("sqlite:///../Data/sampleresults_"+protocol_type+"_g"+str(granularity)+"_j"+str(j)+".db")
    newtab = newdb.create_table(table_name)

    # Database with all the potential configurations that will be used to randomly split the search space among nodes
    spacedb = dataset.connect("sqlite:///../Data/samplespace_" + protocol_type + "_g" + str(granularity) + ".db")
    spacetab = spacedb.create_table(table_name)

    # Get row ids of the configurations that will be sampled from by the split defined by the id "j"
    idxs = list(range(int(j * totnr / nrsplits), int((j + 1) * totnr / nrsplits)))
    random.seed(1)
    allids = list(range(totnr))
    random.shuffle(allids)
    samples = [allids[i] for i in idxs]
    del allids

    ####################################################################################################################
    #  Iterate through samples and use the maximal score among the neighbors to derive the sampling probability
    ####################################################################################################################
    crp = 0.0
    nh = 0.5 ** granularity
    nri = 0
    for s in samples:

        print(nri)
        nri += 1

        # Get the configuration corresponding to the sample id
        q = spacetab.find_one(id=s)
        print(s)
        print(q)

        # Get neighbors from previous simulation results (with lower granularity)
        if veto:
            neighbors = oldtab.find(ap=[q['ap']-nh, q['ap']+nh], ad=[q['ad']-nh, q['ad']+nh],
                                    th=[q['th']-nh, q['th']+nh], tl=[q['tl']-nh, q['tl']+nh],
                                    t1=[q['t1']-nh, q['t1']+nh], t2=[q['t2']-nh, q['t2']+nh],
                                    tx=[q['tx']-nh, q['tx']+nh], bt=[q['bt']-nh, q['bt']+nh],
                                    tt=[q['tt']-nh, q['tt']+nh])
        else:
            neighbors = oldtab.find(ap=[q['ap']-nh, q['ap']+nh], ad=[q['ad']-nh, q['ad']+nh],
                                    th=[q['th']-nh, q['th']+nh], tl=[q['tl']-nh, q['tl']+nh],
                                    t1=[q['t1']-nh, q['t1']+nh], t2=[q['t2']-nh, q['t2']+nh],
                                    tx=[q['tx']-nh, q['tx']+nh])

        # Compute relative probability score
        relprob = threshold
        for n in neighbors:
            if relprob > n['l2']:
                relprob = n['l2']

        # If the relative probability score is sufficiently low
        if relprob < threshold:

            # Compute the cumulative relative probability
            crp += threshold - relprob

            # Add it to the actual sample space database with its cumulative relative probability
            if veto:
                newtab.insert(ap=q['ap'], ad=q['ad'], th=q['th'], tl=q['tl'], t1=q['t1']-nh, t2=q['t2'], tx=q['tx'],
                              bt=q['bt'], tt=q['tt'], li=9999999999999999, l2=9999999999999999, crp=crp)
            else:
                newtab.insert(ap=q['ap'], ad=q['ad'], th=q['th'], tl=q['tl'], t1=q['t1'] - nh, t2=q['t2'], tx=q['tx'],
                              li=9999999999999999, l2=9999999999999999, crp=crp)
            newdb.commit()

    # Finally normalize the relative cumulative probability to get the actual cumulative sampling probability
    newdb.query("BEGIN;")
    newdb.query("UPDATE " + table_name + " SET crp = crp / " + crp + ";")
    newdb.query("END;")
    newdb.commit()

    print('\nDone')
