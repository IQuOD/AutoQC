#!/usr/bin/env python

import numpy as np
import unittest

dummy = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])


class TestSequence(unittest.TestCase):

    def test_by_2(self):
        ll = []
        setUp = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        for i in dummy:
            if i % 2 == 0:
                ll.append(1)
            else:
                ll.append(0)

        self.assertEqual(setUp, ll)
        return self.defaultTestResult()

    def test_greater_five(self):
        ll = []
        setUp = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
        for i in dummy:
            if i > 5:
                ll.append(1)
            else:
                ll.append(0)

        self.assertEqual(setUp, ll)

    def test_by_3(self):
        ll = []
        setUp = [0, 1, 0, 0, 1, 0, 0, 1, 0, 0]
        for i in dummy:
            if i % 3 == 1:
                ll.append(1)
            else:
                ll.append(0)

        self.assertEqual(setUp, ll)

    def test_equal_seven(self):
        ll = []
        setUp = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
        for i in dummy:
            if i == 7:
                ll.append(1)
            else:
                ll.append(0)

        self.assertEqual(setUp, ll)

    def test_less_zero(self):
        ll = []
        setUp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in dummy:
            if i < 0:
                ll.append(1)
            else:
                ll.append(0)

        self.assertEqual(setUp, ll)
