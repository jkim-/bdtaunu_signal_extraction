#! /usr/bin/env python

import sys
import subprocess
import time
import tempfile


if __name__ == '__main__':
    
    import argparse 
    parser = argparse.ArgumentParser(
            description='Compute truth proportion in the test samples. ')
    parser.add_argument('--test', action='store_true',
                        help='Compute truth proportions on tuning sample. ')
    parser.add_argument('--tuning', action='store_true',
                        help='Compute truth proportions on tuning sample. ')
    parser.add_argument('--dbname', default='bdtaunuhad_lite',
                        help='Database name. ')
    parser.add_argument('--verbose', action='store_true',
                        help='Increase verbosity; mainly for debugging. ')

    args = parser.parse_args()

    if args.test == args.tuning:
        print " + No action taken. Please supply either --test or --tuning. "
        sys.exit(1)

    print "+ configurations: \n"
    print "  dbname = {0}".format(args.dbname)
    sys.stdout.flush()

    sql_script = None 
    if args.tuning:
        sql_script = 'sql/compute_truth_tuning_proportion.sql'
        print "  sample type: tuning"
        print "    => query script = {0}".format(sql_script)
        sys.stdout.flush()
    else:
        sql_script = 'sql/compute_truth_test_proportion.sql'
        print "  sample type: test"
        print "    => query script = {0}".format(sql_script)
        sys.stdout.flush()
    print


    verbosity_flag = "-q"
    if args.verbose: 
        verbosity_flag = "-a"

    print "+ querying.\n"
    sys.stdout.flush()

    start = time.time()
    subprocess.check_call(["psql", 
                            verbosity_flag,
                            "-d", args.dbname, 
                            "-f", sql_script])
    end = time.time()

    print "  done. completed in {0} seconds. \n".format(round(end-start, 2))
    sys.stdout.flush()
