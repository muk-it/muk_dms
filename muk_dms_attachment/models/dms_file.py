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

_logger = logging.getLogger(__name__)

class AttachmentFile(models.Model):
    
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
        string="Is Attachment")
    
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
    
    @api.multi
    def check_access(self, operation, raise_exception=False):
        try:
            attachments = self.mapped('attachment')
            res = super(AttachmentFile, self).check_access(operation, raise_exception)
            access_attchment_right = attachments.check_access_rights(operation, raise_exception)
            access_attchment_rule = attachments.check_access_rule(operation) == None
            access = res and access_attchment_right and access_attchment_rule
            if not access and raise_exception:
                raise AccessError(_("This operation is forbidden!"))
            return access
        except AccessError:
            if raise_exception:
                raise AccessError(_("This operation is forbidden!"))
            return False
    
    @api.returns('ir.attachment')
    def attach_file(self, model=False, field=False, id=0, copy=False, public=False):
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
            if copy:
                values.update({
                    'name': record.name,
                    'datas': record.content,
                    'is_document': False
                })
                attachments |= attachments.create(values)
            else:
                values.update({
                    'name': "[F-%s] %s" % (record.id, record.name),
                    'store_document': record.id,
                    'is_document': True
                })
                attachments |= attachments.create(values)
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
    
    @api.multi
    def _before_unlink(self, *largs, **kwargs):
        info = super(AttachmentFile, self)._before_unlink(*largs, **kwargs)
        info['attachments'] = attachments = self.mapped('attachment') | self.mapped('attachments')
        return info
    
    @api.multi
    def _after_unlink(self, result, info, infos, *largs, **kwargs):
        super(AttachmentFile, self)._after_unlink(result, info, infos, *largs, **kwargs)
        if 'attachments' in info:
            info['attachments'].unlink()
        