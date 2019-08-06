###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Actions 
#    (see https://mukit.at).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import os
import base64
import logging

from odoo.exceptions import AccessError, ValidationError

from odoo.addons.muk_utils.tests.common import multi_users
from odoo.addons.muk_dms.tests.common import setup_data_function
from odoo.addons.muk_dms.tests.test_file import FileTestCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class FileActionTestCase(FileTestCase):
    
    def setUp(self):
        super(FileActionTestCase, self).setUp()
        self.action = self.env['muk_dms_actions.action'].sudo()
        
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_available_actions(self):
        self.action.create({'name': "Test 01"})
        self.action.create({'name': "Test 02", 'is_limited_to_single_file': True})
        self.action.create({'name': "Test 03", 'criteria_directory': self.new_root_directory.id})
        self.action.create({'name': "Test 04", 'criteria_directory': self.new_sub_directory.id})
        self.assertTrue(len(self.new_file_root_directory.actions) == 3)
        self.assertTrue(len(self.new_file_root_directory.actions_multi) == 2)
        self.assertTrue(len(self.new_file_sub_directory.actions) == 4)
        self.assertTrue(len(self.new_file_sub_directory.actions_multi) == 3)
    