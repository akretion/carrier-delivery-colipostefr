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
import logging
_logger = logging.getLogger(__name__)

TEMP_TABLE = 'partner_tmp_dropoff_coliposte'

# TODO clean this dirty code
# TODO remove useless haskey (before refactor massive insertion in tmp table)


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

    def refresh_dropoff_site(self, cr, uid, context=None):
        __, country_id = self.pool['ir.model.data'].\
            get_object_reference(cr, uid, 'base', 'fr')

        _logger.info('Start to update existing dropoffsite')
        #UPDATE EXISTING DROPOFF SITE
        cr.execute("""
            UPDATE res_partner as p SET
                name=tmp.name,
                ref=tmp.code,
                street=tmp.street,
                street2=tmp.street2,
                city=tmp.city,
                zip=tmp.zip
                FROM partner_tmp_dropoff_coliposte AS tmp
                    JOIN partner_dropoff_site
                        ON partner_dropoff_site.code = tmp.code
                            AND partner_dropoff_site.dropoff_type = %s
                WHERE
                    p.ref = tmp.code
                    AND p.id = partner_dropoff_site.partner_id
                    AND (
                        p.name != tmp.name
                        OR p.ref != tmp.code
                        OR p.street != tmp.street
                        OR p.street2 != tmp.street2
                        OR p.city != tmp.city
                        OR p.zip != tmp.zip
                        )
            """, (self._dropoff_type,))

        cr.execute("""
            UPDATE partner_dropoff_site as d SET
                weight=tmp.weight,
                lot_routing=tmp.lot_routing,
                longitude=tmp.longitude,
                subtype=tmp.subtype,
                latitude=tmp.latitude,
                distri_sort=tmp.distri_sort,
                version_plan=tmp.version_plan
                FROM partner_tmp_dropoff_coliposte AS tmp
                WHERE
                    d.code = tmp.code
                    AND d.dropoff_type = %s
                    AND (
                        d.weight != tmp.weight
                        OR d.lot_routing != tmp.lot_routing
                        OR d.longitude != tmp.longitude
                        OR d.subtype != tmp.subtype
                        OR d.latitude != tmp.latitude
                        OR d.distri_sort != tmp.distri_sort
                        OR d.version_plan != tmp.version_plan
                        )
            """, (self._dropoff_type,))

        _logger.info('Updating done start massive insertion')
        #INSERT MISSING DROPOFF SITE
        cr.execute("""
            WITH partner AS (
                INSERT INTO res_partner(
                    name,
                    ref,
                    street,
                    street2,
                    city,
                    zip,
                    create_date,
                    active,
                    notification_email_send,
                    country_id)
                SELECT
                    name,
                    code,
                    street,
                    street2,
                    city,
                    zip,
                    now(),
                    True,
                    False,
                    %s
                FROM partner_tmp_dropoff_coliposte
                WHERE code in (
                    SELECT tmp.code
                        FROM partner_tmp_dropoff_coliposte as tmp
                            LEFT JOIN partner_dropoff_site as drop
                                ON drop.code = tmp.code
                                AND drop.dropoff_type = %s
                        WHERE drop.code is NULL)
                RETURNING id as partner_id, ref
                )
            , dropoff AS (
                INSERT INTO partner_dropoff_site(
                    partner_id,
                    code,
                    weight,
                    lot_routing,
                    longitude,
                    subtype,
                    latitude,
                    distri_sort,
                    version_plan,
                    create_date,
                    dropoff_type)
                SELECT
                    partner_id,
                    ref, weight,
                    lot_routing,
                    longitude,
                    subtype,
                    latitude,
                    distri_sort,
                    version_plan,
                    now(),
                    %s
                FROM partner
                    JOIN partner_tmp_dropoff_coliposte
                        ON partner_tmp_dropoff_coliposte.code = partner.ref
                RETURNING id
                )
            SELECT count(id) FROM dropoff""",
            (country_id, self._dropoff_type, self._dropoff_type))
        res = cr.fetchone()
        _logger.info('Insert %s new dropoffsite', res[0])

        #Fill the many2one on the res_partner
        cr.execute("""UPDATE res_partner
            SET dropoff_site_id = partner_dropoff_site.id
            FROM partner_dropoff_site
            WHERE partner_dropoff_site.partner_id = res_partner.id
                AND dropoff_site_id IS DISTINCT FROM partner_dropoff_site.id""")
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
