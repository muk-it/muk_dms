###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Access 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import os
import logging

from odoo.exceptions import AccessError, ValidationError

from odoo.addons.muk_utils.tests.common import multi_users
from odoo.addons.muk_dms.tests.common import setup_data_function
from odoo.addons.muk_dms.tests.test_directory import DirectoryTestCase
from odoo.addons.muk_dms_access.tests.common import DocumentsAccessBaseCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class DirectoryAccessTestCase(DocumentsAccessBaseCase, DirectoryTestCase):
    
    def _setup_test_data(self):
        super(DirectoryAccessTestCase, self)._setup_test_data()
        self.directory_access_root_demo_01 = self.browse_ref("muk_dms_access.directory_access_01_demo")
        self.directory_access_sub_demo_01 = self.browse_ref("muk_dms_access.directory_access_02_demo")
        self.access_group_manager_demo_01 = self.browse_ref("muk_dms_access.access_group_01_demo")
        self.access_group_manager_demo_02 = self.browse_ref("muk_dms_access.access_group_02_demo")
        self.access_group_user_demo_01 = self.browse_ref("muk_dms_access.access_group_03_demo")
        self.access_group_user_demo_02 = self.browse_ref("muk_dms_access.access_group_04_demo")
    
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_inherit_groups(self):
        root_directory = self.create_directory(storage=self.new_storage)
        sub_directory_01 = self.create_directory(directory=root_directory)
        sub_directory_02 = self.create_directory(directory=sub_directory_01)
        root_directory.write({
            'groups': [(4, self.access_group_user_demo_02.id)]
        })
        self.assertTrue(len(sub_directory_01.complete_groups) == 1)
        self.assertTrue(len(sub_directory_02.complete_groups) == 1)
        sub_directory_01.write({
            'groups': [(4, self.access_group_user_demo_01.id)]
        })
        self.assertTrue(len(sub_directory_01.complete_groups) == 2)
        self.assertTrue(len(sub_directory_02.complete_groups) == 2)
        sub_directory_01.write({
            'inherit_groups': False,
        })
        self.assertTrue(len(sub_directory_01.complete_groups) == 1)
        self.assertTrue(len(sub_directory_02.complete_groups) == 1)
        sub_directory_02.write({
            'groups': [(4, self.access_group_user_demo_02.id)]
        })
        self.assertTrue(len(sub_directory_02.complete_groups) == 2)
        sub_directory_02.write({
            'inherit_groups': False,
        })
        self.assertTrue(len(sub_directory_02.complete_groups) == 1)
    
    @multi_users(lambda self: [[self.admin_uid, True], [self.demo_uid, False]])
    @setup_data_function(setup_func='_setup_test_data')
    def test_create_access_directory_manager(self):
        root_directory = self.create_directory(storage=self.new_storage)
        root_directory.write({
            'groups': [(4, self.access_group_manager_demo_01.id)]
        })
        with self.assertRaises(ValidationError) as error:
            sub_directory = self.create_directory(directory=root_directory)
        self.assertEqual(error.exception.name, 'The parent directory has to have the permission to create directories.')  
        root_directory.sudo().write({
            'groups': [(4, self.access_group_manager_demo_02.id)]
        })
        sub_directory = self.create_directory(directory=root_directory)
        self.assertTrue(sub_directory.exists())
    
    @multi_users(lambda self: [[self.admin_uid, True], [self.demo_uid, True]])
    @setup_data_function(setup_func='_setup_test_data')
    def test_create_access_directory_user(self):
        root_directory = self.create_directory(storage=self.new_storage)
        root_directory.write({
            'groups': [(4, self.access_group_user_demo_01.id)]
        })
        with self.assertRaises(ValidationError) as error:
            sub_directory = self.create_directory(directory=root_directory)
        self.assertEqual(error.exception.name, 'The parent directory has to have the permission to create directories.')  
        root_directory.write({
            'groups': [(4, self.access_group_user_demo_02.id)]
        })
        sub_directory = self.create_directory(directory=root_directory)
        self.assertTrue(sub_directory.exists())
    
    @multi_users(lambda self: [[self.admin_uid, True], [self.demo_uid, False]])
    @setup_data_function(setup_func='_setup_test_data')
    def test_move_access_directory_manager(self):
        root_directory_01 = self.create_directory(storage=self.new_storage)
        root_directory_02 = self.create_directory(storage=self.new_storage)
        root_directory_03 = self.create_directory(storage=self.new_storage)
        sub_directory = self.create_directory(directory=root_directory_01)
        root_directory_01.write({
            'groups': [(4, self.access_group_manager_demo_01.id)]
        })
        root_directory_02.write({
            'groups': [(4, self.access_group_manager_demo_02.id)]
        })
        with self.assertRaises(Exception) as error:
            sub_directory.write({
                'parent_directory': root_directory_01.id,
            })
        self.assertTrue(
            isinstance(error.exception, AccessError) or 
            isinstance(error.exception, ValidationError)
        )
        with self.assertRaises(Exception) as error:
            sub_directory.write({
                'parent_directory': root_directory_02.id,
            })
        self.assertTrue(
            isinstance(error.exception, AccessError) or 
            isinstance(error.exception, ValidationError)
        )
        sub_directory.sudo().write({
            'inherit_groups': False,
        })
        sub_directory.sudo(self.env.uid).write({
            'parent_directory': root_directory_02.id,
        })
        self.assertTrue(sub_directory.parent_directory.id == root_directory_02.id)
        sub_directory.write({
            'parent_directory': root_directory_03.id,
        })
        self.assertTrue(sub_directory.parent_directory.id == root_directory_03.id)

    @multi_users(lambda self: [[self.admin_uid, True], [self.demo_uid, True]])
    @setup_data_function(setup_func='_setup_test_data')
    def test_move_access_directory_user(self):
        root_directory_01 = self.create_directory(storage=self.new_storage)
        root_directory_02 = self.create_directory(storage=self.new_storage)
        root_directory_03 = self.create_directory(storage=self.new_storage)
        sub_directory = self.create_directory(directory=root_directory_01)
        root_directory_01.write({
            'groups': [(4, self.access_group_user_demo_01.id)]
        })
        root_directory_02.write({
            'groups': [(4, self.access_group_user_demo_02.id)]
        })
        with self.assertRaises(Exception) as error:
            sub_directory.write({
                'parent_directory': root_directory_01.id,
            })
        self.assertTrue(
            isinstance(error.exception, AccessError) or 
            isinstance(error.exception, ValidationError)
        )
        sub_directory.write({
            'parent_directory': root_directory_02.id,
        })
        self.assertTrue(sub_directory.parent_directory.id == root_directory_02.id)
        sub_directory.write({
            'parent_directory': root_directory_03.id,
        })
        self.assertTrue(sub_directory.parent_directory.id == root_directory_03.id)