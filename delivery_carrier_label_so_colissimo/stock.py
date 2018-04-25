# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields

dropoff_mapping = {
    # commerçants
    '6M': ('A2P',),
    # point cityssimo
    '6J': ('CIT',),
    # Centre de distribution de la poste, Agence Coliposte
    # ou bureau de poste
    '6H': ('CDI', 'ACP', 'BPR'),
    'CMT': ('CMT',),
    'BDP': ('BDP',),
}


class StockPicking(orm.Model):
    _inherit = "stock.picking"

    _columns = {
        'colipostefr_barcode_routage': fields.char('Barcode Routage', size=64),
    }

    def action_done(self, cr, uid, ids, context=None):
        """
        :return: see original method
        """
        if context is None:
            context = {}
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.carrier_type == 'so_colissimo':
                # TODO FIX this constraint
                #self._check_dropoff_site_according_to_carrier(
                    #cr, uid, ids, context=context)
                self.generate_labels(cr, uid, [picking.id], context=context)
        return super(StockPicking, self).action_done(
            cr, uid, ids, context=context)

    def carrier_id_change(self, cr, uid, ids, carrier_id, context=None):
        res = super(StockPicking, self).carrier_id_change(
            cr, uid, ids, carrier_id, context=context)
        if not carrier_id:
            return res
        carrier = self.pool['delivery.carrier'].browse(
            cr, uid, carrier_id, context=context)
        if carrier.type == 'so_colissimo' or carrier.code in ['CMT', 'BDP']:
            if carrier.code in ['6H', '6M', '6J', 'CMT', 'BDP']:
                res['value'].update({'has_final_recipient': True})
                res['domain'].update({
                    'partner_id': [
                        ('dropoff_site_id', '!=', False),
                        ('dropoff_site_id.subtype', 'in',
                         dropoff_mapping[carrier.code])
                    ],
                })
            else:
                res['value'].update({'has_final_recipient': False})
                res['domain'].update({'partner_id': [
                    ('customer', '=', True)]}),
        return res

    def _check_dropoff_site_according_to_carrier(
            self, cr, uid, ids, context=None):
        super(StockPicking, self)._check_dropoff_site_according_to_carrier(
            cr, uid, ids, context=context)
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.carrier_id.type == 'so_colissimo' or pick.carrier_id.code in ['CMT', 'BDP']:
                if pick.carrier_id.code in ['6M', '6H', '6J', 'CMT', 'BDP']:
                    if (not pick.partner_id.dropoff_site_id
                            or pick.partner_id.dropoff_site_id.subtype
                            not in dropoff_mapping[pick.carrier_id.code]):
                        raise orm.except_orm(
                            u"Point Relais",
                            u"Le champ '%s' sélectionné n'est pas compatible "
                            u"avec le transporteur choisi '%s'.\n\n"
                            u"Merci de changer l'un des deux."
                            % (pick.partner_id.name, pick.carrier_id.name))
        return True

    def _partner_data_postefr(
            self, cr, uid, partner_id, max_street_size, context=None):
        "used by partner_id and final_partner_id"
        address = {}
        for field in ['name', 'city', 'zip', 'phone', 'mobile']:
            address[field] = partner_id[field]
        if partner_id.name[0:15].lower() == 'bureau de poste':
            address['name2'] = partner_id.name[16:]
            address['name'] = 'BUREAU DE POSTE'
        elif partner_id.name[0:16].lower() == 'espace cityssimo':
            address['name2'] = partner_id.name[17:]
            address['name'] = 'ESPACE CITYSSIMO'
        elif partner_id.name[0:8].lower() == 'la poste':
            address['name2'] = partner_id.name[9:]
            address['name'] = 'LA POSTE'
        if 'name2' in address:
            # name2 max lenght is 30
            address['name2'] = address['name2'][:30]
        streets = self.pool['res.partner']._get_split_address(
            cr, uid, partner_id, 4, max_street_size, context=context)
        address.update({
            'street': streets[0],
            'street2': streets[1],
            'street3': streets[2],
            'street4': streets[3],
        })
        if partner_id.dropoff_site_id:
            dropoff = partner_id.dropoff_site_id
            if dropoff.lot_routing and dropoff.distri_sort:
                address.update({
                    'lot_routing': dropoff.lot_routing,
                    'distri_sort': dropoff.distri_sort,
                })
                address['_specific_label'] = True
        return address

    def _prepare_address_postefr(self, cr, uid, pick, context=None):
        address = super(StockPicking, self)._prepare_address_postefr(
            cr, uid, pick, context=context)
        if pick.carrier_type == 'so_colissimo':
            address = self._partner_data_postefr(
                cr, uid, pick.partner_id, 35, context=context)
            max_street_size = 35
            if pick.carrier_code in ['6H', '6M', '6J']:
                max_street_size = 20
            if pick.has_final_recipient:
                final_address = self._partner_data_postefr(
                    cr, uid, pick.final_partner_id, max_street_size,
                    context=context)
                address['final_address'] = final_address
            else:
                address['final_address'] = address
                for field in ['email', 'door_code', 'door_code2', 'intercom']:
                    address[field] = pick.partner_id[field]
        return address

    def _prepare_sender_postefr(self, cr, uid, pick, context=None):
        sender = super(StockPicking, self)._prepare_sender_postefr(
            cr, uid, pick, context=context)
        if pick.carrier_type == 'so_colissimo' and pick.carrier_code == '6J':
            sender['chargeur'] = \
                pick.company_id.colipostefr_account_chargeur
        return sender


class StockPickingOut(orm.Model):
    _inherit = "stock.picking.out"

    _columns = {
        'colipostefr_barcode_routage': fields.char('Barcode Routage', size=64),
    }
