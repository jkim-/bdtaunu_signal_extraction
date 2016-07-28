#!/usr/bin/env python

import sys
import math
import numpy as np
import cvxopt as cvx
from iopro import genfromtxt

# function that calls CVXOPT to solve maximum likelihood 
def perform_mle(p, obj_scale=1e-8):

    # get cache dimensions
    N, D = p.shape

    # Specify the objective function and its derivatives
    def F(x=None, z=None):

        # Optionally scale the objective to avoid numerical difficulties
        s = obj_scale

        # Handle call signature F()
        if x is None:
            return 0, cvx.matrix(1.0/D, (D, 1))

        # Handle call signature F(x)
        x_arr = np.array(x.trans()).reshape(-1)
        arg = np.dot(p, x_arr)

        if np.min(arg) <= 0.0:
            return None

        f = -np.sum(np.log(arg))
        f = cvx.matrix(f) * s

        arg_m1 = np.power(arg, -1.0)
        Df = [ -np.dot(arg_m1, p[:,c]) for c in range(D) ]
        Df = cvx.matrix(Df, (1, D)) * s

        if z is None:
            return f, Df

        # Handle call signature F(x, z)
        arg_m2 = -2 * np.log(arg)
        H = np.zeros((D, D))
        for b in range(D):
            for c in range(D):
                H[b, c] = np.sum(np.exp(arg_m2 + np.log(p[:,b]) + np.log(p[:,c]))) * z[0]
        H = cvx.matrix(H) * s

        return f, Df, H

    # Specify the inequality constraints
    G = cvx.matrix(np.diag(-np.ones(D)))
    h = cvx.matrix(np.zeros(D))

    # Specify the equality constraints
    A = cvx.matrix(np.ones(D), (1, D))
    b = cvx.matrix(1.0)

    # Specify required metadata
    dims = { 'l': D, 'q': [], 's': [] }

    # Solve
    sol = cvx.solvers.cp(F, G, h, dims, A, b)

    return sol


def print_solution(sol):
    print
    print 'Solver status: {0}'.format(sol['status'])
    print 'Minimum: {0}'.format(sol['primal objective'])
    print 'Minimizers:', np.array(sol['x']).reshape(-1).tolist()
    print
    print
    sys.stdout.flush()


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('nbag', type=int,
                        help='Number of trials to bag/fit.')
    parser.add_argument('cached_densities_fname', type=str,
                        help='File containing cached kde evaluations.')
    parser.add_argument('cached_weights_fname', type=str, 
                        help='File containing the weight of each point in cached_densities_fname. ')
    parser.add_argument('--output_fname', type=str, default='mle_cvxnl.result.csv',
                        help='Path to store output.')
    parser.add_argument('--obj_scale', type=float, default=1e-8,
                        help='Scale factor to apply to objective function.')
    args = parser.parse_args()

    # Read in cached KDE evalutions of the data sample to fit
    print '+ Configuration parameters:\n'.format(args.cached_densities_fname)
    print '  number of bags: {0}.\n'.format(args.nbag)
    print '  cached densities: {0}.\n'.format(args.cached_densities_fname)
    print '  cached weights: {0}.\n'.format(args.cached_weights_fname)
    print '  output file: {0}.\n'.format(args.output_fname)
    sys.stdout.flush()

    p_raw = genfromtxt(args.cached_densities_fname)
    N, D = p_raw.shape

    # Read in cached weights 
    print '+ Reading cached files.\n'.format(args.cached_weights_fname)
    sys.stdout.flush()

    w = genfromtxt(args.cached_weights_fname)
    if w.shape[0] != N: 
        s = '{0} should have the same number of rows as {1}.'.format(
                args.cached_weights_fname, args.cached_densities_fname)
        raise Exception(s)

    # Scale that determines the overall normalization of the sample
    sample_scale = np.sum(w) / N
    print '  sample counts = {0} '.format(N)
    print '  weighted counts = {0} '.format(np.sum(w))
    print '  sample scale = {0}'.format(sample_scale)
    print '  => will draw {0} records per boostrap sample.\n'.format(int(sample_scale*N))

    # Convert weights to relative frequencies
    w /= np.sum(w)

    # Open the file to write results
    fout = open(args.output_fname, 'w')

    print '+ Solving maximum likelihood.\n'.format(args.output_fname)
    sys.stdout.flush()
    for i in range(args.nbag):

        sys.stdout.write('Bag iteration {0}.\n\n'.format(i+1))
        sys.stdout.flush()

        # Create a bagged sample.
        bag = None 
        if w is None: 
            bag = np.random.choice(N, N)
        else:
            bag = np.random.choice(N, int(N*sample_scale), p=w)
        p = p_raw[bag]

        # Solve the optmization problem
        sol = perform_mle(p, args.obj_scale)

        # Report and write results
        print_solution(sol)

        fout.write(' '.join(map(str, np.array(sol['x']).reshape(-1).tolist())) + '\n')


    # Cleanup
    fout.close()

    print '+ Done. Results written to {0}.\n'.format(args.output_fname)
    sys.stdout.flush()
