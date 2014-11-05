# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#          Yannick VAUCHER, Camptocamp SA
#
##############################################################################

from openerp.osv import orm, fields
from . company import ResCompany
from laposte_api.colissimo_and_so import ColiPosteConfig


class ColiposteFrConfigSettings(orm.TransientModel):
    _name = 'colipostefr.config.settings'

    _description = 'La Poste configuration'
    _inherit = ['res.config.settings', 'abstract.config.settings']
    _prefix = 'colipostefr_'
    _companyObject = ResCompany

    def button_send_image_to_printer(self, cr, uid, ids, context=None):
        """ Implement your own method according to printing solution
        """
        return ColiPosteConfig().get_image_data()

    def get_linked_module(self, cr, uid, context=None):
        modules = [
            'delivery_dropoff_site',
            'delivery_carrier_label_so_colissimo',
            'delivery_carrier_label_colissimo', ]
        ids = self.pool['ir.module.module'].search(
            cr, uid, [('name', 'in', modules)], context=context)
        return ids

    def get_linked_sequence(self, cr, uid, context=None):
        company_id = self._default_company(cr, uid, context=context)
        ids = self.pool['ir.sequence'].search(
            cr, uid, [
                ('name', 'like', '%olissimo%'),
                '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            ], context=context)
        return ids

    _columns = {
        'linked_module': fields.many2many(
            'ir.module.module',
            string='Principaux modules liés',
            readonly=True),
        'linked_sequence': fields.many2many(
            'ir.sequence',
            string='Séquences associées',
            readonly=True),
    }

    _defaults = {
        'linked_module': get_linked_module,
        'linked_sequence': get_linked_sequence,
    }
