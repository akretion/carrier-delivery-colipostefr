# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm
import base64
from cStringIO import StringIO
import time

# TODO clean this dirty code
# TODO the street2 and street3 should be merge into the tmp table
# this will avoid costing post processing step during update

class FileDocument(orm.Model):
    _inherit = "file.document"

    def import_datas(self, cr, uid, file_doc, context=None):
        ""
        super(FileDocument, self).import_datas(cr, uid, file_doc,
                                               context=context)
        # TODO manage execption_messages returned by this method
        self.send_datas_in_temp_table(
            cr, uid, file_doc, context=context)
        self.pool['partner.dropoff.site'].refresh_dropoff_site(
            cr, uid, context=context)

    #TODO Refactor this method and remove the hashkey (is not needed anymore)
    def send_datas_in_temp_table(self, cr, uid, file_doc, context=None):
        header = [
            'code', 'name', 'street', 'street2', 'street3',
            'local', 'zip', 'city', 'latitude', 'longitude',
            'accessibility', 'subtype', 'weight', 'lot_routing',
            'distri_sort', 'version_plan', 'hashkey']
        columns = ', '.join(header)
        base_query = "INSERT INTO partner_tmp_dropoff_coliposte " \
                     "\n (%s) \n  VALUES " % columns
        if file_doc.datas:
            #sql_error_counter = 0
            #sql_error_messages = []
            str_io = StringIO()
            str_io.writelines(base64.b64decode(file_doc.datas))
            str_io.seek(0)
            line = str_io.readline()
            if line:
                # Sql buffer table deletion
                try:
                    cr.execute('DELETE FROM partner_tmp_dropoff_coliposte')
                except Exception, e:
                    raise Exception(e.message)
                vals = {'response': False}
                self.pool['file.document'].write(
                    cr, uid, file_doc.id, vals, context=context)
            else:
                raise Exception(
                    "Le fichier est vide. Pas de mise à jour")
            # first line must not be imported
            line = str_io.readline()
            #print 'Début tmp', time.ctime()
            while line:
                if line[:2] == 'PR':
                    # replace ',' by ';' and add quote to columns
                    # and escape simple quote
                    site = "'" + line[3:].replace("'", "''")
                    site = site.replace(';', "', '")[:-1]
                    site += "','" + line[3:-1].replace("'", "''") + "'"
                    site = site.replace('ESPACE CITYSSIMO', 'CITYSSIMO').replace('BUREAU DE POSTE', 'LA POSTE')
                    query = base_query + " (%s)" % site
                    query = query.replace('\xa0', '')
                    try:
                        cr.execute(query)
                        pass
                    except Exception, e:
                        #sql_error_counter += 1
                        #error is recorded
                        message = "Erreur :" \
                                  " <<<  %s query: %s >>> \n\n" \
                                  % (e.message, query)
                        raise Exception(message)
                        #message = "-------\nErreur " \
                        #          + str(sql_error_counter) + ": " \
                        #          " <<<  %s query: %s >>> \n\n" \
                        #          % (e.message, query)
                        #sql_error_messages.append(message)
                        #if sql_error_counter >= EXCEPT_LIMIT:
                            # errors are raised only when limit is reached
                            #cr.commit()
                            #raise Exception(
                            #    EXCEPT_MESSAGE + ''.join(sql_error_messages))
                else:
                    #print 'break Tmp'
                    break
                line = str_io.readline()
            #print ' end while Tmp', time.ctime()
            #if sql_error_messages:
            #    return sql_error_messages
        return False
