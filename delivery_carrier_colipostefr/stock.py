# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#          Sébastien BEAU
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.config import config
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from laposte_api.colissimo_and_so import (
    ColiPoste,
    InvalidDataForMako,
    InvalidWebServiceRequest)

from laposte_api.exception_helper import (
    InvalidWeight,
    InvalidSize,
    InvalidMissingField,
    InvalidCode,
    InvalidCountry,
    InvalidZipCode,
    InvalidSequence,
    InvalidKeyInTemplate,
    InvalidType)

from datetime import datetime

EXCEPT_TITLE = "'Colissimo and So' library Exception"
LABEL_TYPE = 'zpl2'


def raise_exception(orm, message):
    raise orm.except_orm(EXCEPT_TITLE, map_except_message(message))


def map_except_message(message):
    """Allows to map vocabulary from external library
    to Odoo vocabulary in Exception message
    """
    webservice_mapping = {
        'line2': 'line2 (rue du partner du bon de livraison)',
        '\\xe8': 'e',
        '\\xe9': 'e',
        '\\xe0': 'a',
    }
    model_mapping = {
        'sender': 'company and \ncarrier configuration',
        'delivery': 'delivery order',
        'address': 'customer/partner'}
    for key, val in model_mapping.items():
        message = message.replace('(model: ' + key, '\n(check model: ' + val)
    for key, val in webservice_mapping.items():
        message = message.replace(key, val)
    if 'commercial afin de reinitialiser votre compte client' in message:
        message += ("\n\nEn gros à ce stade, "
                    "si vous avez saisi correctement votre identifiant"
                    "et mot de passe transmis par votre commercial"
                    "\nil est probable que ce dernier"
                    "n'a pas terminé le boulot jusqu'au bout"
                    "\nVraisemblablement, vous allez passez encore beaucoup"
                    "de temps à faire la balle de ping pong entre les"
                    "services: commercial, ADV et Support Intégration Clients."
                    "\nCe dernier est probablement votre meilleur chance."
                    "\nun homme averti en vaut deux"
                    "\nBougez avec la poste"
                    "\nBonne chance\n\n(the developer team)")
    return message


def move_label_content(content, tag, value, axis='y'):
    """ move label content
        :param content: unicode: whole text to parse
        :param tag: str: string to search in content for replacement purpose
        :param value: integer: define position x or y in the label
        :param axis: char: direction x or y
    """
    cpn = tag.split(',')
    if axis == 'y':
        position = str(int(cpn[1]) + value)
        new_tag = '%s,%s' % (cpn[0], position)
    else:
        extract_pos = int(cpn[0][3:])
        position = extract_pos + value
        new_tag = '%s%s,%s' % (cpn[0][:3], position, cpn[1])
    return content.replace(tag, new_tag)


def modify_label_content(content):
    """ International web service label is too long
        to be printed correctly
    """
    tags = ['^FO270,920', '^FO30,920', '^FO670,920', '^FO290,970',
            '^FO27,995', '^FO170,1194', '^FO27,988']
    for tag in tags:
        content = move_label_content(content, tag, -30)
    return content


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def send_douane_doc(self, cr, uid, ids, field_n, arg, context=None):
        result = {}
        for elm in self.browse(cr, uid, ids):
            res = False
            if elm.state == 'done' and elm.carrier_type == 'colissimo':
                eu_country = False
                if elm.partner_id.country_id \
                        and elm.partner_id.country_id.intrastat:
                    # intrastat field identify european countries
                    eu_country = True
                if elm.carrier_code in ['8Q', '7Q']:
                    res = True
                if elm.carrier_code in ['EI', 'AI', 'SO'] and not eu_country:
                    res = True
                elif elm.carrier_code in ['9V', '9L'] \
                        and elm.partner_id.country_id \
                        and elm.partner_id.country_id.code == 'AD':
                    res = True
            result[elm.id] = res
        return result

    _columns = {
        'colipostefr_prise_en_charge': fields.char(
            '||| || |||| pch',
            size=64,
            help="""Code barre de prise en charge :
            cf documentation coliposte pour plus de détails
    - code étiquette sur 2 alfa.
    - coliss_order : valeur 1 ou 2 (selon la méthode de livraison)
    - code postal (5 alfa) ou   prefix pays (étranger)
      + 3 premiers caractères CP
    - N° du compte client fourni par le partner 'La Poste'
    - poids du colis sur 4 numeriques
    - 00 : assurance+recommandation (non implémenté à ce jour)
    - option 'non mécanisable' : valeur 1 ou 0
    - combinaison d'options : FTD+AR+CRBT (valeur de 0 à 7)
    - clé de liaison du code barre précédent sur 1 numérique
      (issu de l'avant dernier caractère)
    - clé de contrôle du code barre actuel sur 1 numérique
    """),
        'colipostefr_insur_recomm': fields.selection([
            ('01', '150 €'), ('02', '300 €'), ('03', '450 €'),
            ('04', '600 €'), ('05', '750 €'), ('06', '900 €'),
            ('07', '1050 €'), ('08', '1200 €'),
            ('09', '1350 €'), ('10', '1500 €'),
            # TODO Recommandation level
            #('21', 'R1'), ('22', 'R2'), ('23', 'R3'),
        ],
            'Insurance',
            help="Insurance amount in € (add valorem)"),
        'colipostefr_send_douane_doc': fields.function(
            send_douane_doc,
            string='Send douane document',
            type='boolean',
            store=False,
            help="Define if document CN23 et CN11 should be "
                 "printed/sent with the parcel"),
    }

    def _prepare_address_postefr(self, cr, uid, pick, context=None):
        address = {}
        for elm in ['name', 'city', 'zip', 'phone', 'mobile']:
            address[elm] = pick.partner_id[elm]
        # 3 is the number of fields street
        # 38 is the field street max length
        res = self.pool['res.partner']._get_split_address(
            cr, uid, pick.partner_id, 3, 38, context=context)
        address['street'], address['street2'], address['street3'] = res
        if pick.partner_id.country_id.code and pick.partner_id.country_id.code:
            address['countryCode'] = pick.partner_id.country_id.code
        return address

    def _prepare_option_postefr(self, cr, uid, pick, context=None):
        option = {}
        if pick.option_ids:
            for opt in pick.option_ids:
                opt_key = str(opt.tmpl_option_id['code'].lower())
                option[opt_key] = True
        if pick.colipostefr_insur_recomm:
            # TODO improve this mechanism option
            option['insurance'] = pick.colipostefr_insur_recomm
        return option

    def _prepare_sender_postefr(self, cr, uid, pick, context=None):
        partner = self.pool['stock.picking']._get_label_sender_address(
            cr, uid, pick, context=context)
        sender = {'support_city': pick.company_id.colipostefr_support_city,
                  'password': pick.company_id.colipostefr_password}
        if partner.country_id:
            sender['country'] = partner.country_id.name
        fields = ['name', 'street', 'zip', 'city',
                  'phone', 'mobile', 'email']
        for elm in fields:
            sender[elm] = partner[elm]
        if pick.carrier_code == '6J':
            sender['chargeur'] = pick.company_id.colipostefr_account_chargeur
        return sender

    def _get_account(self, cr, uid, pick, france, context=None):
        account = pick.company_id.colipostefr_account
        if not france:
            return pick.company_id.colipostefr_world_account or account
        return account

    def _prepare_delivery_postefr(self, cr, uid, pick, number_of_packages,
                                  context=None):
        shipping_date = pick.min_date
        if pick.date_done:
            shipping_date = pick.date_done
        shipping_date = datetime.strptime(
            shipping_date, DEFAULT_SERVER_DATETIME_FORMAT)
        delivery = {
            'ref_client': '%s-pack_number/%s' % (pick.name, number_of_packages),
            'date': shipping_date.strftime('%d/%m/%Y'),
            'parcel_total_number': number_of_packages,
        }
        #if pick.carrier_code not in ['EI', 'AI', 'SO']:
        #    delivery.update({
        #        'cab_prise_en_charge': pick.colipostefr_prise_en_charge,
        #        'cab_suivi': pick.carrier_tracking_ref,
        #    })
        return delivery

    def _prepare_pack_postefr(
            self, cr, uid, packing, picking, option, service, france,
            weight=None, context=None):
        pack_op_obj = self.pool['stock.pack.operation']
        # compute weight
        weight = 0
        pack_op_ids = pack_op_obj.search(
            cr, uid, [('result_package_id', '=', packing.id)],
            context=context)
        for pack_op in pack_op_obj.browse(
                cr, uid, pack_op_ids, context=context):
            weight += pack_op.product_id.weight * pack_op.product_qty
        if packing.ul_id:
            weight += packing.ul_id.weight
        pack = {'weight': weight}
        if france:
            # we do not call webservice to get these infos
            pack['sequence'] = self._get_sequence(
                cr, uid, picking.carrier_code, context=context)
            cab_suivi = service.get_cab_suivi(
                pack['sequence'])
            pack['cab_prise_en_charge'] = \
                self._barcode_prise_en_charge_generate(
                    cr, uid, service, picking, cab_suivi, weight,
                    option, context=context)
            pack['cab_suivi'] = cab_suivi.replace(' ', '')
        return pack

    def _generate_coliposte_label(
            self, cr, uid, picking, service, sender, address, france, option,
            package_ids=None, context=None):
        """ Generate labels and write package numbers received """
        pack_number = 0
        carrier = {}
        deliv = {}
        labels = []
        tracking_refs = []
        if package_ids is None:
            packages = self._get_packages_from_picking(
                cr, uid, picking, context=context)
        else:
            # restrict on the provided packages
            packages = self.pool['stock.quant.package'].browse(
                cr, uid, package_ids, context=context)
        delivery = self._prepare_delivery_postefr(
            cr, uid, picking, len(packages), context=context)
        for packing in packages:
            pack_number += 1
            addr = address.copy()
            deliv.clear()
            deliv = delivery.copy()
            label_info = {
                'file_type': LABEL_TYPE,
            }
            pack = self._prepare_pack_postefr(
                cr, uid, packing, picking, option, service, france,
                context=context)
            pack['name'] = packing.name
            deliv.update(pack)
            deliv['ref_client'] = deliv['ref_client'].replace(
                'pack_number', str(pack_number))
            label = self.get_zpl(service, sender, deliv, addr, option)
            filename = deliv['ref_client'].replace('/', '_')
            label_info.update({
                #'tracking_id': packing.id if packing else False,
                #'file': label['content'],
                'name': '%s.zpl' % filename,
            })
            # uncomment the line below to record a new test unit
            # based on picking datas
            if picking.company_id.colipostefr_unittest_helper and france:
                test_id = self._get_xmlid(cr, uid, picking.id) or 'no_value'
                service._set_unit_test_file_name(
                    test_id, pack['sequence'], pack['cab_suivi'],
                    pack['cab_prise_en_charge'])
                if label['tracking_number']:
                    label_info['name'] = '%s%s.zpl' % (
                        label['tracking_number'], label['filename'])
            if picking.carrier_code in ['EI', 'AI', 'SO']:
                label_info['file'] = modify_label_content(label[0])
                pack['cab_suivi'] = label[2]
                pack['cab_prise_en_charge'] = label[3]
                self.write(cr, uid, [picking.id], carrier)
                picking = self.browse(cr, uid, picking.id, context=context)
                if label[1]:
                    self._create_comment(cr, uid, picking, label[1],
                                         context=None)
            else:
                label_info['file'] = label
            labels.append(label_info)
            pack_vals = {
                'weight': pack['weight'],
                'parcel_tracking': pack['cab_suivi'],
            }
            self.pool['stock.quant.package'].write(
                cr, uid, packing.id, pack_vals, context=context)
            tracking_refs.append(pack['cab_suivi'])
        pick_vals = {
            'number_of_packages': len(packages),
            'carrier_tracking_ref': 'see in packages',
        }
        self.write(cr, uid, picking.id, pick_vals, context=context)
        picking = self.browse(cr, uid, picking.id, context=context)
        self._customize_postefr_picking(cr, uid, picking, context=context)
        return labels

    def _get_tracking_refs(self, cr, uid, picking, context=None):
        tracking_refs = []
        for pack in self._get_packages_from_picking(
                self, cr, uid, picking, context=context):
            if pack.parcel_tracking:
                tracking_refs.append(pack.parcel_tracking)
        return tracking_refs

    def get_zpl(self, service, sender, delivery, address, option):
        try:
            result = service.get_label(sender, delivery, address, option)
        except (InvalidMissingField,
                InvalidDataForMako,
                InvalidKeyInTemplate,
                InvalidWebServiceRequest,
                InvalidKeyInTemplate,
                InvalidCountry,
                InvalidZipCode,
                InvalidSequence,
                InvalidType) as e:
            raise_exception(orm, e.message)
        except Exception as e:
            if config.options.get('debug_mode', False):
                raise
            else:
                raise orm.except_orm(
                    "'Colissimo and So' Library Error", e.message)
        return result

    def _customize_postefr_picking(self, cr, uid, picking, context=None):
        "Use this method to override gls picking"
        return True

    def generate_shipping_labels(self, cr, uid, ids, package_ids=None,
                                 context=None):
        if isinstance(ids, (long, int)):
            ids = [ids]
        assert len(ids) == 1
        pick = self.browse(cr, uid, ids[0], context=context)
        if pick.carrier_type in ['colissimo', 'so_colissimo']:
            if not pick.carrier_code:
                raise orm.except_orm(
                    _("Carrier code missing"),
                    _("'Carrier code' is missing in '%s' delivery method"
                      % pick.carrier_type))
            # Check that labels don't already exist for this picking
            attach_ids = self.pool['ir.attachment'].search(
                cr, uid, [
                    ('res_model','=','stock.picking'),
                    ('res_id', '=', pick.id)], context=context)
            if attach_ids:
                label_ids = self.pool['shipping.label'].search(
                    cr, uid, [('attachment_id', 'in', attach_ids)], context=context)
                if label_ids:
                    raise orm.except_orm(
                        _('Error:'),
                        _('Some labels already exist for the picking %s. '
                            'Please delete the existing labels in the '
                            'attachements of this picking and try again')
                        % pick.name)
            france = True
            if pick.carrier_code in ['EI', 'AI', 'SO']:
                france = False
            try:
                account = self._get_account(
                    cr, uid, pick, france, context=context)
                service = ColiPoste(account).get_service(
                    pick.carrier_type, pick.carrier_code)
            except (InvalidSize, InvalidCode, InvalidType) as e:
                raise_exception(orm, e.message)
            except Exception as e:
                raise orm.except_orm(
                    "'Colissimo and So' Library Error",
                    map_except_message(e.message))
            option = self._prepare_option_postefr(
                cr, uid, pick, context=context)
            sender = self._prepare_sender_postefr(cr, uid, pick,
                                                  context=context)
            address = self._prepare_address_postefr(cr, uid, pick,
                                                    context=context)
            if not france:
                if not pick.partner_id.country_id \
                        and not pick.partner_id.country_id.code:
                    raise orm.except_orm(
                        "'Colissimo and So' Library Error",
                        "EI/AI/BE carrier code must have "
                        "a defined country code")
            return self._generate_coliposte_label(
                cr, uid, pick, service, sender, address, france, option,
                package_ids=package_ids, context=context)
        return super(StockPicking, self).generate_shipping_labels(
            cr, uid, ids, package_ids=package_ids, context=context)

    def _filter_message(self, cr, uid, mess_type, context=None):
        """ Allow to exclude returned message according their type.
            Only used by
        """
        if mess_type in ['INFOS']:
            return False
        return True

    def _create_comment(self, cr, uid, pick, messages, context=None):
        if pick.company_id.colipostefr_webservice_message:
            mess_title = "Web Service ColiPoste International<ul>%s</ul>"
            message = ''
            for mess in messages:
                if 'type' in mess:
                    if self._filter_message(cr, uid, mess['type'],
                                            context=context):
                        message += '<li>%s %s: %s</li>\n' \
                                   % (mess['type'],
                                      mess['id'],
                                      mess['libelle'])
                elif isinstance(mess, (str, unicode)):
                    message += unicode(mess)
            if len(message) > 0:
                vals = {
                    'res_id': pick.id,
                    'model': 'stock.picking',
                    'body': mess_title % message,
                    'type': 'comment',
                }
                self.pool['mail.message'].create(cr, uid, vals,
                                                 context=context)
        return True

    def _get_xmlid(self, cr, uid, id):
        "only used in development"
        xml_id_dict = self.get_xml_id(cr, uid, [id])
        xml_id = False
        if xml_id_dict:
            xml_id = xml_id_dict[id]
            xml_id = xml_id[xml_id.find('.')+1:]
        return xml_id.replace('stock_picking_', '')

    def _get_sequence(self, cr, uid, label, context=None):
        sequence = self.pool['ir.sequence'].next_by_code(
            cr, uid, 'stock.picking_' + label, context=context)
        if not sequence:
            raise orm.except_orm(
                _("Picking sequence"),
                _("There is no sequence defined for the label '%s'") % label)
        return sequence

    def _barcode_prise_en_charge_generate(
            self, cr, uid, service, picking, carrier_track, weight, option,
            context=None):
        """
        :return: the second barcode
        """
        if picking.carrier_code:
            infos = {
                'zip': picking.partner_id.zip or '',
                'countryCode': picking.partner_id
                and picking.partner_id.country_id
                and picking.partner_id.country_id.code or '',
                'weight': weight,
                'carrier_track': carrier_track,
            }
            infos.update(option)
            try:
                barcode = service.get_cab_prise_en_charge(infos)
            except (InvalidWeight, Exception) as e:
                raise_exception(orm, e.message)
        return barcode

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'deposit_slip_id': None,
            'carrier_tracking_ref': None,
            'colipostefr_prise_en_charge': None,
        })
        return super(StockPicking, self).copy(
            cr, uid, id, default, context=context)

    def get_shipping_cost(self, cr, uid, ids, context=None):
        return 0


class ShippingLabel(orm.Model):
    _inherit = 'shipping.label'

    def _get_file_type_selection(self, cr, uid, context=None):
        selection = super(ShippingLabel, self)._get_file_type_selection(
            cr, uid, context=None)
        selection.append(('zpl2', 'ZPL2'))
        selection = list(set(selection))
        return selection
