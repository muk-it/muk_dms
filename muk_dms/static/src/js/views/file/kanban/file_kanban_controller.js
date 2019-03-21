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

odoo.define('muk_dms.FileKanbanController', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var utils = require('muk_web_utils.files');
var async = require('muk_web_utils.async');

var Domain = require('web.Domain');
var KanbanController = require('web.KanbanController');

var FileUpload = require('muk_dms_mixins.FileUpload');

var _t = core._t;
var QWeb = core.qweb;

var FileKanbanController = KanbanController.extend(FileUpload, {
	custom_events: _.extend({}, KanbanController.prototype.custom_events, {
		upload_files: '_onUploadFiles',
    }),
//    _getDirectory: function () {
//        var record = this.model.get(this.handle, {raw: true});
//    	var context = record.getContext();
//    	if (this.selectedDirectory) {
//    		return this.selectedDirectory;
//    	} else if (context.active_model === "muk_dms.directory") {
//    		return context.active_id;
//    	}
//    },
//    _getSidebarDomain: function() {
//    	if (!_.isEmpty(this.activeCategories) && !_.isEmpty(this.activeTags)) {
//    		return ['&', ['category', 'in', this.activeCategories], ['tags', 'in', this.activeTags]];
//    	} else if (!_.isEmpty(this.activeCategories)) {
//    		return [['category', 'in', this.activeCategories]];
//    	} else if (!_.isEmpty(this.activeTags)) {
//    		return [['tags', 'in', this.activeTags]];
//    	}
//    },
	_onUploadFiles: function(event) {
		var directory = this._getDirectory();
		if (directory) {
			utils.getFileTree(event.data.items, true).then(
				this._uploadFiles.bind(this, directory) 
			);
		} else {
			this.do_warn(_t("Upload Error"), _t("No Directory has been selected!"));
		}
	},
});

return FileKanbanController;

});
