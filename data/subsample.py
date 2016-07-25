#!/usr/bin/env python

import numpy as np

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_fname', help='Input csv file.')
    parser.add_argument('output_fname', help='Output csv file.')
    parser.add_argument('subsample_proportion', type=float, help='Subsampling proportion. ')
    args = parser.parse_args()

    with open(args.output_fname, 'w') as fout:
        with open(args.input_fname, 'r') as fin:
            for line in fin:
                if np.random.random() < args.subsample_proportion:
                    fout.write(line)
