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

import os
import re
import json
import base64
import logging
import mimetypes

from openerp.tools.translate import _
from openerp import models, fields, api
from openerp.tools import ustr
from openerp.exceptions import ValidationError, AccessError


from openerp.addons.muk_dms.models import dms_base

_logger = logging.getLogger(__name__)

_img_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/src/img'))

class File(dms_base.DMSModel):
    _name = 'muk_dms.file'
    _description = "File"
    
    _inherit = 'muk_dms.access'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(
        string="Filename", 
        required=True)
    
    settings = fields.Many2one(
        'muk_dms.settings', 
        string="Settings",
        store=True,
        auto_join=True,
        ondelete='restrict', 
        compute='_compute_settings')
    
    content = fields.Binary(
        string='Content', 
        required=True,
        compute='_compute_content',
        inverse='_inverse_content')
    
    reference = fields.Reference(
        selection=[('muk_dms.data', _('Data'))],
        string="Data Reference", 
        readonly=True)
    
    directory = fields.Many2one(
        'muk_dms.directory', 
        string="Directory",
        ondelete='restrict',  
        auto_join=True,
        required=True)
    
    extension = fields.Char(
        string='Extension',
        compute='_compute_extension',
        readonly=True,
        store=True)
    
    mimetype = fields.Char(
        string='Type',
        compute='_compute_mimetype',
        readonly=True,
        store=True)
    
    size = fields.Integer(
        string='Size', 
        readonly=True)
    
    custom_thumbnail = fields.Binary(
        string="Custom Thumbnail")
    
    thumbnail = fields.Binary(
        compute='_compute_thumbnail',
        string="Thumbnail")
    
    path = fields.Char(
        string="Path",
        store=True,
        readonly=True,
        compute='_compute_path')
    
    relational_path = fields.Text(
        string="Path",
        store=True,
        readonly=True,
        compute='_compute_relational_path')
    
    index_content = fields.Text(
        string='Indexed Content',
        compute='_compute_index',
        readonly=True,
        store=True,
        prefetch=False)
    
    locked_by = fields.Reference(
        string='Locked by',
        related='locked.locked_by_ref')
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def notify_change(self, values, refresh=False, operation=None):
        super(File, self).notify_change(values, refresh, operation)
        if "index_files" in values:
            self._compute_index()
        if "save_type" in values:
            self._update_reference_type()
            
    
    def trigger_computation_up(self, fields):
        self.directory.trigger_computation(fields)
        
    def trigger_computation(self, fields, refresh=True, operation=None):
        super(File, self).trigger_computation(fields, refresh, operation)
        values = {}
        if "settings" in fields:
            values.update(self.with_context(operation=operation)._compute_settings(write=False)) 
        if "path" in fields:
            values.update(self.with_context(operation=operation)._compute_path(write=False)) 
            values.update(self.with_context(operation=operation)._compute_relational_path(write=False)) 
        if "extension" in fields:
            values.update(self.with_context(operation=operation)._compute_extension(write=False)) 
        if "mimetype" in fields:
            values.update(self.with_context(operation=operation)._compute_mimetype(write=False)) 
        if "index_content" in fields:
            values.update(self.with_context(operation=operation)._compute_index(write=False)) 
        if values:
            self.write(values);     
            if "settings" in fields:
                self.notify_change({'save_type': self.settings.save_type})
            
    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------
        
    def _compute_settings(self, write=True):
        if write:
            for record in self:
                record.settings = record.directory.settings   
        else:
            self.ensure_one()
            return {'settings': self.directory.settings.id}         
                 
    def _compute_extension(self, write=True):
        if write:
            for record in self:
                record.extension = os.path.splitext(record.name)[1]
        else:
            self.ensure_one()
            return {'extension': os.path.splitext(self.name)[1]}
                          
    def _compute_mimetype(self, write=True):
        def get_mimetype(record):
            mimetype = mimetypes.guess_type(record.name)[0]
            if (not mimetype or mimetype == 'application/octet-stream') and record.content:
                # mimetype = guess_mimetype(base64.b64decode(record.content))
                
                mimetype = mimetypes.guess_extension(base64.b64decode(record.content))
            return mimetype or 'application/octet-stream'
        if write:
            for record in self:
                record.mimetype = get_mimetype(record)
        else:
            self.ensure_one()
            return {'mimetype': get_mimetype(self)}   
                    
    def _compute_path(self, write=True):
        if write:
            for record in self:
                record.path = "%s%s" % (record.directory.path, record.name)   
        else:
            self.ensure_one()
            return {'path': "%s%s" % (self.directory.path, self.name)}   
            
    def _compute_relational_path(self, write=True):
        def get_relational_path(record):
            path = json.loads(record.directory.relational_path)
            path.append({
                'model': record._name,
                'id': record.id,
                'name': record.name})
            return json.dumps(path)  
        if write:
            for record in self:
                record.relational_path = get_relational_path(record)
        else:
            self.ensure_one()
            return {'relational_path': get_relational_path(self)}   
    
    def _compute_index(self, write=True):
        def get_index(record):
            type = record.mimetype.split('/')[0] if record.mimetype else record._compute_mimetype(write=False)['mimetype']  
            index_files = record.settings.index_files if record.settings else record.directory.settings.index_files
            if type and type.split('/')[0] == 'text' and record.content and index_files:
                words = re.findall("[^\x00-\x1F\x7F-\xFF]{4,}", base64.b64decode(record.content))
                return ustr("\n".join(words))
            else:
                return None   
        if write:
            for record in self:
                record.index_content = get_index(record)
        else:
            self.ensure_one()
            return {'index_content': get_index(self)}   
                    
    def _compute_content(self):
        for record in self:
            record.content = record._get_content()
            
    @api.depends('custom_thumbnail')
    def _compute_thumbnail(self):
        for record in self:
            if record.custom_thumbnail:
                record.thumbnail = record.with_context({}).custom_thumbnail        
            else:
                extension = record.extension and record.extension.strip(".") or ""
                path = os.path.join(_img_path, "file_%s.png" % extension)
                if not os.path.isfile(path):
                    path = os.path.join(_img_path, "file_unkown.png")
                with open(path, "rb") as image_file:
                    record.thumbnail = base64.b64encode(image_file.read())
            
    #----------------------------------------------------------
    # Create, Update, Delete
    #----------------------------------------------------------
    
    @api.constrains('name')
    def _check_name(self):
        if not self.check_name(self.name):
            raise ValidationError("The file name is invalid.")
        childs = self.directory.files.mapped(lambda rec: [rec.id, rec.name])
        duplicates = [rec for rec in childs if rec[1] == self.name and rec[0] != self.id]
        if duplicates:
            raise ValidationError("A file with the same name already exists.")
    
    def _after_create(self, vals):
        record = super(File, self)._after_create(vals)
        record._check_recomputation(vals)
        return record
        
    def _after_write_record(self, vals, operation):
        vals = super(File, self)._after_write_record(vals, operation)
        self._check_recomputation(vals, operation)
        return vals
    
    def _check_recomputation(self, values, operation=None):
        fields = []
        if 'name' in values:
            fields.extend(['extension', 'mimetype', 'path'])
        if 'directory' in values:
            fields.extend(['settings', 'path'])
        if 'content' in values:
            fields.extend(['index_content'])
        if fields:
            self.trigger_computation(fields)
        self._check_reference_values(values)
        if 'size' in values:
            self.trigger_computation_up(['size'])
                
    def _inverse_content(self):
        for record in self:
            if record.content:
                content = record.content
                directory = record.directory
                settings = record.settings if record.settings else directory.settings
                reference = record.reference
                if reference:
                    record._update_reference_content(content)
                else:
                    reference = record._create_reference(
                        settings, directory.path, record.name, content)
                record.reference = "%s,%s" % (reference._name, reference.id)
                record.size = len(base64.b64decode(content))
            else:
                record._unlink_reference()
                record.reference = None
    
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or [])
        names = self.directory.files.mapped('name')
        default.update({'name': self.unique_name(self.name, names, self.extension)})
        vals = self.copy_data(default)[0]
        if 'reference' in vals:
            del vals['reference']
        if not 'content' in vals:
            vals.update({'content': self.content})
        new = self.with_context(lang=None).create(vals)
        self.copy_translations(new)
        return new
    
    def _before_unlink_record(self):
        super(File, self)._before_unlink_record()
        self._unlink_reference()
                        
    #----------------------------------------------------------
    # Reference
    #----------------------------------------------------------
    
    def _create_reference(self, settings, path, filename, content):
        self.ensure_one()
        self.check_access('create', raise_exception=True)
        if settings.save_type == 'database':
            return self.env['muk_dms.data_database'].sudo().create({'data': content})
        return None
    
    def _update_reference_content(self, content):
        self.ensure_one()     
        self.check_access('write', raise_exception=True)
        self.reference.sudo().update({'content': content})
    
    def _update_reference_type(self):
        self.ensure_one()     
        self.check_access('write', raise_exception=True)
        if self.reference and self.settings.save_type != self.reference.type():
            reference = self._create_reference(self.settings, self.directory.path, self.name, self.content)
            self._unlink_reference()
            self.reference = "%s,%s" % (reference._name, reference.id)
    
    def _check_reference_values(self, values):
        self.ensure_one()
        self.check_access('write', raise_exception=True)
        if 'content' in values:
            self._update_reference_content(values['content'])
        if 'settings' in values:
            self._update_reference_type()
    
    def _get_content(self):
        self.ensure_one()
        self.check_access('read', raise_exception=True)
        return self.reference.sudo().content() if self.reference else None
    
    def _unlink_reference(self):
        self.ensure_one()
        self.check_access('unlink', raise_exception=True)
        if self.reference:
            self.reference.sudo().delete()
            self.reference.sudo().unlink()