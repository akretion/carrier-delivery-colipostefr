# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import date
from laposte_api.colissimo_and_so import InvalidDataForLaposteInter

from openerp.osv import orm
from openerp.addons.delivery_carrier_colipostefr.stock import LAPOSTE_NEW_WS

_logger = logging.getLogger(__name__)


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def _manage_new_webservice(self, cr, uid, pick, result, carrier,
                               label, context=None):
        super(StockPicking, self)._manage_new_webservice(
            cr, uid, pick, result, carrier, label, context=context)
        self.check_laposte_response(pick, result)
        self.extract_new_ws_info(
            cr, uid, pick, result, carrier, label, context=context)

    def extract_new_ws_info(
            self, cr, uid, pick, result, carrier, label, context=None):
        "Methode nouveau web service"
        carrier['carrier_tracking_ref'] = result.get('parcelNumber')
        # ^LS (Label Shift) allows to shift all field
        # positions to the left
        # ^LS0000 is neutral position sent by web service
        # ^LS0 is equivalant to ^LS0000
        # ^LS-10 move all fields to the right
        label['file'] = result.get('label').replace('^LS0000', '^LS10')
        if result.get('cn23'):
            cn23 = {
                'name': 'CN23_%s.pdf' % result.get('parcelNumber'),
                'res_id': pick.id,
                'res_model': 'stock.picking.out',
                'datas': result['cn23'].encode('base64'),
                'type': 'binary'
            }
            self.pool['ir.attachment'].create(cr, uid, cn23, context=context)
        if result.get('xml_request') and \
                pick.company_id.colipostefr_webservice_message:
            xml = {
                'name': 'laposte_traceability_%s.txt' % pick.name,
                'res_id': pick.id,
                'res_model': 'stock.picking.out',
                'datas': result['xml_request'].encode('base64'),
                'type': 'binary'
            }
            self.pool['ir.attachment'].create(cr, uid, xml, context=context)

    def check_laposte_response(self, pick, result):
        "Methode nouveau web service"
        if pick.carrier_code in LAPOSTE_NEW_WS:
            if isinstance(result, dict) and result.get('status') and \
                    result['status'] == 'error':
                exceptions = u''
                if result.get('message') and result['message'].get('message'):
                    exceptions = [x.__dict__
                                  for x in result['message']['message']]
                mess = u"code transporteur '%s'\nmessages '%s'\n%s" % (
                    pick.carrier_code, exceptions, result)
                raise InvalidDataForLaposteInter(mess)

    def _prepare_delivery_postefr(self, cr, uid, pick, carrier, context=None):
        params = super(StockPicking, self)._prepare_delivery_postefr(
            cr, uid, pick, carrier, context=context)
        articles_weight = [0.02]
        if pick.carrier_code == 'COLI':
            params['date'] = date.today().strftime('%Y-%m-%d')
            params['customs'] = self._prepare_laposte_customs(
                cr, uid, pick, context=context)
            product_prices = params['customs'].pop('product_prices')
            _logger.debug("Product Prices: %s" % product_prices)
            print params.keys()
            print params['customs']
            if params['customs'].get('articles') and params['customs']['articles']:
                articles_weight = [float(x['weight']) * float(x['quantity'])
                                   for x in params['customs']['articles']]
            if params['weight'] < sum(articles_weight):
                # le poids du picking se base sur le weight des stock moves
                # qui sont pas modifiables donc on check la coherence
                # avec les poids de la fiche produit qui sont modifiables
                # le 0.1 est pour ~ l'emballage
                params['weight'] = sum(articles_weight) + 0.1
                _logger.debug("Weight: picking %s sum articles %s" % (
                    pick.weight, sum(articles_weight)))
            params['totalAmount'] = 2
            _logger.debug("totalAmount: %s" % params['totalAmount'])
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

    def _calc_picking_price(self, pick, product_prices):
        return sum([(product_prices.get(x.product_id) or
                     x.product_id.list_price * x.product_qty)
                    for x in pick.move_lines
                    if x.product_id])

    def _prepare_laposte_customs(self, cr, uid, pick, context=None):
        articles = []
        product_prices = {}  # price per product in the sale order
        if pick.move_lines:
            # 99% du temps il y a une seule sale order par picking
            sale_line_id = pick.move_lines[0].sale_line_id
            if sale_line_id:
                product_prices = self._get_product_prices(
                    cr, uid, sale_line_id, context=context)
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
            weight = line.product_id.weight_net or line.product_id.weight or 0
            article['weight'] = round(weight, 3)
            article['originCountry'] = product.country_id.code
            article['description'] = hs.description or False
            article['hs'] = hs.intrastat_code
            article['value'] = (
                product_prices.get(product) or product.list_price)
        _logger.info(articles)
        return {
            "articles": articles,
            "category": 3,  # commercial
            "product_prices": product_prices,
        }

    def _get_product_prices(self, cr, uid, sale_line_id, context=None):
        prices = {}
        sale = sale_line_id.order_id
        if sale:
            for line in sale.order_line:
                if 'price_subtotal_company_currency' in line._columns.keys():
                    subtotal = line.price_subtotal_company_currency
                else:
                    subtotal = line.price_subtotal
                prices[line.product_id] = (
                    subtotal / line.product_uom_qty)
        return prices


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
