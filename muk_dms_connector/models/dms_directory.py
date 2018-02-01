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

from odoo import _
from odoo import models, api, fields

from odoo.addons.muk_dms.models import dms_base

_logger = logging.getLogger(__name__)

class ConnectorDirectory(dms_base.DMSModel):
    
    _inherit = 'muk_dms.directory'
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
        
    @api.multi
    def _generate_dict_fields(self):
        fields = super(ConnectorDirectory, self)._generate_dict_fields()
        if 'thumbnail' in fields: 
            fields.remove('thumbnail')
        if 'custom_thumbnail' in fields: 
            fields.remove('custom_thumbnail')
        return fields