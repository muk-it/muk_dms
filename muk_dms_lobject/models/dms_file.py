###################################################################################
# 
#    Copyright (C) 2018 MuK IT GmbH
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

class LargeObjectFile(models.Model):
    
    _inherit = 'muk_dms.file'      
             
    #----------------------------------------------------------
    # Reference
    #----------------------------------------------------------
    
    @api.multi
    def _create_reference(self, settings, path, filename, content):
        result = super(LargeObjectFile, self)._create_reference(settings, path, filename, content)
        if result:
            return result
        if settings.save_type == 'lobject':
            return self.env['muk_dms.data_lobject'].sudo().create({'data': content})
        return None