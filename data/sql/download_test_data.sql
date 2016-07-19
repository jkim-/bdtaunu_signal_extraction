BEGIN;

CREATE TEMPORARY TABLE test_eid AS
SELECT eid FROM sample_assignments_generic WHERE sample_type=5;

CREATE INDEX ON test_eid (eid);

CREATE TEMPORARY TABLE scores AS
SELECT 
  eid,
  logit_gbdt300_signal_score AS z1,
  logit_gbdt300_dstartau_score AS z2
FROM 
  candidate_optimized_events_scores_generic_t
WHERE 
  logit_gbdt300_signal_score < 0.5 AND logit_gbdt300_signal_score > -4.0 AND 
  logit_gbdt300_dstartau_score < 3.5 AND logit_gbdt300_dstartau_score > -2.0;

CREATE INDEX ON scores (eid);

\copy (SELECT z1, z2 FROM test_eid INNER JOIN scores USING (eid)) TO 'test.csv';

COMMIT;
