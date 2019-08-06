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

from odoo.exceptions import AccessError, ValidationError

from odoo.addons.muk_utils.tests.common import multi_users
from odoo.addons.muk_dms.tests.common import setup_data_function
from odoo.addons.muk_dms.tests.test_file import FileTestCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class FileAttachmentTestCase(FileTestCase):
    
    def setUp(self):
        super(FileAttachmentTestCase, self).setUp()
        self.attachment = self.env['ir.attachment'].sudo()
        self.params = self.env['ir.config_parameter'].sudo()
        self.location = self.params.get_param('ir_attachment.location')
        self.params.set_param('ir_attachment.location', 'document')
        self.new_attachment_storage = self.create_storage(sudo=True)
        self.new_attachment_directory = self.create_directory(
            storage=self.new_attachment_storage
        )
        self.new_attachment_file = self.create_file(
            directory=self.new_attachment_directory
        )
        self.params.set_param(
            'muk_dms_attachment.attachment_directory',
            repr(self.new_attachment_directory.id)
        )

    def tearDown(self):
        self.params.set_param('ir_attachment.location', self.location)
        super(FileAttachmentTestCase, self).tearDown()
        
    def _setup_test_data(self):
        super(FileAttachmentTestCase, self)._setup_test_data()
        self.attachment = self.attachment.sudo(self.env.uid)
        self.new_attachment_storage = self.new_attachment_storage.sudo(self.env.uid)
        self.new_attachment_directory = self.new_attachment_directory.sudo(self.env.uid)
        self.new_attachment_file = self.new_attachment_file.sudo(self.env.uid)
    
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_attach_file(self):
        self.assertTrue(self.new_attachment_directory.count_files == 1)
        attachment = self.new_attachment_file.attach_file(link=False)
        self.assertTrue(attachment.is_store_document_link == False)
        self.assertTrue(self.new_attachment_directory.count_files >= 2)
        self.assertTrue(attachment.store_document != self.new_attachment_file)
        attachment = self.new_attachment_file.attach_file(model='res.partner', link=False)
        self.assertTrue(attachment.is_store_document_link == False)
        self.assertTrue(self.new_attachment_directory.count_files >= 3)
        self.assertTrue(attachment.store_document != self.new_attachment_file)
        attachment = self.new_attachment_file.attach_file(model='res.partner', id=1, link=False)
        self.assertTrue(attachment.is_store_document_link == False)
        self.assertTrue(self.new_attachment_directory.count_files >= 4)
        self.assertTrue(attachment.store_document != self.new_attachment_file)
        attachment = self.new_attachment_file.attach_file(model='res.partner', field='image', id=1, link=False)
        self.assertTrue(attachment.is_store_document_link == False)
        self.assertTrue(self.new_attachment_directory.count_files >= 5)
        self.assertTrue(attachment.store_document != self.new_attachment_file)
        
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_create_attachment_link(self):
        self.assertTrue(self.new_attachment_directory.count_files == 1)
        attachment = self.new_attachment_file.attach_file(link=True)
        self.assertTrue(attachment.is_store_document_link == True)
        self.assertTrue(self.new_attachment_directory.count_files == 1)
        self.assertTrue(attachment.store_document == self.new_attachment_file)
        
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_unlink_attachment_link(self):
        attachment = self.new_attachment_file.attach_file(link=True)
        self.assertTrue(attachment.is_store_document_link == True)
        attachment.unlink()
        self.assertTrue(self.new_attachment_file.exists())
    
   