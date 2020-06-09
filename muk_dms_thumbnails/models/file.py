###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Thumbnails 
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

import io
import re
import base64
import PyPDF2
import logging
import functools
import collections

from collections import defaultdict

from odoo import models, api, fields, tools
from werkzeug._internal import _log

from odoo.addons.muk_utils.tools import image

_logger = logging.getLogger(__name__)

class File(models.Model):
    
    _inherit = 'muk_dms.file'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    automatic_thumbnail = fields.Binary(
        string="Automatic Thumbnail", 
        attachment=False,
        prefetch=False,
        readonly=True)
     
    automatic_thumbnail_medium = fields.Binary(
        string="Medium Automatic Thumbnail",
        attachment=False,
        prefetch=False,
        readonly=True)
     
    automatic_thumbnail_small = fields.Binary(
        string="Small Automatic Thumbnail",
        attachment=False,
        prefetch=False,
        readonly=True)
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    @api.model
    def _resize_thumbnail(self, a_image, crop=True):
        data = image.crop_image(a_image, type='center', size=(256, 256), ratio=(1, 1)) if crop else a_image
        return image.image_resize_image(base64_source=data, size=(256, 256), encoding='base64')
    
    @api.model
    def _make_thumbnail(self, file):
        if re.match('image.*(gif|jpeg|jpg|png)', file.mimetype):    
            return self._resize_thumbnail(file.content, crop=True)
        return None

    def _update_automatic_thumbnail(self):
        updates = defaultdict(set)
        for record in self:
            try:
                thumbnail = self._make_thumbnail(record)
            except Exception:
                message = "Thumnail creation failed for file %s with ID %s."
                _logger.exception(message % (record.name, record.id))
                thumbnail = None
            if thumbnail:
                values = {
                    'automatic_thumbnail': thumbnail
                }
                image.image_resize_images(values, 
                    big_name='automatic_thumbnail',
                    medium_name='automatic_thumbnail_medium', 
                    small_name='automatic_thumbnail_small'
                )
                updates[tools.frozendict(values)].add(record.id)
        with self.env.norecompute():
            for vals, ids in updates.items():
                self.browse(ids).write(dict(vals))
        
    #----------------------------------------------------------
    # Read 
    #----------------------------------------------------------
    
    @api.depends('automatic_thumbnail')
    def _compute_thumbnail(self):
        records = self.with_context({'bin_size': True}).filtered(
            lambda rec: bool(rec.automatic_thumbnail) and \
                not bool(rec.custom_thumbnail)
        )
        for record in records.with_context(self.env.context):
            record.thumbnail = record.automatic_thumbnail        
        super(File, self - records)._compute_thumbnail()
      
    @api.depends('automatic_thumbnail_medium')
    def _compute_thumbnail_medium(self):
        records = self.with_context({'bin_size': True}).filtered(
            lambda rec: bool(rec.automatic_thumbnail_medium) and \
                not bool(rec.custom_thumbnail_medium)
        )
        for record in records.with_context(self.env.context):
            record.thumbnail_medium = record.automatic_thumbnail_medium       
        super(File, self - records)._compute_thumbnail_medium()
      
    @api.depends('automatic_thumbnail_small')
    def _compute_thumbnail_small(self):
        records = self.with_context({'bin_size': True}).filtered(
            lambda rec: bool(rec.automatic_thumbnail_small) and \
                not bool(rec.custom_thumbnail_small)
        )
        for record in records.with_context(self.env.context):
            record.thumbnail_small = record.automatic_thumbnail_small       
        super(File, self - records)._compute_thumbnail_small()

    #----------------------------------------------------------
    # Create, Update, Delete
    #----------------------------------------------------------
    
    @api.model_create_multi
    def create(self, vals_list):
        res =  super(File, self).create(vals_list)
        records_automatic_thumbnail = res.filtered(
            lambda rec: rec.storage.thumbnails == 'immediate'
        )
        records_automatic_thumbnail._update_automatic_thumbnail()
        return res
        
    def write(self, vals):
        if vals.get('content'):
            vals.update({
                'automatic_thumbnail': None,
                'automatic_thumbnail_medium': None,
                'automatic_thumbnail_small': None,
            })
        res = super(File, self).write(vals)
        if vals.get('content'):
            records_automatic_thumbnail = self.filtered(
                lambda rec: rec.storage.thumbnails == 'immediate'
            )
            records_automatic_thumbnail._update_automatic_thumbnail()
        return res
    
    #----------------------------------------------------------
    # Cron Job
    #----------------------------------------------------------
        
    @api.model
    def _generate_thumbnails(self):
        limit = self.env['ir.config_parameter'].sudo().get_param(
            'muk_dms_thumbnails.automatic_thumbnail_cron_limit', 100
        )
        self.search([
            ('automatic_thumbnail', '=',  False), 
            ('storage.thumbnails', '=',  'cron')
        ], limit=limit)._update_automatic_thumbnail()