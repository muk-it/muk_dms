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

import logging

from openerp import _
from openerp import models, api, fields
from openerp.exceptions import ValidationError

from openerp.addons.muk_dms.models import muk_dms_base as base

_logger = logging.getLogger(__name__)

class FileDirectory(base.DMSModel):
    _inherit = 'muk_dms.directory'
    
    def _follow_operation(self, values):
        super(FileDirectory, self)._follow_operation(values)
        self.notify_change_subtree(base.PATH, {})