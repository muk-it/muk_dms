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

from odoo import api, fields, models

class DocumentSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    module_muk_dms_connector = fields.Boolean(
        string="Rest API",
        help="Enables the Document Rest API.")
    
    module_muk_dms_file = fields.Boolean(
        string="File Store",
        help="Enables a new save option to store files into a file store.")
    
    module_muk_dms_access = fields.Boolean(
        string="Access Control",
        help="Allows the creation of groups to define access rights.")
    
    max_upload_size = fields.Char(
        string="Size",
        help="Defines the maximum upload size in MB.")
    
    forbidden_extensions = fields.Char(
        string="Extensions",
        help="Defines a list of forbidden file extensions. (Example: '.exe,.msi')")
    
    @api.model
    def get_values(self):
        res = super(DocumentSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            max_upload_size=get_param('muk_dms.max_upload_size', default=25),
            forbidden_extensions=get_param('muk_dms.forbidden_extensions', default=""),
        )
        return res

    def set_values(self):
        if not self.user_has_groups('muk_dms.group_dms_admin'):
            raise AccessDenied()
        super(DocumentSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('muk_dms.max_upload_size', self.max_upload_size or 25)
        set_param('muk_dms.forbidden_extensions', self.forbidden_extensions or "")