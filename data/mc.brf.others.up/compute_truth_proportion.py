#! /usr/bin/env python

import os
import sys
import subprocess
import time
import tempfile

from utils.BrfWeightTable import BrfWeightTable

if __name__ == '__main__':
    
    import argparse 
    parser = argparse.ArgumentParser(
            description='Compute truth proportion.')
    parser.add_argument('--test', action='store_true',
                        help='Compute proportion for test sample. ')
    parser.add_argument('--tuning', action='store_true',
                        help='Compute proportion for tuning sample. ')
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
        sql_script = 'sql/download_compute_tuning_proportion.sql'
        print "  sample type: tuning"
        print "    => query script = {0}".format(sql_script)
        sys.stdout.flush()
    else:
        sql_script = 'sql/compute_truth_test_proportion.sql'
        print "  sample type: test"
        print "    => query script = {0}".format(sql_script)
        sys.stdout.flush()
    print

    # Handle test sample
    # ------------------

    if not args.tuning:

        print "+ computing truth proportions. "
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

        print "  done. completed in {0} seconds. \n".format(
                round(end-start, 2))
        sys.stdout.flush()

        exit(0)


    # Handle tuning sample
    # ------------------

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

    print "+ computing truth proportions. "
    sys.stdout.flush()

    start = time.time()

    brf_table = BrfWeightTable(args.brf_weight_variations_fname)

    evttype_sums = [ 0.0 ] * 5

    aux_fname = 'compute_truth.tuning.csv'
    with open(aux_fname, 'r') as fin:

        for line in fin:

            colvals = line.strip().split(' ')

            evttype = int(colvals[0])

            w = float(colvals[1])

            b1_brf_w = brf_table.get_weight(colvals[2])
            b2_brf_w = brf_table.get_weight(colvals[3])

            w = w * b1_brf_w * b2_brf_w

            evttype_sums[evttype-1] += w
    end = time.time()

    weight_sum = sum(evttype_sums)
    print '{0:<10}{1:<30}{2:<30}'.format('evttype', 'weight', 'p')
    for i in range(5):
        print '{0:<10}{1:<30}{2:<30}'.format(
                i+1, evttype_sums[i], evttype_sums[i]/weight_sum)
    print
    sys.stdout.flush()

    print "  done. completed in {0} seconds. \n".format(round(end-start, 2))

    if not args.keep_aux:
        print "+ cleaning up. "
        sys.stdout.flush()
        start = time.time()
        os.remove(aux_fname)
        end = time.time()
        print "  done. completed in {0} seconds. \n".format(
                round(end-start, 2))
        sys.stdout.flush()
