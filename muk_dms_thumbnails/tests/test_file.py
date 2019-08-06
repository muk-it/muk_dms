###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Thumbnails 
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

class FileThumbnailTestCase(FileTestCase):
    
    def setUp(self):
        super(FileThumbnailTestCase, self).setUp()
        self.cron_thumbnails = self.browse_ref("muk_dms_thumbnails.cron_dms_file_thumbnails")
    
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_thumbnail_immediate(self):
        storage = self.create_storage(sudo=True)
        storage.write({
            'thumbnails': 'immediate',
        })
        file = self.create_file(storage=storage)
        self.assertFalse(file.automatic_thumbnail)
        file.write({
            'name': "Image.jpg",
            'content': self.file_demo_01.content
        })
        self.assertTrue(file.automatic_thumbnail)
        self.assertTrue(file.automatic_thumbnail_medium)
        self.assertTrue(file.automatic_thumbnail_small)
        
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_thumbnail_cron(self):
        storage = self.create_storage(sudo=True)
        storage.write({
            'thumbnails': 'cron',
        })
        file = self.create_file(storage=storage)
        self.assertFalse(file.automatic_thumbnail)
        file.write({
            'name': "Image.jpg",
            'content': self.file_demo_01.content
        })
        self.assertFalse(file.automatic_thumbnail)
        self.cron_thumbnails.sudo().method_direct_trigger()
        self.assertTrue(file.automatic_thumbnail)
        self.assertTrue(file.automatic_thumbnail_medium)
        self.assertTrue(file.automatic_thumbnail_small)
        