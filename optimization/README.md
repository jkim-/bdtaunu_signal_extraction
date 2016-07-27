Optimizer
=== 

This directory contains code that determines the component proportions by solving maximum likelihood. It bootstraps the cached KDE samples a number of times and outputs the results in one `csv` file. 

The top level directory contains code common to all sub-problems. Just type `make` at this level. 

Each sub-directory contains the specific configurations for each problem instance. The typical procedure is as follows:

1. Run `precompute_component_densities` to cache KDE evaluations for each data point. See `precompute_component_densities.cfg` to see what parameters are configurable. 

2. Solve optimization problem using the cached KDE evalutions:

+ Run `mle_cvxnl.py`. You can use many See help message for usage. 
+ When large number of iterations are required, you can also use `condor_mle_cvxnl.py`. It simply distributes `mle_cvxnl.py` to many nodes in `condor`. To run this, you must adjust a configuration file; see help message and `condor_mle_cvxnl.cfg` for an example. 

3. If you used `condor_mle_cvxnl.py`, you can run `collect_condor_mle_cvxnl_results.py` to gather the results. 

4. Inspect the results. Steps 2 and 3 outputs a file that contains a single bootstrap result on each line. The following are methods that are used to summarize the result for this analysis:

+ You can run `poll_results.py` to get a quick estimate of the bootstrap results. 

+ Use `mle_visual.ipynb` to perform a Gaussian fit. 
