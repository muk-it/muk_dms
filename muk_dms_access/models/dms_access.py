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

from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class DMSAccessModel(models.AbstractModel):
    
    _inherit = 'muk_dms.access'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    inherit_groups = fields.Boolean(
        string="Inherit Groups",
        default=True)
    
    #----------------------------------------------------------
    # Create, Write, Delete
    #----------------------------------------------------------
    
    @api.onchange('inherit_groups') 
    def _onchange_inherit_groups(self):
        if not self.inherit_groups:
            self.groups = self.complete_groups