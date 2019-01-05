#!/usr/bin/env python

"""
    File name: preprocess.py
    Author: Matthias Tsai
    Email: matthias.chinyen.tsai@gmail.com
    Date created: 27/12/2018
    Date last modified: 28/12/2018
    Python Version: 3.5
"""

import pandas as pd
import numpy as np

if __name__ == "__main__":
    """
    Removes unnecessary columns and rows from the original data and renormalizes it using the average of the first rows
    of each column as baseline. The preprocessed voltage traces are then saved in a new csv file. Also saves each 
    individual trace to a numpy array in its corresponding npy file.
    """

    # Clean Brandalise voltage traces
    c = pd.read_csv('../Data/Brandalise_traces.csv', header=None)
    c.drop([25, 26], 'columns', inplace=True)
    for i in range(c.shape[1]):
        c[i] = c[i] - np.mean(c[i][11])
    c.drop(list(range(11)), inplace=True)
    c.to_csv('../Data/Brandalise_clean.csv', header=None, index=False)

    # Clean Letzkus voltage traces
    c = pd.read_csv('../Data/Letzkus_traces.csv', header=None)
    c.drop([0, 1], 'columns', inplace=True)
    for i in range(2, c.shape[1] + 2):
        c[i] = c[i] - np.mean(c[i][5])
    c.drop(list(range(5)), inplace=True)
    c = 1000 * c  # Letzkus is in volts, so we convert to mV
    c.to_csv('../Data/Letzkus_clean.csv', header=None, index=False)

    # Save traces to numpy arrays for Brandalise
    c = pd.read_csv('../Data/Brandalise_clean.csv', header=None)
    for i in range(c.shape[1]):
        a = c.as_matrix([i])
        a = a[~np.isnan(a)]
        a = np.append(a, [0.0] * (100000 - len(a)))
        np.save('../Data/B_{}'.format(i), a)

    # Save traces to numpy arrays for Letzkus
    c = pd.read_csv('../Data/Letzkus_clean.csv', header=None)
    for i in range(c.shape[1]):
        a = c.as_matrix([i])
        a = a[~np.isnan(a)]
        a = np.append(a, [0.0] * (10000 - len(a)))
        np.save('../Data/L_{}'.format(i), a)
