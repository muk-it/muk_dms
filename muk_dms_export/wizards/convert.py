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
import base64
import uuid
import logging
import mimetypes

from odoo import _, api, fields, models

from odoo.addons.muk_utils.tools.http import get_response
from odoo.addons.muk_converter.tools import converter

_logger = logging.getLogger(__name__)

class ConverterWizard(models.TransientModel):
    
    _name = "muk_dms_export.convert"
    _inherit = "muk_converter.convert"
    
    file = fields.Many2one(
        comodel_name='muk_dms.file', 
        string="File",
        required=True)
    
    input_name = fields.Char(
        related="file.name",
        string="Filename",
        store=True)
    
    input_binary = fields.Binary(
        related="file.content",
        string="File",
        store=True)
    
    directory = fields.Many2one(
        comodel_name='muk_dms.directory', 
        string="Directory",
        domain="[('permission_create', '=', True)]")
                
    @api.multi
    def convert_and_save(self):
        self.convert()
        for record in self:
            self.env['muk_dms.file'].create({
                'directory': record.directory.id,
                'name': record.output_name,
                'content': record.output_binary})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }