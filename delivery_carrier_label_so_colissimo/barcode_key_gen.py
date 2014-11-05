# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

CAR = [str(x) for x in range(0,10)]
string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
CAR.extend([x for x in string])


def get_ctrl_key(key):
    CS, MOD = 36, 36
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

    print '  >>> Clé du code de routage =>', get_ctrl_key(routage1)
