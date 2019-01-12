#!/usr/bin/env python

"""
    File name: merge_databases.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 11/01/2019
    Date last modified: 11/01/2019
    Python Version: 3.5
"""

import dataset


if __name__ == "__main__":

    granularity = 1
    protocol_type = 'Letzkus'
    plasticity = 'Claire'
    veto = False

    nrdb = 3

    # Connect with the database where all the results will be merged
    merged_db = dataset.connect('sqlite:///../Data/monteresults_' + protocol_type + '_g' + str(granularity) + '.db')
    table_name = plasticity + '_veto' if veto else plasticity + '_noveto'
    merged_table = merged_db.create_table(table_name)

    for i in range(nrdb):
        db = dataset.connect('sqlite:///../Data/monteresults_'+protocol_type+'_g'+str(granularity)+'_j'+str(i)+'.db')
        table = db.create_table(table_name)
        if veto:
            for row in table.find():
                merged_table.insert(dict(th=row['th'], tl=row['tl'], ap=row['ap'], ad=row['ad'], t1=row['t1'],
                                         t2=row['t2'], tx=row['tx'], bt=row['bt'], tt=row['tt'], score=row['score']))
        else:
            for row in table.find():
                merged_table.insert(dict(th=row['th'], tl=row['tl'], ap=row['ap'], ad=row['ad'], t1=row['t1'],
                                         t2=row['t2'], tx=row['tx'], score=row['score']))
        db.commit()
