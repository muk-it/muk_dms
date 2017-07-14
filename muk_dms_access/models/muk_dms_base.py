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

import os
import string
import unicodedata
import hashlib
import logging

from openerp import _
from openerp import SUPERUSER_ID
from openerp import models, api, fields
from openerp.exceptions import ValidationError, AccessError, UserError

from openerp.addons.muk_dms.models import muk_dms_base as base

_logger = logging.getLogger(__name__)
    
class DMSAdvancedAccessModel(base.DMSModel):
    """ Every model which inherits muk_dms.access must have a many2many 
        field called groups and complete_groups.
        
        groups = fields.Many2many('muk_dms_access.groups', 'muk_dms_groups_[rec._name]_rel', 'aid', 'gid')
        complete_groups = fields.Many2many('muk_dms_access.groups', 'muk_dms_groups_[rec._name]_rel', 'aid', 'gid')
    """
    
    _inherit = 'muk_dms.access'
    
    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        return super(DMSAdvancedAccessModel, self).check_access_rights(operation, raise_exception)
    
    @api.multi
    def check_access_rule(self, operation):
        super(DMSAdvancedAccessModel, self).check_access_rule(operation)
        if self.env.user.id == SUPERUSER_ID or self.user_has_groups('muk_dms.group_muk_dms_manager'):
            return
        for record in self:
            sql = '''
                SELECT perm_%s
                FROM muk_dms_complete_groups_directory_rel r
                JOIN muk_dms_access_groups g ON g.id = r.gid
                JOIN muk_dms_groups_users_rel u ON u.gid = g.id
                WHERE r.aid = %s AND u.uid = %s
            ''' % (operation, record.id, self.env.user.id)
            self.env.cr.execute(sql)
            fetch = self.env.cr.fetchall()
            if not any(list(map(lambda x: x[0], fetch))):
                raise AccessError(_("This operation is forbidden!"))
    
    @api.model
    def _apply_ir_rules(self, query, mode='read'):
        super(DMSAdvancedAccessModel, self)._apply_ir_rules(query, mode)
        
    def _after_read(self, result):
        if self.env.user.id == SUPERUSER_ID or self.user_has_groups('muk_dms.group_muk_dms_manager'):
            return result
        base, model = self._name.split(".")
        sql = '''
            SELECT r.aid
            FROM muk_dms_complete_groups_%s_rel r 
            JOIN muk_dms_access_groups g ON r.gid = g.id
            JOIN muk_dms_groups_users_rel u ON r.gid = u.uid
            WHERE u.uid = %s AND g.perm_read = true
        ''' % (model, self.env.user.id)
        self.env.cr.execute(sql)
        fetch = self.env.cr.fetchall()
        if len(fetch) > 0:
            access_result = []
            access_ids = list(map(lambda x: x[0], fetch))
            for record in result:
                if record['id'] in access_ids:
                    access_result.append(record)
            return access_result
        return []
    
    def _after_search(self, result):
        if self.env.user.id == SUPERUSER_ID or self.user_has_groups('muk_dms.group_muk_dms_manager'):
            return result
        base, model = self._name.split(".")
        sql = '''
            SELECT r.aid
            FROM muk_dms_complete_groups_%s_rel r 
            JOIN muk_dms_access_groups g ON r.gid = g.id
            JOIN muk_dms_groups_users_rel u ON r.gid = u.uid
            WHERE u.uid = %s AND g.perm_read = true
        ''' % (model, self.env.user.id)
        self.env.cr.execute(sql)
        fetch = self.env.cr.fetchall()
        print fetch
        if len(fetch) > 0:
            access_result = self.env[self._name]
            access_ids = list(map(lambda x: x[0], fetch)) 
            for record in result:
                if record.id in access_ids:
                    access_result += record
            return access_result
        return self.env[self._name]
    
    def _after_name_search(self, result):
        if self.env.user.id == SUPERUSER_ID or self.user_has_groups('muk_dms.group_muk_dms_manager'):
            return result
        base, model = self._name.split(".")
        sql = '''
            SELECT r.aid
            FROM muk_dms_complete_groups_%s_rel r 
            JOIN muk_dms_access_groups g ON r.gid = g.id
            JOIN muk_dms_groups_users_rel u ON r.gid = u.uid
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
        return super(DMSAdvancedAccessModel, self).check_field_access_rights(operation, fields)
        
 