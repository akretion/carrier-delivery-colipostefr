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
#from openerp import models, fields
#from openerp import api
from laposte_api.colissimo_and_so import ColiPosteConfig

# TODO move to new api
# seems there is a bug with related field in new api (at least for transient)


class ColiposteFrConfigSettings(orm.TransientModel):
    _name = 'colipostefr.config.settings'
    _description = 'La Poste configuration'
    _inherit = 'res.config.settings'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'account': fields.related(
            'company_id.colipostefr_account',
            string='Compte',
            relation='res.company',
            type='char',
            help="Nombre à 6 caractères.\n"
                 "La valeur par défaut est 964744"),
        'support_city': fields.related(
            'company_id.colipostefr_support_city',
            string='Site de Prise en Charge',
            relation='res.company',
            type='char',
            help="Site de prise en charge de la poste pour son client.\n"
                 "Indiquer votre propre centre de rattachement"),
        'support_city_code': fields.related(
            'company_id.colipostefr_support_city_code',
            string='Code Site de Prise en Charge',
            relation='res.company',
            type='char',
            help="Utile uniquement pour le module colissimo EDI "
                 "(facultatif cependant)"),
        'password': fields.related(
            'company_id.colipostefr_password',
            string='Mot de passe site web',
            relation='res.company',
            type='char',
            help="Le mot de passe doit être identique "
                 "à celui de votre espace client.\n"
                 "Uniquement nécessaire pour les envois à l'étranger.\n"
                 "Mettre un mot de passe complexe"),
        'unittest_helper': fields.related(
            'company_id.colipostefr_unittest_helper',
            string='Unit Test Helper',
            relation='res.company',
            type='boolean',
            help="Seulement utile pour les développeurs.\n"
                 "Si coché enregistre les données du picking ColiPoste\n"
                 "dans le dossier temporaire système du serveur.\n"
                 "Ce fichier peut être utilisé pour créer "
                 "de nouveaux tests unitaires python"),
        'webservice_message': fields.related(
            'company_id.colipostefr_webservice_message',
            string='Enregistre les Messages du Webservice',
            relation='res.company',
            type='boolean',
            help="Pour ColiPoste International. \nSi coché, un commentaire "
                 "sera créé dans le bon de livraison\nsi la réponse du "
                 "web service contient un message additionnel."),
        'repo_task_id': fields.related(
            'company_id.colipostefr_repo_task_id',
            string='Tâche Edi',
            relation='res.company',
            type='many2one',
            help="Liaison à la tâche qui exporte le fichier edi.\n"
                 "Ne pas créer de tâche spécifique ici.\n"
                 "La valeur par défaut pour la principale société d'Odoo "
                 "ne doit pas changer.\nUtilisez une tâche créée "
                 "depuis le repository 'La Poste Edi'\n"
                 "(Configuration > File Exchange > File Repositories "
                 "> La Poste Edi)"),
    }

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    _defaults = {
        'company_id': _default_company,
    }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        # update related fields
        values = {}
        values['currency_id'] = False
        if not company_id:
            return {'value': values}
        company = self.pool.get('res.company').browse(
            cr, uid, company_id, context=context)
        fields = ['account', 'support_city', 'support_city_code',
                  'password', 'webservice_message', 'repo_task_id']
        for field in fields:
            cpny_field = 'colipostefr_%s' % field
            values[field] = company[cpny_field]
        return {'value': values}

    def create(self, cr, uid, values, context=None):
        id = super(ColiposteFrConfigSettings, self).create(
            cr, uid, values, context=context)
        # Hack: to avoid some nasty bug, related fields are not written
        # upon record creation.  Hence we write on those fields here.
        vals = {}
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.related) and fname in values:
                vals[fname] = values[fname]
        self.write(cr, uid, [id], vals, context)
        return id

    # New api bug on transient model
    #company_id = fields.Many2one(
    #    'res.company',
    #    string='Company',
    #    required=True,
    #    )
    #    #default=_default_company
    #account = fields.Char(
    #    string='Compte',
    #    size=6,
    #    store=True, readonly=True,
    #    related='company_id.colipostefr_account',
    #    help="Nombre à 6 caractères.\n"
    #         "La valeur par défaut est 964744"),
    #support_city = fields.Char(
    #    string='Site de Prise en Charge',
    #    size=64,
    #    related='company_id.colipostefr_support_city',
    #    help="Site de prise en charge de la poste pour son client.\n"
    #         "Indiquer votre propre centre de rattachement"),
    #support_city_code = fields.Char(
    #    string='Code Site de Prise en Charge',
    #    size=6,
    #    related='company_id.colipostefr_support_city_code',
    #    help="Utile uniquement pour le module colissimo EDI "
    #         "(facultatif cependant)"),
    #password = fields.Char(
    #    string='Mot de passe site web',
    #    related='company_id.colipostefr_password',
    #    help="Le mot de passe doit être identique "
    #         "à celui de votre espace client.\n"
    #         "Uniquement nécessaire pour les envois à l'étranger.\n"
    #         "Mettre un mot de passe complexe"),
    #unittest_helper = fields.Boolean(
    #    string='Unit Test Helper',
    #    related='company_id.colipostefr_unittest_helper',
    #    help="Seulement utile pour les développeurs.\n"
    #         "Si coché enregistre les données du picking ColiPoste\n"
    #         "dans le dossier temporaire système du serveur.\n"
    #         "Ce fichier peut être utilisé pour créer "
    #         "de nouveaux tests unitaires python"),
    #webservice_message = fields.Boolean(
    #    string='Enregistre les Messages du Webservice',
    #    related='company_id.colipostefr_webservice_message',
    #    help="Pour ColiPoste International. \nSi coché, un commentaire "
    #         "sera créé dans le bon de livraison\nsi la réponse du "
    #         "web service contient un message additionnel."),
    #repo_task_id = fields.Many2one(
    #    'repository.task',
    #    string="Tâche Edi",
    #    related='company_id.colipostefr_repo_task_id',
    #    help="Liaison à la tâche qui exporte le fichier edi.\n"
    #         "Ne pas créer de tâche spécifique ici.\n"
    #         "La valeur par défaut pour la principale société d'Odoo "
    #         "ne doit pas changer.\nUtilisez une tâche créée "
    #         "depuis le repository 'La Poste Edi'\n"
    #         "(Configuration > File Exchange > File Repositories "
    #         "> La Poste Edi)"),

    #@api.onchange('company_id')
    #def change_company(self):
    #    if self.company_id:
    #        self.account = self.company_id.colipostefr_account

    def button_send_image_to_printer(self, cr, uid, ids, context=None):
        """ Implement your own method according to printing solution
        """
        return ColiPosteConfig().get_image_data()
