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

class DataTestCase(dms_case.DMSTestCase):
    
    def setUp(self):
        super(DataTestCase, self).setUp()
        
    def tearDown(self):
        super(DataTestCase, self).tearDown()
    
    def test_access_groups(self):
        group01 = self.browse_ref("muk_dms_access.access_group_01_demo").sudo()
        group02 = self.browse_ref("muk_dms_access.access_group_02_demo").sudo()
        group03 = self.browse_ref("muk_dms_access.access_group_03_demo").sudo()
        group04 = self.browse_ref("muk_dms_access.access_group_04_demo").sudo()
        self.assertTrue(len(group01) == 1)
        self.assertTrue(len(group02) == 1)
        self.assertTrue(len(group03) == 2)
        self.assertTrue(len(group04) == 2)
    