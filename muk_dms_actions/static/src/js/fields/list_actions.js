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

odoo.define('muk_dms_action.ListFileActions', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var registry = require('web.field_registry');
var fields = require('web.relational_fields');
var crash_manager = require('web.crash_manager');

var AbstractFileActions = require('muk_dms_action.AbstractFileActions');

var _t = core._t;
var QWeb = core.qweb;

var ListFileActions = AbstractFileActions.extend({
    events: {
        'click a.dropdown-item': '_onClickAction',
		'click .dropdown-toggle': '_onClickDropdown',
    },
    _render: function () {
    	if (this.value && this.value.count >= 1) {
    		this.$el.html(QWeb.render("muk_dms_actions.ListFileActions", {
    			actions: this.value ? _.pluck(this.value.data, 'data') : [],
        	}));
    		this.$el.addClass('dropdown');
    	}
	},
	_onClickDropdown: function(event) {
		this.$('.dropdown-toggle').dropdown('toggle');
		event.stopPropagation();
		event.preventDefault();
	},
});

registry.add('list.file_actions', ListFileActions);

return ListFileActions;

});