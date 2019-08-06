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
    
    attachment_link = fields.Boolean(
        string="Link Attachments",
        help="""Define if attachments which are created during a file
             action are copied or linked to the file.""")

    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    @api.model
    def _run_action_create_partner(self, action, files):
        if len(self._filter_image_files(files)) == len(self):
            return super(FileAction, self)._run_action_create_partner(action, files)
        partner_record = self.env['res.partner'].create({
            'name': _("New Partner"
        )})
        files.attach_file(
            model='res.partner',
            id=partner_record.id,
            link=action.attachment_link
        )
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit' 
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,activity',
            'name': _("Partner created from Documents"),
            'res_id': partner_record.id,
            'views': [(False, "form")],
            'context': context,
        }  