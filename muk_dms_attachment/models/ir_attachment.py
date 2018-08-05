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
        comodel_name='muk_dms.file', 
        string="Document File",
        index=True,
        copy=False)
    
    is_document = fields.Boolean(
        string="Document",
        default=False)
    
    store_directory = fields.Many2one(
        related="store_document.directory",
        string="Document Directory",
        readonly=True)
    
    #----------------------------------------------------------
    # Function
    #----------------------------------------------------------
    
    @api.model
    def force_clean(self):
        if not self.env.user._is_admin():
            raise AccessError(_('Only administrators can execute this action.'))
        for attach in self.search(['&',['is_document', '=', True], '|', ['res_field', '=', False], ['res_field', '!=', False]]):
            attach.unlink()
        return True
     
    @api.model
    def force_storage(self):
        if not self.env.user._is_admin():
            raise AccessError(_('Only administrators can execute this action.'))
        attachments = self.search(['&', ['is_document', '=', False], '|', ['res_field', '=', False], ['res_field', '!=', False]])
        for index, attach in enumerate(attachments):
            _logger.info(_("Migrate Attachment %s of %s") % (index, len(attachments)))
            attach.write({'datas': attach.datas})
        return True
    
    @api.multi
    def migrate(self):
        storage = self._storage()
        for index, attach in enumerate(self):
            _logger.info(_("Migrate Attachment %s of %s") % (index, len(self)))
            if attach.is_document and storage != 'documents':
                attach.is_document = False
            attach.write({'datas': attach.datas})
    
    @api.multi
    def _attachment_directory(self):
        attachment_directory = self.env['ir.config_parameter'].sudo().get_param(
            'muk_dms_attachment.attachment_directory', None)
        if attachment_directory:
            directory = self.env['muk_dms.directory'].sudo().browse(int(attachment_directory)) 
            if directory.exists() and directory.read(['settings']):
                return directory.id
        raise ValidationError(_('A directory has to be defined.'))
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('datas')
    def _compute_storage_type(self):
        storage = {
            'db': 'Database',
            'file': 'File Storage',
            'lobject': 'Large Object',
            'documents': 'MuK Documents',
        }[self._storage()]
        for attach in self:
            current = None
            if attach.store_document:
                current = 'MuK Documents'
            elif attach.db_datas:
                current = 'Database'
            elif attach.store_lobject:
                current = 'Large Object'
            elif attach.store_fname:
                current = 'File Storage'
            if storage == current:
                attach.storage_type = current
            elif not current:
                attach.storage_type = storage
            else:
                attach.storage_type = "%s >> %s" % (current, storage)
    
    @api.depends('store_fname', 'db_datas', 'store_lobject', 'store_document')
    def _compute_datas(self):
        for attach in self:
            if attach.store_document:
                attach.datas = attach.sudo().store_document.content
            else:
                super(DocumentIrAttachment, attach)._compute_datas()

    #----------------------------------------------------------
    # Create, Write, Delete
    #----------------------------------------------------------

    @api.constrains('store_document')
    def _check_store_document(self):
        for attach in self:
            if attach.store_document.id:
                attachments = attach.sudo().search([
                    '&', ('store_document', '=', attach.store_document.id),
                    '&', ('is_document', '=', False),
                    '|', ('res_field', '=', False),
                    ('res_field', '!=', False)])
                if len(attachments) >= 2:
                    raise ValidationError(_('The file is already referenced by another attachment.'))
    
    @api.multi
    def _inverse_datas(self):
        location = self._storage()
        for attach in self:
            if attach.is_document:
                raise ValidationError(_('The data of an attachment created by a file cannot be changed.'))
            if location == 'documents':
                value = attach.datas
                bin_data = base64.b64decode(value) if value else b''
                vals = {
                    'file_size': len(bin_data),
                    'checksum': self._compute_checksum(bin_data),
                    'index_content': self._index(bin_data, attach.datas_fname, attach.mimetype),
                    'store_fname': False,
                    'db_datas': False,
                    'store_lobject': False,
                }
                if value:
                    if attach.store_document:
                        store_document = attach.store_document
                        directory = attach._attachment_directory()
                        store_document.sudo().write({'content': value, 'directory': directory,})
                    else: 
                        directory = attach._attachment_directory()
                        store_document = self.env['muk_dms.file'].sudo().create({
                            'name': "[A-%s] %s" % (attach.id, attach.datas_fname or attach.name),
                            'directory': directory,
                            'content': value})
                    vals['store_document'] = store_document and store_document.id
                    vals['mimetype'] = store_document and store_document.mimetype
                fname = attach.store_fname
                super(DocumentIrAttachment, attach.sudo()).write(vals)
                if fname:
                    self._file_delete(fname)
            else:
                document = attach.store_document
                super(DocumentIrAttachment, attach)._inverse_datas()
                if document:
                    document.unlink()
    
    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or [])
        if not 'store_document' in default and self.store_document:
            default.update({'store_document': False})
            directory_id = self.store_document.directory.id
            content = self.store_document.content
            copy = super(DocumentIrAttachment, self).copy(default)
            store_document = self.env['muk_dms.file'].sudo().create({
                'name': "[A-%s] %s" % (copy.id, copy.datas_fname or copy.name),
                'directory': directory_id,
                'content': content})
            copy.write({'store_document': store_document.id})
            return copy
        else:
            return super(DocumentIrAttachment, self).copy(default)

    @api.multi
    def write(self, vals):
        result = super(DocumentIrAttachment, self).write(vals)
        if 'datas_fname' in vals and self.exists():
            for attach in self:
                if attach.store_document and not attach.is_document:
                    attach.store_document.write({'name': "[A-%s] %s" % (attach.id, vals['datas_fname'])})
        return result

    @api.multi
    def unlink(self):
        files = set(attach.store_document for attach in self if attach.store_document and not attach.is_document)
        result = super(DocumentIrAttachment, self).unlink()
        for file in files:
            file.sudo().unlink()
        return result