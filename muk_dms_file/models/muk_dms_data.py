# -*- coding: utf-8 -*-

###################################################################################
# 
#    MuK Document Management System
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
from odoo.exceptions import ValidationError, AccessError, MissingError

from odoo.addons.muk_dms.models import muk_dms_data as data
from docutils.parsers.rst.directives import path

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

class SysFileDataModel(models.Model):
    _name = 'muk_dms.system_data'
    _description = 'System File Data Model'
    
    _inherit = 'muk_dms.data'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    filename = fields.Char(string="Filename")
    entry_path = fields.Char(string="Entry Path")
    path = fields.Char(string="Path")
    
    checksum = fields.Char(string="Checksum", readonly=True)
    
    #----------------------------------------------------------
    # Abstract Implementation
    #----------------------------------------------------------
    
    def get_type(self):
        return "File"
    
    def data(self):
        file_path = self.__build_path()
        return self.__read_file(file_path)
    
    def update(self, command, values):
        if str(command) is str(data.RENAME) and 'filename' in values:
            old_file_path = self.__build_path()
            new_file_path = self.__build_path(filename=values['filename'])
            self.__move_file(old_file_path, new_file_path)
            self.filename = values['filename']
        elif str(command) is str(data.REPLACE) and 'file' in values:
            file = base64.decodestring(values['file'])
            file_path = self.__build_path()
            self.__ensure_dir(file_path)
            self.checksum = self.__compute_checksum(file)
            self.__write_file(file_path, file)
        elif str(command) is str(data.MOVE):
            new_entry_path = None
            new_path = None
            if 'entry_path' in values:
                new_entry_path = values['entry_path']
            if 'path' in values:
                new_path = values['path']
            old_file_path = self.__build_path()
            new_file_path = self.__build_path(entry_path=new_entry_path, path=new_path)
            self.__ensure_dir(new_file_path)
            self.__move_file(old_file_path, new_file_path)
            self.__remove_empty_directories(old_file_path)
            if new_entry_path:
                self.entry_path = new_entry_path
            if new_path:
                self.path = new_path
    
    def delete(self):
        file_path = self.__build_path()
        self.__delete_file(file_path)
        self.__remove_empty_directories(file_path)
    
    #----------------------------------------------------------
    # File Helper
    #----------------------------------------------------------
    
    def __build_path(self, entry_path=None, path=None, filename=None):
        return os.path.join(entry_path or self.entry_path, path or self.path,
                            filename or self.filename).replace("\\", "/")

    def __ensure_dir(self, file_path):
        if not os.path.exists(os.path.dirname(file_path)):
            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as exc:
                if not (exc.errno == errno.EEXIST and os.path.isdir(path)):
                    _logger.error("Failed to create the necessary directories: " + str(exc))
                    raise AccessError(_("The System failed to create the necessary directories."))
    
    def __compute_checksum(self, file):
        return hashlib.sha1(file).hexdigest()
    
    def __check_file(self, file, checksum):
        return hashlib.sha1(file).hexdigest() == checksum
    
    def __delete_file(self, file_path):
        try:
            os.remove(file_path)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                _logger.error("Failed to delete the file: " + str(exc))
                raise AccessError(_("The System failed to delete the file."))
            
    def __remove_empty_directories(self, file_path):
        try:
            os.removedirs(os.path.dirname(file_path))
        except OSError as exc:
            if exc.errno != errno.ENOTEMPTY:
                _logger.error("Failed to remove empty directories: " + str(exc))
                raise AccessError(_("The System failed to delete a directory."))
            
    def __move_file(self, old_file_path, new_file_path):
        try:
            shutil.move(old_file_path, new_file_path)
        except IOError as exc:
            if exc.errno == errno.ENOENT:
                _logger.error("Failed to move the file: " + str(exc))
                raise MissingError(_("Something went wrong! Seems that the file is missing."))
            else:
                _logger.error("Failed to move the file: " + str(exc))
                raise AccessError(_("The System failed to rename the file."))
    
    def __read_file(self, file_path):
        with opened_w_error(file_path, "rb") as (file_handler, exc):
            if exc:
                _logger.error("Failed to read the file: " + str(exc))
                raise MissingError(_("Something went wrong! Seems that the file is missing."))
            else:
                file = file_handler.read()
                encode_file = base64.b64encode(file)
                if self.__check_file(file, self.checksum):
                    return encode_file
                else:
                    _logger.error("Failed to read the file: The file has been altered outside of the system.")
                    raise ValidationError(_("The file is corrupted."))
            
    def __write_file(self, file_path, file):
        with opened_w_error(file_path, "wb+") as (file_handler, exc):
            if exc:
                _logger.error("Failed to write the file: " + str(exc))
                raise AccessError(_("The System failed to write the file."))
            else:
                file_handler.write(file)
            
        