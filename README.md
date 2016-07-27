Code for signal extraction and systematics
===

For each problem instance, specialize a directory in each of `data`, `cross_validation`, `optimization`, and `visualization`. You can copy/clone an existing instance for each step. 

The following are the steps for each problem instance. All code and data should be placed into the specialized directory instance that resides in the directory listed in the correspodining bullet. For instance, in step 1, put everything in `data/instance_name`.

1. `data`: Obtain data that conforms to the description described there. It should contain both the data and code that are input into the optimization.
2. `cross_validation`: Run a grid search to find a course, but a good guess, of the bandwidths. 
3. `optimization`: two substeps. 

    1. Fine tune the bandwidths such that the optimization result is unbiased on some reference data. 
    2. Run a sufficiently large number of boostrap instances of the optimization using the test data. A visualization notebook is provided to view the results. 
4. `visualization`: Some visualization notebooks to inspect the final component densities and the stacked densities using the minimizers output from the optimizer. 
