###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Chatter 
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
import textwrap

from odoo import _, models, api, fields

from odoo.addons.muk_utils.tools.file import slugify
from odoo.addons.muk_utils.tools.file import unique_name

_logger = logging.getLogger(__name__)

class Directory(models.Model):
    
    _name = 'muk_dms.directory'

    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'mail.alias.mixin',
        'muk_dms.directory',
    ]
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    alias_process = fields.Selection(
        selection=[
            ('files', 'Single Files'),
            ('directory', 'Subdirectory')
        ], 
        required=True,
        default='directory',
        string='Unpack Emails as', 
        help=textwrap.dedent("""\
            Define how incoming emails are processed:
            - Single Files: The email gets attached to the directory and all attachments are created as files.
            - Subdirectory: A new subdirectory is created for each email and the mail is attached to this \
                            subdirectory. The attachments are created as files of the subdirectory.
            """))
    
    #----------------------------------------------------------
    # Mail Alias
    #----------------------------------------------------------
    
    @api.model
    def get_alias_model_name(self, vals):
        return vals.get('alias_model', 'muk_dms.directory') 
    
    @api.multi
    def get_alias_values(self):
        values = super(Directory, self).get_alias_values()
        values['alias_defaults'] = {'parent_directory': self.id}
        return values
    
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        custom_values = custom_values if custom_values is not None else {}
        parent_directory_id = custom_values.get('parent_directory', None)
        parent_directory = self.sudo().browse(parent_directory_id)
        if not parent_directory_id or not parent_directory.exists():
            raise ValueError("No directory could be found!")
        if parent_directory.alias_process == "files":
            parent_directory._process_message(msg_dict)
            return parent_directory
        names = parent_directory.child_directories.mapped('name')
        subject = slugify(msg_dict.get('subject', _('Alias-Mail-Extraction')), lower=False)
        defaults = dict({'name': unique_name(subject, names, escape_suffix=True)}, **custom_values)
        directory = super(Directory, self).message_new(msg_dict, custom_values=defaults)
        directory._process_message(msg_dict)
        return directory
    
    @api.multi
    def message_update(self, msg_dict, update_vals=None):
        self._process_message(msg_dict, extra_values=update_vals)
        return super(Directory, self).message_update(msg_dict, update_vals=update_vals)
        
    @api.multi
    def _process_message(self, msg_dict, extra_values={}):
        names = self.sudo().files.mapped('name')
        for attachment in msg_dict['attachments']:
            uname = unique_name(attachment.fname, names, escape_suffix=True)
            self.env['muk_dms.file'].sudo().create({
                'content': attachment.content,
                'directory': self.id,
                'name': uname,
            })
            names.append(uname)
        
    #----------------------------------------------------------
    # Create / Update / Delete
    #----------------------------------------------------------
    
    @api.model_create_multi
    def create(self, vals_list):
        return super(Directory, self.with_context(mail_create_nolog=True)).create(vals_list)