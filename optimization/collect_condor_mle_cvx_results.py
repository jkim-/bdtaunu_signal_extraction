#!/usr/bin/env python

import sys
import os

if __name__ == '__main__':

  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('input_dir', help='Directory containing individual results' 
                                        ' output by all condor nodes.')
  parser.add_argument('output_dir', help='Directory to write the results.')
  parser.add_argument('--output_fname', type=str, default='condor_mle_cvxnl_results.csv', 
                      help='File name to write the results.')
  args = parser.parse_args()

  output_fname = args.output_dir + '/' + args.output_fname

  file_list = os.listdir(args.input_dir)
  with open(output_fname, 'w') as w:
    for fname in file_list:
      sys.stdout.write('Copying {0}...\n'.format(fname))
      sys.stdout.flush()
      with open(args.input_dir + '/' + fname, 'r') as f:
        for line in f:
          w.write(line)
  print 'Done.'
