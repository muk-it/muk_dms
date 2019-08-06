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
import time
import hmac
import base64
import hashlib
import logging

from odoo.http import request

from odoo.addons.muk_utils.tests import common

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class DownloadTestCase(common.HttpCase):
    
    def test_file_download(self):
        self.authenticate('admin', 'admin')
        self.assertTrue(self.url_open('/web/file', data={
            'field': 'content_file',
            'filename_field': 'name',
            'model': 'muk_dms.file',
            'id': self.browse_ref("muk_dms.file_01_demo").id,
        }, csrf=True))
        self.assertTrue(self.url_open('/web/file', data={
            'xmlid': 'muk_dms.file_01_demo',
            'field': 'content_file',
            'filename_field': 'name',
        }, csrf=True))
        
      