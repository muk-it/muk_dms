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
import logging

from odoo.addons.muk_utils.tests.common import multi_users
from odoo.addons.muk_dms.tests.common import setup_data_function
from odoo.addons.muk_dms.tests.test_storage import StorageTestCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class StorageLObjectTestCase(StorageTestCase):
    
    @setup_data_function(setup_func='_setup_test_data')
    def test_file_migrate(self):
        storage = self.create_storage(sudo=True)
        file_01 = self.create_file(storage=storage)
        self.assertTrue(file_01.storage.id == storage.id)
        self.assertTrue(file_01.storage.save_type == 'database')
        self.assertTrue(file_01.save_type == 'database')
        storage.write({'save_type': 'file'})
        file_02 = self.create_file(storage=storage)
        self.assertTrue(file_01.storage.id == storage.id)
        self.assertTrue(file_01.storage.save_type == 'file')
        self.assertTrue(file_01.save_type == 'database')
        self.assertTrue(file_02.storage.id == storage.id)
        self.assertTrue(file_02.storage.save_type == 'file')
        self.assertTrue(file_02.save_type == 'file')
        storage.action_storage_migrate()
        self.assertTrue(file_01.storage.id == storage.id)
        self.assertTrue(file_01.storage.save_type == 'file')
        self.assertTrue(file_01.save_type == 'file')
        self.assertTrue(file_02.storage.id == storage.id)
        self.assertTrue(file_02.storage.save_type == 'file')
        self.assertTrue(file_02.save_type == 'file')
        storage.write({'save_type': 'database'})
        storage.action_storage_migrate()
        self.assertTrue(file_01.storage.id == storage.id)
        self.assertTrue(file_01.storage.save_type == 'database')
        self.assertTrue(file_01.save_type == 'database')
        self.assertTrue(file_02.storage.id == storage.id)
        self.assertTrue(file_02.storage.save_type == 'database')
        self.assertTrue(file_02.save_type == 'database')
        
    