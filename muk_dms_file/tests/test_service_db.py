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

import io
import os
import logging
import unittest
import tempfile

from odoo import SUPERUSER_ID
from odoo.tests import common
from odoo.tools import config
from odoo.http import dispatch_rpc, db_list
from odoo.service.db import restore_db, dump_db

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

MASTER_PASSWORD = config['admin_passwd'] or "admin"

LOGIN = "admin"
PASSWORD = "admin"
    
class FileSericeDBCase(common.BaseCase):
    
    @unittest.skipIf(True, "Skipped to avoid side effects on the server.")
    def test_exp_database_rename_clone_delete(self):
        database = common.get_db_name()
        dispatch_rpc('db', 'create_database', [
            MASTER_PASSWORD, "muk_dms_file_create_db_test",
            False, "en", "admin", "admin"
        ])
        self.assertTrue('muk_dms_file_create_db_test' in db_list())
        dispatch_rpc('db', 'duplicate_database', [
            MASTER_PASSWORD, 'muk_dms_file_create_db_test',
            'muk_dms_file_duplicate_db_test'
        ])
        self.assertTrue('muk_dms_file_duplicate_db_test' in db_list())
        dispatch_rpc('db','drop', [MASTER_PASSWORD,  'muk_dms_file_duplicate_db_test'])
        dispatch_rpc('db','drop', [MASTER_PASSWORD, 'muk_dms_file_create_db_test'])
        self.assertTrue('muk_dms_file_create_db_test' not in db_list())
        self.assertTrue('muk_dms_file_duplicate_db_test' not in db_list())
    
    @unittest.skipIf(True, "Skipped to avoid side effects on the server.")
    def test_exp_database_backup_restore(self):
        dispatch_rpc('db', 'create_database', [
            MASTER_PASSWORD, "muk_dms_file_create_db_test",
            False, "en", "admin", "admin"
        ])
        self.assertTrue('muk_dms_file_create_db_test' in db_list())
        dump_stream = dump_db("muk_dms_file_create_db_test", None, 'zip')
        with tempfile.NamedTemporaryFile(delete=False) as data_file:
            data_file.write(dump_stream.read())
        restore_db('muk_dms_file_restore_db_test', data_file.name, True)
        self.assertTrue('muk_dms_file_restore_db_test' in db_list())
        dispatch_rpc('db','drop', [MASTER_PASSWORD, 'muk_dms_file_restore_db_test'])
        dispatch_rpc('db','drop', [MASTER_PASSWORD, 'muk_dms_file_create_db_test'])
        self.assertTrue('muk_dms_file_create_db_test' not in db_list())
        self.assertTrue('muk_dms_file_restore_db_test' not in db_list())