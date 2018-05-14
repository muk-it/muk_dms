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

from openerp.tools.translate import _
from openerp import models, fields, api
from openerp.exceptions import ValidationError, AccessError


from openerp.addons.muk_dms.models import dms_base

_logger = logging.getLogger(__name__)

class Settings(dms_base.DMSModel):
    _name = 'muk_dms.settings'
    _description = "MuK Documents Settings"

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(
        string="Name", 
        required=True)
    
    save_type = fields.Selection(
        selection=[("database", _('Database'))] , 
        string="Save Type", 
        default="database", 
        required=True,
        help="The save type is used to determine how a file is saved to the system.")
    
    index_files = fields.Boolean(
        string="Index Files", 
        default=True,
        help="Indicates if the file data should be indexed to allow faster and better search results.")
    
    system_locks = fields.Boolean(
        string="System Locks", 
        default=True,
        help="Indicates if files and directories should be automatically locked while system operations take place.")
    
    root_directories = fields.One2many(
        'muk_dms.directory', 
        'settings',
         string="Directories",
         copy=False, 
         readonly=True)
        
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def notify_change(self, values, refresh=False, operation=None):
        super(Settings, self).notify_change(values, refresh, operation)
        if self.system_locks:
                self.root_directories.lock_tree(operation=operation)
        for directory in self.root_directories:
            directory.notify_change(values)
        self.root_directories.lock_tree(operation=operation)
        
    #----------------------------------------------------------
    # Create, Update
    #----------------------------------------------------------
           
    @api.onchange('save_type', 'index_files') 
    def _onchange_save_type(self):
        if self._origin.id:
            warning = {
                'title': (_('Information')),
                'message': (_('Changing the settings can cause a heavy migration process.'))
            }
            return {'warning': warning} 
        
    def _after_write_record(self, vals, operation):
        vals = super(Settings, self)._after_write_record(vals, operation)
        self._check_notification(vals, operation)
        return vals
    
    def _check_notification(self, values, operation):
        if 'save_type' in values:
            self.notify_change({'save_type': values['save_type']}, operation=operation)
        if 'index_files' in values:
            self.notify_change({'index_files': values['index_files']}, operation=operation)