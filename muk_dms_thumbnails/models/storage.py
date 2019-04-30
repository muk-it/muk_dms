####################################################################################
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

from odoo import _, models, api, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class Storage(models.Model):
    
    _inherit = 'muk_dms.storage'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    thumbnails = fields.Selection(
        selection=[
            ('immediate', "On Creation/Update"),
            ('cron', "On Cron Job")
        ],
        string="Thumbnails",
        default='cron',
        help="""Thumbnails can be created either directly when
            changing the file or once an hour via cron job.""")
