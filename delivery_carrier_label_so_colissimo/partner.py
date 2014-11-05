# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#          Sébastien BEAU <sebastien.beau@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
import csv
import time

TEMP_TABLE = 'partner_tmp_dropoff_coliposte'


def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield dict([(key, unicode(value, 'utf-8'))
                    for key, value in row.iteritems()])


class AbstractDropoffColiposte(orm.AbstractModel):
    _name = 'abstract.dropoff.coliposte'
    _inherit = 'abstract.dropoff.site'

    _columns = {
        'lot_routing': fields.char(
            'Lot routing',
            size=30,
            help="Lot d'acheminement pour 'So Colissimo'"),
        'distri_sort': fields.char(
            'Distri sort',
            size=30,
            help="Distribution sort pour 'So Colissimo'"),
        'version_plan': fields.char(
            'Version plan',
            size=30,
            help="Plan version pour 'So Colissimo'"),
        'hashkey': fields.char(
            'Hashkey',
            help="Columns concatenation used to compare records and "
                 "avoid future update of identical records"
        )
    }


class PartnerDropoffSite(orm.Model):
    _inherit = ['partner.dropoff.site', 'abstract.dropoff.coliposte']
    _name = 'partner.dropoff.site'
    _dropoff_type = 'colipostefr'

    def get_required_fields(self, cr, uid, context=None):
        required_but_default_val = (
            'notification_email_send',
            'property_account_receivable',
            'property_account_payable')
        required_fields = [
            (field, value)
            for field, value in self.pool['res.partner']._columns.items()
            if value.required is True
            and field not in required_but_default_val]
        required_but_taken_account = (
            'dropoff_type',
            'partner_id')
        required_fields.extend([
            (field, value)
            for field, value in self._columns.items()
            if value.required is True
            and field not in required_but_taken_account
        ])
        return required_fields

    def write_or_create_dropoff_site(
            self, cr, uid, context=None):
        """
        trouver es manque
        """
        # search dropoff in both table
        query = "SELECT id, code, hashkey FROM %s"
        cr.execute(query % TEMP_TABLE)
        new_dropoff = {code: {'id': id, 'hash': hash}
                       for id, code, hash in cr.fetchall()}
        param = "%s WHERE dropoff_type = '%s'" \
                % (self._table, self._dropoff_type)
        cr.execute(query % param)
        original_dropoff = {code: {'id': id, 'hash': hash}
                            for id, code, hash in cr.fetchall()}
        dropoff_to_create = list(
            set(new_dropoff.keys()) - set(original_dropoff.keys()))
        intersection = list(
            set(new_dropoff.keys()) & set(original_dropoff.keys()))
        dropoff_to_update = [
            str(x)
            for x in intersection
            if new_dropoff[x]['hash'] != original_dropoff[x]['hash']]
        dropoff_to_update = tuple(dropoff_to_update)
        print '\n\n   len dropoff to CREATE', len(dropoff_to_create)
        print '\n\n   len dropoff to UPDATE', len(dropoff_to_update)
        print 'Pause du progamme pendant 5 secondes\n------------------------'
        time.sleep(5)
        # initial creation of missing dropoff
        print 'before get_required_fields'
        required_fields = self.get_required_fields(cr, uid)
        print required_fields, time.ctime()
        vals = {
            # TODO evaluate if 'carrier_partner_id' is really needed
            #'carrier_partner_id': pool['ir.model.data'].get_object_reference(
            #cr, uid, 'delivery_carrier_colipostefr', 'partner_la_poste')[1],
            'dropoff_type': self._dropoff_type,
        }
        #test sql
        vals_part = {
            'notification_email_send': 'none',
            'country_id': self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'base', 'fr')[1],
        }
        vals_drop = {
            'dropoff_type': self._dropoff_type,
        }
        field1 = ['name', 'notification_email_send', ]
        required_fields_name = vals.keys() + ['partner_id']
        for elm in required_fields:
            field, model = elm[0], elm[1]
            if field not in required_fields_name:
                if model._type in ('char', 'text'):
                    vals[field] = ' '
                if model._type in ('integer', 'float'):
                    vals[field] = 0
                if model._type in ('many2one'):
                    # TODO add a method to override specific values
                    raise Exception(
                        _("Many2one field '%s' is required but no data "
                          "is defined to insert into 'res.partner/%s' tables"
                          % (field, self._name)))
        print 'start to create', time.ctime()
        import pdb;pdb.set_trace()
        counter_created = 0
        q1 = "INSERT INTO res_partner (id, active, name, "
        "notification_email_send) VALUES (%s, True, ' ', 'none')"
        q2 = "INSERT INTO partner_dropoff_site (id, dropoff_type, code, "
        "partner_id) VALUES (%s, 'colipostefr', %s, %s)"
        q3 = "UPDATE res_partner SET dropoff_site_id = %s WHERE id=%s"
        for code in dropoff_to_create:
            counter_created += 1
            vals['code'] = code
            cr.execute("SELECT nextval('res_partner_id_seq')")
            partner_id = cr.fetchone()[0]
            cr.execute(q1 % partner_id)
            #cr.execute(q2 % (code, "currval('res_partner_id_seq'::regclass)"))
            cr.execute("SELECT nextval('partner_dropoff_site_id_seq')")
            dropoff_id = cr.fetchone()[0]
            cr.execute(q2 % (dropoff_id, code, partner_id))
            cr.execute(q3 % (dropoff_id, partner_id))
            #id = self.create(cr, uid, vals, context=context)
            original_dropoff[code] = {'id': dropoff_id}
            #print 'created id', dropoff_id
            if counter_created % 100 == 0:
                print 'commit 100 dropoffsite', counter_created,
                print '\ntime:', time.ctime()
                cr.commit()
        cr.commit()
        # dropoff update for the whole dropoffs
        fields = ['code', 'city', 'latitude', 'longitude', 'name',
                  'street', 'street2', 'subtype', 'weight', 'zip', 'hashkey']
        query = "SELECT %s FROM %s WHERE code IN %s " \
                % (', '.join(fields), TEMP_TABLE, dropoff_to_update)
        print 'start to fetch whole data'
        cr.execute(query)
        result = cr.fetchall()
        print time.ctime()
        print 'start to write'
        import pdb;pdb.set_trace()
        for res in result:
            vals = {}
            vals = {fields[idx]: val
                    for idx, val in enumerate(res)}
            if vals:
                self.write(cr, uid, original_dropoff[res[0]]['id'], vals,
                           context=context)
                print original_dropoff[res[0]], 'vals', vals
                print 'writed', time.ctime()
        print 'the end'
        return True


class PartnerTmpDropoffColiposte(orm.Model):
    "Allow to import datas"
    _name = 'partner.tmp.dropoff.coliposte'
    _inherit = 'abstract.dropoff.coliposte'
    _description = 'Temporary table for coliposte drop-off sites (mass import)'
    HELP = "see ColiPoste documentation"

    _columns = {
        'name': fields.char('name', help=HELP),
        'street': fields.char('street', help=HELP),
        'street2': fields.char('street2', help=HELP),
        'street3': fields.char('street3', help=HELP),
        'local': fields.char('local', help=HELP),
        'zip': fields.char('zip', help=HELP),
        'city': fields.char('city', help=HELP),
        'accessibility': fields.char('accessibility', help=HELP),
    }

    _sql_constraints = [
        ('code_uniq', 'unique(code)',
         "Record with with the same code already exists : must be unique "
         "('%s' table)" % TEMP_TABLE),
    ]
