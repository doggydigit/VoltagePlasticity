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
    granularity = 1
    algo = 'samplespace_'
    protocol_type = 'Letzkus'
    plasticity = 'Claire'
    veto = False

    # Predefine some specifics dependent stuff
    if granularity == 0 and protocol_type == 'Letzkus' and plasticity == 'Claire' and not veto \
            and algo == 'monteresults_':
        nrdb = 81
    elif granularity == 0 and protocol_type is 'Letzkus' and plasticity is 'Claire' and not veto \
            and algo == 'monteresults_':
        nrdb = 91
    if granularity == 1 and protocol_type == 'Letzkus' and plasticity == 'Claire' and not veto \
            and algo == 'samplespace_':
        nrdb = 64
    else:
        raise NotImplementedError

    # Connect with the database where all the results will be merged and create the table that will contain it
    merged_db = dataset.connect('sqlite:///../Data/' + algo + protocol_type + '_g' + str(granularity) + '.db')
    table_name = plasticity + '_veto' if veto else plasticity + '_noveto'
    if veto:
        raise NotImplementedError
    else:
        if algo == 'monteresults_':
            merged_db.query("CREATE TABLE IF NOT EXISTS " + table_name + " (id INTEGER PRIMARY KEY, th REAL, tl REAL," +
                            " ap REAL, ad REAL, t1 REAL, t2 REAL, tx REAL, li REAL, l2 REAL);")
        elif algo == 'samplespace_':
            merged_db.query("CREATE TABLE IF NOT EXISTS " + table_name + " (id INTEGER PRIMARY KEY, th REAL, tl REAL," +
                            " ap REAL, ad REAL, t1 REAL, t2 REAL, tx REAL);")
        else:
            raise NotImplementedError(algo)

    merged_db.commit()

    maxid = 0

    # Add the databases one by one to the merged database
    for i in range(nrdb):

        print('Base {}'.format(i))

        merged_db.query("BEGIN;")
        merged_db.query("ATTACH DATABASE '../Data/" + algo + protocol_type + "_g" + str(granularity) + "_j"
                        + str(i) + ".db' AS candidate;")
        if veto:
            raise NotImplementedError
        else:
            if algo == 'monteresults_':
                merged_db.query("INSERT INTO main." + table_name + " SELECT id+" + str(maxid)
                                + ", th, tl, ap, ad, t1, t2, tx, li, l2 FROM candidate." + table_name + ";")
            elif algo == 'samplespace_':
                merged_db.query("INSERT INTO main." + table_name + " SELECT id+" + str(maxid)
                                + ", th, tl, ap, ad, t1, t2, tx FROM candidate." + table_name + ";")
            else:
                raise NotImplementedError
        maxid += next(merged_db.query("SELECT max(id) FROM candidate." + table_name + ";"))['max(id)']
        merged_db.query("DETACH DATABASE candidate;")
        merged_db.commit()

    # Remove rows that weren't finished with simulating
    merged_table = merged_db.create_table(table_name)
    merged_table.delete(score=9999999999999999)
    merged_db.commit()

    print('\nDone')
