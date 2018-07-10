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

from odoo import models, fields, api

class AccessGroups(models.Model):
    
    _inherit = 'muk_security.groups'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    files = fields.Many2many(
        comodel_name='muk_dms.file',
        relation='muk_groups_complete_file_rel',
        column1='gid',
        column2='aid',
        readonly=True)
    
    directories = fields.Many2many(
        comodel_name='muk_dms.directory',        
        relation='muk_groups_complete_directory_rel',
        column1='gid',
        column2='aid',
        readonly=True)
    
    count_directories = fields.Integer(
        compute='_compute_count_directories',
        string="Directories")
    
    count_files = fields.Integer(
        compute='_compute_count_files',
        string="Files")

    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------

    @api.depends('directories')
    def _compute_count_directories(self):
        for record in self:
            record.count_directories = len(record.directories)
     
    @api.depends('files')
    def _compute_count_files(self):
        for record in self:
            record.count_files = len(record.files)
