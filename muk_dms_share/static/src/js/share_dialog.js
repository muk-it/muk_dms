/*******************************************************************************
 * 
 * Copyright (C) 2017 MuK IT GmbH
 * 
 * This program is free software: you can redistribute it and/or modify it under
 * the terms of the GNU Affero General Public License as published by the Free
 * Software Foundation, either version 3 of the License, or (at your option) any
 * later version.
 * 
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
 * details.
 * 
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 * 
 ******************************************************************************/

odoo.define('muk_dms_share.dialog', function(require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var ShareDialog = require('muk_web_share.dialog');

var QWeb = core.qweb;
var _t = core._t;

ShareDialog.include({
    formatUrl: function(url) {
    	if(this.__parentedParent && this.__parentedParent.state) {
    		var model = this.__parentedParent.state.model;
    		var data = this.__parentedParent.state.data;
    		if(model === 'muk_dms.file') {
    			var download_url = '/web/content?' + $.param({
            		model: 'muk_dms.file',
        			filename: data.name,
        			filename_field: 'name',
        			field: 'content',
        			id: data.id,
        			download: true
                });
    			return $(QWeb.render('muk_dms_share.FileLink', {
                    widget: this,
                    session: session, 
                    name: data.name || url,
                    url: url,
                    donwload: download_url,
                    id: data.id,
                    mimetype: data.mimetype,
                    extension: data.extension,
                })).html();
    		} else {
    			return this._super.apply(this, arguments);
    		}
    	} 
    	return this._super.apply(this, arguments);
    }
});

});