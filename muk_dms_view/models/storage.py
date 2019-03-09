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

import logging

from odoo import _, models, api, fields

_logger = logging.getLogger(__name__)

class Storage(models.Model):
    
    _inherit = 'muk_dms.storage'

    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    @api.model
    def _build_documents_view_storage(self, storage):
        storage_directories = []
        model = self.env['muk_dms.directory']
        directories = model.search_parents([
            ['storage', '=', storage.id]
        ])
        for record in directories:
            storage_directories.append(
                model._build_documents_view_directory(record)
            )
        return {
            "id": "storage_%s" % storage.id,
            "text": storage.name,
            "icon": "fa fa-database",
            "type": "storage",
            "data": {
                "odoo_id": storage.id,
                "odoo_model": "muk_dms.storage",
            },
            "children": storage_directories,
        }
    
    @api.multi
    def _build_documents_view_initial(self):
            initial_data = []
            for record in self:
                initial_data.append(
                    record._build_documents_view_storage(record)
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
                "key": "dms_documents_storage_%s" % "-".join(map(str, self.ids)),
            },
            "name": self.display_name if len(self) == 1 else _("Documents"),
        }

        