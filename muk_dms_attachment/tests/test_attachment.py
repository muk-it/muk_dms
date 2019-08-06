###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Attachment 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
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

class AttachmentTestCase(DocumentsBaseCase):
    
    def setUp(self):
        super(AttachmentTestCase, self).setUp()
        self.attachment = self.env['ir.attachment'].sudo()
        self.params = self.env['ir.config_parameter'].sudo()
        self.location = self.params.get_param('ir_attachment.location')
        self.params.set_param('ir_attachment.location', 'document')
        self.new_storage = self.create_storage(sudo=True)
        self.new_directory = self.create_directory(self.new_storage)
        self.params.set_param(
            'muk_dms_attachment.attachment_directory',
            repr(self.new_directory.id)
        )

    def tearDown(self):
        self.params.set_param('ir_attachment.location', self.location)
        super(AttachmentTestCase, self).tearDown()
        
    def _setup_test_data(self):
        super(AttachmentTestCase, self)._setup_test_data()
        self.attachment = self.attachment.sudo(self.env.uid)
        self.new_storage = self.new_storage.sudo(self.env.uid)
        self.new_directory = self.new_directory.sudo(self.env.uid)
    
    def create_attachment(self, res_model=None, res_field=None, res_id=0, context={}, sudo=False):
        model = self.attachment.sudo() if sudo else self.attachment
        values = {'name': "Test", 'datas': self.content_base64()}
        if res_model:
            values.update({'res_model': res_model})
        if res_field:
            values.update({'res_field': res_field})
        if res_id:
            values.update({'res_id': res_id})
        return model.with_context(**context).create(values)
    
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_create_attachment(self):
        self.assertTrue(self.new_directory.count_files == 0)
        new_attachment = self.create_attachment()
        new_file_name = "[A-%s] Test" % new_attachment.id
        self.assertTrue(self.new_directory.count_files >= 1)
        self.assertTrue(new_attachment.store_document.exists())
        self.assertTrue(new_attachment.store_document.name == new_file_name)
        self.assertTrue(new_attachment.store_document.directory == self.new_directory)
    
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_write_attachment(self):
        self.assertTrue(self.new_directory.count_files == 0)
        new_attachment = self.create_attachment()
        self.assertTrue(self.new_directory.count_files >= 1)
        new_attachment_datas = base64.b64encode(b"\xff new")
        new_attachment.write({'datas': new_attachment_datas})
        self.assertTrue(new_attachment.datas != self.content_base64())
        self.assertTrue(new_attachment.store_document.content == new_attachment_datas)
    
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_copy_attachment(self):
        self.assertTrue(self.new_directory.count_files == 0)
        new_attachment = self.create_attachment()
        copy_attachment = new_attachment.copy()
        self.assertTrue(self.new_directory.count_files >= 2)
        
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_unlink_attachment(self):
        self.assertTrue(self.new_directory.count_files == 0)
        new_attachment = self.create_attachment()
        new_file = new_attachment.store_document
        self.assertTrue(self.new_directory.count_files >= 1)
        new_attachment.unlink()
        self.assertFalse(new_file.exists())
        
    @unittest.skip("The test takes a long time and is therefore skipped by default.")
    def test_migiration(self):
        self.attachment.force_storage()