BEGIN;

-- 1. Isolate the records of interest
CREATE TEMPORARY TABLE test_eid AS
SELECT eid 
FROM 
  (SELECT eid FROM sample_type_5_generic_dssdpipi_combined) AS Q1
  INNER JOIN
  (SELECT eid FROM sideband_generic WHERE sideband=0
   UNION ALL
   SELECT eid FROM sideband_dssdpipi WHERE sideband=0) AS Q2
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
  (SELECT * FROM candidate_optimized_events_scores_generic_t 
   UNION ALL
   SELECT * FROM candidate_optimized_events_scores_dssdpipi_t) AS q
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
  z1, 
  z2, 
  (brf_correction_weight * 
   cln_weight * llswb1_weight * 
   continuum_logre_density_weight * continuum_logre_normalization_weight) AS w
FROM 
  test_features INNER JOIN event_weights_generic_augmented USING (eid)
;

CREATE TEMPORARY TABLE test_sample_dssdpipi AS
SELECT 
  z1, 
  z2, 
  weight AS w
FROM 
  test_features INNER JOIN event_weights_dssdpipi USING (eid)
;

\copy (SELECT * FROM test_sample UNION ALL SELECT * FROM test_sample_dssdpipi) TO 'tuning.csv' WITH DELIMITER ' ';


COMMIT;


