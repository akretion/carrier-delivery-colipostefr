# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#          Sébastien BEAU <sebastien.beau@akretion.com>
#
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _
from .code128 import code128_image


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def do_transfer(self, cr, uid, ids, context=None):
        """ Used by wizard stock_tranfert_details and js interface
        """
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.carrier_type == 'colissimo':
                self.generate_labels(cr, uid, [picking.id], context=context)
        return super(StockPicking, self).do_transfer(
            cr, uid, ids, context=context)

    def action_done(self, cr, uid, ids, context=None):
        """ Used by stock_picking_wave
        """
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.carrier_type == 'colissimo':
                self.generate_labels(cr, uid, [picking.id], context=context)
        return super(StockPicking, self).action_done(
            cr, uid, ids, context=context)


class StockQuantPackage(orm.Model):
    _inherit = 'stock.quant.package'

    def get_128_barcode(
            self, cr, uid, ids, height=100, thickness=2, context=None):
        assert len(ids) == 1, \
            _('This option should only be used for a single id at a time')
        package = self.browse(cr, uid, ids[0], context=context)
        if package.parcel_tracking:
            tracking = package.parcel_tracking.replace(' ', '')
            return code128_image(tracking, height=height, thickness=thickness)
        else:
            return False
