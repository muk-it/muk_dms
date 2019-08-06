###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Access 
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
import uuid
import base64
import logging
import functools

from odoo import SUPERUSER_ID
from odoo.tests import common

from odoo.addons.muk_dms.tests.common import DocumentsBaseCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class DocumentsAccessBaseCase(DocumentsBaseCase):
    
    def _setup_test_data(self):
        super(DocumentsAccessBaseCase, self)._setup_test_data()
        self.access_group = self.env['muk_security.access_groups']
        
    def create_access_group(self, access={}, users=[], parent=False, sudo=False):
        model = self.access_group.sudo() if sudo else self.access_group
        values = {
            'name': uuid.uuid4().hex,
            'parent_group': parent,
        }
        if users:
            values.update({
                'groups': [(6, 0, users)]
            })
        values.update(access)
        return model.create(values)