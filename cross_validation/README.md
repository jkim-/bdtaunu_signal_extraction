Component cross validation
===

This directory contains configurations to grid search cross validate density components. Just type `make` at this level. 

Each sub-directory corresponds to a specific dataset. To perform grid search on them, do the following:
1. `cd` into the directory of interest. 
2. Type `make` to establish symlinks.
3. Configure the `evttype[x].cfg` files that `grid_search` requires.
4. Run `batch_grid_search.py` using all the event type codes as the argument. 
5. Grid search will produce some visualization data. You can use the notebooks to visualize the result. 
