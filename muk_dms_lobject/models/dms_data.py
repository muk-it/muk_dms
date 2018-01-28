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

import os
import errno
import shutil
import base64
import hashlib
import logging

from odoo import _
from odoo import models, api, fields
from odoo.tools import config, human_size, ustr, html_escape
from odoo.exceptions import ValidationError, AccessError, MissingError

from odoo.addons.muk_fields_lobject import fields as lobject_fields

_logger = logging.getLogger(__name__)

class LargeObjectDataModel(models.Model):
    _name = 'muk_dms.data_lobject'
    _description = 'Large Object Data Model'
    
    _inherit = 'muk_dms.data'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    store_lobject = lobject_fields.LargeObject(
        string="Data")
    
    data = fields.Binary(
        string="Content",
        compute="_compute_data",
        inverse="_inverse_data")
    
    #----------------------------------------------------------
    # Read/Write
    #----------------------------------------------------------
    
    @api.depends('store_lobject')
    def _compute_data(self):
        bin_size = self._context.get('bin_size')
        for record in self:
            if bin_size:
                record.data = record.store_lobject
            else:
                record.data = base64.b64encode(record.store_lobject)
        
    def _inverse_data(self):
        for record in self:
            value = record.data
            bin_data = base64.b64decode(value) if value else b''
            record.store_lobject = bin_data
        
    #----------------------------------------------------------
    # Abstract Implementation
    #----------------------------------------------------------
    
    def type(self):
        return "lobject"
    
    def content(self):
        return self.data
    
    def update(self, values):
        if 'content' in values:
            self.data = values['content']
    
    def delete(self):
        self.data = None
        