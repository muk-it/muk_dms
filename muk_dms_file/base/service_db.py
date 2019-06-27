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

import os
import json
import uuid
import logging
import shutil
import zipfile
import tempfile

from contextlib import closing

from odoo import _, modules, api, sql_db, SUPERUSER_ID
from odoo.tools import osutil, config, exec_pg_command
from odoo.service import db

from odoo.addons.muk_utils.tools import patch

_logger = logging.getLogger(__name__)

@patch.monkey_patch(db)
@db.check_db_management_enabled
def exp_duplicate_database(db_original_name, db_name):
    filestore_paths = []
    connection = sql_db.db_connect(db_original_name)
    with closing(connection.cursor()) as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        if env.get('muk_dms.settings'):
            settings = env['muk_dms.settings'].search([('save_type', '=', 'file')])
            for setting in settings:
                filestore_paths.append({
                    'complete_base_path': setting.complete_base_path,
                    'base_path': setting.base_path,
                    'db_name': db_name})
        res = exp_duplicate_database.super(db_original_name, db_name)
        for path in filestore_paths:
            if os.path.exists(path['complete_base_path']):
                shutil.copytree(path['complete_base_path'], os.path.join(path['base_path'], db_name))
    return res

@patch.monkey_patch(db)
@db.check_db_management_enabled
def exp_drop(db_name):
    filestore_paths = []
    connection = sql_db.db_connect(db_name)
    with closing(connection.cursor()) as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        if env.get("muk_dms.settings"):
            settings = env['muk_dms.settings'].search([('save_type', '=', 'file')])
            filestore_paths = settings.mapped('complete_base_path')
    res = exp_drop.super(db_name)
    for path in filestore_paths:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
    return res

@patch.monkey_patch(db)
@db.check_db_management_enabled
def dump_db(db_name, stream, backup_format='zip'):
    if backup_format == 'zip':
        filestore_paths = []
        connection = sql_db.db_connect(db_name)
        with closing(connection.cursor()) as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            if env.get("muk_dms.settings"):
                settings = env['muk_dms.settings'].search([('save_type', '=', 'file')])
                for setting in settings:
                    filestore_paths.append({
                        'complete_base_path': setting.complete_base_path,
                        'base_path': setting.base_path,
                        'db_name': db_name})
        res = dump_db.super(db_name, False, backup_format)
        with osutil.tempdir() as dump_dir:
            with zipfile.ZipFile(res, 'r') as zip:
                zip.extractall(dump_dir)
            with open(os.path.join(dump_dir, 'dms_system_files.json'), 'w') as fh:                
                dms_system_files = []
                for path in filestore_paths:
                    filestore_id = uuid.uuid4().hex
                    dms_system_files.append({
                        'id': filestore_id,
                        'data': path})
                    if os.path.exists(path['complete_base_path']):
                        shutil.copytree(path['complete_base_path'], os.path.join(
                            dump_dir, 'dms_system_files', filestore_id))
                json.dump(dms_system_files, fh, indent=4)
            if stream:
                osutil.zip_dir(dump_dir, stream, include_dir=False, fnct_sort=lambda file_name: file_name != 'dump.sql')
            else:
                t=tempfile.TemporaryFile()
                osutil.zip_dir(dump_dir, t, include_dir=False, fnct_sort=lambda file_name: file_name != 'dump.sql')
                t.seek(0)
                return t
    else:
        return dump_db.super(db_name, stream, backup_format)

@patch.monkey_patch(db)
@db.check_db_management_enabled
def restore_db(db, dump_file, copy=False):
    res = restore_db.super(db, dump_file, copy)
    with osutil.tempdir() as dump_dir:
        if zipfile.is_zipfile(dump_file):
            with zipfile.ZipFile(dump_file, 'r') as zip:
                dms_system_files = [m for m in zip.namelist() if m.startswith('dms_system_files/')]
                zip.extractall(dump_dir, ['dms_system_files.json'] + dms_system_files)
                if dms_system_files:
                    system_file_path = os.path.join(dump_dir, 'dms_system_files')
                    with open(os.path.join(dump_dir, 'dms_system_files.json')) as file:
                        data = json.load(file)
                        for info in data:
                            shutil.move(os.path.join(system_file_path, info['id']),
                                os.path.join(info['data']['base_path'], db))
    return res

@patch.monkey_patch(db)
@db.check_db_management_enabled
def exp_rename(old_name, new_name):
    filestore_paths = []
    connection = sql_db.db_connect(old_name)
    with closing(connection.cursor()) as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        if env.get("muk_dms.settings"):
            settings = env['muk_dms.settings'].search([('save_type', '=', 'file')])
            for setting in settings:
                filestore_paths.append({
                    'complete_base_path': setting.complete_base_path,
                    'base_path': setting.base_path,
                    'db_name': db_name})
        res = exp_rename.super(old_name, new_name)
        for path in filestore_paths:
            if os.path.exists(path['complete_base_path']):
                shutil.move(path['complete_base_path'], os.path.join(path['base_path'], new_name))
    return res
