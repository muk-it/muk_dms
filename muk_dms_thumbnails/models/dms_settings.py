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
import errno
import logging

from odoo import _
from odoo import models, api, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ThumbnailSettings(models.Model):
    
    _inherit = 'muk_dms.settings'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    thumbnails = fields.Selection(
        selection=[
            ('immediate', "On Creation/Update"),
            ('cron', "On Cron Job")
        ],
        string="Thumbnails Settings",
        default='cron',
        help="Thumbnails can be created either directly when changing the file or once an hour via cron job.")
    
    protect_thumbnails = fields.Boolean(
        string="Protect Thumbnails",
        default=True,
        help="If this flag is enabled thumbnails set by a user wont be changed.")
    
    @api.multi
    def _check_notification(self, vals, *largs, **kwargs):
        super(ThumbnailSettings, self)._check_notification(vals, *largs, **kwargs)
        if 'thumbnails' in vals:
            self.suspend_security().notify_change({'thumbnails': vals['thumbnails']})
        if 'protect_thumbnails' in vals:
            self.suspend_security().notify_change({'protect_thumbnails': vals['protect_thumbnails']})