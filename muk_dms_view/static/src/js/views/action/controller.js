/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Documents View 
*    (see https://mukit.at).
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Lesser General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Lesser General Public License for more details.
*
*    You should have received a copy of the GNU Lesser General Public License
*    along with this program. If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define('muk_dms_view.DocumentsViewController', function(require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var config = require('web.config');
var session = require('web.session');
var web_client = require('web.web_client');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');

var DocumentsController = require('muk_dms_view.DocumentsController');
var DocumentFileInfoDialog = require('muk_dms_dialogs.DocumentFileInfoDialog');
var DocumentDirectoryInfoDialog = require('muk_dms_dialogs.DocumentDirectoryInfoDialog');
var DocumentDropFileDialog = require('muk_dms_dialogs.DocumentDropFileDialog');
var DocumentDropFilesDialog = require('muk_dms_dialogs.DocumentDropFilesDialog');

var _t = core._t;
var QWeb = core.qweb;

var DocumentsViewController = DocumentsController.extend({
    _loadContextMenuBasic: function($jstree, node, menu) {
    	var self = this;
    	menu.info = {
			separator_before: false,
			separator_after: false,
			icon: "fa fa-info",
			label: _t("Info"),
			action: function (data) {
				self._openInfo(node);
			},
		};
    	menu.open = {
			separator_before: false,
			separator_after: false,
			icon: "fa fa-external-link",
			label: _t("Open"),
			action: function (data) {
				self._openNode(node);
			},
		};
    	menu.edit = {
			separator_before: false,
			separator_after: false,
			icon: "fa fa-pencil-square-o",
			label: _t("Edit"),
			action: function (data) {
				self._editNode(node);
			},
			_disabled: function (data) {
    			return !node.data.perm_write;
			},
		};
    	return this._super($jstree, node, menu);
    },
    _loadContextMenuDirectory: function($jstree, node, menu) {
    	var self = this;
    	menu = this._super($jstree, node, menu);
    	menu.upload = {
			separator_before: false,
			separator_after: false,
			icon: "fa fa-upload",
			label: _t("Upload"),
			action: function(data) {
				self._uploadFilesDialog(node);
			},
	    	_disabled: function (data) {
				return !node.data.perm_create;
			},
    	};
    	menu.create = {
			separator_before: false,
			separator_after: false,
			icon: "fa fa-plus",
			label: _t("Create"),
			action: false,
			submenu: {
				directory: {
					separator_before: false,
					separator_after: false,
					label: _t("Directory"),
					icon: "fa fa-folder-o",
					action: function(data) {
						self._createNode(node, "muk_dms.directory");
					},
					_disabled: function (data) {
		    			return !node.data.perm_create;
	    			},
				},
				file : {
					separator_before: false,
					separator_after: false,
					label: _t("File"),
					icon: "fa fa-file-o",
					action: function(data) {
						self._createNode(node, "muk_dms.file");
					},
					_disabled: function (data) {
		    			return !node.data.perm_create;
	    			},
				},
			}	
		};
    	return menu;
    },
    _loadContextMenuFile: function($jstree, node, menu) {
    	var self = this;
    	menu.replace = {
			separator_before: false,
			separator_after: false,
			icon: "fa fa-retweet",
			label: _t("Replace"),
			action: function(data) {
				self._replaceFile(node);
			},
	    	_disabled: function (data) {
				return !node.data.perm_write;
			},
    	};
    	var operations = {};
    	_.each(node.data.actions, function(action, index, list) {
    		operations['operation_' + action[0]] = {
				separator_before: false,
				separator_after: false,
				label: action[1],
				icon: "fa fa-gear",
				action: function(data) {
					self._executeOperation(node, action[0]);
				},
    		};
    	});
    	if (!_.isEmpty(operations)) {
	    	menu.operation = {
				separator_before: false,
				separator_after: false,
				icon: "fa fa-gears",
				label: _t("Operation"),
				action: false,
				submenu: operations,
			};
    	}
    	return this._super($jstree, node, menu);
    },
});

return DocumentsViewController;

});