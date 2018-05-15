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

from openerp import models, fields, api
from openerp.tools.safe_eval import safe_eval


class DocumentSettings(models.TransientModel):
    _name = 'dms.config.settings'
    _inherit = 'res.config.settings'
    # _inherit = 'base.config.settings'
    
    module_muk_dms_access = fields.Boolean(
        string="Access Control",
        help="Allows the creation of groups to define access rights.")
    
    module_muk_dms_attachment = fields.Boolean(
        string="Attachment Storage Location",
        help="Allows attachments to be stored inside of MuK Documents.")
    
    module_muk_dms_attachment_rules = fields.Boolean(
        string="Attachment Storage Rules",
        help="Allows attachments to be automatically placed in the right directory.")
    
    module_muk_dms_finder = fields.Boolean(
        string="Finder",
        help="Enables the Document Finder.")
    
    module_muk_dms_file = fields.Boolean(
        string="File Store",
        help="Enables a new save option to store files into a file store.")
    
    module_muk_dms_lobject = fields.Boolean(
        string="Large Objects ",
        help="Enables a new save option to store files into large objects.")
    
    max_upload_size = fields.Char(
        string="Size",
        help="Defines the maximum upload size in MB. Default (25MB)")
    
    forbidden_extensions = fields.Char(
        string="Extensions",
        help="Defines a list of forbidden file extensions. (Example: '.exe,.msi')")


    def get_default_dms_template_user_id(self, cr, uid, fields, context=None):
        icp = self.pool.get('ir.config_parameter')
        # we use safe_eval on the result, since the value of the parameter is a nonempty string
        return {
            'max_upload_size': safe_eval(icp.get_param(cr, uid, 'muk_dms.max_upload_size', '25')),
            'forbidden_extensions': safe_eval(icp.get_param(cr, uid, 'auth_signup.allow_uninvited', '''False''')),
        }

    def set_dms_user_id(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool.get('ir.config_parameter')
        # we store the repr of the values, since the value of the parameter is a required string
        icp.set_param(cr, uid, 'muk_dms.max_upload_size', repr(config.max_upload_size))
        icp.set_param(cr, uid, 'muk_dms.forbidden_extensions', repr(config.forbidden_extensions))
