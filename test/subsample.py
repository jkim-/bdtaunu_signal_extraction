import numpy as np
with open('test.small.csv', 'w') as fout:
    with open('data/test.csv', 'r') as fin:
        for line in fin:
            if np.random.random() < 0.001:
                fout.write(line)
