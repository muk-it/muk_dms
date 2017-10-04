# -*- coding: utf-8 -*-

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
from odoo.tools import pg_varchar, ustr

Default = object()    

def convert_to_file(value, records):
    if isinstance(value, models.BaseModel) and value._name == "muk_dms.file":
        if value.exists():
            return value
    elif isinstance(value, dict):
        if 'id' in value:
            return records.env['muk_dms.file'].sudo().browse(value['id'])
    return None

class Document(fields.Field):
    type = 'document'
    column_type = None

    def convert_to_export(self, value, record):
        if isinstance(value, models.BaseModel) and value._name == "muk_dms.file":
            if value.exists():
                return value.with_context({}).content
        elif isinstance(value, dict):
            if 'content' in value and value['content'] and not re.match(r"^\d+(\.\d*)? \w+$", value['content']):
                return value['content']
            elif 'id' in value:
                file = records.env['muk_dms.file'].sudo().browse(value['id'])
                return file.with_context({}).content
        return None

    def convert_to_display_name(self, value, record):
        if isinstance(value, models.BaseModel) and value._name == "muk_dms.file":
            if value.exists():
                return value.name
        elif isinstance(value, dict):
            if 'name' in value:
                return value['name']
        return None

    def read(self, records):
        domain = [
            ('reference_model', '=', records._name),
            ('reference_field', '=', self.name),
            ('reference_id', 'in', records.ids),
        ]
        files = { 
            file.reference_id: {
                'id': file.id,
                'name': file.name,
                'content': file.content,
                'directory': file.directory.name_get(),
                'perm_write': file.perm_write,
                'perm_unlink': file.perm_unlink,
                'locked': file.locked.locked_by_ref and file.locked.locked_by_ref.name_get() or 
                    not (len(file.locked) == 0 or file.locked.id == False),
            }
            for file in records.env['muk_dms.file'].sudo().search(domain)
        }
        for record in records:
            record._cache[self.name] = files.get(record.id, None)
        
    def write(self, records, value):
        if isinstance(value, models.BaseModel) and value._name == "muk_dms.file":
            if value.exists():
                for record in records:
                    value.write({
                        'reference_model': record._name,
                        'reference_field': self.name,
                        'reference_id': record.id
                    })
        elif isinstance(value, dict):            
            values = {}
            if 'directory' in value and isinstance(value['directory'], list):
                if isinstance(value['directory'][0], list):
                    values['directory'] = value['directory'][0][0]
                else:
                    values['directory'] = value['directory'][0]
            if 'name' in value and value['name']:
                values['name'] = value['name']
            if 'content' in value and value['content'] and not re.match(r"^\d+(\.\d*)? \w+$", value['content']):
                values['content'] = value['content']
            domain = [
                ('reference_model', '=', records._name),
                ('reference_field', '=', self.name),
                ('reference_id', 'in', records.ids),
            ]
            files = records.env['muk_dms.file'].sudo().search(domain)
            with records.env.norecompute():
                if 'content' in value and not value['content']:
                    files.unlink()
                else:
                    files.write(values)
                    if 'directory' in values and 'name' in values and 'content' in values:
                        for record in (records - records.browse(files.mapped('reference_id'))):
                            values.update({
                                'reference_model': record._name,
                                'reference_field': self.name,
                                'reference_id': record.id
                            })
                            files.create(values)
            
      
        
        
