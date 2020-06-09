###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents Field 
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

from odoo import api, models, fields

_logger = logging.getLogger(__name__)

class Base(models.AbstractModel):
    
    _inherit = 'base'

    def unlink(self):
        file_ids = set()
        if 'muk_dms.file' in self.env:
            query = 'SELECT id FROM muk_dms_file WHERE reference_model=%s AND reference_id IN %s'
            for sub_ids in self.env.cr.split_for_in_conditions(self.ids):
                self.env.cr.execute(query, (self._name, sub_ids))
                file_ids |= set([row[0] for row in self.env.cr.fetchall()])
        super(Base, self).unlink()
        if file_ids and 'muk_dms.file' in self.env:
            self.env['muk_dms.file'].sudo().browse(list(file_ids)).unlink()