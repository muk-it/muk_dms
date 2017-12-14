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

import os
import string
import unicodedata
import hashlib
import logging

from odoo import _
from odoo import SUPERUSER_ID
from odoo import models, api, fields
from odoo.exceptions import ValidationError, AccessError, UserError

from odoo.addons.muk_dms.models import dms_base

_logger = logging.getLogger(__name__)
    
class DMSAdvancedAccessModel(dms_base.DMSAbstractModel):
    
    _inherit = 'muk_dms.access'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    perm_access = fields.Boolean(
        compute='_compute_perm_access', 
        string="Access")
    
    inherit_groups = fields.Boolean(
        string="Inherit Groups",
        default=True)
    
    #----------------------------------------------------------
    # Function
    #----------------------------------------------------------
        
    @api.model
    def _add_magic_fields(self):
        super(DMSAdvancedAccessModel, self)._add_magic_fields()
        def add(name, field):
            if name not in self._fields:
                self._add_field(name, field)
        base, model = self._name.split(".")
        add('groups', fields.Many2many(
            _module=base,
            comodel_name='muk_dms_access.groups',
            relation='muk_groups_%s_rel' % model,
            column1='aid',
            column2='gid',
            string="Groups",
            automatic=True))
        add('complete_groups', fields.Many2many(
            _module=base,
            comodel_name='muk_dms_access.groups',
            relation='muk_groups_complete_%s_rel' % model,
            column1='aid',
            column2='gid',
            string="Complete Groups", 
            compute='_compute_groups', 
            store=True,
            automatic=True))

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        if operation == 'access':
            return True
        return super(DMSAdvancedAccessModel, self).check_access_rights(operation, raise_exception)
    
    @api.multi
    def check_access_rule(self, operation):
        if operation != 'access':
            super(DMSAdvancedAccessModel, self).check_access_rule(operation)
        if self.env.user.id == SUPERUSER_ID or self.user_has_groups('muk_dms.group_dms_admin'):
            return
        base, model = self._name.split(".")
        for record in self:
            sql = '''
                SELECT perm_%s                
                FROM muk_groups_complete_%s_rel r
                JOIN muk_dms_access_groups g ON g.id = r.gid
                JOIN muk_dms_groups_users_rel u ON u.gid = g.id
                WHERE r.aid = %s AND u.uid = %s
            ''' % (operation, model, record.id, self.env.user.id)
            self.env.cr.execute(sql)
            fetch = self.env.cr.fetchall()
            if not any(list(map(lambda x: x[0], fetch))):
                raise AccessError(_("This operation is forbidden!"))
    
    @api.model
    def _apply_ir_rules(self, query, mode='read'):
        super(DMSAdvancedAccessModel, self)._apply_ir_rules(query, mode)
        
    def _after_read(self, result):
        result = super(DMSAdvancedAccessModel, self)._after_read(result)
        if self.env.user.id == SUPERUSER_ID or self.user_has_groups('muk_dms.group_dms_admin'):
            return result
        base, model = self._name.split(".")
        sql = '''
            SELECT r.aid
            FROM muk_groups_complete_%s_rel r
            JOIN muk_dms_access_groups g ON r.gid = g.id
            JOIN muk_dms_groups_users_rel u ON r.gid = u.gid
            WHERE u.uid = %s AND g.perm_read = true
        ''' % (model, self.env.user.id)
        self.env.cr.execute(sql)
        fetch = self.env.cr.fetchall()
        result = [result] if not isinstance(result, list) else result
        if len(fetch) > 0:
            access_result = []
            access_ids = list(map(lambda x: x[0], fetch))
            for record in result:
                if record['id'] in access_ids:
                    access_result.append(record)
            return access_result
        return []
    
    def _after_search(self, result):
        result = super(DMSAdvancedAccessModel, self)._after_search(result)
        if self.env.user.id == SUPERUSER_ID or self.user_has_groups('muk_dms.group_dms_admin'):
            return result
        base, model = self._name.split(".")
        sql = '''
            SELECT r.aid
            FROM muk_groups_complete_%s_rel r
            JOIN muk_dms_access_groups g ON r.gid = g.id
            JOIN muk_dms_groups_users_rel u ON r.gid = u.gid
            WHERE u.uid = %s AND g.perm_read = true
        ''' % (model, self.env.user.id)
        self.env.cr.execute(sql)
        fetch = self.env.cr.fetchall()
        if len(fetch) > 0:
            access_result = self.env[self._name]
            access_ids = list(map(lambda x: x[0], fetch)) 
            if isinstance(result, (int, long)):
                if result in access_ids:
                    return result
            else:
                for record in result:
                    if record.id in access_ids:
                        access_result += record
                return access_result
        return self.env[self._name]
    
    def _after_name_search(self, result):
        result = super(DMSAdvancedAccessModel, self)._after_name_search(result)
        if self.env.user.id == SUPERUSER_ID or self.user_has_groups('muk_dms.group_dms_admin'):
            return result
        base, model = self._name.split(".")
        sql = '''
            SELECT r.aid
            FROM muk_groups_complete_%s_rel r
            JOIN muk_dms_access_groups g ON r.gid = g.id
            JOIN muk_dms_groups_users_rel u ON r.gid = u.gid
            WHERE u.uid = %s AND g.perm_read = true
        ''' % (model, self.env.user.id)
        self.env.cr.execute(sql)
        fetch = self.env.cr.fetchall()
        if len(fetch) > 0:
            access_result = []
            access_ids = list(map(lambda x: x[0], fetch)) 
            for tuple in result:
                if tuple[0] in access_ids:
                    access_result.append(tuple)
            return access_result
        return []
    
    @api.model
    def check_field_access_rights(self, operation, fields):
        fields = super(DMSAdvancedAccessModel, self).check_field_access_rights(operation, fields)
        if self.env.user.id == SUPERUSER_ID or self.user_has_groups('muk_dms.group_dms_admin'):
            return fields
        if operation == 'write' and 'groups' in fields:
            base, model = self._name.split(".")
            sql = '''
                SELECT r.aid
                FROM muk_groups_complete_%s_rel r
                JOIN muk_dms_access_groups g ON r.gid = g.id
                JOIN muk_dms_groups_users_rel u ON r.gid = u.gid
                WHERE u.uid = %s AND g.perm_access = true
            ''' % (model, self.env.user.id)
            self.env.cr.execute(sql)
            fetch = self.env.cr.fetchall()
            if len(fetch) == 0:
                raise AccessError(_("This operation is forbidden!"))
        return fields
        
    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------
        
    @api.one
    def _compute_perm_access(self):
        try:
            self.perm_access = self.check_access('access')
        except AccessError:
             self.perm_access = False
    
    def _compute_groups(self, write=True):
        if write:
            for record in self:
                record.complete_groups = record.groups
        else:
            self.ensure_one()
            return {'complete_groups': [(6, 0, self.groups.mapped('id'))]}      
    
    #----------------------------------------------------------
    # Create, Write, Delete
    #----------------------------------------------------------
    
    @api.onchange('inherit_groups') 
    def _onchange_inherit_groups(self):
        if not self.inherit_groups:
            self.groups = self.complete_groups