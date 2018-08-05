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
import logging

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

    def test_access_rights_manger(self):
        directory01 = self.directory01.sudo(self.demouser)
        directory02 = self.directory02.sudo(self.demouser)
        directory03 = self.directory03.sudo(self.demouser)
        directory04 = self.directory04.sudo(self.demouser)
        directory05 = self.directory05.sudo(self.demouser)
        # directory01
        self.assertTrue(directory01.permission_read)
        self.assertFalse(directory01.permission_create)
        self.assertFalse(directory01.permission_write) 
        self.assertFalse(directory01.permission_unlink)
        # directory02
        self.assertTrue(directory02.permission_read)
        self.assertFalse(directory02.permission_create)
        self.assertFalse(directory02.permission_write) 
        self.assertFalse(directory02.permission_unlink)
        # directory03
        self.assertTrue(directory03.permission_read)
        self.assertTrue(directory03.permission_create)
        self.assertTrue(directory03.permission_write) 
        self.assertTrue(directory03.permission_unlink)
        # directory04
        self.assertTrue(directory04.permission_read)
        self.assertTrue(directory04.permission_create)
        self.assertTrue(directory04.permission_write) 
        self.assertTrue(directory04.permission_unlink)
        # directory05
        self.assertTrue(directory05.permission_read)
        self.assertTrue(directory05.permission_create)
        self.assertTrue(directory05.permission_write) 
        self.assertTrue(directory05.permission_unlink)
        
    def test_access_search(self):
        files = self.file.sudo(self.demouser)
        directory = self.directory.sudo(self.demouser)
        self.assertTrue(directory.search([]))
        self.assertTrue(directory.name_search(name='Media'))
        for file in files.search([]):
            self.assertTrue(file.permission_read)
