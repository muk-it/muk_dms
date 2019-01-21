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

from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class Category(models.Model):
    
    _name = 'muk_dms.category'
    _description = "Document Category"
    
    _inherit = [
        'muk_utils.mixins.hierarchy',
    ]
    
    _order = "name asc"
    
    _parent_store = True
    _parent_name = "parent_category"
    
    _parent_path_sudo = False
    _parent_path_store = True
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(
        string='Name', 
        required=True, 
        translate=True)
    
    active = fields.Boolean(
        default=True, 
        help="The active field allows you to hide the category without removing it.")
    
    parent_category = fields.Many2one(
        comodel_name='muk_dms.category', 
        context="{'dms_category_show_path': True}",
        string='Parent Category',
        index=True,
        ondelete='cascade')
    
    child_categories = fields.One2many(
        comodel_name='muk_dms.category', 
        inverse_name='parent_category',
        string='Child Categories')
    
    parent_path = fields.Char(
        string="Parent Path", 
        index=True)
    
    directories = fields.One2many(
        comodel_name='muk_dms.directory', 
        inverse_name='category',
        string='Directories')
    
    files = fields.One2many(
        comodel_name='muk_dms.file', 
        inverse_name='category',
        string='Files')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Category name already exists!"),
    ]
       
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = list(args or [])
        if not (name == '' and operator == 'ilike') :
            if '/' in name:
                domain += [('parent_path_names', operator, name)]  
            else:
                domain += [(self._rec_name, operator, name)]
        records = self.browse(self._search(domain, limit=limit, access_rights_uid=name_get_uid))
        return models.lazy_name_get(records.sudo(name_get_uid or self.env.uid)) 
            
    @api.multi
    def name_get(self):
        if self.env.context.get('dms_category_show_path'):
            res = []
            for record in self:
                names = record.parent_path_names
                if not names:
                    res.append(super(Category, record).name_get()[0])
                elif not len(names) > 50:
                    res.append((record.id, names))
                else:
                    res.append((record.id, ".." + names[-48:]))
            return res
        return super(Category, self).name_get()

    #----------------------------------------------------------
    # Create
    #----------------------------------------------------------
    
    @api.constrains('parent_category')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive categories.'))
        return True
    