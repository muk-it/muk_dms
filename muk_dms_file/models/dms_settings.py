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
import logging

from odoo import _
from odoo import models, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.muk_dms.models import dms_base

_logger = logging.getLogger(__name__)

class SystemSettings(dms_base.DMSModel):
    _inherit = 'muk_dms.settings'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    save_type = fields.Selection(
        selection_add=[('file', "File System")])
    
    base_path = fields.Char(
        string="Path")
        
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
            
    def _check_notification(self, values, operation):
        super(SystemSettings, self)._check_notification(values, operation)
        if 'base_path' in values:
            self.notify_change({'base_path': values['base_path']}, operation=operation)