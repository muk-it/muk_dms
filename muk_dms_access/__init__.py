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

import models

from odoo import api, SUPERUSER_ID

def _auto_default_group(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    access_groups = env['muk_dms_access.groups'].search([])
    
    if not access_groups.check_existence():
        settings = env['muk_dms.settings'].search([])
        category = env['ir.module.category'].search([['name', '=', 'Documents']], limit=1)
        group = env['res.groups'].search([['name', '=', 'User'], ['category_id', '=', category.id]], limit=1)
        access_group = access_groups.create({
            'name': "Default Group",
            'perm_read': True,
            'perm_create': True,
            'perm_write': True,
            'perm_unlink': True,
            'perm_access': False,
        })
        access_group.additional_users = group.users
        for setting in settings:
            for root in setting.root_directories:
                root.groups = access_group