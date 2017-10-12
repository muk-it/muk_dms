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

from odoo import models, fields, api

from odoo.addons.muk_dms.models import dms_base

class DocumentGroups(dms_base.DMSModel):
    _name = 'muk_dms_access.groups'
    _description = "Access Groups"
    
    _parent_store = True
    _parent_name = "parent_group"
    _parent_order = 'parent_left'
    _order = 'parent_left'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(
        string="Group Name", 
        required=True)
    
    parent_group = fields.Many2one(
        'muk_dms_access.groups', 
        string='Parent Group', 
        ondelete='cascade', 
        auto_join=True,
        index=True)
    
    child_groups = fields.One2many(
        'muk_dms_access.groups', 
        'parent_group', 
        string='Child Groups')
    
    parent_left = fields.Integer(
        string='Left Parent', 
        index=True)
    
    parent_right = fields.Integer(
        string='Right Parent', 
        index=True)
    
    perm_read = fields.Boolean(
        string='Read')
    
    perm_create = fields.Boolean(
        string='Create')
    
    perm_write = fields.Boolean(
        string='Write')
    
    perm_unlink = fields.Boolean(
        string='Unlink')
    
    perm_access = fields.Boolean(
        string='Access')
    
    departments = fields.Many2many(
        'hr.department',
        'muk_dms_groups_department_rel',
        'gid',
        'did',
        string='Departments')
    
    jobs = fields.Many2many(
        'hr.job',
        'muk_dms_groups_job_rel',
        'gid',
        'jid',
        string='Jobs')
    
    additional_users = fields.Many2many(
        'res.users',
        'muk_dms_groups_add_users_rel',
        'gid',
        'uid', 
        string='Additional Users')
    
    users = fields.Many2many(
        'res.users',
        'muk_dms_groups_users_rel',
        'gid',
        'uid', 
        string='Users', 
        compute='_compute_users', 
        store=True)
    
    files = fields.Many2many(
        'muk_dms.file',
        'muk_groups_complete_file_rel',
        'gid',
        'aid',
        readonly=True)
    
    directories = fields.Many2many(
        'muk_dms.directory',        
        'muk_groups_complete_directory_rel',
        'gid',
        'aid',
        readonly=True)
    
    count_users = fields.Integer(
        compute='_compute_count_users',
        string="Users")
    
    count_directories = fields.Integer(
        compute='_compute_count_directories',
        string="Directories")
    
    count_files = fields.Integer(
        compute='_compute_count_files',
        string="Files")
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the group must be unique!')
    ]
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def trigger_computation_up(self, fields, operation=None):
        parent_group = self.parent_group
        if parent_group:
            parent_group.trigger_computation(fields, False)
            
    def trigger_computation_down(self, fields, operation=None):
        for child in self.child_groups:
            child.with_context(is_subnode=True).trigger_computation(fields, False, operation)
            
    def trigger_computation(self, fields, refresh=True, operation=None):
        super(DocumentGroups, self).trigger_computation(fields, refresh, operation)
        values = {}
        if "users" in fields:
            values.update(self.with_context(operation=operation)._compute_users(write=False))
        if values:
            self.write(values);   
            if "users" in fields:
                self.trigger_computation_down(fields, operation)

    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------
        
    def _compute_users(self, write=True):
        def get_users(record):
            users = record.env['res.users']
            if record.parent_group:
                users |= record.parent_group._get_users()
            employees = record.env['hr.employee']
            employees += record.departments.manager_id
            employees |= record.departments.member_ids
            employees |= record.jobs.employee_ids
            for employee in employees:
                users += employee.user_id
            users |= record.additional_users
            return users
        if write:
            for record in self:
                record.users = get_users(record)
        else:
            self.ensure_one()
            return {'users': [(6, 0, get_users(self).mapped('id'))]}
    
    @api.depends('users')
    def _compute_count_users(self):
        for record in self:
            record.count_users = len(record.users)
    
    @api.depends('directories')
    def _compute_count_directories(self):
        for record in self:
            record.count_directories = len(record.directories)
     
    @api.depends('files')
    def _compute_count_files(self):
        for record in self:
            record.count_files = len(record.files)
    
    #----------------------------------------------------------
    # Create, Write, Delete
    #----------------------------------------------------------
    
    def _after_create(self, vals):
        record = super(DocumentGroups, self)._after_create(vals)
        record._check_recomputation(vals)
        return record
        
    def _after_write_record(self, vals, operation):
        vals = super(DocumentGroups, self)._after_write_record(vals, operation)
        self._check_recomputation(vals, operation)
        return vals
    
    def _check_recomputation(self, values, operation=None):
        fields = []
        if any(field in values for field in ['parent_group', 'departments', 'jobs', 'additional_users']):
            fields.extend(['users'])
        if fields:
            self.trigger_computation(fields, operation=operation)