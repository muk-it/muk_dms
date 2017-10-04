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

odoo.define('muk_dms_preview_file.PreviewHelper', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var Model = require("web.Model");

var PreviewGenerator = require('muk_preview.PreviewGenerator');
var PreviewDialog = require('muk_preview.PreviewDialog');

var File = new Model('muk_dms.file', session.user_context);

var QWeb = core.qweb;
var _t = core._t;

var PreviewHelper = core.Class.extend({
	createFilePreviewDialog: function(id) {
		File.query(['name', 'mimetype', 'extension'])
		.filter([['id', '=', id]])
		.first().then(function(file) {
			var download_url = session.url(
	    		'/web/content', {
	    			model: 'muk_dms.file',
	    			filename: file.name,
	    			filename_field: 'name',
	    			field: 'content',
	    			id: file.id,
	    			download: true
	    	});
			PreviewDialog.createPreviewDialog(self, download_url,
				file.mimetype, file.extension, file.name);
		});
	},
	createFilePreviewContent: function(id) {
		return File.query(['name', 'mimetype', 'extension'])
		.filter([['id', '=', id]])
		.first().then(function(file) {
			var download_url = session.url(
	    		'/web/content', {
	    			model: 'muk_dms.file',
	    			filename: file.name,
	    			filename_field: 'name',
	    			field: 'content',
	    			id: file.id,
	    			download: true
	    	});
			return PreviewGenerator.createPreview(self, download_url,
				file.mimetype, file.extension, file.name);
		});
	}
});

PreviewHelper.createFilePreviewDialog = function(id) {
    return new PreviewHelper().createFilePreviewDialog(id);
};

PreviewHelper.createFilePreviewContent = function(id) {
    return new PreviewHelper().createFilePreviewContent(id);
};

return PreviewHelper;

});