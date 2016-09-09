#! /usr/bin/env python

import os
import sys
import subprocess
import time
import tempfile

from utils.BrfWeightTable import BrfWeightTable

if __name__ == '__main__':
    
    import argparse 
    parser = argparse.ArgumentParser(description='Download test data.')
    parser.add_argument('--test', action='store_true',
                        help='Download the test sample. ')
    parser.add_argument('--tuning', action='store_true',
                        help='Download the tuning sample. ')
    parser.add_argument('--brf_weight_variations_fname',
                        default='brf_weight_variations.dat',
                        help='Branching fraction weight variations '
                             'configuration file name. ')
    parser.add_argument('--dbname', default='bdtaunuhad_lite',
                        help='Database name. ')
    parser.add_argument('--keep_aux', action='store_true',
                        help='Keep auxiliary file; mainly for debugging. ')
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

    print "+ downloading data from database. "
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

    # stop here if downloading test sample
    if not args.tuning:
        exit(0)

    print "+ converting to tuning data. "
    sys.stdout.flush()

    start = time.time()

    brf_table = BrfWeightTable(args.brf_weight_variations_fname)

    tuning_fname = 'tuning.csv'
    aux_fname = 'tuning.aux.csv'
    with open(tuning_fname, 'w') as fout:

        with open(aux_fname, 'r') as fin:

            for line in fin:

                colvals = line.strip().split(' ')

                w = float(colvals[2])

                b1_brf_w = brf_table.get_weight(colvals[3])
                b2_brf_w = brf_table.get_weight(colvals[4])

                w = w * b1_brf_w * b2_brf_w

                outvals = [ colvals[0], colvals[1], str(w) ]

                fout.write(' '.join(outvals) +'\n')


    end = time.time()

    print "  done. completed in {0} seconds. \n".format(round(end-start, 2))
    sys.stdout.flush()

    if not args.keep_aux:
        print "+ cleaning up. "
        sys.stdout.flush()
        start = time.time()
        os.remove(aux_fname)
        end = time.time()
        print "  done. completed in {0} seconds. \n".format(round(end-start, 2))
        sys.stdout.flush()
