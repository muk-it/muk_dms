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
import shutil
import base64
import unittest

from openerp import _
from openerp.tests import common

class DMSAccessTestCase(common.TransactionCase):
    
    at_install = False
    post_install = True
    
    def setUp(self):
        super(DMSAccessTestCase, self).setUp()
        
        self.manager = self.ref('base.user_root')
        self.user = self.ref('base.user_demo')
        
        self.root_model_manager = self.env['muk_dms.root'].sudo(self.manager)
        self.dir_model_manager = self.env['muk_dms.directory'].sudo(self.manager)
        self.file_model_manager = self.env['muk_dms.file'].sudo(self.manager)
        self.group_model_manager = self.env['muk_dms_access.groups'].sudo(self.manager)
        
        self.dir_model_user = self.env['muk_dms.directory'].sudo(self.user)
        self.file_model_user = self.env['muk_dms.file'].sudo(self.user)

        self.root_dir = self.dir_model_manager.create({'name': 'Root_Directory'})
        self.dir = self.dir_model_manager.create({'name': 'Directory', 'parent_id': self.root_dir.id})
        self.root = self.root_model_manager.create({'name': 'Database Settings', 'root_directory': self.root_dir.id, 'save_type': 'database'})
        self.group = self.group_model_manager.create({'name': 'Test Group', 'additional_users': [[6, False, [self.user]]], 
                                                      'perm_read': True, 'perm_create': True, 'perm_write': True, 'perm_unlink': True})
        
    def tearDown(self):
        super(DMSAccessTestCase, self).tearDown()
    
    def test_read_access(self):
        self.assertTrue(self.dir in self.dir_model_manager.search([]))
        self.assertFalse(self.dir in self.dir_model_user.search([]))
        self.dir.write({'groups': [[6, False, [self.group.id]]]})
        self.assertTrue(self.dir in self.dir_model_user.search([]))
    
        