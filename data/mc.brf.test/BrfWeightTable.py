# Class that reads in file containing mode string, weight, 
# weight uncertainty, and the amount of fluctuation
#
# Valid file format:
# 1. No header. 
# 2. Space separated. 
# 3. Each line contains exactly 4 columns. 
#    + Column 1: string. indicates the mode. 
#    + Column 2: float. indicates the weight. 
#    + Column 3: float. indicates the uncertainty on the weight. 
#    + Column 4: float. the number of standard devations to 
#                       change the weight by. 
#                       + (-) for increase (decrease).
class BrfWeightTable:

    def __init__(self, lookup_fname):

        self.table = {}

        # populate lookup table a line at a time
        with open(lookup_fname, 'r') as fin:

            for line in fin:

                # tokenize the line
                colvals = line.strip().split(' ')

                if len(colvals) != 4:
                    raise RuntimeError(
                            'BrfWeightTable: ' + lookup_fname +
                            ' must contain exact 4 columns per line. ')

                # convert the values
                weight = float(colvals[1])
                weight_std = float(colvals[2])
                z_score = float(colvals[3])

                # insert into the table
                if self.table.has_key(colvals[0]):
                    raise RuntimeError(
                              'BrfWeightTable: ' + colvals[0] + 
                              ' already exists. ')

                self.table[colvals[0]] = (weight, weight_std, z_score)

    # return the pair (weight, weight_std, z_score) for the given key
    def get_weight_raw(self, key):
        return self.table.get(key)

    # return weight + z_score * weight_std for the given key
    def get_weight(self, key):

        weight_raw = self.table.get(key)

        # no correction for None. this can happen when the given mode key
        # used to to find a correction was intentionally ommited.
        if weight_raw is None: return 1.0

        return weight_raw[0] + weight_raw[2] * weight_raw[1]


if __name__ == '__main__':

    brf_table = BrfWeightTable('brf_weight_variations.test.dat')

    for i in brf_table.table.items():
        print i

    print 

    print brf_table.get_weight_raw('Bp_Dstar0_e_nu')
    print brf_table.get_weight_raw('nonexistent_key')
    print brf_table.get_weight('Bp_Dstar0_e_nu')
    print brf_table.get_weight('nonexistent_key')
