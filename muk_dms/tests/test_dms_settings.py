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
import collections

from odoo import _
from odoo.tests import common

from odoo.tests import common

from odoo.addons.muk_dms.tests import dms_case

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

_compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

class SettingsTestCase(dms_case.DMSTestCase):
    
    def setUp(self):
        super(SettingsTestCase, self).setUp()
        self.settings = self.browse_ref("muk_dms.settings_demo").sudo()
        
    def tearDown(self):
        super(SettingsTestCase, self).tearDown()
    
    def test_compute_root_top_directories(self):
        root_top_directories = self.settings.root_directories.filtered(
                lambda r: r.is_root_directory == True)
        self.assertTrue(_compare(root_top_directories, self.settings.root_top_directories))
    