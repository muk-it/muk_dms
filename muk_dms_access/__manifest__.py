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
    'name': "MuK Documents Access",
    'summary': """Access Control""",
    'description': """ 
        MuK Documents Access enables access control groups.
        These groups can be used to customize the security
        of your document management system.
    """,
    'version': '11.0.1.0.6',   
    'category': 'Document Management',   
    'license': 'AGPL-3',    
    'author': "MuK IT",
    'website': "http://www.mukit.at",
    'contributors': [
        "Mathias Markl <mathias.markl@mukit.at>",
        "Kerrim Abdelhamed <kerrim.adbelhamed@mukit.at>",
    ],
    'depends': [
        'hr',
        'muk_dms',
    ],
    "data": [
        "security/dms_access_security.xml",
        'security/ir.model.access.csv',
        'views/dms_groups_view.xml',
        'views/dms_directory_view.xml',
        'views/dms_file_view.xml',
    ],
    "demo": [
        "demo/dms_hr_demo.xml",
        "demo/dms_access_groups_demo.xml",
        "demo/dms_settings_demo.xml",
        "demo/dms_directory_demo.xml",
        "demo/dms_file_demo.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    'images': [
        'static/description/banner.png'
    ],
    "post_init_hook": '_auto_default_group',
    "application": False,
    "installable": True,
}
