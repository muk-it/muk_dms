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

import os
import base64
import logging
import unittest

from odoo import _
from odoo.tests import common

from odoo.addons.muk_dms.tests import dms_case

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class DataTestCase(dms_case.DMSTestCase):
    
    def setUp(self):
        super(DataTestCase, self).setUp()
        self.group = self.browse_ref("muk_dms_access.access_group_01_demo").sudo()
        
    def tearDown(self):
        super(DataTestCase, self).tearDown()
    
    def test_hr_update(self):
        department = self.env['hr.department'].sudo().create({
            'name': "TestDepartment"})
        job = self.env['hr.job'].sudo().create({
            'name': "TestJob",
            'department_id': department.id,
            'description': "TestDescription"})
        employee = self.env['hr.employee'].sudo().create({
            'name': "TestEmployee",
            'department_id': department.id,
            'job_id': job.id,
            'user_id': self.dmsuser.id})
        self.group.departments |= department
        self.group.jobs |= job
        self.assertTrue(self.group.count_users >= 1)
        department.manager_id = employee
        job.employee_ids = self.env['hr.employee']
        employee.unlink()
        job.unlink()
        department.unlink()
        
    def test_group_update(self):
        group = self.env['res.groups'].sudo().create({
            'name': "TestGroup"})
        self.group.groups |= group
        group.users |= self.dmsuser
        self.assertTrue(self.group.count_users >= 1)
        group.unlink()
    