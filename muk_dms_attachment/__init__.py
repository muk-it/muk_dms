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

from . import models

from odoo import api, SUPERUSER_ID

def _uninstall_force_storage(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    config = env['ir.config_parameter']
    config.sudo().set_param('ir_attachment.location', 'file')
    attachment = env['ir.attachment']
    attachment.sudo().force_clean()
    attachment.sudo().force_storage()