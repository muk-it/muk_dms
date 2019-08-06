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

odoo.define('muk_dms_view.client_refresh.channel', function (require) {
"use strict";

var config = require('web.config');	
var session = require('web.session');		

var WebClient = require('web.WebClient');
var BusService = require('bus.BusService');

WebClient.include({
    refresh: function(message) {
    	var action = this.action_manager.getCurrentAction();
    	var controller = this.action_manager.getCurrentController();
    	if (!this.call('bus_service', 'isMasterTab') || session.uid !== message.uid && 
    			(message.model === 'muk_dms.directory' || message.model === 'muk_dms.file'),
    			action && controller && controller.widget && action.tag === "muk_dms_view.documents") {
    		controller.widget.reload(message);
        } else {
        	this._super.apply(this, arguments);
        }
    },
});

});
