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
        'ir.attachment', 
        string="Attachment",
        compute='_compute_attachment',
        help="Reference to the attachment, if the file was created from one.")
    
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
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    def _compute_attachment(self):
        attachment = self.env['ir.attachment'].sudo()
        for record in self:
            attachment = attachment.search([
                '&', ['store_document', '=', record.id],
                '|', ['res_field', '=', False], ['res_field', '!=', False]])
            if len(attachment) > 1:
                _logger.warn(_("Multiple Attachments link to the same file!"))
            record.attachment = attachment.search([], limit=1)
    
    #----------------------------------------------------------
    # Delete
    #----------------------------------------------------------
            
    def _before_unlink_record(self):
        super(AttachmentFile, self)._before_unlink_record()
        if self.attachment:
            self.attachment.unlink()