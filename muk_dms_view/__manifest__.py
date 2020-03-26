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

{
    "name": "MuK Documents View",
    "summary": """Documents View""",
    "version": '12.0.1.0.2',   
    "category": 'Document Management',   
    "license": "LGPL-3",
    "website": "http://www.mukit.at",
    'live_test_url': 'https://mukit.at/r/SgN',
    "author": "MuK IT",
    "contributors": [
        "Mathias Markl <mathias.markl@mukit.at>",
    ],
    "depends": [
        "muk_web_preview",
        "muk_web_client_refresh",
        "muk_dms_actions",
    ],
    "data": [
        "template/assets.xml",
        "views/storage.xml",
        "views/directory.xml",
        "views/documents.xml",
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
    "application": False,
    "installable": True,
}