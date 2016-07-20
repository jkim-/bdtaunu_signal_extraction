BEGIN;

CREATE TEMPORARY TABLE test_eid AS
SELECT eid FROM sample_assignments_generic WHERE sample_type=5;

CREATE INDEX ON test_eid (eid);

CREATE TEMPORARY TABLE scores AS
SELECT 
  eid,
  logit_logre_signal_score AS z1,
  logit_logre_dstartau_score AS z2
FROM 
  candidate_optimized_events_scores_generic_t
WHERE 
  logit_logre_signal_score < 0.0 AND logit_logre_signal_score > -5.0 AND 
  logit_logre_dstartau_score < 5.0 AND logit_logre_dstartau_score > -1.5;

CREATE INDEX ON scores (eid);

\copy (SELECT z1, z2 FROM test_eid INNER JOIN scores USING (eid)) TO 'test.csv';

COMMIT;
