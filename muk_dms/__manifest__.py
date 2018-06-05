# -*- coding: utf-8 -*-

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

{
    "name": "MuK Documents",
    "summary": """Document Management System""",
    "description": """ 
        
    """,
    "version": '10.0.1.2.1',   
    "category": 'Document Management',   
    "license": "AGPL-3",
    "website": "http://www.mukit.at",
    "author": "MuK IT",
    "contributors": [
        "Mathias Markl <mathias.markl@mukit.at>",
        "Kerrim Abdelhamed <kerrim.adbelhamed@mukit.at>",
    ],
    "depends": [
        "muk_web_preview",
        "muk_web_client_refresh",
    ],
    "data": [
        "security/dms_security.xml",
        "security/ir.model.access.csv",
        "template/assets.xml",
        "views/dms_menu.xml",
        "views/dms_actions.xml",
        "views/dms_settings_view.xml",
        "views/dms_directory_view.xml",
        "views/dms_file_view.xml",
        "views/dms_data_view.xml",
        "views/dms_lock_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "images": [
        'static/description/banner.png'
    ],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "application": True,
    "installable": True,
    
}
