import numpy as np
import pandas as pd

def time_and_describe(function):
    #import time
    def wrapper(*args, **kwargs):
        print '{}...'.format(kwargs['desc'].capitalize())
        this_start = time.time()
        result = function(*args, **kwargs)
        print 'Done {}.'.format(kwargs['desc'])
        print '\tThis took {} seconds'.format(time.time() - this_start)
        print '\tTotal elasped time: {}s'.format(time.time() - kwargs['start_time'])
        print
        if result is not None: return result
    return wrapper

@time_and_describe
def get_raw_data(fname_template, components, desc=None, start_time=None):

    n = len(components)
    raw_data = []

    for i in range(n):
        tmp_component = []
        for evttype in components[i]:
            tmp_component.append(pd.read_csv(fname_template.format(evttype), sep=' ', header=None).as_matrix())
        raw_data.append(tmp_component)

    return raw_data

@time_and_describe
def split_data(raw_data, components, ratios, num_points, desc=None, start_time=None):

    n = len(components)
    test_sample = []
    validation_sample = []
    tuning_sample = []

    for i in range(n):
        n_points = int(num_points*ratios[i])
        print '{} components, each with n_points = {}'.format(components[i], n_points)
        tmp_test, tmp_val, tmp_tuning = [], [], []

        for j in range(len(components[i])):

            num_raw = float(len(raw_data[i][j]))

            #np.random.seed(1) #1 / 5.995
            #np.random.seed(2) #1 / 1.99
            #np.random.seed(3) #1 / 15.985
            #np.random.seed(4) #1.5 / 1.99
            #np.random.seed(5) #1.5 / 15.985
            #np.random.seed(5) #1.5 / 2.98
            #np.random.seed(7) #2 / 15.985
            #np.random.seed(8) #2 / 2.98
            #np.random.seed(9) #2 / 25.975
            np.random.seed(10) #secret
            raw_data[i][j] = np.random.permutation(raw_data[i][j])

            cum_w = np.cumsum(raw_data[i][j][:,2])
            if cum_w[-1] < 3*n_points:
                print cum_w[-1], 3*n_points
                raise ValueError('Trying to sample a larger number than number of data points,\n \
                                  decrease num_points variable.')
            last_test_idx = np.searchsorted(cum_w, n_points) + 1
            last_val_idx = np.searchsorted(cum_w, 2*n_points) + 1

            tmp_test.append(raw_data[i][j][:last_test_idx])
            tmp_val.append(raw_data[i][j][last_test_idx:last_val_idx])
            tmp_tuning.append(raw_data[i][j][last_val_idx:])

        test_sample.append(np.concatenate(tmp_test))
        validation_sample.append(np.concatenate(tmp_val))
        #normalize tuning
        if len(components[i]) > 1:
            num_tuning = []
            for j in range(len(components[i])):
                num_tuning.append(np.sum(tmp_tuning[j][:,2]))
            min_w = min(num_tuning)
            tmp_tuning_normed = []
            for j in range(len(components[i])):
                cum_w_tune = np.cumsum(tmp_tuning[j][:,2])
                last_idx = np.searchsorted(cum_w_tune, min_w)
                tmp_tuning_normed.append(tmp_tuning[j][:last_idx,:])
            tuning_sample.append(np.concatenate(tmp_tuning_normed))
        else:
            tuning_sample.append(np.concatenate(tmp_tuning))


    test_sample = np.concatenate(test_sample)
    validation_sample = np.concatenate(validation_sample)
    #tuning_sample = np.concatenate(tuning_sample)

    return test_sample, validation_sample, tuning_sample

@time_and_describe
def write_to_file(test, val, tuning, desc=None, start_time=None):

    np.savetxt('test.csv', test, fmt='%20.18f')
    np.savetxt('validation.csv', val, fmt='%20.18f')
    for i in range(len(tuning)):
        np.savetxt('evttype{0}.tuning.csv'.format(i+1), tuning[i], fmt='%20.18f')

if __name__ == '__main__':
    
    import time
    import argparse
    import ast

    parser = argparse.ArgumentParser(
            description='Split data set into test, validation, and tuning sets in specified proportions.\n'+
                         'Example: python split_test_data.py \'[[1,2,3,4],[5]]\' \'[0.04,0.96]\'',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('components', type=str, nargs=1,
                        help='Components as a string to be literal_eval\'ed')
    parser.add_argument('ratios', type=str, nargs=1,
                        help='Ratios as a string to be literal_eval\'ed')
    parser.add_argument('-n', type=int, nargs=1, default=1000, metavar='num_points',
                        help='Number of points per component per sample type (default=1000)')
#    parser.add_argument('-o', type=str, nargs=1, metavar='output_fname',
#                        help='Name of the file to write the combined data.')
    args = parser.parse_args()

    input_fname_template = 'evttype{}.test.csv'
#    output_fname_template = 'evttype{}.test.output.csv'
    components = ast.literal_eval(args.components[0])
    ratios = ast.literal_eval(args.ratios[0])
    if np.sum(ratios) != 1.:
        raise ValueError('Ratio does not sum to 1.')
    else:
        ratios = [x/float(y) for x,y in zip(ratios, [len(x) for x in components])]
        ratios = [x/min(ratios) for x in ratios]
    num_points = args.n # per component

    #input_fname_template = 'evttype{}.train.csv'
    #output_fname_template = 'evttype{}.train.output.csv'
    #components = [[1,2,3,4]]
    #ratios = [1.]
    #num_points = 100000 # per component

    n = len(components)

    print

    start = time.time()

    raw_data = get_raw_data(input_fname_template, components,
                            desc='reading in raw data', 
                            start_time=start)
    test, val, tuning = split_data(raw_data, components, ratios, num_points,
                                   desc='splitting data',
                                   start_time=start)
    write_to_file(test, val, tuning,
                  desc='writing out to file',
                  start_time=start)
