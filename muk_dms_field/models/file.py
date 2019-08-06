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

import logging

from odoo import models, api, fields, tools

_logger = logging.getLogger(__name__)

class FieldFile(models.Model):
    
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
    # Settings
    #----------------------------------------------------------
    
    @api.model_cr_context
    def _auto_init(self):
        res = super(FieldFile, self)._auto_init()
        tools.create_index(self._cr, 'muk_dms_file_reference_idx',
                           self._table, ['reference_model', 'reference_id'])
        return res
    
    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------
        
    @api.depends('reference_model', 'reference_id')
    def _compute_reference_name(self):
        for record in self:
            if record.reference_model and record.reference_id:
                reference = self.env[record.reference_model].browse(record.reference_id)
                record.reference_name = reference.display_name
  