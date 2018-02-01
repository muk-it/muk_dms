# -*- coding: utf-8 -*-

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

import logging

from odoo import _
from odoo.exceptions import AccessError, ValidationError, MissingError

from odoo.addons.muk_dms_connector.services import connector
from odoo.addons.muk_dms_connector.tools import utils

_logger = logging.getLogger(__name__)
    
class DocumentAccessConnector(connector.DocumentConnector):
    
    def access(self, env, id, model='muk_dms.file', operation=None):
        record = env[model].browse([id])
        if record.check_existence():
            if operation:
                return record.check_access(operation)
            else:
                return {
                    'read': record.check_access('read'),
                    'create': record.check_access('create'),
                    'write': record.check_access('write'),
                    'unlink': record.check_access('unlink'),
                    'access': record.check_access('access'),
                }
        else:
            raise MissingError(_("The record is missing!"))