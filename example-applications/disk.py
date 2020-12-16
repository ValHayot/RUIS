import os

import numpy as np

with open("dummy-data", "wb") as fout:
    np.save(fout, np.random.rand(10**5, 2 * 10**4))


with open("dummy-data", "rb") as fin:
    data = np.load(fin)

with open("dummy-data", "wb") as fout:
    np.save(fout, data + 1)


os.remove("dummy-data")