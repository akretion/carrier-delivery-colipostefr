# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date
from openerp.osv import orm


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def _prepare_delivery_postefr(self, cr, uid, pick, carrier, context=None):
        params = super(StockPicking, self)._prepare_delivery_postefr(
            cr, uid, pick, carrier, context=context)
        if pick.carrier_code == 'COLI':
            params['date'] = date.today().strftime('%Y-%m-%d')
            params['customs'] = self._prepare_laposte_customs(
                cr, uid, pick, context=context)
            params['totalAmount'] = '%.f' % (  # truncate to string
                # totalAmount is in centimes
                self._calc_picking_price(pick) * 100)
            params['options'] = self.pool['stock.picking'].browse(
                cr, uid, pick.id, context=context)._laposte_get_options()
        return params

    def _laposte_get_options(self, cr, uid, ids, context=None):
        """Define options for the shipment.

        Like insurance, cash on delivery...

        COMES FROM roulier_laposte V8 with ~ no change
        """
        pick = self.browse(cr, uid, ids[0], context=context)
        options = pick._roulier_get_options()
        if 'insuranceValue' in options:
            if pick.laposte_recommande:
                options['recommendationLevel'] = pick.laposte_recommande
                del options['insuranceValue']
            else:
                options['insuranceValue'] = int(pick.laposte_insurance)
        if 'cod' in options:
            options['codAmount'] = 0
        return options

    def _roulier_get_options(self, cr, uid, id, context=None):
        # COMES FROM roulier_laposte V8 with ~ no change
        mapping_options = self._laposte_map_options()
        options = {}
        pick = self.browse(cr, uid, id, context=context)[0]
        if pick.option_ids:
            for opt in pick.option_ids:
                opt_key = str(opt.tmpl_option_id['code'])
                if opt_key in mapping_options:
                    options[mapping_options[opt_key]] = True
                else:
                    options[opt_key] = True
        return options

    def _laposte_map_options(self):
        # COMES FROM roulier_laposte V8 with ~ no change
        return {
            'NM': 'nonMachinable',
            'FCR': 'ftd',
            'COD': 'cod',
            'ACK': 'returnReceipt',
            'INS': 'insuranceValue',
        }

    def _prepare_sender_postefr(self, cr, uid, pick, context=None):
        sender = super(StockPicking, self)._prepare_sender_postefr(
            cr, uid, pick, context=context)
        if pick.carrier_code == 'COLI':
            partner = self.pool['stock.picking.out']._get_label_sender_address(
                cr, uid, pick, context=context)
            sender['country'] = partner.country_id.code
            sender['firstname'] = '.'
        return sender

    def _calc_picking_price(self, pick):
        return sum([x.product_id.list_price * x.product_qty
                    for x in pick.move_lines
                    if x.product_id])

    def _prepare_laposte_customs(self, cr, uid, pick, context=None):
        articles = []
        for line in pick.move_lines:
            article = {}
            articles.append(article)
            product = line.product_id
            # stands for harmonized_system
            hs = product.product_tmpl_id.get_hs_code_recursively()
            if not hs:
                raise orm.except_orm(
                    u"Déclaration d'échange de bien",
                    u"Les propriétés DEB/DES (onglet Compta) du produit '%s' "
                    u"ne sont pas correctement remplis." % product.name)
            article['quantity'] = '%.f' % line.product_qty
            article['weight'] = round(
                line.product_id.weight_net, 3)
            article['originCountry'] = product.country_id.code
            article['description'] = hs.description or False
            article['hs'] = hs.intrastat_code
            article['value'] = product.list_price  # unit price is expected
        return {
            "articles": articles,
            "category": 3,  # commercial
        }


class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'

    def action_process(self, cr, uid, ids, context=None):
        """Open the partial picking wizard"""
        if context is None:
            context = {}
        IRDm = self.pool['ir.model.data']
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.carrier_id and pick.carrier_id.id != (
                    IRDm.get_object_reference(
                    cr, uid, 'delivery_roulier_coliposte',
                    'delivery_carrier_COLI')[1]):
                continue
            products = [x.product_id.name for x in pick.move_lines
                        if not x.product_id.country_id]
            if products:
                raise orm.except_orm(
                    u"Produits sans pays d'origine",
                    u"Les produits suivant:\n\n %s\n\n n'ont pas de "
                    u"pays d'origine spécifié.\n"
                    u"Merci de compléter la fiche produit."
                    % '\n'.join(products))
        return super(StockPickingOut, self).action_process(
            cr, uid, ids, context=context)
