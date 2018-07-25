###################################################################################
# 
#    Copyright (C) 2018 MuK IT GmbH
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

from odoo import models, api

from odoo.addons.muk_utils.tools import patch

_logger = logging.getLogger(__name__)

@api.multi
@patch.monkey_patch_model(models.BaseModel)
def unlink(self):
    if 'muk_dms.file' in self.env:
        cr = self.env.cr
        files = self.env['muk_dms.file'].sudo()
        try:
            for sub_ids in cr.split_for_in_conditions(self.ids):
                query = 'SELECT id FROM muk_dms_file WHERE reference_model=%s AND reference_id IN %s'
                cr.execute(query, (self._name, sub_ids))
                files |= files.browse([row[0] for row in cr.fetchall()])
        except Exception:
            _logger.exception("Failed to delete referenced files.")
        unlink.super(self)
        if files.exists():
            files.unlink()
    else:
        unlink.super(self)

