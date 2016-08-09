#! /usr/bin/env python

import sys
import subprocess
import time
import tempfile

def instantiate_tempfile(in_fname, s):
    temp = tempfile.NamedTemporaryFile()
    with open(in_fname, 'r') as r:
        for line in r:
            temp.write(line.format(s))
    temp.flush()
    return temp


if __name__ == '__main__':
    
    import argparse 
    parser = argparse.ArgumentParser(description='Download kde training data.')
    parser.add_argument('evttype', type=int, 
                        help='Integer index for the event type. ')
    parser.add_argument('--undersample', type=float, default=1.0,
                        help='Database name. ')
    parser.add_argument('--dbname', default='bdtaunuhad_lite',
                        help='Database name. ')
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

    print "+ downloading..."
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

    print "  done. completed in {0} seconds. \n".format(round(end-start, 2))
    sys.stdout.flush()
