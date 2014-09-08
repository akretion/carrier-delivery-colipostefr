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
from report import report_sxw
from openerp.osv import osv
import pooler


class DepositSlipReport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(DepositSlipReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
        })

report_sxw.report_sxw('report.stock.picking.deposit',
                      'stock.picking',
                      parser=DepositSlipReport)
