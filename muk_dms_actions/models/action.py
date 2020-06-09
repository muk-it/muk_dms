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

import os
import re
import time
import logging
import datetime
import dateutil
import textwrap

from pytz import timezone
from ast import literal_eval

from odoo import _, models, api, fields
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression

from odoo.addons.web.controllers.main import clean_action

_logger = logging.getLogger(__name__)

class FileAction(models.Model):
    
    _name = 'muk_dms_actions.action'
    _description = "Action"
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(
        string='Name', 
        required=True, 
        translate=True)
    
    active = fields.Boolean(
        string='Active',
        default=True)
    
    criteria_directory = fields.Many2one(
        comodel_name='muk_dms.directory',
        context="{'dms_directory_show_path': True}",
        string="Directory Criteria")
    
    criteria_category = fields.Many2one(
        comodel_name='muk_dms.category',
        context="{'dms_category_show_path': True}", 
        string="Category Criteria")
    
    criteria_tags = fields.Many2many(
        comodel_name='muk_dms.tag',
        relation='muk_dms_action_criteria_tag_rel',         
        domain="""
            ['|', ['category', '=', False],
            ['category', 'child_of', criteria_category]]
        """,
        column1='muk_dms_action_id',
        column2='muk_dms_tag_id',
        string='Tag Criteria')
    
    criteria_domain = fields.Char(
        string="Domain Criteria")
    
    filter_domain = fields.Char(
        compute='_compute_filter_domain',
        string="Filter Domain")
    
    set_directory = fields.Many2one(
        comodel_name='muk_dms.directory', 
        context="{'dms_directory_show_path': True}",
        string="Set Directory")
    
    set_category = fields.Many2one(
        comodel_name='muk_dms.category',
        context="{'dms_category_show_path': True}", 
        string="Set Category")
    
    set_tags = fields.Many2many(
        comodel_name='muk_dms.tag',
        relation='muk_dms_action_set_tag_rel',         
        domain="""
            ['|', ['category', '=', False],
            ['category', 'child_of', set_category]]
        """,
        column1='muk_dms_action_id',
        column2='muk_dms_tag_id',
        string='Set Tags')
    
    state = fields.Selection(
        selection=[
            ('create_partner', "Create a Partner"),
        ],
        string="File Action")
    
    server_action_model = fields.Many2one(
        comodel_name='ir.model',
        string='Server Action Model', 
        default=lambda self: self.env['ir.model'].sudo().search(
            [["model", "=", "muk_dms.file"]], limit=1
        ),
        prefetch=False,
        readonly=True)
    
    server_actions = fields.Many2many(
        comodel_name='ir.actions.server',
        relation='muk_dms_action_server_action_rel',
        column1='muk_dms_action_id',
        column2='ir_server_action_id',
        string='Server Actions',
        domain='[["model_name","=","muk_dms.file"]]')
    
    is_limited_to_single_file = fields.Boolean(
        string="Action is limited to a single File",
        help="If checked the action is limited to a single file record.")
    
    is_single_file_action = fields.Boolean(
        compute='_compute_is_single_file_action',
        string="Can only be triggered on single records")
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    @api.model
    def _get_eval_context(self):
        return {
            'time': time,
            'datetime': datetime,
            'dateutil': dateutil,
            'uid': self.env.uid,
            'user': self.env.user
        }
    
    @api.model
    def _filter_image_files(self, files):
        regex_image = re.compile(r".*\.(gif|jpeg|jpg|png)$")
        return files.filtered(lambda rec: regex_image.match(rec.name))
        
    @api.model
    def _run_action(self, action, files):
        if action.state and hasattr(self, '_run_action_%s' % action.state):
            return getattr(self, '_run_action_%s' % action.state)(action, files)
        return None
    
    @api.model
    def _run_action_create_partner(self, action, files):
        filtered_files = self._filter_image_files(files)
        created_partner_records = self.env['res.partner']
        for file in filtered_files.with_context(bin_size=False):
            partner_record = self.env['res.partner'].create({
                'name': os.path.splitext(file.name)[0] or _("New Partner"),
                'image': file.content
            })
            created_partner_records |= partner_record
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,activity',
        }  
        if len(created_partner_records) == 1:
            context = dict(self.env.context)
            context['form_view_initial_mode'] = 'edit' 
            action.update({
                'name': _("Partner created from Documents"),
                'res_id': created_partner_records.id,
                'views': [(False, "form")],
                'context': context,
            })
        else:
            action.update({
                'context': self.env.context,
                'domain': [['id','in',created_partner_records.ids]],
                'name': _("Partners created from Documents"),
            })
        return action
        
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def trigger_actions(self, file_ids):
        model = self.env['muk_dms.file']
        files = model.browse(file_ids)
        action_result = False
        for record in self:
            values = {}
            if record.set_directory:
                values['directory'] = record.set_directory.id
            if record.set_category: 
                values['category'] = record.set_category.id
            if record.set_tags: 
                values['tags'] = [(4, tag.id) for tag in record.set_tags] 
            files.write(values)   
            if record.set_category:
                for file in files:
                    tags_to_remove = file.tags.filtered(
                        lambda rec: rec.category and \
                        rec.category != file.category
                    )
                file.write({'tags': [(3, tag.id) for tag in tags_to_remove]})
            action_result = self._run_action(record, files)
            server_action_context = {'active_model': files._name}
            if len(files) == 1:
                server_action_context['active_id'] = files.id
            if len(files) >= 1:
                server_action_context['active_ids'] = file_ids
            server_action = record.server_actions.with_context(**server_action_context).run()
            action_result = server_action if not action_result else action_result
        return clean_action(action_result) if action_result else False
    
    #----------------------------------------------------------
    # View
    #----------------------------------------------------------
    
    @api.onchange('criteria_category')
    def _change_category(self):
        self.criteria_tags = self.criteria_tags.filtered(
            lambda rec: not rec.category or \
            rec.category == self.criteria_category
        )
        
    @api.onchange('set_category')
    def _change_category(self):
        self.set_tags = self.set_tags.filtered(
            lambda rec: not rec.category or \
            rec.category == self.set_category
        )
        
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('criteria_directory', 'criteria_category', 'criteria_tags', 'criteria_domain')
    def _compute_filter_domain(self):
        for record in self:
            filter_domain = []
            if record.criteria_directory:
                filter_domain.append([
                    ['directory', 'child_of', record.criteria_directory.id]
                ])
            if record.criteria_category:
                filter_domain.append([
                    ['category', 'child_of', record.criteria_category.id]
                ])
            if record.criteria_tags:
                filter_domain.append([
                    ['tags', 'in', record.criteria_tags.ids]
                ])
            if record.criteria_domain:
                domain = filter_domain.append(safe_eval(
                    record.criteria_domain, self._get_eval_context()
                )) 
            record.filter_domain = expression.AND(filter_domain)
    
    @api.depends('state', 'is_limited_to_single_file')
    def _compute_is_single_file_action(self):
        limited = self.filtered('is_limited_to_single_file')
        (self - limited).update({'is_single_file_action': False})
        limited.update({'is_single_file_action': True})