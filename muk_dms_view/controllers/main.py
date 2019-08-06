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

import base64
import logging

import werkzeug.utils
import werkzeug.wrappers

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

class DocumentController(http.Controller):

    @http.route('/dms/replace/file/<int:id>', type='http', auth="user")
    def replace(self, id, file, content_only=False, **kw):
        record = request.env['muk_dms.file'].browse([id])
        content = base64.b64encode(file.read())
        if file.filename == record.name or content_only:
            record.write({'content': content})
        else:
             record.write({
                'name': file.filename,
                'content': content})
        return werkzeug.wrappers.Response(status=200)
             
    @http.route('/dms/upload/file/<int:id>', type='http', auth="user")
    def upload(self, id, file, **kw):
        record = request.env['muk_dms.directory'].browse([id])
        content = base64.b64encode(file.read())
        request.env['muk_dms.file'].create({
            'name': file.filename,
            'directory': record.id,
            'content': content})
        return werkzeug.wrappers.Response(status=200)
