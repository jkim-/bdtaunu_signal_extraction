#!/usr/bin/env python

import sys
import os
import datetime
import tempfile
import subprocess

def write_condor_submit_file(fout, output_dirname, node_idx, config_parser):

    # assemble file names to place output
    result_fname = '{0}/result/{1}.csv'.format(output_dirname, node_idx)
    out_fname = '{0}/out/{1}.out'.format(output_dirname, node_idx)
    err_fname = '{0}/err/{1}.err'.format(output_dirname, node_idx)
    log_fname = '{0}/log/{1}.log'.format(output_dirname, node_idx)

    # assemble cached file names for the optimizer
    cached_densities_path = '{0}/{1}'.format(config_parser.get('job_config', 'cached_input_dir'),
                                             config_parser.get('job_config', 'cached_densities_fname'))
    cached_weights_path = '{0}/{1}'.format(config_parser.get('job_config', 'cached_input_dir'),
                                           config_parser.get('job_config', 'cached_weights_fname'))
  
    # incrementally assemble arguments to mle_cvxnl.py
    arguments = config_parser.get('job_config', 'bags') + ' '
    arguments += cached_densities_path + ' '
    arguments += cached_weights_path + ' '
    arguments += '--output_fname={0}'.format(result_fname) + ' '
    arguments += '--obj_scale={0}'.format(config_parser.get('job_config', 'obj_scale'))
  
    # write condor submit file
    fout.write('executable = {0}/mle_cvxnl.py\n'.format(config_parser.get('job_config', 'exec_dir')))
    fout.write('universe = vanilla\n')
    fout.write('arguments = {0}\n'.format(arguments))
    fout.write('output = {0}\n'.format(out_fname))
    fout.write('error = {0}\n'.format(err_fname))
    fout.write('log = {0}\n'.format(log_fname))
    fout.write('request_memory = {0}\n'.format(config_parser.get('job_config', 'request_memory')))
    fout.write('accounting_group = {0}\n'.format(config_parser.get('job_config', 'user_group')))
    fout.write('accounting_group_user = {0}\n'.format(config_parser.get('job_config', 'user_name')))
    fout.write('getenv = True\n')
    fout.write('\n')
    fout.write('queue\n')

# Mainly for debugging only. prints file contents line by line
def print_condor_submit_file(f):
    f.seek(0)
    for line in f:
      print line,


if __name__ == '__main__':

    from ConfigParser import SafeConfigParser
    import argparse
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('cfg_fname', type=str, 
                                 help='Path to the configuration file.')
    argument_parser.add_argument('--debug', action='store_true')
    args = argument_parser.parse_args()

    config_parser = SafeConfigParser()
    config_parser.read(args.cfg_fname)

    # Create output directory
    dirname = '{0}/{1}'.format(config_parser.get('job_config', 'output_dir'),
                               config_parser.get('job_config', 'output_dirname'))
    for d in [ 'result', 'out', 'err', 'log' ]:
      os.makedirs(dirname + '/' + d) 
  
    # Dispatch jobs one node at a time
    nodes = int(config_parser.get('job_config', 'nodes'))
    for i in range(nodes):

        # Write condor submit file
        f = tempfile.NamedTemporaryFile()
        write_condor_submit_file(f, dirname, i, config_parser)

        # Debug only 
        if args.debug and i == 0: 
          print_condor_submit_file(f)
        f.seek(0)
    
        # Submit job
        subprocess.check_call(['condor_submit', f.name])

        f.close()
