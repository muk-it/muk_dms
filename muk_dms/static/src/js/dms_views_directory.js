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

var FormController = require('web.FormController');
var ListRenderer = require('web.ListRenderer');
var KanbanView = require('web.KanbanView');

var QWeb = core.qweb;
var _t = core._t;

FormController.include({
	_updateButtons: function() {
        this._super.apply(this, arguments);
        if(this.$buttons && this.modelName === 'muk_dms.directory') {
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
        }
	}
});

ListRenderer.include({
	_setDecorationClasses: function (record, $tr) {
		this._super.apply(this, arguments);
		if(record.model === 'muk_dms.directory' && !record.data.perm_unlink) {
			$tr.addClass("no_unlink");
		} else {
			$tr.removeClass("no_unlink");
		}
	},
});

});