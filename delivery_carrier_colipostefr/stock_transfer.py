# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#          Sébastien BEAU
##############################################################################

from openerp import models, api
from openerp.exceptions import Warning


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        #TODO forbid from js interface
        for item in self.item_ids:
            if self.picking_id.carrier_type in ('colissimo', 'so_colissimo'):
                if not item.result_package_id:
                    raise Warning(
                        u"Pour le transporteur '%s' \ntous les produits "
                        u"à livrer \ndoivent être "
                        "mis dans un colis."
                        % self.picking_id.carrier_id.name)
        return super(StockTransferDetails, self).do_detailed_transfer()
