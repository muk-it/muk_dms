###################################################################################
# 
#    MuK Document Management System
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

from odoo import api, SUPERUSER_ID
from odoo.tools import config

from . import models

def _install_force_storage(cr, registry):
    if config.get("auto_storage_migration", False):
        if not config.get("dms_attachment_directory", False):
            raise ValueError("Storage Migration needs a default Directory.")
        env = api.Environment(cr, SUPERUSER_ID, {})
        params = env['ir.config_parameter'].sudo()
        param.set_param(
            'muk_dms_attachment.attachment_directory',
            config.get("dms_attachment_directory")
        )
        params.set_param('ir_attachment.location', 'document')
        attachment = env['ir.attachment'].sudo().force_storage()
    
def _uninstall_force_storage(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    params = env['ir.config_parameter'].sudo()
    location = params.get_param('ir_attachment.location')
    if location == 'document':
        params.set_param('ir_attachment.location', 'file')
        attachment = env['ir.attachment'].sudo().force_storage()
