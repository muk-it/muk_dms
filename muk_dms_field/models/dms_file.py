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

import logging

from odoo import _
from odoo import models, api, fields

from odoo.addons.muk_dms.models import dms_base

_logger = logging.getLogger(__name__)

class FieldFile(dms_base.DMSModel):
    _inherit = 'muk_dms.file'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    reference_name = fields.Char(
        string="Reference Name",
        compute='_compute_reference_name',
        readonly=True,
        store=True)
    
    reference_model = fields.Char(
        string="Reference Model",
        readonly=True,
        help="The database object this record will be attached to.")
    
    reference_field = fields.Char(
        string="Reference Field",
        readonly=True)
    
    reference_id = fields.Integer(
        string="Reference ID",
        readonly=True,
        help="The record id this is attached to.")
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
        
    def trigger_computation(self, fields, refresh=True, operation=None):
        super(FieldFile, self).trigger_computation(fields)
        if "reference_name" in fields:
            self._compute_reference_name()
    
    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------
        
    @api.depends('reference_model', 'reference_id')
    def _compute_reference_name(self):
        for record in self:
            if record.reference_model and record.reference_id:
                reference = self.env[record.reference_model].browse(record.reference_id)
                record.reference_name = reference.display_name
                
    #----------------------------------------------------------
    # Create, Update
    #----------------------------------------------------------
    
    def _check_recomputation(self, values, operation=None):
        super(FieldFile, self)._check_recomputation(values, operation)
        if 'reference_model' in values or 'reference_id' in values:
            self.trigger_computation(['reference_name'])
