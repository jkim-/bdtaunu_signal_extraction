BEGIN;

-- 1. Isolate the records of interest
CREATE TEMPORARY TABLE evttype_eid AS
SELECT
  eid 
FROM 
  -- Isolate sample type and event type.
  (SELECT eid
   FROM 
     (sample_type_6_generic_dssdpipi_combined 
      INNER JOIN  
      (SELECT * FROM event_labels_generic_augmented
        UNION ALL
        SELECT * FROM event_labels_dssdpipi_augmented) AS q
      USING (eid))
   WHERE 
     grouped_dss_evttype={0}) AS Q1

  INNER JOIN 

  -- Isolate non-sideband
  (SELECT eid
   FROM (SELECT * FROM sideband_generic
         UNION ALL
         SELECT * FROM sideband_dssdpipi) AS q
   WHERE sideband=0) AS Q2

  USING (eid)

-- undersampling
WHERE random() < :undersample;
;

CREATE INDEX ON evttype_eid (eid);


-- 2. Join records with the features
CREATE TEMPORARY TABLE evttype_features AS
SELECT 
  eid,
  logit_logre_signal_score AS z1,
  logit_logre_dstartau_score AS z2
FROM 
  evttype_eid 
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
  
CREATE INDEX ON evttype_features (eid);

-- 3. Join records with the weights
CREATE TEMPORARY TABLE evttype_training_generic AS
SELECT 
  z1, 
  z2, 
  (lumi_weight * 
   brf_correction_weight * 
   cln_weight * llswb1_weight * 
   continuum_logre_density_weight * continuum_logre_normalization_weight) AS w
FROM 
  evttype_features INNER JOIN event_weights_generic_augmented USING (eid)
;

CREATE TEMPORARY TABLE evttype_training_dssdpipi AS
SELECT 
  z1, 
  z2, 
  weight AS w
FROM 
  evttype_features INNER JOIN event_weights_dssdpipi USING (eid)
;

\copy (SELECT * FROM evttype_training_generic UNION ALL SELECT * FROM evttype_training_dssdpipi) TO 'evttype{0}.train.csv' WITH DELIMITER ' ';

COMMIT;

