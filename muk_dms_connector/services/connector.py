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

from odoo.addons.muk_dms_connector.tools import utils

_logger = logging.getLogger(__name__)

class DocumentConnector(object):

    def _find(self, env, path, model):
        records = env[model].search([['path', '=', path]])
        records = records.check_existence()
        if records:
            return records.generate_dict()
        else:
            raise MissingError(_("The record is missing!"))
    
    def find(self, env, path, model=None):
        if model:
            return self._find(env, path, model)
        else:
            result = []
            try:
                result.append(self._find(env, path, 'muk_dms.directory'))
            except MissingError:
                pass
            try:
                result.append(self._find(env, path, 'muk_dms.file'))
            except MissingError:
                pass
            if result:
               return result
            else:
                raise MissingError(_("The record is missing!"))
    
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
                }
        else:
            raise MissingError(_("The record is missing!"))
    
    def mkdir(self, env, directory_id, name):
        directory_model = env['muk_dms.directory']
        return directory_model.create({
            'parent_directory': directory_id,
            'name': name}).generate_dict()
    
    def touch(self, env, directory_id, filename): 
        file_model = env['muk_dms.file']
        return file_model.create({
            'name': filename,
            'content': utils.empty_file_base64(),
            'directory': directory_id}).generate_dict()
    
    def rmdir(self, env, id):
        return env['muk_dms.directory'].browse([id]).unlink()
    
    def unlink(self, env, id):
        return env['muk_dms.file'].browse([id]).unlink()
    
    def rename(self, env, id, name, model='muk_dms.file'):
        record = env[model].browse([id])
        if record.check_existence():
            record.write({'name': name})
        else:
            raise MissingError(_("The record is missing!"))
    
    def lock(self, env, id): 
        return env['muk_dms.file'].user_lock()
    
    def release(self, env, id): 
        return env['muk_dms.file'].user_unlock()