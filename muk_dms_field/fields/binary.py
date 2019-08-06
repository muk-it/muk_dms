###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Field 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
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
        'filename': False,
        'directory': False, 
        'context_dependent': True,
    }

    def read(self, records):
        domain = [
            ('reference_model', '=', records._name),
            ('reference_field', '=', self.name),
            ('reference_id', 'in', records.ids),
        ]
        cache = records.env.cache
        model = records.env['muk_dms.file'].sudo()
        files = model.with_context(active_test=False).search(domain)
        file_values = {file.reference_id: file.content for file in files}
        for record in records:
            cache.set(record, self, file_values.get(record.id, False))
            
    def create(self, record_values):
        if not record_values:
            return
        env = record_values[0][0].env
        model = env['muk_dms.file'].sudo()
        with env.norecompute():
            for record, value in record_values:
                if value:
                    model.create([{
                            'name': self.filename(record) if callable(self.filename) else self.filename,
                            'directory': self.directory(record) if callable(self.directory) else self.directory,
                            'reference_model': record._name,
                            'reference_field': self.name,
                            'reference_id': record.id,
                            'content': value,
                        } for record, value in record_values if value
                    ])

    def write(self, records, value):
        files = records.env['muk_dms.file'].sudo().search([
            ('reference_model', '=', records._name),
            ('reference_field', '=', self.name),
            ('reference_id', 'in', records.ids),
        ])
        with records.env.norecompute():
            if value:
                files.write({'content': value})
                existing_records = records.browse(files.mapped('reference_id'))
                if len(existing_records) < len(records):
                    files.create([{
                            'name': self.filename(record) if callable(self.filename) else self.filename,
                            'directory': self.directory(record) if callable(self.directory) else self.directory,
                            'reference_model': record._name,
                            'reference_field': self.name,
                            'reference_id': record.id,
                            'content': value,
                        } for record in (records - existing_records)
                    ])
            else:
                files.unlink()