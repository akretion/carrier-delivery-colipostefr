# -*- encoding: utf-8 -*-
##############################################################################
#
#   Copyright (C) 2014 Akretion David BEAL
#                               Sébastien BEAU
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _
from .code128 import code128_image


class StockPicking(orm.Model):
    _inherit = ['stock.picking', 'abstract.coliposte.picking']
    _name = 'stock.picking'

    def action_done(self, cr, uid, ids, context=None):
        """
        :return: see original method
        """
        if context is None:
            context = {}
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.carrier_type == 'colissimo':
                self.generate_labels(cr, uid, [picking.id], context=context)
        return super(StockPicking, self).action_done(
            cr, uid, ids, context=context)


class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'

    def get_128_barcode(self, cr, uid, ids, context=None):
        assert len(ids) == 1, \
            _('This option should only be used for a single id at a time')
        picking = self.browse(cr, uid, ids[0], context=context)
        tracking = picking.carrier_tracking_ref.replace(' ', '')
        return code128_image(tracking, height=100, thickness=2)
