# Class that reads in file containing mode string, weight, weight uncertainty.
#
# Valid file format:
# 1. No header. 
# 2. By default, space, tab, or comma.
# 3. Each line contains at least 1 column, and at most 3 columns. 
#    + Column 1: string. indicates the mode. 
#    + Column 2: float. indicates the weight. 
#                        defaults to 1.0 if not provided. 
#    + Column 3: float. indicates the uncertainty on the weight. 
#                        defaults to 0.0 if not provided. 
class BrfWeightTable:

    def __init__(self, lookup_fname):

        self.table = {}

        # populate lookup table a line at a time
        with open(lookup_fname, 'r') as fin:

            for line in fin:

                # tokenize the line
                colvals = line.strip().split(' ')

                # decide the weights and their fluctuations depending on
                # the number of columns present
                ncols = len(colvals)
                if ncols not in range(1, 4):
                    raise RuntimeError(
                            'BrfWeightTable: ' + lookup_fname + 
                            ' must contain at least 1 and at most 3' + 
                            'columns. ')

                weight, fluc_weight = 1.0, 0.0
                if ncols == 2:
                    weight = float(colvals[1])
                elif ncols == 3:
                    weight = float(colvals[1])
                    fluc_weight = float(colvals[2])

                # insert into the table
                if self.table.has_key(colvals[0]):
                    raise RuntimeError(
                              'BrfWeightTable: ' + colvals[0] + 
                              ' already exists. ')

                self.table[colvals[0]] = (weight, fluc_weight)

    # return the pair (weight, fluc_weight) for the given key
    def get_weight_pair(self, key):
        return self.table.get(key)

    # return weight + fluc_factor * fluc_weight for the given key
    def get_weight(self, key, fluc_factor=0.0):

        weight_pair = self.table.get(key)

        # no correction for None. this can happen when the given mode key
        # used to to find a correction was intentionally ommited.
        if weight_pair is None: return 1.0

        return weight_pair[0] + fluc_factor * weight_pair[1]


if __name__ == '__main__':

    brf_table = BrfWeightTable('test.dat')

    for i in brf_table.table.items():
        print i

    print 

    print brf_table.get_weight_pair('Bp_Dstar0_e_nu')
    print brf_table.get_weight_pair('nonexistent_key')
    print brf_table.get_weight('Bp_Dstar0_e_nu', -1.0)
    print brf_table.get_weight('nonexistent_key', -1.0)
