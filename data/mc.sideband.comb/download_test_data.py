#! /usr/bin/env python

import sys
import subprocess
import time
import tempfile

if __name__ == '__main__':
    
    import argparse 
    parser = argparse.ArgumentParser(description='Download test data.')
    parser.add_argument('--test', action='store_true',
                        help='Download the test sample. ')
    parser.add_argument('--tuning', action='store_true',
                        help='Download the tuning sample. ')
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
        sql_script = 'sql/download_tuning_data.sql'
        print "  sample type: tuning"
        print "    => query script = {0}".format(sql_script)
        sys.stdout.flush()
    else:
        sql_script = 'sql/download_test_data.sql'
        print "  sample type: test"
        print "    => query script = {0}".format(sql_script)
        sys.stdout.flush()
    print

    print "+ downloading..."
    sys.stdout.flush()

    start = time.time()
    verbosity_flag = "-q"
    if args.verbose: 
        verbosity_flag = "-a"
    subprocess.check_call(["psql", 
                            verbosity_flag,
                            "-d", args.dbname, 
                            "-f", sql_script])
    end = time.time()

    print "  done. completed in {0} seconds. \n".format(round(end-start, 2))
    sys.stdout.flush()
