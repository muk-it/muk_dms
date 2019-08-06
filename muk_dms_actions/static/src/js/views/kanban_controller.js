/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Documents Actions 
*    (see https://mukit.at).
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
*    along with this program. If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define('muk_dms.FileActionKanbanController', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var session = require('web.session');

var FileKanbanController = require('muk_dms.FileKanbanController');

var _t = core._t;
var QWeb = core.qweb;

FileKanbanController.include({
	custom_events: _.extend({}, FileKanbanController.prototype.custom_events, {
        file_action: '_onFileAction',
    }),
    _onFileAction: function(event) {
    	var self = this;
    	this._rpc({
            model: 'muk_dms_actions.action',
            method: 'trigger_actions',
            args: [[event.data.action], this.model.get(event.data.recordID).res_id],
        }).then(function (result) {
        	if (_.isObject(result)) {
                return self.do_action(result);
            } else {
                return self.reload();
            }
        });
    	event.stopPropagation();
    },
});

});
