###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Attachment 
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

import os
import re
import json
import urllib
import base64
import logging
import mimetypes

from odoo import _, SUPERUSER_ID
from odoo import models, api, fields
from odoo.tools import ustr
from odoo.exceptions import ValidationError, AccessError

from odoo.addons.muk_security.tools.security import NoSecurityUid

_logger = logging.getLogger(__name__)

class File(models.Model):
    
    _inherit = 'muk_dms.file'
              
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    attachment = fields.Many2one(
        comodel_name='ir.attachment', 
        compute='_compute_attachment',
        compute_sudo=True,
        readonly=True,
        copy=False,
        string="Attachment",
        help="Reference to the attachment, if the file was created from one.")
    
    is_attachment = fields.Boolean(
        compute='_compute_attachment',
        compute_sudo=True,
        readonly=True,
        copy=False,
        string="Is Attachment")
    
    attachments = fields.One2many(
        comodel_name='ir.attachment',
        inverse_name="store_document",
        domain=[
            '&', ('is_store_document_link', '=', True),
            '|', ('res_field', '=', False), ('res_field', '!=', False)
        ],
        string="Attachments",
        readonly=True,
        copy=False,
        help="Attachments linked to a file.")
    
    #----------------------------------------------------------
    # Function
    #----------------------------------------------------------
    
    @api.returns('ir.attachment')
    def attach_file(self, model=None, field=None, id=0, link=True, public=False):
        attachments = self.env['ir.attachment'].sudo()
        for record in self:
            values = {
                'type': 'binary',
                'datas_fname': record.name,
                'public': public
            }
            if model:
                values.update({'res_model': model})
            if field:
                values.update({'res_field': field})
            if id:
                values.update({'res_id': id})
            if link:
                values.update({
                    'name': "[F-%s] %s" % (record.id, record.name),
                    'store_document': record.id,
                    'is_store_document_link': True
                })
                attachments |= attachments.create(values)
            else:
                values.update({
                    'name': record.name,
                    'datas': record.content,
                    'is_store_document_link': False
                })
                attachments |= attachments.create(values)
        return attachments
        
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.multi
    def _compute_attachment(self):
        attachments = self.env['ir.attachment'].sudo().search([
            '&', ['store_document', 'in', self.ids],
            '&', ('is_store_document_link', '=', False),
            '|', ('res_field', '=', False), ('res_field', '!=', False)
        ])
        data = {attach.store_document.id: attach for attach in attachments}
        for record in self:
            if record.id in data:
                record.update({
                    'attachment': data[record.id],
                    'is_attachment': True,
                })
            else:
                record.update({
                    'attachment': None,
                    'is_attachment': False,
                })
    
    @api.multi
    def read(self, fields=None, load='_classic_read'):
        self.check_attachment_access('read', True)
        return super(File, self).read(fields, load=load)
     
    #----------------------------------------------------------
    # Security
    #----------------------------------------------------------
     
    @api.model
    def _get_attachments_from_files(self, file_ids, search_uid=None):
        if file_ids:
            return self.env['ir.attachment'].sudo(search_uid or SUPERUSER_ID).search([
                '&', ['store_document', 'in', file_ids],
                '&', ('is_store_document_link', '=', False),
                '|', ('res_field', '=', False), ('res_field', '!=', False)
            ]).sudo(self.env.uid)
        return self.env['ir.attachment']
    
    def _get_attachments_with_no_access(self, operation, file_ids):
        attachments = self._get_attachments_from_files(file_ids)
        if operation == 'read':
            return attachments - self._get_attachments_from_files(file_ids, self.env.uid)
        else:
            attachments_with_no_access_ids = set()
            for attachment in attachments:
                try:
                    attachment.check(operation, values=None)
                except AccessError:
                    attachments_with_no_access_ids |= attachment.id
            return self.env['ir.attachment'].browse(list(attachments_with_no_access_ids))
        
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        result = super(File, self)._search(args, offset, limit, order, False, access_rights_uid)
        if self.env.user.id == SUPERUSER_ID or isinstance(self.env.uid, NoSecurityUid):
            return len(result) if count else result
        if not result:
            return 0 if count else []
        file_ids = set(result)
        attachments = self._get_attachments_with_no_access('read', result)
        file_ids -= set(attachments.sudo().mapped('store_document').ids)
        return len(file_ids) if count else list(file_ids)
     
    @api.multi
    def _filter_access(self, operation):
        records = super(File, self)._filter_access(operation)
        if self.env.user.id == SUPERUSER_ID or isinstance(self.env.uid, NoSecurityUid):
            return records
        attachments = self._get_attachments_with_no_access(operation, records.ids)
        return records - attachments.sudo().mapped('store_document')

    @api.multi
    def check_access(self, operation, raise_exception=False):
        res = super(File, self).check_access(operation, raise_exception)
        try:
            return res and self.check_attachment_access(
                operation, raise_exception=raise_exception
            )
        except AccessError:
            if raise_exception:
                raise
            return False
        
    @api.multi
    def check_attachment_access(self, operation, raise_exception=False):
        if self.env.user.id == SUPERUSER_ID or isinstance(self.env.uid, NoSecurityUid):
            return None
        attachments = self._get_attachments_from_files(self.ids)
        if not attachments:
            return True
        try:
            return attachments.check(operation, values=None) is None
        except AccessError:
            if raise_exception:
                raise
            return False
    
    #----------------------------------------------------------
    # Create, Update, Delete
    #----------------------------------------------------------
    
    @api.multi
    def write(self, vals):
        if 'content' in vals:
            self.check_attachment_access('write', True)
        return super(File, self).write(vals)
    
    @api.multi
    def unlink(self):
        self.check_attachment_access('unlink', True)
        attachments = self.sudo().mapped('attachment')
        attachments |= self.sudo().mapped('attachments')
        result = super(File, self).unlink()
        if attachments:
            attachments.sudo().unlink()
        return result
