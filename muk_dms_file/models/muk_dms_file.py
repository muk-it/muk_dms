# -*- coding: utf-8 -*-

###################################################################################
# 
#    MuK Document Management System
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

from openerp import _
from openerp import models, api, fields
from openerp.exceptions import ValidationError

from openerp.addons.muk_dms.models import muk_dms_base as base
from openerp.addons.muk_dms.models import muk_dms_data as data

from . import muk_dms_root as root

_logger = logging.getLogger(__name__)

class SysFileFile(base.DMSModel):
    _inherit = 'muk_dms.file'
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    def notify_change(self, change, values):
        super(SysFileFile, self).notify_change(change, values)
        if str(change) is str(base.PATH):
            self._update_file(data.MOVE, {'path': self.directory.get_path()})
        elif str(change) is str(base.ROOT):
            _logger.info("Migrating file from %s to %s" % (self.type, values))
            values = self.copy_data(None)[0]
            values['file'] =  self._get_file()
            self._delete_file()
            rec_file = self._create_file(values, self.directory, self.directory.get_root())
            self.file_ref = rec_file._name + ',' + str(rec_file.id)
    
    def _create_file(self, values, rec_dir, rec_root):
        result = super(SysFileFile, self)._create_file(values, rec_dir, rec_root)
        if result:
            return result
        elif rec_root.save_type == root.SAVE_SYSTEM:
            rec_data = self.env['muk_dms.system_data'].sudo().create({'filename': values['filename'],
                                                                      'entry_path': rec_root.entry_path,
                                                                      'path': rec_dir.get_path()})
            rec_data.sudo().update(data.REPLACE, {'file': values['file']})
            return rec_data
        return False
    
    #----------------------------------------------------------
    # Create, Update
    #----------------------------------------------------------
    
    def _append_values_wirte(self, values):
        values = super(SysFileFile, self)._append_values_wirte(values)
        if 'directory' in values:
            rec_dir = self.env['muk_dms.directory'].sudo().browse([values['directory']])
            self._update_file(data.MOVE, {'path': rec_dir.get_path()})
        return values