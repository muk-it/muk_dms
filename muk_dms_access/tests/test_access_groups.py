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
import logging

from odoo.exceptions import AccessError, ValidationError

from odoo.addons.muk_utils.tests.common import multi_users
from odoo.addons.muk_dms.tests.common import setup_data_function
from odoo.addons.muk_dms_access.tests.common import DocumentsAccessBaseCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class AccessGroupsTestCase(DocumentsAccessBaseCase):
    
    @setup_data_function(setup_func='_setup_test_data')
    def test_access_groups_relations(self):
        storage = self.create_storage(sudo=True)
        directory_01 = self.create_directory(storage=storage)
        directory_02 = self.create_directory(storage=storage)
        access_group = self.create_access_group(users=[self.env.uid])
        directory_01.write({'groups': [(4, access_group.id)]})
        directory_02.write({'groups': [(4, access_group.id)]})
        self.assertTrue(access_group.count_directories == 2)
