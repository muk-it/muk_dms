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

import os
import re
import json
import urllib
import base64
import logging
import mimetypes

from odoo import _
from odoo import models, api, fields
from odoo.exceptions import ValidationError, AccessError

from odoo.addons.muk_utils.tools import utils_os
from odoo.addons.muk_thumbnails.tools import thumbnail

_logger = logging.getLogger(__name__)

class ThumbnailFile(models.Model):
    
    _inherit = 'muk_dms.file'
              
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    is_user_thumbnail = fields.Boolean(
        string="User Thumbnail")
    
    failed_auto_thumbnail = fields.Boolean(
        string="Failed Thumbnail")
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    def notify_change(self, values, *largs, **kwargs):
        super(ThumbnailFile, self).notify_change(values, *largs, **kwargs)
        if 'protect_thumbnails' in values and not values['protect_thumbnails']:
            self.filtered(lambda rec: rec.is_user_thumbnail).write({
                'is_user_thumbnail': False,
                'failed_auto_thumbnail': False,
                'custom_thumbnail': False})
        if 'thumbnails' in values and values['thumbnails'] == 'immediate':
            self.filtered(lambda rec: (not rec.is_user_thumbnail or not rec.settings.protect_thumbnails) and (
                not rec.failed_auto_thumbnail and not rec.custom_thumbnail)).create_thumbnail()
    
    @api.model
    def no_thumbnail_extensions(self):
        params = self.env['ir.config_parameter'].sudo()
        no_thumbnail_extensions = params.get_param('muk_dms_thumbnails.no_thumbnail_extensions', default="")
        return [x.strip().strip(".") for x in no_thumbnail_extensions.split(',')]
                
    @api.multi
    def create_thumbnail(self):
        for record in self:
            content_base64 = record.with_context({}).content
            content_binary = content_base64 and base64.b64decode(content_base64) or None
            extension = utils_os.get_extension(content_binary, record.name, record.mimetype)
            if content_binary and extension in thumbnail.imports() and extension not in self.no_thumbnail_extensions():
                try:
                    image = thumbnail.create_thumbnail(record.name, content_binary, record.mimetype, "base64")
                    record.write({
                        'custom_thumbnail': image,
                        'is_user_thumbnail': False,
                        'failed_auto_thumbnail': False})
                except Exception:
                    _logger.exception("ASD")
                    record.write({
                        'custom_thumbnail': None,
                        'is_user_thumbnail': False,
                        'failed_auto_thumbnail': True})
            else:
                record.write({
                    'custom_thumbnail': None,
                    'is_user_thumbnail': False,
                    'failed_auto_thumbnail': True})
    
    #----------------------------------------------------------
    # View
    #----------------------------------------------------------
    
    @api.onchange('custom_thumbnail') 
    def _onchange_directory_type(self):
        if self.custom_thumbnail:
            self.is_user_thumbnail = True
        else:
            self.is_user_thumbnail = False
            
    #----------------------------------------------------------
    # Update
    #----------------------------------------------------------
            
    @api.multi
    def _after_write(self, result, vals, olds, *largs, **kwargs):
        if any(field in vals for field in ['content', 'name', 'settings']) and not 'custom_thumbnail' in vals:
            records = self.filtered(lambda rec: not rec.is_user_thumbnail or not rec.settings.protect_thumbnails)
            records.filtered(lambda rec: rec.settings.thumbnails == 'immediate').create_thumbnail()
            records.filtered(lambda rec: rec.settings.thumbnails == 'cron').write(
                {'custom_thumbnail': None, 'is_user_thumbnail': False, 'failed_auto_thumbnail': False})
        return super(ThumbnailFile, self)._after_write(result, vals, olds, *largs, **kwargs)
    
    #----------------------------------------------------------
    # Cron Job
    #----------------------------------------------------------
    
    @api.model
    def _generate_thumbnails(self):
        records = self.search([
            '&', ('settings.thumbnails', '=', 'cron'),
            '&', ('custom_thumbnail', '=', False),
            '&', ('failed_auto_thumbnail', '=', False),
            '|', ('settings.protect_thumbnails', '=', False),
            ('is_user_thumbnail', '=', False)])
        records.create_thumbnail()
        
     