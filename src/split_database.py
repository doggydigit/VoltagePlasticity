#!/usr/bin/env python

"""
    File name: split_databases.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 11/01/2019
    Date last modified: 11/01/2019
    Python Version: 3.5
"""

import dataset
from math import floor


if __name__ == "__main__":

    # Specifics of the run
    granularity = 0
    protocol_type = 'Letzkus'
    plasticity = 'Claire'
    veto = False

    # Predefine some specifics dependent stuff
    table_name = plasticity + '_veto' if veto else plasticity + '_noveto'
    if granularity == 0 and protocol_type is 'Letzkus' and plasticity is 'Claire' and not veto:
        nrdb = 91
    else:
        raise NotImplementedError

    # Create database splits one by one
    for i in range(nrdb):

        print('Base {}'.format(i))

        db = dataset.connect('sqlite:///../Data/monteresults_'+protocol_type+'_g'+str(granularity+1)+"_j"+str(i)+'.db')
        db.query("CREATE TABLE IF NOT EXISTS "+table_name+" (id INTEGER PRIMARY KEY AUTOINCREMENT, th REAL, tl REAL,"
                                                          " ap REAL, ad REAL, t1 REAL, t2 REAL, tx REAL, score REAL);")
        db.commit()

        db.query("BEGIN;")
        db.query("ATTACH DATABASE '../Data/monteresults_"+protocol_type+"_g"+str(granularity)+".db' AS candidate;")

        if granularity == 0 and protocol_type is 'Letzkus' and plasticity is 'Claire' and not veto:
            itl = str((i % 13) * 0.5 + 2)
            iad = str(int(floor(float(i) / 13.) + 1))
            condition = "tl = " + itl + " AND ad = " + iad
        else:
            raise NotImplementedError

        db.query("INSERT INTO main." + table_name + " SELECT NULL, th, tl, ap, ad, t1, t2, tx, score FROM candidate."
                 + table_name + " WHERE " + condition + ";")
        db.query("DETACH DATABASE candidate;")
        db.commit()

    print('\nDone')
