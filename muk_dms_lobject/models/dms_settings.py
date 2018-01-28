# -*- coding: utf-8 -*-

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
import logging

from odoo import _
from odoo import models, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.muk_dms.models import dms_base

_logger = logging.getLogger(__name__)

class LargeObjectSettings(dms_base.DMSModel):
    
    _inherit = 'muk_dms.settings'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    save_type = fields.Selection(
        selection_add=[('lobject', "Large Object")])