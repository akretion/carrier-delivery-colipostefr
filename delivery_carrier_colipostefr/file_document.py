# -*- coding: utf-8 -*-
###############################################################################
#
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
from openerp.addons.file_repository.file_repository import get_full_path
from tempfile import TemporaryFile


class FileDocument(orm.Model):
    _inherit = "file.document"

    def export_file_document(
            self, cr, uid, connection, filedocument, context=None):
        sent_file = super(FileDocument, self).export_file_document(
            cr, uid, connection, filedocument, context=context)
        #if crypted file
        #file_content = "%s.gpg %s PGP" % (document.name, size)
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
