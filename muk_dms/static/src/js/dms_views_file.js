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

var FormController = require('web.FormController');
var ListRenderer = require('web.ListRenderer');
var KanbanRecord = require('web.KanbanRecord');

var PreviewHelper = require('muk_dms_preview_file.PreviewHelper');

var QWeb = core.qweb;
var _t = core._t;

FormController.include({
	_updateButtons: function() {
        this._super.apply(this, arguments);
        if(this.$buttons && this.modelName === 'muk_dms.file') {
            var renderer = this.renderer;
            var data = renderer.state.data;
            if(!data.perm_create) {
        		this.$buttons.find('.o_form_button_create').hide();
        	} else {
        		this.$buttons.find('.o_form_button_create').show();
        	}
        	if(!data.perm_write) {
        		this.$buttons.find('.o_form_button_edit').hide();
	    	} else {
	    		this.$buttons.find('.o_form_button_edit').show();
	    	}
        	if(!data.editor &&
					data.locked &&
					data.locked instanceof Object) {
				var $edit = this.$buttons.find('.o_form_button_edit');
				$edit.prop("disabled", true);
				$edit.text(_t("Locked!"));
			} else {
				var $edit = this.$buttons.find('.o_form_button_edit');
				$edit.prop("disabled", false);
				$edit.text(_t("Edit"));
			}
        }
	}
});

ListRenderer.include({
	_setDecorationClasses: function (record, $tr) {
		this._super.apply(this, arguments);
		if(record.model === 'muk_dms.file') {
			if(record.data.locked && 
					record.data.locked instanceof Object) {
				$tr.addClass("locked");
			} else {
				$tr.removeClass("locked");
			}
			if(!record.data.perm_unlink) {
				$tr.addClass("no_unlink");
			} else {
				$tr.removeClass("no_unlink");
			}
		}
	},
});

KanbanRecord.include({
	start: function() {
		var self = this;
		this._super.apply(this, arguments);
		if (this.modelName === 'muk_dms.file') {
			this.$(".muk_image").click(function(e) {
				e.stopPropagation();
		        PreviewHelper.createFilePreviewDialog($(e.currentTarget).data('id'), self);
			});
			this.$(".muk_filename").click(function(e) {
				e.stopPropagation();
				self._openRecord();
			});
		}
	}
});

});