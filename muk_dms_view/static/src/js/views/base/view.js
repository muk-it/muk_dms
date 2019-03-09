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

odoo.define('muk_dms_view.DocumentTreeView', function(require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var config = require('web.config');
var session = require('web.session');
var web_client = require('web.web_client');

var Widget = require('web.Widget');
var Dialog = require('web.Dialog');
var ControlPanelMixin = require('web.ControlPanelMixin');

var DocumentsModel = require('muk_dms_view.DocumentsModel');
var DocumentsRenderer = require('muk_dms_view.DocumentsRenderer');
var DocumentsController = require('muk_dms_view.DocumentsController');

var _t = core._t;
var QWeb = core.qweb;

var DocumentTreeView = Widget.extend({
	config: {
		DocumentsModel: DocumentsModel,
		DocumentsRenderer: DocumentsRenderer,
		DocumentsController: DocumentsController,
	},
	init: function(parent, params, action) {
		
		console.log(params, action)
		
		this._super.apply(this, arguments);
		var settings = $.extend(true, {}, {
			dnd: true, contextmenu: true,
        }, params || {}, action.params && action.params || {})
        
        
        console.log(settings);
        
		this.controller = new this.config.DocumentsController(this,
			this.config.DocumentsModel, this.config.DocumentsRenderer, settings
        );
    },
    refresh: function(message) {
    	this.controller.refresh(message);
    },
    start: function () {
        return $.when(this._super.apply(this, arguments))
	        .then(this._update_cp.bind(this))
	     	.then(this._update_view.bind(this));
    },
    _update_cp: function() {
    },
    _update_view: function() {
    	this.controller.appendTo(this.$('.mk_treeview'));
    },
});

return DocumentTreeView;

});