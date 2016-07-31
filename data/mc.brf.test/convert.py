from BrfWeightTable import BrfWeightTable

if __name__ == '__main__':

    brf_table = BrfWeightTable('test.dat')
    fluc_scale = -1.0

    with open('evttype4.train.csv', 'w') as fout:

        with open('evttype4.train.brf.csv', 'r') as fin:

            for line in fin:

                colvals = line.strip().split(' ')

                w = float(colvals[2])

                b1_brf_w = brf_table.get_weight(colvals[3], fluc_scale)
                b2_brf_w = brf_table.get_weight(colvals[4], fluc_scale)

                w = w * b1_brf_w * b2_brf_w

                outvals = [ colvals[0], colvals[1], str(w) ]

                fout.write(' '.join(outvals) +'\n')

