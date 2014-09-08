#!/usr/bin/env python
# -*- coding: utf-8 -*-



import unittest
import label
from label import CAB

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.seq = range(10)

    def test_7A(self):
        cab = CAB({}, {})
        key = '20524 75203'
        res = cab._build_control_key(key)
        self.assertEqual(res, '2')

    def test_pc(self):
        cab = CAB({}, {})
        key = '900 001 0860 00003'
        res = cab._build_control_key(key)
        self.assertEqual(res, '7')

if __name__ == '__main__':
    unittest.main()
