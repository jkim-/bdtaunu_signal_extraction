BEGIN;

CREATE TEMPORARY TABLE evttype_kde_sample AS
SELECT
  eid 
FROM 
  (SELECT * 
   FROM 
     (sample_assignments_generic 
      INNER JOIN  
      event_labels_generic_augmented
      USING (eid))
   WHERE 
     sample_type=6 AND
     grouped_dss_evttype=4) AS Q
WHERE random() < 0.01;

CREATE INDEX ON evttype_kde_sample (eid);


CREATE TEMPORARY VIEW training_sample AS
SELECT 
  logit_gbdt300_signal_score AS z1,
  logit_gbdt300_dstartau_score AS z2,
  lumi_weight AS w
FROM 
  (evttype_kde_sample INNER JOIN event_weights_generic_augmented USING (eid))
  INNER JOIN 
  candidate_optimized_events_scores_generic_t USING (eid)
WHERE 
  logit_gbdt300_signal_score < 0.5 AND logit_gbdt300_signal_score > -4.0 AND 
  logit_gbdt300_dstartau_score < 3.5 AND logit_gbdt300_dstartau_score > -2.0;

\copy (SELECT * FROM training_sample) TO 'evttype4.train.csv' WITH CSV HEADER DELIMITER ' '

COMMIT;
