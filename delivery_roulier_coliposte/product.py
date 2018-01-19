# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm


class ProductCategory(orm.Model):
    _inherit = 'product.category'

    def get_hs_code_recursively(self, cr, uid, ids, context=None):
        # backport of v8 intrastat
        cat = self.browse(cr, uid, ids[0], context=context)
        if cat.intrastat_id:
            res = cat.intrastat_id
        elif cat.parent_id:
            res = cat.parent_id.get_hs_code_recursively()
        else:
            res = None
        return res


class ProductTemplate(orm.Model):
    _inherit = 'product.template'

    def get_hs_code_recursively(self, cr, uid, ids, context=None):
        # backport of v8 intrastat
        prd = self.browse(cr, uid, ids[0], context=context)
        if prd.intrastat_id:
            res = prd.intrastat_id
        elif prd.categ_id:
            res = prd.categ_id.get_hs_code_recursively()
        else:
            res = None
        return res

    def get_origin_country(self, cr, uid, ids, context=None):
        product  = self.browse(cr, uid, ids[0], context=context)
        return product.country_id and product.country_id.code or None
