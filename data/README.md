Data download scripts
---

+ `download_kde_trainig_data.py`: Downloads the data from the table `candidate_optimized_events_scores_generic_t` of database `bdtaunuhad_lite` into a csv file, which represent the generic MC. The following are basic instructions for use, use `python download_kde_trainig_data -h` to see the full set of available parameters. 

  Input (required): event type index. 

    Presently, the event type index is `grouped_dss_evttype`, which has the following index convention:
    + 1: Dtau.
    + 2: D\*tau.
    + 3: D\*\* SL.
    + 4: SLhad.
    + 5: Cont.

  Output: CSV file of 3 columns, (`z1`, `z2`, `w`). 

    Presently, the columns contain values for the follwoing:
    + `z1`: `logit_gbdt300_signal_score`.
    + `z2`: `logit_gbdt300_dstartau_score`.
    + `w`: `lumi_weight`.


  Undersampling (optional):

    At present, the number of rows in the database requires the following undersampling to get at most ~1M points in each file:
    + 1: 1.0
    + 2: 1.0
    + 3: 0.55
    + 4: 0.14
    + 5: 0.14
