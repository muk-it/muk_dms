###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents View 
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

from odoo import _, models, api, fields

_logger = logging.getLogger(__name__)

class Directory(models.Model):
    
    _inherit = 'muk_dms.directory'

    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    @api.model
    def _build_documents_view_directory(self, directory):
        return {
            "id": "directory_%s" % directory.id,
            "text": directory.name,
            "icon": "fa fa-folder-o",
            "type": "directory",
            "data": {
                "odoo_id": directory.id,
                "odoo_model": "muk_dms.directory",
            },
            "children": directory.count_elements > 0,
        }
        
    @api.multi
    def _build_documents_view_initial(self):
        if len(self) == 1:
            return [self._build_documents_view_directory(self)]
        else:
            initial_data = []
            subdirectories = self.env['muk_dms.directory']
            for record in self.with_context(prefetch_fields=False):
                subdirectories |= (record.search([
                    ('parent_directory', 'child_of', record.id)
                ]) - record)
            for record in self - subdirectories:
                initial_data.append(
                    record._build_documents_view_directory(record)
                )
            return initial_data
            
    #----------------------------------------------------------
    # Actions
    #----------------------------------------------------------
    
    @api.multi
    def action_open_documents_view(self):
        return {
            "type": "ir.actions.client",
            "tag": "muk_dms_view.documents",
            "params": {
                "model": {
                    "initial": self._build_documents_view_initial(),
                },
                "key": "dms_documents_directory_%s" % "-".join(map(str, self.ids)),
            },
            "name": self.display_name if len(self) == 1 else _("Documents"),
        }

        