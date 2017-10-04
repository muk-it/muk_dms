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

import os
import errno
import shutil
import base64
import hashlib
import logging

from contextlib import contextmanager

from odoo import _
from odoo import models, api, fields
from odoo.tools import config, human_size, ustr, html_escape
from odoo.exceptions import ValidationError, AccessError, MissingError

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# Static Functions
#----------------------------------------------------------

@contextmanager
def opened_w_error(filename, mode="r"):
    try:
        f = open(filename, mode)
    except IOError, err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()

class SystemFileDataModel(models.Model):
    _name = 'muk_dms.data_system'
    _description = 'System File Data Model'
    
    _inherit = 'muk_dms.data'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    base_path = fields.Char(
        string="Base Path")
    
    dms_path = fields.Char(
        string="Document Path")
    
    checksum = fields.Char(
        string="Checksum",
        readonly=True)
    
    #----------------------------------------------------------
    # Abstract Implementation
    #----------------------------------------------------------
    
    def type(self):
        return "file"
    
    def content(self):
        if self.env.context.get('bin_size'):
            file_path = self._build_path()
            return human_size(self._read_size(file_path))
        else:
            file_path = self._build_path()
            return self._read_file(file_path)
    
    def update(self, values):
        if 'content' in values:
            file = base64.decodestring(values['content'])
            file_path = self._build_path()
            self._ensure_dir(file_path)
            self.checksum = self._compute_checksum(file)
            self._write_file(file_path, file)
        elif 'base_path' in values:
            old_file_path = self._build_path()
            new_file_path = self._build_path(base_path=values['base_path'], dms_path=self.dms_path)
            self._ensure_dir(new_file_path)
            self._move_file(old_file_path, new_file_path)
            self._remove_empty_directories(old_file_path)
            self.base_path = values['base_path']
        elif 'dms_path' in values:
            old_file_path = self._build_path()
            new_file_path = self._build_path(base_path=self.base_path, dms_path=values['dms_path'])
            self._ensure_dir(new_file_path)
            self._move_file(old_file_path, new_file_path)
            self._remove_empty_directories(old_file_path)
            self.dms_path = values['dms_path']
    
    def delete(self):
        file_path = self._build_path()
        self._delete_file(file_path)
        self._remove_empty_directories(file_path)
    
    def update_checksum(self):
        for record in self:
            file_path = record._build_path()
            with opened_w_error(file_path, "rb") as (file_handler, exc):
                if exc:
                    _logger.error("Failed to read the file: " + str(exc))
                    raise MissingError(_("Something went wrong! Seems that the file is missing."))
                else:
                    file = file_handler.read()
                    record.checksum = record._compute_checksum(file)
    
    #----------------------------------------------------------
    # File Helper
    #----------------------------------------------------------
    
    def _build_path(self, base_path=None, dms_path=None):
        base_path = (base_path or self.base_path)
        dms_path = (dms_path or self.dms_path)
        return os.path.normpath(base_path + dms_path)

    def _ensure_dir(self, file_path):
        if not os.path.exists(os.path.dirname(file_path)):
            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as exc:
                if not (exc.errno == errno.EEXIST and os.path.isdir(path)):
                    _logger.error("Failed to create the necessary directories: " + str(exc))
                    raise AccessError(_("The System failed to create the necessary directories."))
    
    def _compute_checksum(self, file):
        return hashlib.sha1(file).hexdigest()
    
    def _check_file(self, file, checksum):
        return hashlib.sha1(file).hexdigest() == checksum
    
    def _delete_file(self, file_path):
        try:
            os.remove(file_path)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                _logger.error("Failed to delete the file: " + str(exc))
                raise AccessError(_("The System failed to delete the file."))
            
    def _remove_empty_directories(self, file_path):
        try:
            os.removedirs(os.path.dirname(file_path))
        except OSError as exc:
            if exc.errno != errno.ENOTEMPTY:
                _logger.error("Failed to remove empty directories: " + str(exc))
                raise AccessError(_("The System failed to delete a directory."))
            
    def _move_file(self, old_file_path, new_file_path):
        try:
            shutil.move(old_file_path, new_file_path)
        except IOError as exc:
            if exc.errno == errno.ENOENT:
                _logger.error("Failed to move the file: " + str(exc))
                raise MissingError(_("Something went wrong! Seems that the file is missing."))
            else:
                _logger.error("Failed to move the file: " + str(exc))
                raise AccessError(_("The System failed to rename the file."))
    
    def _read_file(self, file_path):
        with opened_w_error(file_path, "rb") as (file_handler, exc):
            if exc:
                _logger.error("Failed to read the file: " + str(exc))
                raise MissingError(_("Something went wrong! Seems that the file is missing."))
            else:
                file = file_handler.read()
                encode_file = base64.b64encode(file)
                if self._check_file(file, self.checksum):
                    return encode_file
                else:
                    _logger.error("Failed to read the file: The file has been altered outside of the system.")
                    raise ValidationError(_("The file is corrupted."))
                
    def _read_size(self, file_path):
        return os.path.getsize(file_path)
            
    def _write_file(self, file_path, file):
        with opened_w_error(file_path, "wb+") as (file_handler, exc):
            if exc:
                _logger.error("Failed to write the file: " + str(exc))
                raise AccessError(_("The System failed to write the file."))
            else:
                file_handler.write(file)
            
        