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

odoo.define('muk_dms_field_widgets.binary', function(require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var registry = require('web.field_registry');
var field_utils = require('web.field_utils');
var field_widgets = require('web.basic_fields');

var AbstractField = require('web.AbstractField');

var _t = core._t;
var QWeb = core.qweb;

var FieldDocumentBinary = field_widgets.FieldBinaryFile.extend({
	supportedFieldTypes: ['document_binary'],
	willStart: function () {
		var self = this;
		return $.when(this._super.apply(this, arguments)).then(function() {
        	var $max_upload = self._rpc({
                model: 'muk_dms.file',
                method: 'max_upload_size',        	
                args: [],
            }).then(function(max_upload_size) {
            	var max_upload = parseInt(max_upload_size) || 25;
            	self.max_upload_size = max_upload * 1024 * 1024;
            });
        	var $file_record = $.Deferred();
        	if(self.res_id && self.value) {
	        	self._rpc({
	               fields: [
                   		'name', 'mimetype', 'extension', 
     				  	'directory', 'size', 'locked'
     				],
                   domain: [
   	                	['reference_model', '=', self.model],
   	                    ['reference_field', '=', self.name],
   	                    ['reference_id', '=', self.res_id],
                   ],
                   model: 'muk_dms.file',
                   method: 'search_read',
                   context: session.user_context,
	            }).then(function(file_record) {
	            	self.file_record = file_record;
	            	$file_record.resolve();
	            });
        	} else {
            	$file_record.resolve();
        	}
        	return $.when($max_upload, $file_record);
        });
    },
    _parseValue: function (value) {
        return field_utils.parse['binary'](value, this.field, this.parseOptions);
    },
    _renderReadonly: function () {
    	this._super.apply(this, arguments);
        if (this.file_record && this.file_record.length > 0 && this.value) {
        	if (!this.filename_value) {
                this.$el.find('span.fa-download').append(" " + this.file_record[0].name);
            }
        }
    },
});

registry.add('document_binary', FieldDocumentBinary);

return FieldDocumentBinary;

});
