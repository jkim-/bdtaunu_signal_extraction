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
    parser.add_argument('--brf_weight_varied_fname',
                        default='brf_weight_varied.dat',
                        help='Branching fraction weight variations '
                             'configuration file name. ')
    parser.add_argument('--brf_weight_default_fname',
                        default='brf_weight_default.dat',
                        help='Default branching fraction weights '
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

    print "+ querying database. "
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

    brf_table_default = BrfWeightTable(args.brf_weight_default_fname)
    brf_table_varied = BrfWeightTable(args.brf_weight_varied_fname)

    # first pass: compute weight normalization 
    w_default_dict, w_varied_dict = {}, {}
    aux_fname = 'tuning.aux.csv'
    with open(aux_fname, 'r') as fin:

        for line in fin:

            colvals = line.strip().split(' ')

            w = float(colvals[2])
            b1_mode, b2_mode = colvals[3], colvals[4]
            evttype = colvals[5]

            b1_brf_w_default = brf_table_default.get_weight(b1_mode)
            b2_brf_w_default = brf_table_default.get_weight(b2_mode)
            w_default = w * b1_brf_w_default * b2_brf_w_default

            b1_brf_w_varied = brf_table_varied.get_weight(b1_mode)
            b2_brf_w_varied = brf_table_varied.get_weight(b2_mode)
            w_varied = w * b1_brf_w_varied * b2_brf_w_varied

            if evttype not in w_default_dict:
                w_default_dict[evttype] = w_default
                w_varied_dict[evttype] = w_varied
            else:
                w_default_dict[evttype] += w_default
                w_varied_dict[evttype] += w_varied

    w_norm_dict = {}
    w_default_sum, w_varied_sum = 0.0, 0.0
    for evttype in w_default_dict.keys():
        w_default_sum += w_default_dict[evttype]
        w_varied_sum += w_varied_dict[evttype]
        w_norm_dict[evttype] = w_default_dict[evttype] / w_varied_dict[evttype]

    print '  truth proportions: \n'
    print '{0:<10}{1:<20}{2:<20}{3:<20}{4:<20}'.format('evttype', 'default w', 'varied w', 'adjusted w', 'tuning p')
    for i in sorted(w_norm_dict.keys()):
        print '{0:<10}{1:<20}{2:<20}{3:<20}{4:<20}'.format(
                i, 
                w_default_dict[i], 
                w_varied_dict[i], 
                w_varied_dict[i]*w_norm_dict[i], 
                w_varied_dict[i]*w_norm_dict[i]/w_default_sum)
    print
    sys.stdout.flush()

    # second pass: write out tuning data
    tuning_fname = 'tuning.csv'
    with open(tuning_fname, 'w') as fout:

        with open(aux_fname, 'r') as fin:

            for line in fin:

                colvals = line.strip().split(' ')

                w = float(colvals[2])
                b1_mode, b2_mode = colvals[3], colvals[4]
                evttype = colvals[5]

                b1_brf_w_varied = brf_table_varied.get_weight(b1_mode)
                b2_brf_w_varied = brf_table_varied.get_weight(b2_mode)

                w_varied = w * b1_brf_w_varied * b2_brf_w_varied * w_norm_dict[evttype]

                outvals = [ colvals[0], colvals[1], str(w_varied) ]

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
