###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Attachment 
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
import re
import base64
import hashlib
import itertools
import logging
import mimetypes
import textwrap

from collections import defaultdict

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import config, human_size, ustr, html_escape
from odoo.tools.mimetypes import guess_mimetype

_logger = logging.getLogger(__name__)

class DocumentIrAttachment(models.Model):
    
    _inherit = 'ir.attachment'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    store_document = fields.Many2one(
        comodel_name='muk_dms.file', 
        string="Document File",
        auto_join=False,
        index=True,
        copy=False)
    
    store_document_directory = fields.Many2one(
        related="store_document.directory",
        string="Document Directory",
        readonly=True)
    
    is_store_document_link = fields.Boolean(
        string="Is Document Link",
        default=False,
        help=textwrap.dedent("""\
            There are two possible ways in which a file and an attachment can be related.
            - True: The attachment is a link to a file. A file can have any number of links.
            - False: The attachment stores its contents in a file. This is a one to one relationship.
        """))
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------

    @api.model
    def _get_datas_inital_vals(self):
        vals = super(DocumentIrAttachment, self)._get_datas_inital_vals()
        vals.update({'store_document': False})
        return vals
    
    @api.model
    def _get_datas_clean_vals(self, attach):
        vals = super(DocumentIrAttachment, self)._get_datas_clean_vals(attach)
        if self._storage() != 'document' and attach.store_document:
            vals['store_document'] = attach.store_document
        return vals
    
    @api.model
    def _clean_datas_after_write(self, vals):
        super(DocumentIrAttachment, self)._clean_datas_after_write(vals)
        if 'store_document' in vals:
            vals['store_document'].unlink()
    
    @api.model
    def _get_attachment_directory(self, attach):
        params = self.env['ir.config_parameter'].sudo()
        attachment_directory_id = params.get_param(
            'muk_dms_attachment.attachment_directory', None
        )
        if attachment_directory_id:
            model = self.env['muk_dms.directory'].sudo()
            directory = model.browse(int(attachment_directory_id)) 
            if directory.exists():
                return directory
        raise ValidationError(_('A directory has to be defined.'))
    
    #----------------------------------------------------------
    # Function
    #----------------------------------------------------------
    
    @api.model
    def storage_locations(self):
        locations = super(DocumentIrAttachment, self).storage_locations()
        locations.append('document')
        return locations
    
    @api.model
    def force_storage(self):
        if not self.env.user._is_admin():
            raise AccessError(_('Only administrators can execute this action.'))
        if self._storage() != 'document':
            return super(DocumentIrAttachment, self).force_storage()
        else:
            storage_domain = {
                'document': ('store_document', '=', False),
            }
            record_domain = [
                '&', ('type', '=', 'binary'),
                '&', storage_domain[self._storage()], 
                '&', ('is_store_document_link', '=', False),
                '|', ('res_field', '=', False), ('res_field', '!=', False)
            ]
            self.search(record_domain).migrate(batch_size=100)
            return True
    
    def migrate(self, batch_size=None):
        if self._storage() != 'document':
            self.with_context(migration=True).write({
                'is_store_document_link': False
            })
        return super(DocumentIrAttachment, self).migrate(batch_size=batch_size)
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------

    def _compute_datas(self):
        for attach in self:
            if attach.store_document:
                attach.datas = attach.sudo().store_document.content
            else:
                super(DocumentIrAttachment, attach)._compute_datas()

    #----------------------------------------------------------
    # Constrains
    #----------------------------------------------------------

    @api.constrains('store_document', 'is_store_document_link')
    def _check_store_document(self):
        for attach in self:
            if attach.store_document and attach.store_document.id:
                attachments = attach.sudo().search([
                    '&', ('is_store_document_link', '=', False),
                    '&', ('store_document', '=', attach.store_document.id),
                    '|', ('res_field', '=', False), ('res_field', '!=', False)])
                if len(attachments) >= 2:
                    raise ValidationError(_('The file is already referenced by another attachment.'))
                
    @api.constrains('store_document', 'is_store_document_link')
    def _check_is_store_document_link(self):
        for attach in self:
            if attach.is_store_document_link and not attach.store_document:
                raise ValidationError(_('A linked attachments has to be linked to a file.'))
    
    #----------------------------------------------------------
    # Create, Write, Delete
    #----------------------------------------------------------
    
    def _inverse_datas(self):
        location = self._storage()
        for attach in self:
            if location == 'document':
                if attach.is_store_document_link:
                    raise ValidationError(_('The data of an attachment created by a file cannot be changed.'))
                value = attach.datas
                bin_data = base64.b64decode(value) if value else b''
                vals = self._get_datas_inital_vals()
                vals = self._update_datas_vals(vals, attach, bin_data)
                if value:
                    directory = self._get_attachment_directory(attach)
                    if attach.store_document:
                        attach.store_document.sudo().write({
                            'directory': directory and directory.id,
                            'content': value
                        })
                        store_document = attach.store_document
                    else: 
                        store_document = self.env['muk_dms.file'].sudo().create({
                            'name': "[A-%s] %s" % (attach.id, attach.name),
                            'directory': directory and directory.id,
                            'content': value
                        })
                    vals['store_document'] = store_document and store_document.id
                elif not value and attach.store_document:
                    attach.store_document.unlink()
                clean_vals = self._get_datas_clean_vals(attach)
                models.Model.write(attach.sudo(), vals)
                self._clean_datas_after_write(clean_vals)
            else:
                super(DocumentIrAttachment, attach)._inverse_datas()
    
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or [])
        if not 'store_document' in default and self.store_document:
            default.update({'store_document': False})
            file = self.store_document.sudo()
            copy = super(DocumentIrAttachment, self).copy(default)
            store_document = self.env['muk_dms.file'].sudo().create({
                'name': "[A-%s] %s" % (copy.id, copy.name),
                'directory': file.directory.id,
                'content': file.content})
            copy.write({'store_document': store_document.id})
            return copy
        else:
            return super(DocumentIrAttachment, self).copy(default)

    def write(self, vals):
        result = super(DocumentIrAttachment, self).write(vals)
        # if 'name' in vals and vals['name']:
        #     for attach in self:
        #         if attach.store_document and not attach.is_store_document_link:
        #             attach.store_document.sudo().write({
        #                 'name': "[A-%s] %s" % (attach.id, vals['name'])
        #             })
        return result

    def unlink(self):
        files = self.env['muk_dms.file']
        for attach in self.sudo():
            if attach.store_document and not attach.is_store_document_link:
                files |= attach.store_document
        result = super(DocumentIrAttachment, self).unlink()
        if files:
            files.sudo().unlink()
        return result