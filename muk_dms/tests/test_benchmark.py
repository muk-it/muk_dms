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

    def test_file_search_benchmark_super_limit_80(self): 
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo().with_context(bin_size=True)
        _logger.info("Searching files with limit = 80 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search)([], limit=80))
        _logger.info("%s files have been found." % count_files)
        
    def test_file_search_benchmark_super_limit_500(self): 
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo().with_context(bin_size=True)
        _logger.info("Searching files with limit = 500 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search)([], limit=500))
        _logger.info("%s files have been found." % count_files)

    def test_file_search_benchmark_super_limit_none(self): 
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo().with_context(bin_size=True)
        _logger.info("Searching files with no limit and context bin_size = True") 
        count_files = len(track_function_wrapper(model.search)([]))
        _logger.info("%s files have been found." % count_files)

    def test_file_search_benchmark_admin_limit_80(self): 
        admin_uid = self.browse_ref("base.user_admin").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(admin_uid).with_context(bin_size=True)
        _logger.info("Searching files with limit = 80 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search)([], limit=80))
        _logger.info("%s files have been found." % count_files)
        
    def test_file_search_benchmark_admin_limit_500(self): 
        admin_uid = self.browse_ref("base.user_admin").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(admin_uid).with_context(bin_size=True)
        _logger.info("Searching files with limit = 500 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search)([], limit=500))
        _logger.info("%s files have been found." % count_files)

    def test_file_search_benchmark_admin_limit_none(self): 
        admin_uid = self.browse_ref("base.user_admin").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(admin_uid).with_context(bin_size=True)
        _logger.info("Searching files with no limit and context bin_size = True") 
        count_files = len(track_function_wrapper(model.search)([]))
        _logger.info("%s files have been found." % count_files)

    def test_file_search_benchmark_demo_limit_80(self): 
        demo_uid = self.browse_ref("base.user_demo").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(demo_uid).with_context(bin_size=True)
        _logger.info("Searching files with limit = 80 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search)([], limit=80))
        _logger.info("%s files have been found." % count_files)
        
    def test_file_search_benchmark_demo_limit_500(self): 
        demo_uid = self.browse_ref("base.user_demo").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(demo_uid).with_context(bin_size=True)
        _logger.info("Searching files with limit = 500 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search)([], limit=500))
        _logger.info("%s files have been found." % count_files)

    def test_file_search_benchmark_demo_limit_none(self): 
        demo_uid = self.browse_ref("base.user_demo").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(demo_uid).with_context(bin_size=True)
        _logger.info("Searching files with no limit and context bin_size = True") 
        count_files = len(track_function_wrapper(model.search)([]))
        _logger.info("%s files have been found." % count_files)

    def test_file_search_read_benchmark_super_limit_80(self): 
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo().with_context(bin_size=True)
        _logger.info("Searching files and reading all fields with limit = 80 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search_read)([], limit=80))
        _logger.info("%s files have been found." % count_files)
        
    def test_file_search_read_benchmark_super_limit_500(self): 
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo().with_context(bin_size=True)
        _logger.info("Searching files and reading all fields with limit = 500 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search_read)([], limit=500))
        _logger.info("%s files have been found." % count_files)

    def test_file_search_read_benchmark_super_limit_none(self): 
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo().with_context(bin_size=True)
        _logger.info("Searching files and reading all fields with no limit and context bin_size = True") 
        count_files = len(track_function_wrapper(model.search_read)([]))
        _logger.info("%s files have been found." % count_files)

    def test_file_search_read_benchmark_admin_limit_80(self): 
        admin_uid = self.browse_ref("base.user_admin").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(admin_uid).with_context(bin_size=True)
        _logger.info("Searching files and reading all fields with limit = 80 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search_read)([], limit=80))
        _logger.info("%s files have been found." % count_files)
        
    def test_file_search_read_benchmark_admin_limit_500(self): 
        admin_uid = self.browse_ref("base.user_admin").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(admin_uid).with_context(bin_size=True)
        _logger.info("Searching files and reading all fields with limit = 500 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search_read)([], limit=500))
        _logger.info("%s files have been found." % count_files)

    def test_file_search_read_benchmark_admin_limit_none(self): 
        admin_uid = self.browse_ref("base.user_admin").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(admin_uid).with_context(bin_size=True)
        _logger.info("Searching files and reading all fields with no limit and context bin_size = True") 
        count_files = len(track_function_wrapper(model.search_read)([]))
        _logger.info("%s files have been found." % count_files)

    def test_file_search_read_benchmark_demo_limit_80(self): 
        demo_uid = self.browse_ref("base.user_demo").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(demo_uid).with_context(bin_size=True)
        _logger.info("Searching files and reading all fields with limit = 80 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search_read)([], limit=80))
        _logger.info("%s files have been found." % count_files)
        
    def test_file_search_read_benchmark_demo_limit_500(self): 
        demo_uid = self.browse_ref("base.user_demo").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(demo_uid).with_context(bin_size=True)
        _logger.info("Searching files and reading all fields with limit = 500 and context bin_size = True")   
        count_files = len(track_function_wrapper(model.search_read)([], limit=500))
        _logger.info("%s files have been found." % count_files)

    def test_file_search_read_benchmark_demo_limit_none(self): 
        demo_uid = self.browse_ref("base.user_demo").id
        track_function_wrapper = track_function(return_tracking=False)
        model =  self.env['muk_dms.file'].sudo(demo_uid).with_context(bin_size=True)
        _logger.info("Searching files and reading all fields with no limit and context bin_size = True") 
        count_files = len(track_function_wrapper(model.search_read)([]))
        _logger.info("%s files have been found." % count_files)
    
    @unittest.skip("Takes to long to be tested every time.")
    def test_file_search_read_profile_admin(self):
        @track_function()
        @profile(minimum_queries=35)
        def profile_function(model):
            model.search_read([])
        admin_uid = self.browse_ref("base.user_admin").id
        model =  self.env['muk_dms.file'].sudo(admin_uid)
        profile_function(model.with_context(bin_size=True))
        
    