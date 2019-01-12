#!/usr/bin/env python

"""
    File name: merge_databases.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 11/01/2019
    Date last modified: 12/01/2019
    Python Version: 3.5
"""

import dataset


if __name__ == "__main__":

    # Specifics of the run
    granularity = 0
    protocol_type = 'Letzkus'
    plasticity = 'Claire'
    veto = False
    nrdb = 81

    # Connect with the database where all the results will be merged and create the table that will contain it
    merged_db = dataset.connect('sqlite:///../Data/monteresults_' + protocol_type + '_g' + str(granularity) + '.db')
    table_name = plasticity + '_veto' if veto else plasticity + '_noveto'
    merged_db.query("CREATE TABLE IF NOT EXISTS " + table_name + " (id INTEGER PRIMARY KEY, th REAL, tl REAL, ap REAL, "
                    "ad REAL, t1 REAL, t2 REAL, tx REAL, score REAL);")
    merged_db.commit()

    maxid = 0

    # Add the databases one by one to the merged database
    for i in range(nrdb):

        print('Job {}'.format(i))

        merged_db.query("BEGIN;")
        merged_db.query("ATTACH DATABASE '../Data/monteresults_" + protocol_type + "_g" + str(granularity) + "_j"
                        + str(i) + ".db' AS candidate;")
        merged_db.query("INSERT INTO main." + table_name + " SELECT id+" + str(maxid)
                        + ", th, tl, ap, ad, t1, t2, tx, score FROM candidate." + table_name + ";")
        maxid += next(merged_db.query("SELECT max(id) FROM candidate." + table_name + ";"))['max(id)']
        merged_db.query("DETACH DATABASE candidate;")
        merged_db.commit()

    merged_table = merged_db.create_table('table_name')
    print(merged_table.count())
    merged_table.delete(score=9999999999999999)
    merged_db.commit()
    print(merged_table.count())

    print('\nDone')
