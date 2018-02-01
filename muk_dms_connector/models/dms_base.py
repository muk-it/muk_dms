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
import string
import unicodedata
import hashlib
import logging

from odoo import _
from odoo import SUPERUSER_ID
from odoo import models, api, fields
from odoo.exceptions import ValidationError, AccessError, UserError

from odoo.addons.muk_dms.models import dms_base

_logger = logging.getLogger(__name__)
    
class ConnectorAccessModel(dms_base.DMSAbstractModel):
    
    _inherit = 'muk_dms.access'
    
    #----------------------------------------------------------
    # Function
    #----------------------------------------------------------
        
    @api.multi
    def _generate_dict_fields(self):
        fields = self._fields.keys()
        fields.remove('id')
        fields.append('.id')
        return fields
    
    @api.multi
    def generate_dict(self):
        result = []
        fields = self._generate_dict_fields()
        for record in self:
            export = record.export_data(fields)['datas'][0]
            data = dict(zip(fields, export))
            data['model'] = self._name
            result.append(data)
        return result