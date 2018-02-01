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

import json
import inspect
import logging

from odoo import http
from odoo.http import request
from odoo.http import Response

from odoo.addons.muk_dms_connector.services import connector

_logger = logging.getLogger(__name__)

class WebConnector(http.Controller):
    
    def __init__(self):
        super(WebConnector, self).__init__()
        self.connection = connector.DocumentConnector()    