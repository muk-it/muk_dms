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
import re
import json
import urllib
import base64
import logging
import mimetypes

from odoo import _
from odoo import models, api, fields
from odoo.tools import ustr
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)

class SystemFile(models.Model):
    
    _inherit = 'muk_dms.file'
              
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    def notify_change(self, values, *largs, **kwargs):
        super(SystemFile, self).notify_change(values, *largs, **kwargs)
        if "base_path" in values:
            self._check_reference_values({'base_path': values['base_path']})         
    
    #----------------------------------------------------------
    # Reference
    #----------------------------------------------------------
    
    @api.multi
    def _create_reference(self, settings, path, filename, content):
        result = super(SystemFile, self)._create_reference(settings, path, filename, content)
        if result:
            return result
        if settings.read(['save_type', 'base_path']) and settings.save_type == 'file':
            reference = self.env['muk_dms.data_system'].sudo().create(
                {'base_path': settings.base_path,
                 'dms_path': os.path.join(path, filename)})
            reference.sudo().update({'content': content})
            return reference
        _logger.info("NOT SAVED: %s, %s" % (settings.read(['save_type', 'base_path']), settings.save_type))
        return None

    @api.multi
    def _check_reference_values(self, values):
        super(SystemFile, self)._check_reference_values(values)
        if 'path' in values:
            self._update_reference_values({'dms_path': values['path']})
        if "base_path" in values:
            self._update_reference_values({'base_path': values['base_path']})
