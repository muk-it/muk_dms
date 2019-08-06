###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Actions 
#    (see https://mukit.at).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import logging

from ast import literal_eval
from collections import defaultdict

from odoo import models, api, fields
from odoo.tools import frozendict
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
        tags_domain = [('criteria_tags', '=', False)]
        category_domain = [('criteria_category', '=', False)]
        directory_domain = [('criteria_directory', '=', False)]
        no_prefetch = self.with_context(prefetch_fields=False)
        directory_ids = no_prefetch.mapped('directory.id')
        category_ids = self.mapped('category.id')
        tags_ids = self.mapped('tags.id')
        if directory_ids:
            directory_domain = expression.OR([directory_domain,
                [('criteria_directory', 'parent_of', directory_ids)],
            ])
        if category_ids:
            category_domain = expression.OR([category_domain,
                [('criteria_category', 'parent_of', category_ids)],
            ])
        if tags_ids:
            tags_domain = expression.OR([tags_domain,
                [('criteria_tags', 'in', tags_ids)],
            ])
        updatesdict = defaultdict(set)  
        actiondict = defaultdict(lambda : [set(), set()])
        action_model = self.env['muk_dms_actions.action']
        actions = action_model.search(expression.AND([
            directory_domain, category_domain, tags_domain
        ]))
        for action in actions:
            is_single = action.is_single_file_action
            domain = literal_eval(action.filter_domain)
            action_files = self.search(expression.AND([
                [['id', 'in', self.ids]], domain
            ]))
            for file_id in action_files.ids:
                if not is_single:
                    actiondict[file_id][1].add(action.id)
                actiondict[file_id][0].add(action.id)
        for id, vals in actiondict.items():
            actions_values = {
                'actions': [(6, 0, list(vals[0]))],
                'actions_multi': [(6, 0, list(vals[1]))]
            }
            updatesdict[frozendict(actions_values)].add(id)
        for values, ids in updatesdict.items():
            self.browse(ids).update(dict(values))
            