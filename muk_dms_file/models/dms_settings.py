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
import logging

from odoo import _
from odoo import models, api, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class SystemSettings(models.Model):
    
    _inherit = 'muk_dms.settings'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    save_type = fields.Selection(
        selection_add=[('file', "File System")])
    
    base_path = fields.Char(
        string="Path")
    
    complete_base_path = fields.Char(
        compute="_compute_complete_base_path",
        string="Path")
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('base_path')
    def _compute_complete_base_path(self):
        for record in self:
            if record.base_path:
                record.complete_base_path = os.path.join(record.base_path,self.env.cr.dbname)
            else:
                record.complete_base_path = None
    
    #----------------------------------------------------------
    # Create, Update
    #----------------------------------------------------------
           
    @api.constrains('base_path', 'save_type')
    def _check_base_path(self):
        if self.save_type == 'file':
            if not self.base_path:
                raise ValidationError(_("The save type (File System) requires a path attribute."))
            if not os.path.isdir(self.base_path):
                raise ValidationError(_("The given path does not exists."))
            if not os.access(self.base_path, os.W_OK):
                raise ValidationError(_("Odoo requires to have access rights for the given path."))
    
    @api.multi
    def _check_notification(self, vals, *largs, **kwargs):
        super(SystemSettings, self)._check_notification(vals, *largs, **kwargs)
        if 'base_path' in vals:
            self.suspend_security().notify_change({'base_path': vals['base_path']})
            
    #----------------------------------------------------------
    # File Synchronization
    #----------------------------------------------------------
    
    @api.model
    def _synchronize_filestore(self, force_delete=False):
        def report(info, paths):
            message = "%s\n" % info
            message += "The delete flag is set to '%s', " % file_delete
            message += "the files will %s be deleted." % ("" if file_delete else "not")
            if not file_delete:
                message += "\nChange the settings, if you want the files to be deleted."
            for path in paths:
                message += "\n - %s" % path
            return message
        params = self.env['ir.config_parameter'].sudo()
        if not self.user_has_groups("muk_dms.group_dms_admin"):
            raise AccessError(_("No permission to run this task."))
        file_delete = True if force_delete else params.get_param('muk_dms_file.delete_out_of_sync_files')
        settings = self.sudo().search([('save_type', '=', 'file')])
        data_files = settings.mapped('settings_files')
        system_file_paths = set()
        for base_path in settings.mapped('complete_base_path'):
            for path, subdirs, files in os.walk(base_path):
                for name in files:
                    system_file_paths.add(os.path.join(path, name))
        data_file_paths = set(file.reference._build_path() for file in data_files if file.reference)
        no_sync_data_file_paths = data_file_paths - system_file_paths
        no_sync_system_file_paths = system_file_paths - data_file_paths
        if no_sync_data_file_paths:
            info = "The following files exist in the ERP system, but not in the file system."
            _logger.warning(report(info, no_sync_data_file_paths))
            if file_delete:
                for file in data_files:
                    if file.reference and file.reference._build_path() in no_sync_data_file_paths:
                        file.unlink()
        if  no_sync_system_file_paths:
            info = "The following files exist in the file system, but not in the ERP system."
            _logger.warning(report(info, no_sync_system_file_paths))
            if file_delete:
                for path in no_sync_system_file_paths:
                    try:
                        os.remove(path)
                        os.removedirs(os.path.dirname(path))
                    except OSError as exc:
                        if exc.errno != errno.ENOTEMPTY:
                            _logger.exception("Failed to delete file!")
