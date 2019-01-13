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
import uuid
import base64
import logging
import functools

from odoo import SUPERUSER_ID
from odoo.tests import common

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# Decorators
#----------------------------------------------------------

def setup_data_function(setup_func='_setup_test_data'):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            getattr(self, setup_func)()
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

#----------------------------------------------------------
# Test Cases
#----------------------------------------------------------

class DocumentsBaseCase(common.TransactionCase):
    
    def setUp(self):
        super(DocumentsBaseCase, self).setUp()
        self.super_uid = SUPERUSER_ID
        self.admin_uid = self.browse_ref("base.user_admin").id
        self.demo_uid = self.browse_ref("base.user_demo").id
        
    def _setup_test_data(self):
        self.storage = self.env['muk_dms.storage']
        self.directory = self.env['muk_dms.directory']
        self.file = self.env['muk_dms.file']
    
    def multi_users(self, super=True, admin=True, demo=True):
        return [[self.super_uid, super], [self.admin_uid, admin], [self.demo_uid, demo]]
    
    def content_base64(self):
        return base64.b64encode(b"\xff data")
        
    def create_storage(self, save_type="database", sudo=True):
        model = self.storage.sudo() if sudo else self.storage
        return model.create({
            'name': "Test Storage",
            'save_type': save_type,
        })
            
    def create_directory(self, storage=False, directory=False, sudo=True):
        model = self.directory.sudo() if sudo else self.directory
        if not storage and not directory:
            storage = self.create_storage()
        if directory:
            return model.create({
                'name': uuid.uuid4().hex,
                'is_root_directory': False,
                'parent_directory': directory.id,
            })
        return model.create({
            'name': uuid.uuid4().hex,
            'is_root_directory': True,
            'root_storage': storage.id,
        }) 
        
    def create_file(self, directory=False, content=False, sudo=True):
        model = self.file.sudo() if sudo else self.file
        if not directory:
            directory = self.create_directory()
        return model.create({
            'name': uuid.uuid4().hex,
            'directory': directory.id,
            'content': content or self.content_base64(),
        }) 