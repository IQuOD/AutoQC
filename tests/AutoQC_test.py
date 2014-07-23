#!/usr/bin/env python

import numpy as np

dummy = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

def by_2():
    ll = []
    for i in dummy:
        if i%2 == 0:
            ll.append(1)
        else:
            ll.append(0)

    assert [1, 0, 1, 0, 1, 0, 1, 0, 1, 0] == ll

