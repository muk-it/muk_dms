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



 openerp.med_dms_preview_file_PreviewHelper = function (instance) {


openerp.med_preview_PreviewDialog(instance);
openerp.med_preview_PreviewGenerator(instance); 
var PreviewGenerator =  new instance.web.PreviewGenerator();

var File =  new instance.web.Model("muk_dms.file");

var _t = instance.web._t,
   _lt = instance.web._lt;
var QWeb = instance.web.qweb;

instance.web.PreviewHelper = instance.web.Class.extend({



	createFilePreviewDialog: function(id) {
		File.query(['name', 'mimetype', 'extension'])
		.filter([['id', '=', id]])
		.all().then(function(file) {
			var download_url = openerp.session.url(
	    		'/web/binary/saveas', {
	    			model: 'muk_dms.file',
	    			filename: file[0].name,
	    			filename_field: 'name',
	    			field: 'content',
	    			id: file[0].id,
	    			download: true
	    	});
			new instance.web.PreviewDialog(parent,new instance.web.PreviewGenerator(self, {}), download_url, file[0].mimetype, file[0].extension, file[0].name).open();
		});
	},
	createFilePreviewContent: function(id) {
		return File.query(['name', 'mimetype', 'extension'])
		.filter([['id', '=', id]])
		.all().then(function(file) {
			var download_url = openerp.session.url(
	    		'/web/binary/saveas', {
	    			model: 'muk_dms.file',
	    			filename: file[0].name,
	    			filename_field: 'name',
	    			field: 'content',
	    			id: file[0].id,
	    			download: true
	    	});
			return PreviewGenerator.createPreview(download_url,file[0].mimetype, file[0].extension, file[0].name);
		});
	},



});

 };