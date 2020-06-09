###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Access 
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

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    documents_access_groups_user_view = fields.Boolean(
        string="Show Access Groups on User Form",
        help="Allows users to edit the access groups of a directory.")
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env.ref('muk_dms_access.view_dms_directory_form').write({
            'active': self.documents_access_groups_user_view,
        })
        self.env.ref('muk_dms_access.view_dms_directory_manager_form').write({
            'active': not self.documents_access_groups_user_view,
        })
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        view = self.env.ref('muk_dms_access.view_dms_directory_form')
        res.update(documents_access_groups_user_view=bool(view.active))
        return res
