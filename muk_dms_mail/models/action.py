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

import os
import re
import time
import logging
import datetime
import dateutil
import textwrap

from pytz import timezone
from ast import literal_eval
from dateutil.relativedelta import relativedelta

from odoo import _, models, api, fields
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression

from odoo.addons.web.controllers.main import clean_action

_logger = logging.getLogger(__name__)

class FileAction(models.Model):
    
    _inherit = 'muk_dms_actions.action'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    activity_done = fields.Boolean(
        string="Mark all as done",
        default=False)
    
    activity_create = fields.Boolean(
        string="Create a new Activity",
        default=False)
    
    activity_type = fields.Many2one(
        comodel_name='mail.activity.type', 
        string="Activity")

    activity_summary = fields.Char(
        string="Summary")
    
    activity_note = fields.Html(
        string="Note"
    )
    
    activity_deadline_value = fields.Integer(
        string="Due Date in")
    
    activity_deadline_unit = fields.Selection(
        selection=[
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months'),
        ], 
        string="Due type", 
        default='days')
    
    assigned_user = fields.Many2one(
        comodel_name='res.users', 
        string="Assigned to")
        
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.multi
    def trigger_actions(self, file_ids):
        result = super(FileAction, self).trigger_actions(file_ids)
        files = self.env['muk_dms.file'].browse(file_ids)
        if self.filtered('activity_done'):
            feedback = _("Closed by operation!")
            if len(self) == 1 and self.activity_done:
                feedback = _("Closed by operation: %s") % self.name
            files.mapped('activity_ids').action_feedback(feedback=feedback)
        for record in self.filtered('activity_create'):
            values = {
                'activity_type_id': record.activity_type.id,
                'summary': record.activity_summary or '',
                'note': record.activity_note or '',
            }
            if record.activity_deadline_value > 0:
                today = fields.Date.context_today(record)
                delta_unit = record.activity_deadline_unit
                delta_value = record.activity_deadline_value
                values['date_deadline'] = today + relativedelta(**{delta_unit: delta_value})
            values['user_id'] = record.assigned_user.id if  record.assigned_user else self.env.user
            files.activity_schedule(**values)
        return result
        
    #----------------------------------------------------------
    # Constrains
    #----------------------------------------------------------
    
    @api.constrains('activity_type', 'activity_create')
    def _check_activity_type(self):
        for record in self:
            if record.activity_create and not record.activity_type:
                raise ValidationError(_('An activity has to have a type!'))