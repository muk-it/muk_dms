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
    except IOError as err:
        yield None, err
    except UnicodeDecodeError as err:
        yield None, err
    except UnicodeEncodeError as err:
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
    
    complete_base_path = fields.Char(
        compute="_compute_complete_base_path",
        string="Path")
    
    dms_path = fields.Char(
        string="Document Path")
    
    checksum = fields.Char(
        string="Checksum",
        readonly=True)
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('base_path')
    def _compute_complete_base_path(self):
        for record in self:
            if record.base_path:
                record.complete_base_path = os.path.join(record.base_path, self.env.cr.dbname)
            else:
                record.complete_base_path = None
    
    #----------------------------------------------------------
    # Abstract Implementation
    #----------------------------------------------------------
    
    @api.model
    def type(self):
        return "file"
    
    @api.multi
    def content(self):
        self.ensure_one()
        file_path = self._build_path()
        if self.env.context.get('bin_size'):
            return human_size(self._read_size(file_path))
        else:
            return self._read_file(file_path)
    
    @api.multi
    def update(self, values):
        for record in self:
            if 'content' in values:
                file = base64.b64decode(values['content'])
                file_path = record._build_path()
                record._ensure_dir(file_path)
                record.checksum = record._compute_checksum(file)
                record._write_file(file_path, file)
            if 'base_path' in values:
                old_file_path = record._build_path()
                new_file_path = record._build_path(
                    base_path=values['base_path'],
                    dms_path=record.dms_path)
                record._ensure_dir(new_file_path)
                record._move_file(old_file_path, new_file_path)
                record._remove_empty_directories(old_file_path)
                record.base_path = values['base_path']
            if 'dms_path' in values:
                old_file_path = record._build_path()
                new_file_path = record._build_path(
                    base_path=record.base_path, 
                    dms_path=values['dms_path'])
                record._ensure_dir(new_file_path)
                record._move_file(old_file_path, new_file_path)
                record._remove_empty_directories(old_file_path)
                record.dms_path = values['dms_path']
    
    @api.multi
    def update_checksum(self):
        missing = []
        for record in self:
            file_path = record._build_path()
            with opened_w_error(file_path, "rb") as (file_handler, exception):
                if exception:
                    missing.append(file_path)
                    _logger.error("Failed to read the file (%s): %s" % (file_path, str(exception)))
                else:
                    file = file_handler.read()
                    record.checksum = record._compute_checksum(file)
        if missing:
            message = _("Something went wrong! Seems that some files are missing.\n")
            for path in missing:
                message += "\n - %s" % path
            raise MissingError(message)
    
    
    @api.multi
    def unlink(self):
        paths = [record._build_path() for record in self]
        super(SystemFileDataModel, self).unlink()
        for path in paths:
            self._delete_file(path)
            self._remove_empty_directories(path)
    
    #----------------------------------------------------------
    # File Helper
    #----------------------------------------------------------
    
    @api.model
    def _build_path(self, base_path=None, dms_path=None):
        base_path = base_path and os.path.join(base_path, self.env.cr.dbname) or self.complete_base_path
        dms_path = dms_path or self.dms_path
        return os.path.normpath("%s%s" % (base_path, dms_path))

    @api.model
    def _ensure_dir(self, file_path):
        if not os.path.exists(os.path.dirname(file_path)):
            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as exc:
                if not (exc.errno == errno.EEXIST and os.path.isdir(path)):
                    _logger.exception("Failed to create the necessary directories!")
                    raise AccessError(_("The System failed to create the necessary directories."))
    
    @api.model
    def _compute_checksum(self, file):
        return hashlib.sha1(file).hexdigest()
    
    @api.model
    def _check_file(self, file, checksum):
        return hashlib.sha1(file).hexdigest() == checksum
    
    @api.model
    def _read_file(self, file_path):
        with opened_w_error(file_path, "rb") as (file_handler, exception):
            if exception:
                _logger.error("Failed to read the file (%s): %s" % (file_path, str(exception)))
                raise MissingError(
                    _("Something went wrong! Seems that the file (%s) is missing or broken.") %
                    os.path.basename(file_path))
            else:
                file = file_handler.read()
                encode_file = base64.b64encode(file)
                if self._check_file(file, self.checksum):
                    return encode_file
                else:
                    _logger.error(
                        "Failed to read the file (%s): The file has been altered outside of the system." %
                        os.path.basename(file_path))
                    raise ValidationError(_("The file (%s) is corrupted.") % os.path.basename(file_path))
              
    @api.model            
    def _read_size(self, file_path):
        try:
            return os.path.getsize(file_path)
        except OSError as exc:
            _logger.error("Failed to read the file (%s): %s" % (file_path, str(exc)))
            raise MissingError(
                _("Something went wrong! Seems that the file (%s) is missing or broken.") %
                os.path.basename(file_path))
        
    @api.model
    def _write_file(self, file_path, file):
        with opened_w_error(file_path, "wb+") as (file_handler, exception):
            if exception:
                _logger.error("Failed to write the file(%s): %s" % (file_path, str(exception)))
                raise AccessError(_("The System failed to write the file (%s).") % os.path.basename(file_path))
            else:
                file_handler.write(file)  
    
    @api.model
    def _move_file(self, old_file_path, new_file_path):
        try:
            shutil.move(old_file_path, new_file_path)
        except IOError as exc:
            _logger.error("Failed to move the file(%s): %s" % (old_file_path, str(exc)))
            if exc.errno == errno.ENOENT:
                raise MissingError(
                _("Something went wrong! Seems that the file (%s) is missing or broken.") %
                os.path.basename(old_file_path))
            else:
                raise AccessError(_("The System failed to rename the file(%s).") % os.path.basename(old_file_path))
    
    @api.model
    def _delete_file(self, file_path):
        try:
            os.remove(file_path.encode("utf-8"))
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                _logger.error("Failed to delete the file(%s): %s" % (file_path, str(exc)))
                raise AccessError(_("The System failed to delete the file (%s).") % os.path.basename(old_file_path))
    
    @api.model
    def _remove_empty_directories(self, file_path):
        try:
            os.removedirs(os.path.dirname(file_path))
        except OSError as exc:
            if not (exc.errno == errno.ENOTEMPTY or exc.errno == errno.ENOENT):
                _logger.error("Failed to remove empty directories: " + str(exc))
                raise AccessError(_("The System failed to delete a directory."))
