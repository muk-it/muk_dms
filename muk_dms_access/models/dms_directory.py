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

from odoo import models, api

_logger = logging.getLogger(__name__)

class AccessDirectory(models.Model):
    
    _inherit = 'muk_dms.directory'
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    def trigger_computation(self, fields, *largs, **kwargs):        
        super(AccessDirectory, self).trigger_computation(fields, *largs, **kwargs)
        for record in self:
            if "complete_groups" in fields:
                record.trigger_computation_down(fields)
                
    @api.model
    def check_group_values(self, values):
        check = any(field in values for field in ['parent_directory', 'inherit_groups'])
        if super(AccessDirectory, self).check_group_values(values) or check:
            return True
        return False
    
    @api.multi
    @api.returns('muk_security.groups')
    def get_groups(self):
        groups = super(AccessDirectory, self).get_groups()
        if self.parent_directory and self.inherit_groups:
            groups |= self.parent_directory.complete_groups
        return groups
        