# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: David BEAL
#    Copyright 2014 Akretion
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class ResCompany(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'colipostefr_account': fields.char(
            'Compte',
            size=6,
            help="Nombre à 6 caractères.\n"
                 "La valeur par défaut est 964744"),
        'colipostefr_support_city': fields.char(
            'Site de Prise en Charge',
            size=64,
            help="Site de prise en charge de la poste pour son client.\n"
                 "Indiquer votre propre centre de rattachement"),
        'colipostefr_support_city_code': fields.char(
            'Code Site de Prise en Charge',
            size=6,
            help="Utile uniquement pour le module colissimo EDI (facultatif cependant)"),
        'colipostefr_password': fields.char(
            'Mot de passe site web',
            help="Le mot de passe doit être identique "
                 "à celui de votre espace client.\n"
                 "Uniquement nécessaire pour les envois à l'étranger.\n"
                 "Mettre un mot de passe complexe"),
        'colipostefr_unittest_helper': fields.boolean(
            'Unit Test Helper',
            help="Seulement utile pour les développeurs.\n"
                 "Si coché enregistre les données du picking ColiPoste\n"
                 "dans le dossier temporaire système du serveur.\n"
                 "Ce fichier peut être utilisé pour créer "
                 "de nouveaux tests unitaires python"),
        'colipostefr_webservice_message': fields.boolean(
            'Enregistre les Messages du Webservice',
            help="Pour ColiPoste International. \nSi coché, un commentaire "
                 "sera créé dans le bon de livraison\nsi la réponse du "
                 "web service contient un message additionnel."),
        'colipostefr_repo_task_id': fields.many2one(
            'repository.task',
            string="Tâche Edi",
            help="Liaison à la tâche qui exporte le fichier edi.\n"
                 "Ne pas créer de tâche spécifique ici.\n"
                 "La valeur par défaut pour la principale société d'Odoo "
                 "ne doit pas changer\n"
                 "Utilisez une tâche créée depuis le repository 'La Poste Edi'\n"
                 "(Configuration > File Exchange > File Repositories "
                 "> La Poste Edi)"),
    }

    _defaults = {
        'colipostefr_account': '',
        'colipostefr_support_city': '... PFC',
        'colipostefr_password': '',
        'colipostefr_unittest_helper': False,
        'colipostefr_webservice_message': True,
    }
