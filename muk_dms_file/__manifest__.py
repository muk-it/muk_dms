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

{
    'name': "MuK Documents File",
    'summary': """Document Management System""",
    'description': """ 
        This module extends MuK Documents to use the local file system to store and load files.
        
        I case you want to change the save type of an existing Root Setting be aware that this
        can trigger a heavy migration process, depending on how many files are currently stored.
        
        Before you start the migration process make sure the following conditions are met:
            - no one else is using the system at the time of migration
            - no files are locked either by the system or users
            - Odoo has writing rights to the given directory path
    """,
    'version': '1.0.0',   
    'category': 'Document Management',   
    'license': 'AGPL-3',    
    'author': "MuK IT",
    'website': "http://www.mukit.at",
    'contributors': [
        "Mathias Markl <mathias.markl@mukit.at>",
        "Kerrim Abdelhamed <kerrim.adbelhamed@mukit.at>",
    ],
    'depends': [
        'muk_dms',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/muk_dms_view_root.xml',
        'views/muk_dms_view_data.xml',
    ],
    'images': [
        'static/description/banner.png'
    ],
    "installable": True,
}
