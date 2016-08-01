#! /usr/bin/env python

import argparse
import subprocess

parser = argparse.ArgumentParser(description='Batch produce visualization data. ')
parser.add_argument('evttypes', type=int, nargs='+',
                   help='any combination of the numeric codes infixed in a cfg file. ')
args = parser.parse_args()

print

print 'Will launch the following event types: {0}'.format(args.evttypes)

fname_prefix = 'evttype'

print 'To monitor progress, use the following command in the shell: '
print '  tail -f {0}[i].out\n'.format(fname_prefix)

for evttype in args.evttypes:

  print 'Producing individual component data for {0}{1}...'.format(fname_prefix, evttype)

  out_fname = '{0}{1}.out'.format(fname_prefix, evttype)
  cfg_fname = '{0}{1}.cfg'.format(fname_prefix, evttype)
  with open(out_fname, 'w') as f: 
    subprocess.check_call(
        ['../visualize_individual_components', cfg_fname], 
         stdout=f)

print 'Producing stacked component data...'
cfg_fname = '/stacked_components.cfg'
with open(out_fname, 'w') as f: 
    subprocess.check_call(
        ['../visualize_stacked_components', cfg_fname], 
         stdout=f)

print
print 'Done. '
