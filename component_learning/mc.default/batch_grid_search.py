#! /local/dchao/software/anaconda2/bin/python

import argparse
import subprocess

parser = argparse.ArgumentParser(description='Grid search launcher. ')
parser.add_argument('--skip_cross_validation', action='store_true',
                   help='Whether to skip cross validation')
parser.add_argument('--adapted', action='store_true',
                   help='Perform adapted cross validation. ')
parser.add_argument('evttypes', type=int, nargs='+',
                   help='any combination of the numeric codes infixed in a cfg file. ')
args = parser.parse_args()

print

print 'Will launch the following event types: {0}'.format(args.evttypes)
print 'Skipping cross validation: {0}\n'.format(args.skip_cross_validation)
print 'Adapted cross validation: {0}\n'.format(args.adapted)

fname_prefix = 'evttype'
if args.adapted: fname_prefix = 'adapted_' + fname_prefix

print 'To monitor progress, use the following command in the shell: '
print '  tail -f {0}[i].out\n'.format(fname_prefix)

for evttype in args.evttypes:

  print 'Processing {0}{1}.'.format(fname_prefix, evttype)

  out_fname = '{0}{1}.out'.format(fname_prefix, evttype)
  cfg_fname = '{0}{1}.cfg'.format(fname_prefix, evttype)
  with open(out_fname, 'w') as f: 
    subprocess.check_call(
        ['./grid_search', 
         '--skip_cross_validation={0}'.format(int(args.skip_cross_validation)), 
         cfg_fname], 
         stdout=f)

print
print 'Done. '
