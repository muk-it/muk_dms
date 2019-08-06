###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents View 
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

import logging

from odoo import _, http
from odoo.http import request

from odoo.addons.muk_utils.tools import file

_logger = logging.getLogger(__name__)

class BackendController(http.Controller):

    @http.route('/dms/view/tree/create/directory', type='json', auth="user")
    def create_directory(self, parent_directory, name=None, context=None, **kw):
        parent = request.env['muk_dms.directory'].sudo().browse(parent_directory)
        uname = file.unique_name(name or _("New Directory"), parent.child_directories.mapped('name'))
        directory = request.env['muk_dms.directory'].with_context(context or request.env.context).create({
            'name': uname,
            'parent_directory': parent_directory
        })
        return {
            'id': "directory_%s" % directory.id,
            'text': directory.name,
            'icon': "fa fa-folder-o",
            'type': "directory",
            'data': {
                'odoo_id': directory.id,
                'odoo_model': "muk_dms.directory",
                'odoo_record': {},
                'name': directory.name,
                'perm_read': directory.permission_read,
                'perm_create': directory.permission_create,
                'perm_write': directory.permission_write,
                'perm_unlink': directory.permission_unlink,
                'parent': "directory_%s" % parent_directory,
            },
            'children': False,
        }    