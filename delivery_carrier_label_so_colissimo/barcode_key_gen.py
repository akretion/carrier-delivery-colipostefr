#!/usr/bin/env python
# -*- coding: utf-8 -*-

CAR = [str(x) for x in range(0,10)]
string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
CAR.extend([x for x in string])

def get_ctrl_key(key):

    CS, MOD = 36,36

    for i in key:
        Y = CAR.index(i)
        CS += Y
        if CS > MOD:
            CS -= MOD
        CS *= 2
        if CS > MOD:
            CS = CS - MOD - 1


        print i, Y

    CS = MOD + 1 - CS
    if CS == MOD:
        CS = 0

    return CAR[CS]


if __name__ == '__main__':

    routage1 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZa'

    #print CAR
    print '  >>> Clé du code de routage =>', get_ctrl_key(routage1)
