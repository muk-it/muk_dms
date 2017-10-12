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
odoo.define('muk_dms_views.file', function(require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var FormView = require('web.FormView');
var ListView = require('web.ListView');
var KanbanView = require('web_kanban.KanbanView');

var PreviewHelper = require('muk_dms_preview_file.PreviewHelper');

var QWeb = core.qweb;
var _t = core._t;

FormView.include({
	load_record: function(record) {
		this._super.apply(this, arguments);
		if (this.$buttons && this.model === "muk_dms.file") {
			if(!this.datarecord.perm_create) {
				this.$buttons.find('.o_form_button_create').hide();
			}
			if(!this.datarecord.perm_write) {
				this.$buttons.find('.o_form_button_edit').hide();
			}
			if(!this.datarecord.editor &&
					this.datarecord.locked &&
					this.datarecord.locked instanceof Array) {
				var $edit = this.$buttons.find('.o_form_button_edit');
				$edit.prop("disabled", true);
				$edit.text(_t("Locked!"));
			}
        }
	}
});

ListView.include({
	compute_decoration_classnames: function (record) {
		var classnames = this._super.apply(this, arguments);
		if(this.model === "muk_dms.file" && 
				record.attributes.locked && 
				record.attributes.locked instanceof Array) {
			classnames = $.grep([classnames, "locked"], Boolean).join(" ");
		}
		if(this.model === "muk_dms.file" && 
				!record.attributes.perm_unlink) {
			classnames = $.grep([classnames, "no_unlink"], Boolean).join(" ");
		}
		return classnames;
	}
});

var FileKanbanView = KanbanView.extend({
	init: function() {
		this._super.apply(this, arguments);
		this.events = _.extend(this.events, {
            'click .muk_image': 'preview_file',
            'click .muk_filename': 'select_file',
        });
	},
	preview_file: function(e) {
        e.stopPropagation();
        PreviewHelper.createFilePreviewDialog($(e.currentTarget).data('id'));
    },
    select_file: function(e) {
    	e.data = {id: $(e.currentTarget).data('id')};
    	this.open_record(e, {});
    }
});

core.view_registry.add('dms_file_kanban', FileKanbanView);

return FileKanbanView;

});