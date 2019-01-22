# VoltagePlasticity

Protocol

1) Preprocess data with preprocess.py

2) Parameter search
    2.1) Grid search with gridsearch.py for full brute parameter search within desired grid range
    2.2) Monte Carlo search with montesearch with increasing granularity. Use merge_databases.py followed by split_database.py when increasing granularity to create a new database distribution of the parameter configurations to simulate in order to have equal parameter search space between computing nodes.
    2.3) Distribution sampling by first evaluating the distribution through a low granularity grid or MC search. Follow by merging all node databases and apply model_distribution.py to evaluate the lower granularity parameter search space distribution that will be used for sampling and create the databases that will be used to distribute simulation computation. Finally run samplesearch.py to actually sample and siumulate the lower granularity configurations.
