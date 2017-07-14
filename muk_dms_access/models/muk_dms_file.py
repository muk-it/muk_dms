# -*- coding: utf-8 -*-

###################################################################################
# 
#    MuK Document Management System
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

from openerp import _
from openerp import SUPERUSER_ID
from openerp import models, api, fields
from openerp.exceptions import ValidationError, AccessError, UserError

from openerp.addons.muk_dms.models import muk_dms_base as base

class AccessFile(base.DMSModel):
    _inherit = 'muk_dms.file'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    groups = fields.Many2many('muk_dms_access.groups', 'muk_dms_groups_file_rel', 'aid', 'gid', string="Groups")
    complete_groups = fields.Many2many('muk_dms_access.groups', 'muk_dms_complete_groups_file_rel', 'aid', 'gid',
                                        string="Complete Groups", compute='_compute_groups', store=True)
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    @api.returns('muk_dms_access.groups')
    def _get_groups(self):
        self.ensure_one()
        groups = self.env['muk_dms_access.groups']
        groups |= self.directory._get_groups()
        groups |= self.groups
        return groups
    
    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------
    
    @api.one
    @api.depends('directory', 'groups')
    def _compute_groups(self):
        self.complete_groups = self._get_groups()
        
    #----------------------------------------------------------
    # Create, Write 
    #----------------------------------------------------------
    
    def _before_create(self, vals):
        vals = super(AccessFile, self)._before_create(vals)
        if self.env.user.id == SUPERUSER_ID or self.user_has_groups('muk_dms.group_muk_dms_manager'):
            return vals
        if 'directory' in vals:
            if not self.env['muk_dms.direcotry'].sudo().browse(vals['directory'])._compute_perm_create():
                raise AccessError(_("This operation is forbidden!"))
        return vals
    
    def _after_create(self, result, vals):
        result = super(AccessFile, self)._after_create(result, vals)
        self.env.add_todo(self._fields['complete_groups'], result)
        self.recompute()
        return result
        
    def _follow_operation(self, values):
        super(AccessFile, self)._follow_operation(values)
        if not set(values.keys()).isdisjoint(['directory', 'groups']):
            self.env.add_todo(self._fields['complete_groups'], self)
            self.recompute()
        