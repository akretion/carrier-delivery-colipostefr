# -*- coding: utf-8 -*-
###############################################################################
#
#   delivery_carrier_so_colissimo_edi for OpenERP
#   Copyright (C) 2013 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import orm
from openerp.tools.translate import _
from datetime import datetime
import unicodecsv
from cStringIO import StringIO
from csv import Dialect
from _csv import QUOTE_MINIMAL, register_dialect
import base64
from tools import DEFAULT_SERVER_DATETIME_FORMAT
#import gnupg   # not mandatory


class LaposteDialect(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ';'
    quotechar = '"'
    escapechar = '\\'
    doublequote = False
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = QUOTE_MINIMAL
register_dialect("laposte_dialect", LaposteDialect)


class DepositSlip(orm.Model):
    _inherit = "deposit.slip"

    def create_header_vals(self, cr, uid, deposit, context=None):
        company = deposit.picking_ids[0].company_id
        create_date = datetime.strptime(deposit.create_date,
                                        DEFAULT_SERVER_DATETIME_FORMAT)
        create_date_format = datetime.strftime(create_date, "%Y%m%d%H%M")
        validate_date = datetime.strftime(datetime.now(), "%Y%m%d%H%M")
        vals = {
            "Type d'enregistrement": "BBB001",
            "Identifiant du bordereau": deposit.name,
            "Identifiant du client": company.colipostefr_account,
            "Date expédition": create_date_format,
            #Important : cette date doit
            #correspondre à la date réelle de dépôt physique des colis sur le site
            #d’entrée du trafic et à la date d’émission du fichier EDI.
            "Date d'émission du bordereau": validate_date,
            "Version Format Fichier": "02.00",
            "Site Prise en charge": company.colipostefr_support_city_code or '',
            "Nom commercial": company.name,
        }
        return vals

    def _coliposte_default_phone(self, cr, uid, phone, mobile, context=None):
        "You can inherit to customize"
        return (phone, mobile)

    def _coliposte_default_mail(self, cr, uid, mail, context=None):
        "You can inherit to customize"
        return mail

    def phone_number_formating(self, cr, uid, number, context=None):
        if number:
            format_number = number.replace(".", "").replace(" ", "")
            if "+" in format_number:
                format_number = "0" + format_number[3:]
            return format_number
        else:
            return ''

    def create_lines_vals(self, cr, uid, deposit, context=None):
        lines = []
        for picking in deposit.picking_ids:
            if picking.carrier_code not in ['EI', 'AI']:
                address = picking.partner_id
                #TODO
                #dropoff_site = picking.dropoff_site_id
                non_machi = "N"
                #TODO
                #if picking.non_machinable:
                #    non_machi = "O"
                dropoff_code = ''
                #TODO
                #if picking.to_dropoff_site:
                    #dropoff_code = dropoff_site.code
                AR = "N"
                if picking.carrier_code == "6C":
                    AR = "O"
                weight = int(picking.weight*1000)
                name = address.name.replace(' ', '`')
                if address.title:
                    name = address.title.shorcut.replace('.', '') + "`" + name
                else:
                    name = "M`" + name
                phone = self.phone_number_formating(
                    cr, uid, address.phone, context=context)
                mobile = self.phone_number_formating(
                    cr, uid, address.mobile, context=context)
                phone, mobile = self._coliposte_default_phone(
                    cr, uid, phone, mobile, context=context)
                barcode_routage = ""
                sequence = picking.carrier_tracking_ref[2:-1].replace(' ', '')
                #TODO
                #if picking.coliss_barcode_routage:
                #    cab_label = picking.coliss_barcode_routage.replace(' ', '')[1:]
                #    cab_content = picking.coliss_barcode_routage.replace(' ', '')[:-1]
                #    barcode_routage = "%s`%s`%s`%s`%s" % (
                #        dropoff_site.lot_routing,
                #        dropoff_site.distri_sort,
                #        dropoff_site.version_plan,
                #        cab_label,
                #        cab_content
                #    )
                country_code = ''
                if address.country_id:
                    country_code = address.country_id.code

                vals = {
                    "Type d'enregistrement": "DDD001",
                    "Code produit": picking.carrier_code,
                    "Numéro du colis": sequence,
                    "Poids du colis": weight,
                    "Code postal de livraison": address.zip,
                    "Contre-remboursement": 0,
                    "Devise Contre remboursement": "EUR",
                    "Assurance Ad Valorem": 0,
                    "Devise assurance": "EUR",
                    "Livraison Samedi": "O",
                    "Non Mécanisable": non_machi,
                    "Nom du destinataire": name,
                    #picking.address_id.company #si pas magento ca marche comment ?
                    "Raison sociale": "",
                    "Première ligne d’adresse": "",
                    "Seconde ligne d'adresse": "",
                    "Troisième ligne d'adresse": address.street,
                    "Quatrième ligne d’adresse": "",
                    "Code postal du destinataire": address.zip,
                    "Commune du destinataire": address.city,
                    "Commentaire 1": "",
                    "Information de routage": barcode_routage,
                    "Code Pays Destinataire": country_code,
                    "Niveau de recommandation": "",
                    "Accusé réception": AR,
                    "Type de TRI Colis": "NON",
                    "Franc de taxe et de droit": "N",
                    #TODO
                    "Identifiant Colissimo du destinataire": "",
                    "Téléphone": phone,
                    "Courriel": self._coliposte_default_mail(cr, uid, address.email, context=context),
                    "Téléphone portable": mobile,
                    "Code avoir/promotion": "",
                    "Type Alerte Destinataire": "",
                }
                if not phone and not mobile and not address.email:
                    raise orm.except_orm(
                        'Information manquante',
                        "L'un des champs suivant ne doit pas être vide:\n"
                        "mobile, phone, email\n"
                        "(sous peine de surtaxation de La Poste)")
                #'Référence chargeur' field is defined
                #by delivery_carrier_label_so_colissimo module
                if deposit.carrier_type == 'so_colissimo':
                    so_colissimo = {
                        'Référence chargeur': picking.company_id.\
                        colipostefr_account_chargeur,
                        "Code porte": address.door_code or "",
                        "Code porte 2": address.door_code2 or "",
                        "Interphone": address.intercom or "",
                        "Identifiant du point de retrait": dropoff_code or "",
                    }
                    vals.update(so_colissimo)
                lines.append(vals)
        return lines

    def create_csv(self, cr, uid, header, lines, context=None):
        f = StringIO()
        b = unicodecsv.DictWriter(f, [
            "Type d'enregistrement", "Identifiant du bordereau",
            "Identifiant du client", "Date expédition",
            "Date d'émission du bordereau", "Version Format Fichier",
            "Site Prise en charge", "Nom commercial"],
            dialect=LaposteDialect, encoding='ISO-8859-1')
        b.writerow(header)
        w = unicodecsv.DictWriter(f, [
            "Type d'enregistrement", "Code produit", "Numéro du colis",
            "Poids du colis", "Code postal de livraison",
            "Contre-remboursement", "Devise Contre remboursement",
            "Assurance Ad Valorem", "Devise assurance", "Livraison Samedi",
            "Non Mécanisable", "Nom du destinataire", "Raison sociale",
            "Première ligne d’adresse", "Seconde ligne d'adresse",
            "Troisième ligne d'adresse", "Quatrième ligne d’adresse",
            "Code postal du destinataire", "Commune du destinataire",
            "Référence chargeur", "Code porte", "Code porte 2", "Interphone",
            "Commentaire 1", "Information de routage", "Code Pays Destinataire",
            "Niveau de recommandation",
            "Accusé réception", "Type de TRI Colis", "Franc de taxe et de droit",
            "Identifiant Colissimo du destinataire", "Téléphone", "Courriel",
            "Téléphone portable", "Identifiant du point de retrait",
            "Code avoir/promotion", "Type Alerte Destinataire"],
            dialect=LaposteDialect, encoding='ISO-8859-1')
        for line in lines:
            w.writerow(line)
        f.seek(0)
        datas = f.read()
        return datas

    #def create_encrypted_file(self, cr, uid, str_datas, context=None):
    # NOT mandatory
    #    gpg = gnupg.GPG(gnupghome='/home/tmp')
    #    encrypted_datas = gpg.encrypt(str_datas, 'testgpguser@mydomain.com')
    #    encrypted_string = str(encrypted_datas)
    #    return encrypted_string

    def prepare_doc_vals(self, cr, uid, deposit, name, datas, context=None):
        task = deposit.picking_ids[0].company_id.colipostefr_repo_task_id
        if not task:
            raise orm.except_orm(
                _("Carrier task"),
                _("You must define a task for EDI in "
                  "Settings > Configuration > Carrier > ColiPoste fr"))
        task_id = task._model._name+','+str(task.id)
        return {'name': name,
                'active': True,
                'repository_id': task.repository_id.id,
                'direction': 'output',
                'task_id': task_id,
                'datas': datas,
                'datas_fname': name
                }

    def create_file_document(
            self, cr, uid, header, lines, deposit, context=None):
        document_obj = self.pool['file.document']
        company = deposit.picking_ids[0].company_id
        create_date = datetime.strptime(deposit.create_date,
                                        DEFAULT_SERVER_DATETIME_FORMAT)
        create_date_format = datetime.strftime(create_date, "%Y%m%d.%H%M")
        name = "%s.%s" % (company.colipostefr_account, create_date_format)
        unencrypted_string = self.create_csv(
            cr, uid, header, lines, context=context)
        unencrypted_datas = base64.encodestring(unencrypted_string)
        vals = self.prepare_doc_vals(
            cr, uid, deposit, name, unencrypted_datas, context=context)
        document_id = document_obj.create(cr, uid, vals, context=context)
        ##create encrypted file
        #encrypted_string = self.create_encrypted_file(cr, uid, datas, context=context)
        #encrypted_file = base64.encodestring(encrypted_string)
        #encrypted_vals = {
        #    'name': "%s.gpg" % name,
        #    'active': True,
        #    'datas': encrypted_file,
        #    'datas_fname': "%s.gpg" % name,
        #}
        #encrypted_doc_id = document_obj.create(cr, uid, encrypted_vals, context=context)
        #document_ids = [document_id, encrypted_doc_id]
        #return document_ids
        return document_id

    def create_edi_file(self, cr, uid, ids, context=None):
        document_ids = []
        for deposit in self.browse(cr, uid, ids, context=context):
            if not deposit.picking_ids:
                continue
            header = self.create_header_vals(cr, uid, deposit, context=context)
            lines = self.create_lines_vals(cr, uid, deposit, context=context)
            if lines:
                document_ids = self.create_file_document(
                    cr, uid, header, lines, deposit, context=context)
        return document_ids
