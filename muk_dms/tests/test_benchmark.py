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

from odoo import SUPERUSER_ID
from odoo.tests import common
from odoo.tools.profiler import profile
from odoo.tools import config, convert_file
from odoo.modules.module import get_resource_path
from odoo.modules.module import get_module_resource

from odoo.addons.muk_utils.tests.common import multi_users
from odoo.addons.muk_utils.tests.common import track_function

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class BenchmarkTestCase(common.SavepointCase): 
    
    @classmethod
    def setUpClass(cls):
        super(BenchmarkTestCase, cls).setUpClass()
        cls._clean_existing_records()
        cls._setup_benchmark_data()
        
    @classmethod
    def _clean_existing_records(cls):
        cls.env['muk_dms.category'].search([]).unlink()
        cls.env['muk_dms.directory'].search([]).unlink()
        cls.env['muk_dms.storage'].search([]).unlink()
        cls.env['muk_dms.tag'].search([]).unlink()   
        
    @classmethod
    def _load(cls, module, *args):
        convert_file(cls.cr, 'muk_dms', get_module_resource(module, *args),
            {}, 'init', False, 'test', cls.registry._assertion_report)
  
    @classmethod  
    def _setup_benchmark_data(cls):
        cls._load('muk_dms', 'tests', 'data', 'muk_dms.category.csv')
        cls._load('muk_dms', 'tests', 'data', 'muk_dms.storage.csv')
        cls._load('muk_dms', 'tests', 'data', 'muk_dms.tag.csv')
        cls._load('muk_dms', 'tests', 'data', 'muk_dms.directory.csv')
        cls._load('muk_dms', 'tests', 'data', 'muk_dms.file.csv')

    def _benchmark_table(self, data):
        columns = len(data[0]) - 1
        format = "{:8}" + "{:30}" * columns
        result = (format.format(*data[0]) + "\n")
        for row in data[1:]:
            result += (format.format(*row) + "\n")
        return result

    #----------------------------------------------------------
    # File
    #----------------------------------------------------------

    def test_file_search_benchmark(self):
        demo_uid = self.browse_ref("base.user_demo").id
        admin_uid = self.browse_ref("base.user_admin").id
        track_function_wrapper = track_function(return_tracking=True)
        model =  self.env['muk_dms.file'].with_context(bin_size=True)
        
        benchmark_data_super = ['Super']
        benchmark_data_admin = ['Admin']
        benchmark_data_demo = ['Demo']
        
        file_search = track_function_wrapper(model.sudo().search)
        file_search_result, tracking = file_search([], limit=80)
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_result, tracking = file_search([], limit=500)
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_result, tracking = file_search([])
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        
        file_search = track_function_wrapper(model.sudo(admin_uid).search)
        file_search_result, tracking = file_search([], limit=80)
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_result, tracking = file_search([], limit=500)
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_result, tracking = file_search([])
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        
        file_search = track_function_wrapper(model.sudo(demo_uid).search)
        file_search_result, tracking = file_search([], limit=80)
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_result, tracking = file_search([], limit=500)
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_result, tracking = file_search([])
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))

        info_message = "\n\nSearching files with bin_size = True | "
        info_message += "Benchmark with Limit 80 / 500 / None (1500)\n\n"
        info_message += self._benchmark_table([
            ["User", "Search Limit 80", "Search Limit 500", "Search No Limit"], 
            benchmark_data_super, benchmark_data_admin, benchmark_data_demo
        ])
        info_message += "\nLegend: Queries | Query Time | Server Time | Total Time\n"
        _logger.info(info_message)
        
    def test_file_search_read_benchmark(self):
        demo_uid = self.browse_ref("base.user_demo").id
        admin_uid = self.browse_ref("base.user_admin").id
        track_function_wrapper = track_function(return_tracking=True)
        model =  self.env['muk_dms.file'].with_context(bin_size=True)
        
        benchmark_data_super = ['Super']
        benchmark_data_admin = ['Admin']
        benchmark_data_demo = ['Demo']
        
        file_search_read = track_function_wrapper(model.sudo().search_read)
        file_search_read_result, tracking = file_search_read(limit=80)
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_read_result, tracking = file_search_read(limit=500)
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_read_result, tracking = file_search_read()
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        
        file_search_read = track_function_wrapper(model.sudo(admin_uid).search_read)
        file_search_read_result, tracking = file_search_read(limit=80)
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_read_result, tracking = file_search_read(limit=500)
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_read_result, tracking = file_search_read()
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        
        file_search_read = track_function_wrapper(model.sudo(demo_uid).search_read)
        file_search_read_result, tracking = file_search_read(limit=80)
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_read_result, tracking = file_search_read(limit=500)
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        file_search_read_result, tracking = file_search_read()
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))

        info_message = "\n\nSearching and reading all fields with bin_size = True | "
        info_message += "Benchmark with Limit 80 / 500 / None (1500)\n\n"
        info_message += self._benchmark_table([
            ["User", "Search Limit 80", "Search Limit 500", "Search No Limit"], 
            benchmark_data_super, benchmark_data_admin, benchmark_data_demo
        ])
        info_message += "\nLegend: Queries | Query Time | Server Time | Total Time\n"
        _logger.info(info_message)
        
    #----------------------------------------------------------
    # Directory
    #----------------------------------------------------------

    def test_directory_search_benchmark(self):
        demo_uid = self.browse_ref("base.user_demo").id
        admin_uid = self.browse_ref("base.user_admin").id
        track_function_wrapper = track_function(return_tracking=True)
        model =  self.env['muk_dms.directory'].with_context(bin_size=True)
        
        benchmark_data_super = ['Super']
        benchmark_data_admin = ['Admin']
        benchmark_data_demo = ['Demo']
        
        directory_search = track_function_wrapper(model.sudo().search)
        directory_search_result, tracking = directory_search([], limit=80)
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_result, tracking = directory_search([], limit=250)
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_result, tracking = directory_search([])
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        
        directory_search = track_function_wrapper(model.sudo(admin_uid).search)
        directory_search_result, tracking = directory_search([], limit=80)
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_result, tracking = directory_search([], limit=250)
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_result, tracking = directory_search([])
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        
        directory_search = track_function_wrapper(model.sudo(demo_uid).search)
        directory_search_result, tracking = directory_search([], limit=80)
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_result, tracking = directory_search([], limit=250)
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_result, tracking = directory_search([])
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))

        info_message = "\n\nSearching directories with bin_size = True | "
        info_message += "Benchmark with Limit 80 / 250 / None (500)\n\n"
        info_message += self._benchmark_table([
            ["User", "Search Limit 80", "Search Limit 500", "Search No Limit"], 
            benchmark_data_super, benchmark_data_admin, benchmark_data_demo
        ])
        info_message += "\nLegend: Queries | Query Time | Server Time | Total Time\n"
        _logger.info(info_message)
        
    def test_directory_search_read_benchmark(self):
        demo_uid = self.browse_ref("base.user_demo").id
        admin_uid = self.browse_ref("base.user_admin").id
        track_function_wrapper = track_function(return_tracking=True)
        model =  self.env['muk_dms.directory'].with_context(bin_size=True)
        
        benchmark_data_super = ['Super']
        benchmark_data_admin = ['Admin']
        benchmark_data_demo = ['Demo']
        
        directory_search_read = track_function_wrapper(model.sudo().search_read)
        directory_search_read_result, tracking = directory_search_read(limit=80)
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_read_result, tracking = directory_search_read(limit=250)
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_read_result, tracking = directory_search_read()
        benchmark_data_super.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        
        directory_search_read = track_function_wrapper(model.sudo(admin_uid).search_read)
        directory_search_read_result, tracking = directory_search_read(limit=80)
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_read_result, tracking = directory_search_read(limit=250)
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_read_result, tracking = directory_search_read()
        benchmark_data_admin.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        
        directory_search_read = track_function_wrapper(model.sudo(demo_uid).search_read)
        directory_search_read_result, tracking = directory_search_read(limit=80)
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_read_result, tracking = directory_search_read(limit=250)
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))
        model.clear_caches()
        directory_search_read_result, tracking = directory_search_read()
        benchmark_data_demo.append("%sq %.3fs %.3fs %.3fs" % tuple(tracking[1:]))

        info_message = "\n\nSearching and reading all fields with bin_size = True | "
        info_message += "Benchmark with Limit 80 / 250 / None (500)\n\n"
        info_message += self._benchmark_table([
            ["User", "Search Limit 80", "Search Limit 250", "Search No Limit"], 
            benchmark_data_super, benchmark_data_admin, benchmark_data_demo
        ])
        info_message += "\nLegend: Queries | Query Time | Server Time | Total Time\n"
        _logger.info(info_message)
    
    @unittest.skip("Takes to long to be tested every time.")
    def test_file_search_read_profile_admin(self):
        @track_function()
        @profile(minimum_queries=35)
        def profile_function(model):
            model.search_read([])
        admin_uid = self.browse_ref("base.user_admin").id
        model =  self.env['muk_dms.file'].sudo(admin_uid)
        profile_function(model.with_context(bin_size=True))
        
    