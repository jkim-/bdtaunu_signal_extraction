Overview
---

This directory contains the analysis data viewed under various schemes as well as the code to download them. 

Each sub-directory contains a specific instance of a queried dataset. The datasets currently available and their specific settings are documented below.

Despite the differences for which each dataset is queried, they must contain the following data files: 

1. Training data: `evttypeX.train.csv`, where `X` runs from `1` up to the maximum number of event type components in the query instance.
2. Tuning data: `tuning.csv`. 
2. Test data: `test.csv`. 

Furthermore, all data files must conform to the following standard:
+ 3 columns: `z1`, `z2`, `w`. `z1` and `z2` are the features, and `w` is the record weight. If no weights are desired, set `w` to `1.0`. 
+ Space separated. 
+ No headers. 

To make obtaining the data straighforward, all subdirectories must contain the following scripts that download the training and test data, respectively:

+ `download_kde_training_data.py`: Downloads the training data for the various event type components. Its first positional argument should correspond to the event type code, and should also take an optional argument for undersampling. 

+ `download_test_data.py`: Downloads the test and the tuning. 

The scripts available in this top level directory are general purpose. `subsample.py`, for instance, should not be used as a substitue for the sub-sampling functionality in `download_kde_training_data.py`.

Datasets
---

The following are the datasets that are currently available:

+ `mc.central.logre`: This is the simulated data meant to represent our best knowledge of physics. 

   + Training data source: `candidate_optimized_events_scores_generic_t` joined with `sample_assignment_generic` with `sample_type=6`. Sidebands removed.
   + Test data source: `candidate_optimized_events_scores_generic_t` joined with `sample_assignment_generic` with `sample_type=5`. Sidebands removed.
   + Event type categories: `grouped_dss_evttype`. 
   + `z1`: `logit_logre_signal_score`. 
   + `z2`: `logit_logre_dstartau_score`. 
   + Training `w`: `lumi_weight`, `cln_weight`, `llswb1_weight`, `logre_density_weight`, `logre_normalization_weight`. 
   + Tuning `w`: `lumi_weight`, `cln_weight`, `llswb1_weight`, `logre_density_weight`, `logre_normalization_weight`. 
   + Testing `w`: `cln_weight`, `llswb1_weight`, `logre_density_weight`, `logre_normalization_weight`. `lumi_weight` not included since it was pre-allocated when it was inserted into the database. 
   + Training data undersampling: `[1.0, 1.0, 0.55, 0.14, 0.16]`.


+ `mc.llswb2.logre`: All settings the same as mc.central.logre, except that llswb2 weights are used instead of llswb1 weights. 

   + Training data source: `candidate_optimized_events_scores_generic_t` joined with `sample_assignment_generic` with `sample_type=6`. Sidebands removed.
   + Test data source: `candidate_optimized_events_scores_generic_t` joined with `sample_assignment_generic` with `sample_type=5`. Sidebands removed.
   + Event type categories: `grouped_dss_evttype`. 
   + `z1`: `logit_logre_signal_score`. 
   + `z2`: `logit_logre_dstartau_score`. 
   + Training `w`: `lumi_weight`, `cln_weight`, `llswb2_weight`, `logre_density_weight`, `logre_normalization_weight`. 
   + Tuning `w`: `lumi_weight`, `cln_weight`, `llswb2_weight`, `logre_density_weight`, `logre_normalization_weight`. 
   + Testing `w`: `cln_weight`, `llswb1_weight`, `logre_density_weight`, `logre_normalization_weight`. `lumi_weight` not included since it was pre-allocated when it was inserted into the database. 
   + Training data undersampling: `[1.0, 1.0, 0.55, 0.14, 0.16]`.


+ `mc.linearq2.logre`: All settings the same as mc.central.logre, except that linearq2 weights are used instead of cln weights. 

   + Training data source: `candidate_optimized_events_scores_generic_t` joined with `sample_assignment_generic` with `sample_type=6`. Sidebands removed.
   + Test data source: `candidate_optimized_events_scores_generic_t` joined with `sample_assignment_generic` with `sample_type=5`. Sidebands removed.
   + Event type categories: `grouped_dss_evttype`. 
   + `z1`: `logit_logre_signal_score`. 
   + `z2`: `logit_logre_dstartau_score`. 
   + Training `w`: `lumi_weight`, `linearq2_weight`, `llswb2_weight`, `logre_density_weight`, `logre_normalization_weight`. 
   + Tuning `w`: `lumi_weight`, `linearq2_weight`, `llswb2_weight`, `logre_density_weight`, `logre_normalization_weight`. 
   + Testing `w`: `cln_weight`, `llswb1_weight`, `logre_density_weight`, `logre_normalization_weight`. `lumi_weight` not included since it was pre-allocated when it was inserted into the database. 
   + Training data undersampling: `[1.0, 1.0, 0.55, 0.14, 0.16]`.


+ (NEEDS UPDATE) `mc.default`: This is simulated data based on the defaults of those output from the BABAR framework. 

   + Training data source: `candidate_optimized_events_scores_generic_t` joined with `sample_assignment_generic` with `sample_type=6`.
   + Test data source: `candidate_optimized_events_scores_generic_t` joined with `sample_assignment_generic` with `sample_type=5`.
   + Event type categories: `grouped_dss_evttype`. 
   + `z1`: `logit_gbdt300_signal_score`. 
   + `z2`: `logit_gbdt300_dstartau_score`. 
   + Training `w`: `lumi_weight` in `event_weight_generic_augmented`. 
   + Testing `w`: `1.0`, since was pre-allocated when it was inserted into the database. 
   + Training data undersampling: `[1.0, 1.0, 0.55, 0.14, 0.14]`.


Event type reference
---

The following is a quick reference for the various event type category codes:

+ `grouped_dss_evttype`:
    1. Dtau.
    2. D\*tau.
    3. D\*\* SL.
    4. SLhad.
    5. Cont.
