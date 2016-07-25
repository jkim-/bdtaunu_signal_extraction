#!/usr/bin/env python

import sys
import os
import numpy as np

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser('Back of the envelope result estimation. ')
    parser.add_argument('input_fname', help='File containing optimization results. ')
    args = parser.parse_args()

    l = []
    with open(args.input_fname, 'r') as f:
        for line in f:
            l.append(map(float, line.strip().split()))

    arr = np.array(l)
    mean = np.mean(arr, axis=0)
    std = np.std(arr, axis=0)
    res = std / mean
    print 'mean: ', mean
    print 'stdev: ', std
    print 'res: ', res
