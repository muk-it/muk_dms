###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Chatter 
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

from odoo.tools import mute_logger
from odoo.exceptions import AccessError, ValidationError

from odoo.addons.muk_utils.tests.common import multi_users
from odoo.addons.muk_dms.tests.common import setup_data_function
from odoo.addons.muk_dms.tests.test_directory import DirectoryTestCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class DirectoryActionTestCase(DirectoryTestCase):
    
    def setUp(self):
        super(DirectoryActionTestCase, self).setUp()
        self.params = self.env['ir.config_parameter'].sudo()
        self.params.set_param("mail.catchall.domain", "mydomain.com")
    
    @mute_logger('odoo.addons.mail.mail_thread')
    @setup_data_function(setup_func='_setup_test_data')
    def test_mail_alias_files(self):
        self.create_directory(storage=self.new_storage).write({
            'alias_process': 'files', 'alias_name': 'directory+test'
        })
        with open(os.path.join(_path, 'tests', 'data', 'mail01.eml'), 'r') as file:
            self.env['mail.thread'].message_process(None, file.read())
        with open(os.path.join(_path, 'tests', 'data', 'mail02.eml'), 'r') as file:
            self.env['mail.thread'].message_process(None, file.read())
            
    @mute_logger('odoo.addons.mail.mail_thread')
    @setup_data_function(setup_func='_setup_test_data')
    def test_mail_alias_directory(self):
        self.create_directory(storage=self.new_storage).write({
            'alias_process': 'directory', 'alias_name': 'directory+test'
        })
        with open(os.path.join(_path, 'tests', 'data', 'mail01.eml'), 'r') as file:
            self.env['mail.thread'].message_process(None, file.read())
        with open(os.path.join(_path, 'tests', 'data', 'mail02.eml'), 'r') as file:
            self.env['mail.thread'].message_process(None, file.read())
    