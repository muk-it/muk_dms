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

from odoo import _
from odoo import SUPERUSER_ID
from odoo import models, api, fields
from odoo.exceptions import ValidationError, AccessError, UserError

from odoo.addons.muk_dms.models import dms_base

class AccessFile(dms_base.DMSModel):
    
    _inherit = 'muk_dms.file'
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def trigger_computation(self, fields, refresh=True, operation=None):
        super(AccessFile, self).trigger_computation(fields, refresh, operation)
        values = {}
        if "complete_groups" in fields:
            values.update(self.with_context(operation=operation)._compute_groups(write=False))
        if values:
            self.write(values);   
    
    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------
    
    def _compute_groups(self, write=True):
        def get_groups(record):
            groups = record.env['muk_dms_access.groups']
            if record.inherit_groups:
                groups |= record.directory.complete_groups
            groups |= record.groups
            return groups
        if write:
            for record in self:
                record.users = get_groups(record)
        else:
            self.ensure_one()
            return {'complete_groups': [(6, 0, get_groups(self).mapped('id'))]}
        
    #----------------------------------------------------------
    # Create, Write 
    #----------------------------------------------------------
    
    def _check_recomputation(self, values, operation=None):
        super(AccessFile, self)._check_recomputation(values, operation)
        fields = []
        if any(field in values for field in ['groups', 'directory', 'inherit_groups']):
            fields.extend(['complete_groups'])
        if fields:
            self.trigger_computation(fields, operation=operation)
        