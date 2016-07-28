import sys
import subprocess
import time
import tempfile

if __name__ == '__main__':
    
    import argparse 
    parser = argparse.ArgumentParser(description='Download kde training data.')
    parser.add_argument('--dbname', default='bdtaunuhad_lite',
                        help='Database name. ')
    parser.add_argument('--verbose', action='store_true',
                        help='Increase verbosity; mainly for debugging. ')

    args = parser.parse_args()

    sql_script = 'sql/download_test_data.sql'
    print "+ configurations: \n"
    print "  dbname = {0}".format(args.dbname)
    print
    sys.stdout.flush()

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
