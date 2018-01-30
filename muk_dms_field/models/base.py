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

import re
import hashlib
import logging
import psycopg2

from odoo import _
from odoo import models, api, fields
from odoo.tools import ustr, pycompat, human_size

_logger = logging.getLogger(__name__)

unlink = models.BaseModel.unlink

def documents_unlink(self):
    files = []
    if 'muk_dms.file' in self.env:
        file = self.env['muk_dms.file'].sudo()
        fields = file.fields_get_keys()
        if 'reference_model' in fields and 'reference_id' in fields:
            files = file.search([
                ('reference_model', '=', self._name),
                ('reference_id', 'in', self.ids),
            ])
    unlink(self)
    if files:
        files.unlink()
    
models.BaseModel.unlink = documents_unlink