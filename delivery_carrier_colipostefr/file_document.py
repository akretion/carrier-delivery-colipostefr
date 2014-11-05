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
from openerp.addons.file_repository.file_repository import get_full_path
from tempfile import TemporaryFile


class FileDocument(orm.Model):
    _inherit = "file.document"

    def export_file_document(
            self, cr, uid, connection, filedocument, context=None):
        sent_file = super(FileDocument, self).export_file_document(
            cr, uid, connection, filedocument, context=context)
        file_content = "%s %s" % (filedocument.name, filedocument.file_size)
        control_file = TemporaryFile('w+b')
        control_file.write(file_content)
        control_file.seek(0)
        full_path = get_full_path(filedocument.repository_id.home_folder,
                                  filedocument.task_id.folder)
        connection.send(full_path, 'control.file', control_file)
        return sent_file

    def create(self, cr, uid, vals, context=None):
        if 'file_type' not in vals:
            vals.update({'file_type': 'export'})
        return super(FileDocument, self).create(cr, uid, vals, context=context)
