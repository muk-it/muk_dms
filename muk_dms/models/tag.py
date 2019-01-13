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

import logging

from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class Tag(models.Model):
    
    _name = 'muk_dms.tag'
    _description = "Document Tag"
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(
        string='Name', 
        required=True, 
        translate=True)
    
    active = fields.Boolean(
        default=True, 
        help="The active field allows you to hide the tag without removing it.")
    
    color = fields.Integer(
        string='Color Index', 
        default=10)

    directories = fields.Many2many(
        comodel_name='muk_dms.directory',
        relation='muk_dms_directory_tag_rel', 
        column1='tid',
        column2='did',
        string='Directories')
    
    files = fields.Many2many(
        comodel_name='muk_dms.file',
        relation='muk_dms_file_tag_rel', 
        column1='tid',
        column2='fid',
        string='Files')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]