# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright 2015 Camptocamp SA
##############################################################################

from openerp.osv import orm


class StockQuantPackage(orm.Model):
    _inherit = 'stock.quant.package'

    def get_weight(self, cr, uid, ids, context=None):
        """ Compute the weight of a pack

        Get all the children packages and sum the weight of all
        the product and the weight of the Logistic Units of the packages.

        So if I put in PACK65:
         * 1 product A of 2kg
         * 2 products B of 4kg
        The box of PACK65 weights 0.5kg
        And I put in PACK66:
         * 1 product A of 2kg
        The box of PACK66 weights 0.5kg

        Then I put PACK65 and PACK66 in the PACK67 having a box that
        weights 0.5kg, the weight of PACK67 should be: 13.5kg

        """
        pack_op_obj = self.pool['stock.pack.operation']
        weight = 0
        package_ids = self.search(cr, uid,
                                  [('id', 'child_of', ids)],
                                  context=context)
        for package in self.browse(cr, uid, package_ids, context=context):
            operation_ids = pack_op_obj.search(
                cr, uid,
                ['|',
                 '&',
                 ('package_id', '=', package.id),
                 ('result_package_id', '=', False),
                 ('result_package_id', '=', package.id),
                 ('product_id', '!=', False),
                 ],
                context=context)
            operations = pack_op_obj.browse(cr, uid, operation_ids,
                                            context=context)
            for operation in operations:
                weight += operation.product_id.weight * operation.product_qty

            if package.ul_id:
                weight += package.ul_id.weight
        return weight
