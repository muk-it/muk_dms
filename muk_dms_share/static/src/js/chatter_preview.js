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

odoo.define('muk_dms_share.ChatterPreview', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var Thread = require('mail.ChatThread');

var PreviewDialog = require('muk_preview.PreviewDialog');

var QWeb = core.qweb;
var _t = core._t;

Thread.include({
	init: function() {
		this._super.apply(this, arguments);
		this.events = _.extend(this.events, {
            'click a[href="#dms_preview"]': '_onDMSFilePreview',
        });
	},
	_onDMSFilePreview: function (event) {
		event.preventDefault();
		event.stopPropagation();
	    var $target = $(event.currentTarget);
	    PreviewDialog.createPreviewDialog(this, $target.data('dms_url'),
	    		 $target.data('dms_mimetype'),  $target.data('dms_extension'),
	    		 $target.data('dms_name'));
    },
});

});