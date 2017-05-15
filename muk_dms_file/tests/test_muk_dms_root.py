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
import base64
import unittest

from openerp import _
from openerp.tests import common

from . import muk_dms_file_test as dms_file_test

_path = os.path.dirname(os.path.dirname(__file__))

class RootTestCase(dms_file_test.DMSFileTestCase):
    
    @unittest.expectedFailure  
    def test_root_save_type_constrain(self):
        dir = self.dir_model.create({'name': 'New_Directory'})
        self.root = self.root_model.create({'name': 'Database Settings', 'root_directory': dir.id, 'save_type': 'file'})