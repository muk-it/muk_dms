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
import base64
import logging
import unittest

from odoo import _
from odoo.tests import common

from odoo.addons.muk_dms.tests import dms_case

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class AccessTestCase(dms_case.DMSTestCase):
    
    def setUp(self):
        super(AccessTestCase, self).setUp()
        self.directory01 = self.browse_ref("muk_dms_access.directory_access_01_demo")
        self.directory02 = self.browse_ref("muk_dms_access.directory_access_02_demo")
        self.directory03 = self.browse_ref("muk_dms_access.directory_access_03_demo")
        self.directory04 = self.browse_ref("muk_dms_access.directory_access_04_demo")
        self.directory05 = self.browse_ref("muk_dms_access.directory_access_05_demo")
        
    def tearDown(self):
        super(AccessTestCase, self).tearDown()
    
    def test_access_groups(self):
        group01 = self.browse_ref("muk_dms_access.access_group_01_demo").sudo()
        group02 = self.browse_ref("muk_dms_access.access_group_02_demo").sudo()
        group03 = self.browse_ref("muk_dms_access.access_group_03_demo").sudo()
        group04 = self.browse_ref("muk_dms_access.access_group_04_demo").sudo()
        self.assertTrue(group01.count_users == 1)
        self.assertTrue(group02.count_users == 1)
        self.assertTrue(group03.count_users == 2)
        self.assertTrue(group04.count_users == 2)
    
    def test_access_rights_user(self):
        directory01 = self.directory01.sudo(self.dmsuser.id)
        directory02 = self.directory02.sudo(self.dmsuser.id)
        directory03 = self.directory03.sudo(self.dmsuser.id)
        directory04 = self.directory04.sudo(self.dmsuser.id)
        directory05 = self.directory05.sudo(self.dmsuser.id)
        # directory01
        self.assertFalse(directory01.check_access('read'))
        # directory02
        self.assertFalse(directory02.check_access('read'))
        # directory03
        self.assertFalse(directory03.check_access('read'))
        # directory04
        self.assertTrue(directory04.perm_read)
        self.assertFalse(directory04.perm_create)
        self.assertTrue(directory04.perm_write) 
        self.assertFalse(directory04.perm_unlink)
        self.assertFalse(directory04.perm_access)
        # directory05
        self.assertTrue(directory05.perm_read)
        self.assertTrue(directory05.perm_create)
        self.assertTrue(directory05.perm_write) 
        self.assertTrue(directory05.perm_unlink)
        self.assertFalse(directory05.perm_access)
        
    def test_access_rights_manger(self):
        directory01 = self.directory01.sudo(self.dmsmanager.id)
        directory02 = self.directory02.sudo(self.dmsmanager.id)
        directory03 = self.directory03.sudo(self.dmsmanager.id)
        directory04 = self.directory04.sudo(self.dmsmanager.id)
        directory05 = self.directory05.sudo(self.dmsmanager.id)
        # directory01
        self.assertTrue(directory01.perm_read)
        self.assertFalse(directory01.perm_create)
        self.assertFalse(directory01.perm_write) 
        self.assertFalse(directory01.perm_unlink)
        self.assertFalse(directory01.perm_access)
        # directory02
        self.assertTrue(directory02.perm_read)
        self.assertFalse(directory02.perm_create)
        self.assertFalse(directory02.perm_write) 
        self.assertFalse(directory02.perm_unlink)
        self.assertFalse(directory02.perm_access)
        # directory03
        self.assertTrue(directory03.perm_read)
        self.assertTrue(directory03.perm_create)
        self.assertTrue(directory03.perm_write) 
        self.assertTrue(directory03.perm_unlink)
        self.assertTrue(directory03.perm_access)
        # directory04
        self.assertTrue(directory04.perm_read)
        self.assertTrue(directory04.perm_create)
        self.assertTrue(directory04.perm_write) 
        self.assertTrue(directory04.perm_unlink)
        self.assertTrue(directory04.perm_access)
        # directory05
        self.assertTrue(directory05.perm_read)
        self.assertTrue(directory05.perm_create)
        self.assertTrue(directory05.perm_write) 
        self.assertTrue(directory05.perm_unlink)
        self.assertFalse(directory05.perm_access)
        
    def test_access_search(self):
        user_files = self.env['muk_dms.file'].sudo(self.dmsuser.id)
        user_directory = self.env['muk_dms.directory'].sudo(self.dmsuser.id)
        manager_directory = self.env['muk_dms.directory'].sudo(self.dmsmanager.id)
        self.assertTrue(manager_directory.search([]))
        self.assertTrue(manager_directory.name_search(name='Media'))
        for directory in user_directory.search([]):
            self.assertTrue(user_directory.browse(directory.id))
        for file in user_files.search([]):
            self.assertTrue(file.perm_read)
