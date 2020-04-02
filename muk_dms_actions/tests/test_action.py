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
import unittest

from odoo import _
from odoo.tests import common

from odoo.addons.muk_utils.tests.common import multi_users
from odoo.addons.muk_dms.tests.common import setup_data_function
from odoo.addons.muk_dms.tests.common import DocumentsBaseCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class ActionTestCase(DocumentsBaseCase):

    def setUp(self):
        super(ActionTestCase, self).setUp()
        self.action = self.env['muk_dms_actions.action'].sudo()
        self.new_storage = self.create_storage(sudo=True)
        self.new_directory = self.create_directory(self.new_storage)
        self.new_file = self.create_file(directory=self.new_directory)
        self.test_category = self.env['muk_dms.category'].create({
            'name': "Test Category",
        })
        self.test_tag = self.env['muk_dms.tag'].create({
            'name': "Test Tag",
        })

    def _setup_test_data(self):
        super(ActionTestCase, self)._setup_test_data()
        self.test_tag = self.test_tag.sudo(self.env.uid)
        self.test_category = self.test_category.sudo(self.env.uid)
        self.new_directory = self.new_directory.sudo(self.env.uid)
        self.new_file = self.new_file.sudo(self.env.uid)
        self.action = self.action.sudo(self.env.uid)
    
    @setup_data_function(setup_func='_setup_test_data')
    def test_criteria_directory(self):
        test_action_directory = self.action.create({
            'criteria_directory': self.new_directory.id,
            'name': "Test Criteria Directory",
        })
        self.assertEqual(test_action_directory.filter_domain,
            "[('directory', 'child_of', %s)]" % self.new_directory.id)
    
    @setup_data_function(setup_func='_setup_test_data')
    def test_criteria_category(self):
        test_action_category = self.action.create({
            'criteria_category': self.test_category.id,
            'name': "Test Criteria Category",
        })
        self.assertEqual(test_action_category.filter_domain,
            "[('category', 'child_of', %s)]" % self.test_category.id)
   
    @setup_data_function(setup_func='_setup_test_data')
    def test_criteria_tags(self):
        test_action_tags = self.action.create({
            'criteria_tags': [(4, self.test_tag.id)],
            'name': "Test Criteria Tag",
        })
        self.assertEqual(test_action_tags.filter_domain,
            "[('tags', 'in', [%s])]" % self.test_tag.id)
   
    @setup_data_function(setup_func='_setup_test_data')
    def test_criteria_mulit(self):
        test_action_multi = self.action.create({
            'criteria_directory': self.new_directory.id,
            'criteria_category': self.test_category.id,
            'name': "Test Criteria Multi",
        })
        domain_01 = "('directory', 'child_of', %s)" % self.new_directory.id
        domain_02 = "('category', 'child_of', %s)" % self.test_category.id
        self.assertEqual(test_action_multi.filter_domain,
            "['&', %s, %s]" % (domain_01, domain_02))
        
    @setup_data_function(setup_func='_setup_test_data')
    def test_set_directory(self):
        test_action = self.action.create({
            'set_directory': self.new_directory.id,
            'name': "Test Set Directory",
        })
        test_action.trigger_actions(self.new_file.ids)
        self.assertTrue(self.new_file.directory.id == self.new_directory.id)
        
    @setup_data_function(setup_func='_setup_test_data')
    def test_set_category(self):
        test_action = self.action.create({
            'set_category': self.test_category.id,
            'name': "Test Set Category",
        })
        test_action.trigger_actions(self.new_file.ids)
        self.assertTrue(self.new_file.category.id == self.test_category.id)
        
    @setup_data_function(setup_func='_setup_test_data')
    def test_set_tags(self):
        test_action = self.action.create({
            'set_tags': [(4, self.test_tag.id)],
            'name': "Test Set Tag",
        })
        test_action.trigger_actions(self.new_file.ids)
        self.assertTrue( self.test_tag.id in self.new_file.tags.ids)
        
    @setup_data_function(setup_func='_setup_test_data')
    def test_file_action(self):
        test_action = self.action.create({
            'state': "create_partner",
            'name': "Test File Action",
        })
        counter = self.env['res.partner'].sudo().search_count([])
        test_action.trigger_actions(self.browse_ref("muk_dms.file_01_demo").ids)
        self.assertTrue(self.env['res.partner'].sudo().search_count([]) > counter)
        
    @setup_data_function(setup_func='_setup_test_data')
    def test_server_action(self):
        action = self.browse_ref("muk_dms.action_dms_attachment_migrate")
        test_action = self.action.create({
            'server_actions': [(4, action.id)],
            'name': "Test Server Action",
        })
        test_action.trigger_actions(self.new_file.ids)