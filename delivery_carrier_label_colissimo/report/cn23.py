# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Chafique DELLI <chafique.delli@akretion.com>
#
##############################################################################

import time

from openerp.report import report_sxw


class cn23(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(cn23, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw(
    'report.stock.picking.cn23',
    'stock.picking',
    'delivery_carrier_label_colissimo/report/cn23.mako',
    parser=cn23)
