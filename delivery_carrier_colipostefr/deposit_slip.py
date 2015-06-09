# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import unicodecsv
from cStringIO import StringIO
from csv import Dialect
from _csv import QUOTE_MINIMAL, register_dialect
import base64

# This code is used by Colissimo and So Colissimo
# TODO this code is not fully updated for So Colissimo
# coorection will be firstly defined in v7 branch


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
            # Important : cette date doit
            # correspondre à la date réelle de dépôt physique des colis sur
            # le site d’entrée du trafic et à la date d’émission du fich EDI.
            "Date d'émission du bordereau": validate_date,
            "Version Format Fichier": "02.00",
            "Site Prise en charge": (company.colipostefr_support_city_code
                                     or ''),
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

    def name_formatting(self, cr, uid, address, context=None):
        '''La Poste EDI specs page 12 : the field must contain
        Title`Firstname`Lastname
        Title can be 'M.' or 'MME', but the experience at Barroux Abbey
        shows that any title can be used
        '''
        assert address, 'Address must not be empty'
        name_split = address.name.split(' ')
        if len(name_split) >= 2:
            res = u'%s`%s' % (name_split[0], ' '.join(name_split[1:]))
        else:
            res = u'`%s' % address.name
        if address.title:
            if address.title.shortcut:
                res = u'%s`%s' % (address.title.shortcut, res)
            else:
                res = u'%s`%s' % (address.title, res)
        else:
            res = u'%s`%s' % ('M.', res)
        if len(res) > 37:  # max size is 35 + 2 x '`'
            res = res[0:37]
        return res

    def create_edi_lines(self, cr, uid, deposit, context=None):
        lines = []
        for picking in deposit.picking_ids:
            if picking.carrier_code not in ['EI', 'AI']:
                address = picking.partner_id
                # TODO So Colissimo see correction in V7 branch
                # dropoff_site = picking.dropoff_site_id
                non_machi = "N"
                # TODO
                # if picking.non_machinable:
                #     non_machi = "O"
                dropoff_code = None
                # TODO So Colissimo see correction in V7 branch
                # if picking.to_dropoff_site:
                #     dropoff_code = dropoff_site.code
                AR = "N"
                if picking.carrier_code == "6C":
                    AR = "O"
                name = self.name_formatting(
                    cr, uid, address, context=context)
                phone = self.phone_number_formating(
                    cr, uid, address.phone, context=context)
                mobile = self.phone_number_formating(
                    cr, uid, address.mobile, context=context)
                phone, mobile = self._coliposte_default_phone(
                    cr, uid, phone, mobile, context=context)
                email = self._coliposte_default_mail(
                    cr, uid, address.email, context=context)
                if not phone and not mobile and not email:
                    raise orm.except_orm(
                        _('Error'),
                        _(u"Information manquante sur le bon de "
                          u"livraison %s : il faut renseigner au moins "
                          u"le téléphone, le portable ou l'e-mail sur "
                          u"le partenaire %s "
                          u"pour éviter une surtaxation par La Poste)")
                        % (picking.name, picking.partner_id.name))
                country_code = ''
                if address.country_id:
                    country_code = address.country_id.code
                for pack in picking._get_packages_from_picking():
                    if not pack.parcel_tracking:
                        raise orm.except_orm(
                            _('Missing Parcel tracking on package %s')
                            % pack.name)
                    sequence = pack.parcel_tracking[2:-1]
                    weight = int(pack.weight*1000)
                    # TODO So Colissimo see correction in V7 branch
                    barcode_routage = ''
                    # if picking.coliss_barcode_routage:
                    #     cab_label = pick.c_barcode_routage.replace(
                    #         ' ', '')[1:]
                    #     cab_content = pick.c_barcode_routage.replace(
                    #         ' ','')[:-1]
                    #     barcode_routage = "%s`%s`%s`%s`%s" % (
                    #         dropoff_site.lot_routing,
                    #         dropoff_site.distri_sort,
                    #         dropoff_site.version_plan,
                    #         cab_label,
                    #         cab_content
                    #     )
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
                        "Raison sociale": "",
                        "Première ligne d’adresse": "",
                        "Seconde ligne d'adresse": "",
                        "Troisième ligne d'adresse": address.street,
                        "Quatrième ligne d’adresse": address.street2 or "",
                        "Code postal du destinataire": address.zip,
                        "Commune du destinataire": address.city,
                        "Commentaire 1": "",
                        "Information de routage": barcode_routage,
                        "Code Pays Destinataire": country_code,
                        "Niveau de recommandation": "",
                        "Accusé réception": AR,
                        "Type de TRI Colis": "NON",
                        "Franc de taxe et de droit": "N",
                        "Identifiant Colissimo du destinataire": '',
                        "Téléphone": phone,
                        "Courriel": email,
                        "Téléphone portable": mobile,
                        "Code avoir/promotion": "",
                        "Type Alerte Destinataire": "",
                    }
                    vals.update(
                        self._complete_edi_lines(
                            cr, uid, picking, deposit, address, dropoff_code,
                            context=context)
                    )
                    lines.append(vals)
        return lines

    def _complete_edi_lines(self, cr, uid, picking, deposit, address,
                            dropoff_code, context=None):
        # TODO move to so_colissimo module
        # don't forget to split demo/res_partner.csv field before
        # to drop dependency on 'delivery_carrier_b2c' module
        values = {}
        if deposit.carrier_type == 'so_colissimo':
            values = {
                'Référence chargeur':
                picking.company_id.colipostefr_account_chargeur,
                "Code porte": address.door_code or "",
                "Code porte 2": address.door_code2 or "",
                "Interphone": address.intercom or "",
                "Identifiant du point de retrait": dropoff_code or "",
            }
        return values

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
            "Commentaire 1", "Information de routage",
            "Code Pays Destinataire", "Niveau de recommandation",
            "Accusé réception", "Type de TRI Colis",
            "Franc de taxe et de droit",
            "Identifiant Colissimo du destinataire", "Téléphone", "Courriel",
            "Téléphone portable", "Identifiant du point de retrait",
            "Code avoir/promotion", "Type Alerte Destinataire"],
            dialect=LaposteDialect, encoding='ISO-8859-1')
        for line in lines:
            w.writerow(line)
        f.seek(0)
        datas = f.read()
        return datas

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
                'datas_fname': name,
                'file_type': 'export',
                }

    def _file_document_name(self, cr, uid, header, lines, deposit,
                            context=None):
        company = deposit.picking_ids[0].company_id
        create_date = datetime.strptime(
            deposit.create_date, DEFAULT_SERVER_DATETIME_FORMAT)
        create_date_format = datetime.strftime(create_date, "%Y%m%d.%H%M%S")
        return "%s.%s_001.tmp" % (company.colipostefr_account,
                                  create_date_format)

    def create_file_document(
            self, cr, uid, header, lines, deposit, context=None):
        document_obj = self.pool['file.document']
        name = self._file_document_name(cr, uid, header, lines, deposit,
                                        context=context)
        unencrypted_string = self.create_csv(
            cr, uid, header, lines, context=context)
        unencrypted_datas = base64.encodestring(unencrypted_string)
        vals = self.prepare_doc_vals(
            cr, uid, deposit, name, unencrypted_datas, context=context)
        document_id = document_obj.create(cr, uid, vals, context=context)
        return document_id

    def create_edi_file(self, cr, uid, ids, context=None):
        document_ids = []
        for deposit in self.browse(cr, uid, ids, context=context):
            if not deposit.picking_ids:
                continue
            if deposit.carrier_type in ('colissimo', 'so_colissimo'):
                header = self.create_header_vals(
                    cr, uid, deposit, context=context)
                lines = self.create_edi_lines(
                    cr, uid, deposit, context=context)
                if lines:
                    document_ids = self.create_file_document(
                        cr, uid, header, lines, deposit, context=context)
        return document_ids
