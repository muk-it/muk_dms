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
import time
import logging
import unittest
import threading
import functools

from odoo.tests import tagged
from odoo.tools.profiler import profile
from odoo.tools import config, convert_file
from odoo.modules.module import get_resource_path
from odoo.modules.module import get_module_resource

from odoo.addons.muk_utils.tests.common import multi_users
from odoo.addons.muk_utils.tests.common import track_function
from odoo.addons.muk_dms.tests.test_benchmark import BenchmarkTestCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

@tagged('-standard', 'benchmark')
class BenchmarkTestCase(BenchmarkTestCase): 
    
    @classmethod  
    def _setup_benchmark_data(cls):
        super(BenchmarkTestCase, cls)._setup_benchmark_data()
        cls._load('muk_dms_access', 'tests', 'data', 'muk_dms_actions.action.csv')
        
    #----------------------------------------------------------
    # File
    #----------------------------------------------------------

    def _file_kanban_fields(self):
        return self._file_kanban_fields() + ['actions']