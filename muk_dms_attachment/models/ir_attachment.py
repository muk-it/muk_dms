## -*- coding: utf-8 -*-

###################################################################################
# 
#    MuK Document Management System
#
#    Copyright (C) 2018 MuK IT GmbH
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

import base64
import hashlib
import itertools
import logging
import mimetypes
import os
import re
from collections import defaultdict

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import config, human_size, ustr, html_escape
from odoo.tools.mimetypes import guess_mimetype

_logger = logging.getLogger(__name__)

class DocumentIrAttachment(models.Model):
    
    _inherit = 'ir.attachment'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    storage_type = fields.Char(
        compute='_compute_storage_type',
        string="Storage Type")
    
    store_document = fields.Many2one(
        'muk_dms.file', 
        string="Document File",)
    
    #----------------------------------------------------------
    # Function
    #----------------------------------------------------------
    
    @api.multi
    def migrate(self):
        for attach in self:
            attach.write({'datas': attach.datas})
    
    @api.model
    def force_storage(self):
        """Override force_storage without calling super,
           cause domain need to be edited."""
        if not self.env.user._is_admin():
            raise AccessError(_('Only administrators can execute this action.'))
        domain = {
            'db': ['|',['store_fname', '!=', False],['store_document', '!=', False]],
            'file': ['|',['db_datas', '!=', False],['store_document', '!=', False]],
            'documents': ['|',['store_fname', '!=', False],['db_datas', '!=', False]],
        }[self._storage()]
        for attach in self.search(domain):
            attach.write({'datas': attach.datas})
        return True
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('datas')
    def _compute_storage_type(self):
        storage = {
            'db': 'Database',
            'file': 'File Storage',
            'documents': 'MuK Documents',
        }[self._storage()]
        for attach in self:
            current = None
            if attach.store_document:
                current = 'MuK Documents'
            elif attach.db_datas:
                current = 'Database'
            elif attach.store_fname:
                current = 'File Storage'
            if storage == current:
                attach.storage_type = current
            elif not current:
                attach.storage_type = storage
            else:
                attach.storage_type = "%s >> %s" % (current, storage)
    
    @api.depends('store_fname', 'db_datas', 'store_document')
    def _compute_datas(self):
        bin_size = self._context.get('bin_size')
        for attach in self:
            if attach.store_document:
                attach.datas = attach.sudo().store_document.content
            else:
                super(DocumentIrAttachment, attach)._compute_datas()

    #----------------------------------------------------------
    # Create, Write, Delete
    #----------------------------------------------------------

    def _compute_mimetype(self, values):
        mimetype = super(DocumentIrAttachment, self)._compute_mimetype(values)
        if not mimetype or mimetype == 'application/octet-stream':
            mimetype = None
            for attach in self:
                if attach.mimetype:
                    mimetype = attach.mimetype
                if not mimetype and attach.datas_fname:
                    mimetype = mimetypes.guess_type(attach.datas_fname)[0]
        return mimetype or 'application/octet-stream'

    def _attachment_directory(self, vals):
        directory = self.env['ir.config_parameter'].sudo().get_param(
            'muk_dms_attachment.attachment_directory', None)
        if directory:
            return directory
        raise ValidationError(_('A directory has to be defined.'))
        
    def _inverse_datas(self):
        """Override _inverse_datas without calling super,
           cause vals need to be changed accordingly."""
        location = self._storage()
        for attach in self:
            value = attach.datas
            bin_data = base64.b64decode(value) if value else b''
            vals = {
                'file_size': len(bin_data),
                'checksum': self._compute_checksum(bin_data),
                'index_content': self._index(bin_data, attach.datas_fname, attach.mimetype),
                'store_fname': False,
                'db_datas': value,
            }
            if value and location == 'file':
                vals['store_fname'] = self._file_write(value, vals['checksum'])
                vals['store_document'] = False
                vals['db_datas'] = False
            elif value and location == 'documents':
                directory = self._attachment_directory(vals)
                store_document = self.env['muk_dms.file'].sudo().create({
                    'name': "[A-%s] %s" % (attach.id, attach.datas_fname or attach.name),
                    'directory': directory,
                    'content': value})
                vals['store_document'] = store_document.id
                vals['mimetype'] = store_document.mimetype
                vals['store_fname'] = False
                vals['db_datas'] = False
            fname = attach.store_fname
            super(DocumentIrAttachment, attach.sudo()).write(vals)
            if fname:
                self._file_delete(fname)
    
    @api.multi
    def copy(self, default=None):
        if 'store_document' in default:
            datas = self.env['muk_dms.file'].sudo().browse(default['store_document']).content
            default.update({'datas': datas})
            del default['store_document']
        return super(DocumentIrAttachment, self).copy(default)

    @api.multi
    def unlink(self):
        files = set(attach.store_document for attach in self if attach.store_document)
        print("unlink", files)
        result = super(DocumentIrAttachment, self).unlink()
        for file in files:
            file.sudo().unlink()
        return result