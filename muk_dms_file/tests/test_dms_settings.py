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

class SettingsTestCase(dms_case.DMSTestCase):
    
    def setUp(self):
        super(SettingsTestCase, self).setUp()
        self.settings = self.env['muk_dms.settings'].sudo().create({
            'name': "SystemDataTestSettings",
            'save_type': "file",
            'base_path': os.path.join(_path, 'tests')})
        self.root_directory = self.env['muk_dms.directory'].sudo().create({
            'name': "RootTestDir",
            'is_root_directory': True,
            'settings': self.settings.id})
        self.sub_directory = self.env['muk_dms.directory'].sudo().create({
            'name': "SubTestDir",
            'is_root_directory': False,
            'parent_directory': self.root_directory.id})
        self.file = self.env['muk_dms.file'].sudo().create({
            'name': "file.txt",
            'directory': self.root_directory.id,
            'content': self.file_base64()})
        
    def tearDown(self):
        super(SettingsTestCase, self).tearDown()
        self.root_directory.unlink()
    
    def test_change_save_type(self):
        self.settings.write({
            'save_type': "database",
            'base_path': None})
        self.assertTrue(self.file.content)
        