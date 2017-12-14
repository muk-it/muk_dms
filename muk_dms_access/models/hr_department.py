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

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class DocumentDepartment(models.Model):

    _inherit = 'hr.department'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    groups = fields.Many2many(
        'muk_dms_access.groups',
        'muk_dms_groups_department_rel',
        'did',
        'gid',
        string='Groups')
    
    #----------------------------------------------------------
    # Create, Update, Delete
    #----------------------------------------------------------
    
    @api.multi
    def write(self, vals):
        result = super(DocumentDepartment, self).write(vals)
        if any(field in vals for field in ['parent_id', 'jobs_ids', 'manager_id', 'member_ids']):
            for record in self:
                for group in record.groups:
                    group.trigger_computation(['users'])
        return result
    
    @api.multi
    def unlink(self):
        groups = record.env['muk_dms_access.groups']
        for record in self:
            groups |= record.groups
        result = super(DocumentDepartment, self).unlink()
        for group in groups:
            group.trigger_computation(['users'])
        return result