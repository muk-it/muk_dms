###################################################################################
# 
#    Copyright (C) 2017 MuK IT GmbH
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
###################################################################################

import re
import logging

from odoo import _
from odoo import models, api, fields
from odoo.tools import pg_varchar, ustr, human_size

_logger = logging.getLogger(__name__)

class DocumentBinary(fields.Field):
    
    type = 'document_binary'
    column_type = None
    
    _slots = {
        'prefetch': False,             
        'context_dependent': True,
        'filename': False,
        'directory': False,
    }
    
    def _setup_attrs(self, model, name):
        super(DocumentBinary, self)._setup_attrs(model, name)
        if self.directory is not None:
            directory = self.directory
            self.directory = directory if callable(directory) else lambda model: directory
        if self.filename is not None:
            filename = self.filename
            self.filename = filename if callable(filename) else lambda model: filename

    def read(self, records):
        domain = [
            ('reference_model', '=', records._name),
            ('reference_field', '=', self.name),
            ('reference_id', 'in', records.ids),
        ]
        files = {
            file.reference_id: file.content 
            for file in records.env['muk_dms.file'].sudo().with_context(active_test=False).search(domain)
        }
        cache = records.env.cache
        for record in records:
            cache.set(record, self, files.get(record.id, False))
        
    def write(self, records, value, create=False):
        if create:
            files = records.env['muk_dms.file'].sudo()
        else:
            files = records.env['muk_dms.file'].sudo().with_context(active_test=False).search([
                ('reference_model', '=', records._name),
                ('reference_field', '=', self.name),
                ('reference_id', 'in', records.ids),
            ])
        with records.env.norecompute():
            if value:
                for record in (records - (records - records.browse(files.mapped('reference_id')))):
                    files.write({
                        'content': value,
                        'name': self.filename(record) if callable(self.filename) else self.filename
                    })
                for record in (records - records.browse(files.mapped('reference_id'))):
                    files.create({
                        'name': self.filename(record) if callable(self.filename) else self.filename,
                        'directory': self.directory(record) if callable(self.directory) else self.directory,
                        'reference_model': record._name,
                        'reference_field': self.name,
                        'reference_id': record.id,
                        'content': value,
                    })
            else:
                files.unlink()
