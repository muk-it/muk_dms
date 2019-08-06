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
from odoo.addons.muk_dms.tests.test_file import FileTestCase
from odoo.addons.muk_dms_access.tests.common import DocumentsAccessBaseCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class FileAccessTestCase(DocumentsAccessBaseCase, FileTestCase):

    def _setup_test_data(self):
        super(FileAccessTestCase, self)._setup_test_data()
        self.directory_access_root_demo_01 = self.browse_ref("muk_dms_access.directory_access_01_demo")
        self.directory_access_sub_demo_01 = self.browse_ref("muk_dms_access.directory_access_02_demo")
        self.access_group_manager_demo_01 = self.browse_ref("muk_dms_access.access_group_01_demo")
        self.access_group_manager_demo_02 = self.browse_ref("muk_dms_access.access_group_02_demo")
        self.access_group_user_demo_01 = self.browse_ref("muk_dms_access.access_group_03_demo")
        self.access_group_user_demo_02 = self.browse_ref("muk_dms_access.access_group_04_demo")
        self.file_access_demo_01 = self.browse_ref("muk_dms_access.file_access_01_demo")
        self.file_access_demo_02 = self.browse_ref("muk_dms_access.file_access_02_demo")
        self.file_access_demo_03 = self.browse_ref("muk_dms_access.file_access_03_demo")
        
    @multi_users(lambda self: [[self.admin_uid, True], [self.demo_uid, False]])
    @setup_data_function(setup_func='_setup_test_data')
    def test_create_access_file_manager(self):
        directory = self.create_directory(storage=self.new_storage)
        directory.write({
            'groups': [(4, self.access_group_manager_demo_01.id)]
        })
        with self.assertRaises(ValidationError) as error:
            file = self.create_file(directory=directory)
        self.assertEqual(error.exception.name, 'The directory has to have the permission to create files.')  
        directory.sudo().write({
            'groups': [(4, self.access_group_manager_demo_02.id)]
        })
        file = self.create_file(directory=directory)
        self.assertTrue(file.exists())
        
    @multi_users(lambda self: [[self.admin_uid, True], [self.demo_uid, True]])
    @setup_data_function(setup_func='_setup_test_data')
    def test_create_access_file_user(self):
        directory = self.create_directory(storage=self.new_storage)
        directory.write({
            'groups': [(4, self.access_group_user_demo_01.id)]
        })
        with self.assertRaises(ValidationError) as error:
            file = self.create_file(directory=directory)
        self.assertEqual(error.exception.name, 'The directory has to have the permission to create files.')  
        directory.sudo().write({
            'groups': [(4, self.access_group_user_demo_02.id)]
        })
        file = self.create_file(directory=directory)
        self.assertTrue(file.exists())
        
    @multi_users(lambda self: [[self.admin_uid, True], [self.demo_uid, False]])
    @setup_data_function(setup_func='_setup_test_data')
    def test_move_access_file_manager(self):
        file = self.create_file(storage=self.new_storage)
        directory = self.create_directory(storage=self.new_storage)
        directory.write({
            'groups': [(4, self.access_group_manager_demo_01.id)]
        })
        with self.assertRaises(Exception) as error:
            file.write({
                'directory': directory.id,
            })
        self.assertTrue(
            isinstance(error.exception, AccessError) or 
            isinstance(error.exception, ValidationError)
        )
        directory.sudo().write({
            'groups': [(4, self.access_group_manager_demo_02.id)]
        })
        file.write({
            'directory': directory.id,
        })
        self.assertTrue(file.directory.id == directory.id)
        
    @multi_users(lambda self: [[self.admin_uid, True], [self.demo_uid, True]])
    @setup_data_function(setup_func='_setup_test_data')
    def test_move_access_file_user(self):
        file = self.create_file(storage=self.new_storage)
        directory = self.create_directory(storage=self.new_storage)
        directory.write({
            'groups': [(4, self.access_group_user_demo_01.id)]
        })
        with self.assertRaises(Exception) as error:
            file.write({
                'directory': directory.id,
            })
        self.assertTrue(
            isinstance(error.exception, AccessError) or 
            isinstance(error.exception, ValidationError)
        )
        directory.sudo().write({
            'groups': [(4, self.access_group_user_demo_02.id)]
        })
        file.write({
            'directory': directory.id,
        })
        self.assertTrue(file.directory.id == directory.id)