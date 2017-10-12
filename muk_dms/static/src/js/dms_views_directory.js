/**********************************************************************************
* 
*    Copyright (C) 2017 MuK IT GmbH
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Affero General Public License as
*    published by the Free Software Foundation, either version 3 of the
*    License, or (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Affero General Public License for more details.
*
*    You should have received a copy of the GNU Affero General Public License
*    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/
odoo.define('muk_dms_views.directory', function(require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var FormView = require('web.FormView');
var ListView = require('web.ListView');
var KanbanView = require('web_kanban.KanbanView');

var QWeb = core.qweb;
var _t = core._t;

FormView.include({
	load_record: function(record) {
		this._super.apply(this, arguments);
		if (this.$buttons && this.model === "muk_dms.directory") {
			if(!this.datarecord.perm_create) {
				this.$buttons.find('.o_form_button_create').hide();
			}
			if(!this.datarecord.perm_write) {
				this.$buttons.find('.o_form_button_edit').hide();
			}
        }
	}
});

ListView.include({
	compute_decoration_classnames: function (record) {
		var classnames = this._super.apply(this, arguments);
		if(this.model === "muk_dms.directory" && 
				!record.attributes.perm_unlink) {
			classnames = $.grep([classnames, "no_unlink"], Boolean).join(" ");
		}
		return classnames;
	}
});

var DirectoryKanbanView = KanbanView.extend({
	init: function() {
		this._super.apply(this, arguments);
		this.events = _.extend(this.events, {
            'click .muk_info_files': 'info_files',
            'click .muk_info_directories': 'info_directories',
        });
	},
	info_files: function(e) {
        e.stopPropagation();
        this.do_action({
        	type: 'ir.actions.act_window',
            res_model: "muk_dms.file",
            name: 'Document Files',
            views: [
            	[false, 'kanban'],
                [false, 'list'],
                [false, 'form'],
            ],
            target: 'current',
            domain: [
            	["directory", "=",  $(e.currentTarget).data('id')]
            ],
            context: {},
        });
    },
    info_directories: function(e) {
    	e.stopPropagation();
    	this.do_action({
        	type: 'ir.actions.act_window',
            res_model: "muk_dms.directory",
            name: 'Document Directories',
            views: [
            	[false, 'kanban'],
                [false, 'list'],
                [false, 'hierarchy'],
                [false, 'form'],
            ],
            target: 'current',
            domain: [
            	["parent_directory", "=",  $(e.currentTarget).data('id')]
            ],
            context: {},
        });
    }
});

core.view_registry.add('dms_directory_kanban', DirectoryKanbanView);

return DirectoryKanbanView;

});