###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents File 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import os
import logging

from odoo import models, api, fields, tools
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

class Storage(models.Model):
    
    _inherit = 'muk_dms.storage'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    save_type = fields.Selection(
        selection_add=[('file', "Filestore")])
    
    #----------------------------------------------------------
    # Actions
    #----------------------------------------------------------
    
    @api.multi
    def action_storage_migrate(self):
        if not self.env.user.has_group('muk_dms.group_dms_manager'):
            raise AccessError(_('Only managers can execute this action.'))
        records = self.filtered(lambda rec: rec.save_type == 'file')
        files = self.env['muk_dms.file'].with_context(active_test=False).sudo()
        for record in records:
            domain = ['&', ('content_file', '=', False), ('storage', '=', record.id)]
            files |= files.search(domain)
        files.action_migrate()
        super(Storage, self - records).action_storage_migrate()
