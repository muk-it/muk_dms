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

from odoo import models, fields, api

from odoo.addons.muk_dms.models import muk_dms_base as base
from pandas.core.config_init import default

class DMSGroups(base.DMSModel):
    _name = 'muk_dms_access.groups'
    _description = "Access Groups"
    
    _parent_store = True
    _parent_name = "parent_id"
    _parent_order = 'parent_left'
    _order = 'parent_left'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(string="Group Name", required=True)
    
    parent_id = fields.Many2one('muk_dms_access.groups', string='Parent Group', index=True)
    child_id = fields.One2many('muk_dms_access.groups', 'parent_id', string='Child Groups')
    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)
    
    perm_read = fields.Boolean(string='Permission Read')
    perm_create = fields.Boolean(string='Permission Create')
    perm_write = fields.Boolean(string='Permission Write')
    perm_unlink = fields.Boolean(string='Permission Unlink')
    
    departments = fields.Many2many('hr.department','muk_dms_groups_department_rel','gid','did', string='Departments')
    jobs = fields.Many2many('hr.job','muk_dms_groups_job_rel','gid','jid', string='Jobs')
    additional_users = fields.Many2many('res.users', 'muk_dms_groups_add_users_rel', 'gid', 'uid', string='Additional Users')
    
    users = fields.Many2many('res.users', 'muk_dms_groups_users_rel', 'gid', 'uid', string='Users', compute='_compute_users', store=True)
    
    files = fields.Many2many('muk_dms.file', 'muk_dms_groups_file_rel', 'gid', 'aid', readonly=True)
    directories = fields.Many2many('muk_dms.directory', 'muk_dms_groups_directory_rel', 'gid', 'aid', readonly=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the group must be unique!')
    ]
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    def get_child_list(self):
        self.ensure_one()
        childs = self.child_id
        for child in self.child_id:
            childs |= child.get_child_list()
        return childs
    
    @api.multi
    @api.returns('res.users')
    def _get_users(self):
        self.ensure_one()
        users = self.env['res.users']
        if self.parent_id:
            users |= self.parent_id._get_users()
        employees = self.env['hr.employee']
        employees += self.departments.manager_id
        employees |= self.departments.member_ids
        employees |= self.jobs.employee_ids
        for employee in employees:
            users += employee.user_id
        users |= self.additional_users
        return users

    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------
    
    @api.one
    @api.depends('parent_id', 'departments', 'jobs', 'additional_users')
    def _compute_users(self):
        self.users = self._get_users()
    
    #----------------------------------------------------------
    # Create, Write 
    #----------------------------------------------------------
    
    def _after_create(self, result, vals):
        result = super(DMSGroups, self)._after_create(result, vals)
        self.env.add_todo(self._fields['users'], result | result.get_child_list())
        self.recompute()
        return result
        
    def _follow_operation(self, values):
        super(DMSGroups, self)._follow_operation(values)
        if not set(values.keys()).isdisjoint(['parent_id', 'departments', 'jobs', 'additional_users']):
            self.env.add_todo(self._fields['users'], self | self.get_child_list())
            self.recompute()
        