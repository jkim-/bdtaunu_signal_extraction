BEGIN;

-- 1. Isolate the records of interest
CREATE TEMPORARY TABLE test_eid AS
SELECT eid 
FROM 
  (SELECT eid FROM sample_assignments_generic WHERE sample_type=5) AS Q1
  INNER JOIN
  (SELECT eid FROM sideband_generic WHERE sideband=0) AS Q2
  USING (eid)
;

CREATE INDEX ON test_eid (eid);


-- 2. Join records with the features
CREATE TEMPORARY TABLE test_features AS
SELECT 
  eid
FROM 
  test_eid
  INNER JOIN 
  candidate_optimized_events_scores_generic_t 
  USING (eid)
WHERE 
  logit_gbdt300_signal_score IS NOT NULL AND 
  logit_gbdt300_dstartau_score IS NOT NULL AND 
  logit_logre_signal_score IS NOT NULL AND 
  logit_logre_dstartau_score IS NOT NULL
;
  
CREATE INDEX ON test_features (eid);


-- 3. Join records with the weights
CREATE TEMPORARY TABLE test_sample AS
SELECT 
  eid,
  (brf_correction_weight * 
   cln_weight * llswb1_weight * 
   continuum_logre_density_weight * continuum_logre_normalization_weight) AS w
FROM 
  test_features INNER JOIN event_weights_generic_augmented USING (eid)
;

CREATE INDEX ON test_sample (eid);


-- 4. Join records with the event type labels
CREATE TEMPORARY TABLE test_sample_labeled AS
SELECT 
  grouped_dss_evttype AS evttype,
  w
FROM 
  test_sample INNER JOIN event_labels_generic_augmented USING (eid)
;

-- 5. Tally the proportions
SELECT
  evttype, 
  SUM(w), 
  SUM(w) / (SELECT SUM(w) FROM test_sample_labeled) AS p
FROM test_sample_labeled
GROUP BY evttype
ORDER BY evttype;


COMMIT;


