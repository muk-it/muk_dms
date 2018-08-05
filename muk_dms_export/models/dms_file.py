###################################################################################
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

import logging

from odoo import models, api, fields

from odoo.addons.muk_converter.tools import converter

_logger = logging.getLogger(__name__)

class ExportFile(models.Model):
    
    _inherit = 'muk_dms.file'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    is_exportable = fields.Boolean(
        compute='_compute_is_exportable',
        string="Exportable")
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    def export_file(self):
        record = next(iter(self)) if len(self) > 1 else self
        return {
            "type": "ir.actions.act_window",
            "res_model": "muk_dms_export.convert",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "context": {
                'default_file': record.id,
                'default_directory': record.directory.id}
        }
        
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.multi
    def _compute_is_exportable(self):
        for record in self:
            record.is_exportable = record.extension and record.extension.strip(".") in converter.imports()
            
            