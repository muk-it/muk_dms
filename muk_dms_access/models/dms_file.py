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

class AccessFile(models.Model):
    
    _inherit = 'muk_dms.file'
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
        
    @api.model
    def check_group_values(self, values):
        check = any(field in values for field in ['directory', 'inherit_groups'])
        if super(AccessFile, self).check_group_values(values) or check:
            return True
        return False
    
    @api.multi
    @api.returns('muk_security.groups')
    def get_groups(self):
        groups = super(AccessFile, self).get_groups()
        if self.inherit_groups:
            groups |= self.directory.complete_groups
        return groups