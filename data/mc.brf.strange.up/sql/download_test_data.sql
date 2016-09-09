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
  eid,
  logit_logre_signal_score AS z1,
  logit_logre_dstartau_score AS z2
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

-- 3. Join records with the weights and labels
CREATE TEMPORARY TABLE test_sample AS
SELECT 
  z1, 
  z2, 
  (brf_correction_weight * 
   cln_weight * llswb1_weight * 
   continuum_logre_density_weight * continuum_logre_normalization_weight) AS w,
  grouped_dss_evttype AS evttype
FROM 
  (test_features INNER JOIN event_weights_generic_augmented USING (eid)) AS Q
  INNER JOIN
  event_labels_generic_augmented USING (eid)

;


-- 4. Tally the proportions
SELECT
  evttype, 
  SUM(w), 
  SUM(w) / (SELECT SUM(w) FROM test_sample) AS p
FROM test_sample
GROUP BY evttype
ORDER BY evttype;

-- 5. Download to CSV
\copy (SELECT z1, z2, w FROM test_sample) TO 'test.csv' WITH DELIMITER ' ';


COMMIT;


