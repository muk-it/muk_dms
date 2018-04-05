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

import os
import re
import json
import urllib
import base64
import logging
import mimetypes

from odoo import _
from odoo import models, api, fields
from odoo.tools import ustr
from odoo.exceptions import ValidationError, AccessError

from odoo.addons.muk_dms.models import dms_base

_logger = logging.getLogger(__name__)

class AttachmentFile(dms_base.DMSModel):
    
    _inherit = 'muk_dms.file'
              
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    attachment = fields.Many2one(
        comodel_name='ir.attachment', 
        compute='_compute_attachment',
        string="Attachment",
        help="Reference to the attachment, if the file was created from one.")
    
    is_attachment = fields.Boolean(
        compute='_compute_attachment',
        string="Attachment")
    
    attachments = fields.One2many(
        comodel_name='ir.attachment',
        inverse_name="store_document",
        string="Attachments",
        domain=[
            '&', ('is_document', '=', True),
            '|', ('res_field', '=', False),
            ('res_field', '!=', False)],
        readonly=True)
    
    #----------------------------------------------------------
    # Function
    #----------------------------------------------------------
    
    def check_access(self, operation, raise_exception=False):
        try:
            access = super(AttachmentFile, self).check_access(operation, raise_exception)
            if self.attachment.exists() and operation in ('read', 'create', 'write', 'unlink'):
                return access and (self.attachment.check(operation) == None)
            return access
        except AccessError:
            if raise_exception:
                raise AccessError(_("This operation is forbidden!"))
            return False
    
    @api.returns('ir.attachment')
    def attach_file(self, model=None, field=None, id=None, copy=False, public=False):
        attachments = self.env['ir.attachment'].sudo()
        for record in self:
            if copy:
                attachments |= attachments.create({
                'type': 'binary',
                'name': record.name,
                'datas_fname': record.name,
                'datas': record.content,
                'is_document': False,
                'res_model': model,
                'res_field': field,
                'res_id': id,
                'public': public})
            else:
                attachments |= attachments.create({
                'type': 'binary',
                'name': "[F-%s] %s" % (record.id, record.name),
                'datas_fname': record.name,
                'store_document': record.id,
                'is_document': True,
                'res_model': model,
                'res_field': field,
                'res_id': id,
                'public': public})
        return attachments
        
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.multi
    def _compute_attachment(self):
        attachment = self.env['ir.attachment'].sudo()
        for record in self:
            attachment = attachment.search([
                '&', ['store_document', '=', record.id],
                '&', ('is_document', '=', False),
                '|', ('res_field', '=', False),
                ('res_field', '!=', False)], limit=1)
            record.update({
                'attachment': attachment,
                'is_attachment': attachment.exists(),
            })
    
    #----------------------------------------------------------
    # Delete
    #----------------------------------------------------------
            
    def _before_unlink_record(self, operation):
        info = super(AttachmentFile, self)._before_unlink(operation)
        attachments = self.mapped('attachment') | self.mapped('attachments')
        info['attachments'] = attachments
        return info
    
    def _after_unlink(self, result, info, infos, operation):
        super(AttachmentFile, self)._after_unlink(result, info, infos, operation)
        if 'attachments' in info:
            for attachment in info['attachments']:
                attachment.unlink()