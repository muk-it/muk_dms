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
import base64
import logging
import unittest

from odoo import _
from odoo.tests import common

from odoo.addons.muk_dms.tests import dms_case

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class AttachmentTestCase(dms_case.DMSTestCase):
    
    def setUp(self):
        super(AttachmentTestCase, self).setUp()
        self.directory = self.browse_ref("muk_dms_attachment.directory_attachment_demo")
        self.attachment = self.browse_ref("muk_dms_attachment.attachment_demo")
        
    def tearDown(self):
        super(AttachmentTestCase, self).tearDown()
        
    @unittest.skip("The test takes a long time and is therefore skipped by default.")
    def test_migiration(self):
        self.env['ir.attachment'].sudo().force_storage()
        self.assertTrue(self.attachment.store_document.id)
        copy = self.attachment.copy()
        copy.unlink()
        
    def test_copy(self):
        copy = self.attachment.copy()
        copy.unlink()