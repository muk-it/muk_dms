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
import time
import logging
import unittest
import threading
import functools

from odoo import sql_db
from odoo.tools.profiler import profile

from odoo.addons.muk_utils.tests.common import multi_users
from odoo.addons.muk_utils.tests.common import track_function
from odoo.addons.muk_dms.tests.common import setup_data_function
from odoo.addons.muk_dms.tests.common import DocumentsBaseCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class BenchmarkTestCase(DocumentsBaseCase): 
    
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_search_read_benchmark(self):
        _logger.info("Reading all fields of %s files with context bin_size = True" %
            len(track_function(self.file.with_context(bin_size=True).search_read)([])))
      
    @track_function
    @setup_data_function()
    @profile(minimum_queries=35)
    def test_search_read_profile(self):
        _logger.info("Reading all fields of %s files with context bin_size = True" %
            len(self.file.sudo(self.demo_uid).with_context(bin_size=True).search_read([])))
        
    