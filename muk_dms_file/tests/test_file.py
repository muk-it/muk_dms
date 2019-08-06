###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents File 
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

class FileFilestoreTestCase(FileTestCase):

    def _setup_test_data(self):
        super(FileFilestoreTestCase, self)._setup_test_data()
        self.new_storage.write({'save_type': 'file'})
    
    @multi_users(lambda self: self.multi_users())
    @setup_data_function(setup_func='_setup_test_data')
    def test_content_file(self):
        storage = self.create_storage(save_type="file", sudo=True)
        lobject_file = self.create_file(storage=storage)
        self.assertTrue(lobject_file.content)
        self.assertTrue(lobject_file.content_file)
        self.assertTrue(lobject_file.with_context({'bin_size': True}).content)
        self.assertTrue(lobject_file.with_context({'bin_size': True}).content_file)
        self.assertTrue(lobject_file.with_context({'human_size': True}).content_file)
        self.assertTrue(lobject_file.with_context({'base64': True}).content_file)
        self.assertTrue(lobject_file.with_context({'stream': True}).content_file)
        oid = lobject_file.with_context({'oid': True}).content_file
        self.assertTrue(oid)
        lobject_file.write({'content': base64.b64encode(b"\xff content")})
        self.assertTrue(oid != lobject_file.with_context({'oid': True}).content_file)
        self.assertTrue(lobject_file.export_data(['content']))
        self.assertTrue(lobject_file.export_data(['content'], raw_data=True))
        lobject_file.unlink()