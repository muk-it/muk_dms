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
import logging

from odoo import _
from odoo import models, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.muk_dms.models import muk_dms_base as base
from odoo.addons.muk_dms.models import muk_dms_root as root

_logger = logging.getLogger(__name__)

"""Save Types"""
SAVE_SYSTEM = "file"

class FileRoot(base.DMSModel):
    _inherit = 'muk_dms.root'
        
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    entry_path = fields.Char(string="Path")
    
    #----------------------------------------------------------
    # Local
    #----------------------------------------------------------
    
    save_types = [(root.SAVE_DATABASE, _('Database')), (SAVE_SYSTEM, _('File System'))] 
    
    #----------------------------------------------------------
    # Create, Update
    #----------------------------------------------------------
    
    @api.one
    @api.constrains('entry_path', 'save_type')
    def _check_root_save_type(self):
        _logger.debug("Checking save_type constrains.")
        if self.save_type == SAVE_SYSTEM:
            if not self.entry_path:
                raise ValidationError(_("The save type (File) needs an entry path attribute."))
            if not os.path.isdir(self.entry_path):
                raise ValidationError(_("The given path does not exists."))
            if not os.access(self.entry_path, os.W_OK):
                raise ValidationError(_("MuK DMS needs to have access rights for the given path."))

    def _after_write(self, result, vals):
        result = super(FileRoot, self)._after_write(result, vals)
        if 'save_type' in vals:
            self.root_directory.notify_change(base.ROOT, vals['save_type'])
        return result