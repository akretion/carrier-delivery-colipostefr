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


class ResCompany(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'colipostefr_account': fields.char(
            'Compte Principal',
            size=6,
            help="Nombre à 6 caractères.\n"
                 "La valeur par défaut est 964744"),
        'colipostefr_world_account': fields.char(
            'Compte International',
            size=6,
            help="Nombre à 6 caractères.\n"
                 "La valeur par défaut est 964744\n"
                 "Potentiellement c'est le même N° que le compte principal."
                 "Dans ce cas, vous pouvez laisser ce champ vide."),
        'colipostefr_support_city': fields.char(
            'Site de Prise en Charge',
            size=64,
            help="Site de prise en charge de la poste pour son client.\n"
                 "Indiquer votre propre centre de rattachement"),
        'colipostefr_support_city_code': fields.char(
            'Code Site de Prise en Charge',
            size=6,
            help="Utile uniquement pour le module colissimo EDI "
                 "(facultatif cependant)"),
        'colipostefr_password': fields.char(
            'Mot de passe site web',
            help="Le mot de passe doit être identique "
                 "à celui de votre espace client.\n"
                 "(https://www.coliposte.fr/pro/services/accueil_pro.jsp)"
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
            help=u"Pour ColiPoste International. \nSi coché, un commentaire "
                 u"sera créé dans le bon de livraison\nsi la réponse du "
                 u"web service contient un message additionnel.\n"
                 u"De plus le fichier xml envoyé au web service "
                 u"sera stocké dans les pièces jointes."),
        'colipostefr_repo_task_id': fields.many2one(
            'repository.task',
            string="Tâche Edi",
            help="Liaison à la tâche qui exporte le fichier edi.\n"
                 "Ne pas créer de tâche spécifique ici.\n"
                 "La valeur par défaut pour la principale société d'Odoo "
                 "ne doit pas changer.\nUtilisez une tâche créée "
                 "depuis le repository 'La Poste Edi'\n"
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
