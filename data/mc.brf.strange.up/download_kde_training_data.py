#! /usr/bin/env python

import sys
import os
import subprocess
import time
import tempfile

from utils.BrfWeightTable import BrfWeightTable

def instantiate_tempfile(in_fname, s):
    temp = tempfile.NamedTemporaryFile()
    with open(in_fname, 'r') as r:
        for line in r:
            temp.write(line.format(s))
    temp.flush()
    return temp


if __name__ == '__main__':
    
    import argparse 
    parser = argparse.ArgumentParser(
            description='Download kde training data.')
    parser.add_argument('evttype', type=int, 
                        help='Integer index for the event type. ')
    parser.add_argument('--undersample', type=float, default=1.0,
                        help='Database name. ')
    parser.add_argument('--brf_weight_varied_fname', 
                        default='brf_weight_varied.dat',
                        help='Branching fraction weight variations '
                             'configuration file name. ')
    parser.add_argument('--dbname', default='bdtaunuhad_lite',
                        help='Database name. ')
    parser.add_argument('--keep_aux', action='store_true',
                        help='Keep auxiliary file; mainly for debugging. ')
    parser.add_argument('--verbose', action='store_true',
                        help='Increase verbosity; mainly for debugging. ')

    args = parser.parse_args()

    sql_script_template = 'sql/download_training_data_template.sql'
    print "+ configurations: \n"
    print "  evttype = {0}".format(args.evttype)
    print "  undersample = {0}".format(args.undersample)
    print "  dbname = {0}".format(args.dbname)
    print
    sys.stdout.flush()

    print "+ downloading data from database."
    sys.stdout.flush()

    start = time.time()
    temp = instantiate_tempfile(sql_script_template, args.evttype)
    verbosity_flag = "-q"
    if args.verbose: 
        verbosity_flag = "-a"
    subprocess.check_call(["psql", 
                            verbosity_flag,
                            "-d", args.dbname, 
                            "-v", "undersample={0}".format(args.undersample),
                            "-f", temp.name])
    end = time.time()
    temp.close()

    print "  done. completed in {0} seconds. \n".format(round(end-start, 2))
    sys.stdout.flush()

    print "+ converting to training data. "
    sys.stdout.flush()

    start = time.time()

    brf_table = BrfWeightTable(args.brf_weight_varied_fname)

    train_fname = 'evttype{0}.train.csv'.format(args.evttype)
    aux_fname = 'evttype{0}.aux.csv'.format(args.evttype)
    with open(train_fname, 'w') as fout:

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
