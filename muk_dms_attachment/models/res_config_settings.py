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

from ast import literal_eval

from odoo import api, fields, models
from odoo.exceptions import AccessDenied

class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    documents_attachment_location = fields.Selection(
        selection=lambda self: self._attachment_location_selection(),
        string='Attachment Storage Location',
        required=True,
        default='file',
        help="System Attachment storage location.")
    
    documents_attachment_location_changed = fields.Boolean(
        compute='_compute_documents_attachment_location_changed',
        string='Attachment Storage Location Changed')
    
    documents_attachment_directory = fields.Many2one(
        comodel_name='muk_dms.directory', 
        string="Default Directory", 
        context="{'dms_directory_show_path': True}",
        config_parameter='muk_dms_attachment.attachment_directory',
        help="""After an attachment has been created, it is automatically saved
            in the default directory should no other rule exist.""")
        
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('ir_attachment.location', self.documents_attachment_location)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            documents_attachment_location=params.get_param('ir_attachment.location', 'file'),
        )
        return res
        
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('documents_attachment_location')
    def _compute_documents_attachment_location_changed(self):
        params = self.env['ir.config_parameter'].sudo()
        location = params.get_param('ir_attachment.location', 'file')
        for record in self:
            check = location != self.documents_attachment_location
            record.documents_attachment_location_changed = check
