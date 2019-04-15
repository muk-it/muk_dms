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

from ast import literal_eval

from odoo import models, api, fields
from odoo.osv import expression

_logger = logging.getLogger(__name__)

class File(models.Model):

    _inherit = 'muk_dms.file'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    actions = fields.Many2many(
        comodel_name='muk_dms_actions.action',
        compute='_compute_available_actions',
        string='Available Actions',
        prefetch=False)
    
    actions_multi = fields.Many2many(
        comodel_name='muk_dms_actions.action',
        compute='_compute_available_actions',
        string='Available Multi Actions',
        prefetch=False)
    
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    def _compute_available_actions(self):
        tags = self.mapped('tags')
        categories = self.mapped('category')
        directories = self.mapped('directory')
        tags_domain = [('criteria_tags', '=', False)]
        category_domain = [('criteria_category', '=', False)]
        directory_domain = [('criteria_directory', '=', False)]
        if directories:
            directory_domain = expression.OR([directory_domain,
                [('criteria_directory', 'parent_of', directories.ids)],
            ])
        if categories:
            category_domain = expression.OR([category_domain,
                [('criteria_category', 'parent_of', categories.ids)],
            ])
        if tags:
            tags_domain = expression.OR([tags_domain,
                [('criteria_tags', 'in', tags.ids)],
            ])
        actions = self.env['muk_dms_actions.action'].search(
            expression.AND([directory_domain, category_domain, tags_domain])
        )
        for action in actions:
            domain = literal_eval(action.filter_domain)
            action_files = self.search(expression.AND([
                [['id', 'in', self.ids]], domain
            ]))
            values = {'actions': [(4, action.id)]}
            if not action.is_single_file_action:
                values.update({
                    'actions_multi': [(4, action.id)]
                })
            action_files.update(values)
            