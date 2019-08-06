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

odoo.define('muk_dms_action.AbstractFileActions', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var registry = require('web.field_registry');
var fields = require('web.relational_fields');
var crash_manager = require('web.crash_manager');

var AbstractField = require('web.AbstractField');

var _t = core._t;
var QWeb = core.qweb;

var AbstractFileActions = AbstractField.extend({
    fieldsToFetch: {display_name: {type: 'char'}},
    supportedFieldTypes: ['many2many'],
    className: 'mk_file_action',
    init: function () {
        this._super.apply(this, arguments);
        if (this.field.relation !== "muk_dms_actions.action") {
            throw _.str.sprintf(_t(
        		"The field '%s' must be a many2many field with a " +
        		"relation to file actions for the widget to work."
            ), this.field.string);
        }
    },
    isSet: function () {
        return this.value && this.value.count >= 1;
    },
	_onClickAction: function(event) {
		this.trigger_up('file_action', {
            action: $(event.currentTarget).data("id"),
            recordID: this.dataPointID,
        });
		event.stopPropagation();
		event.preventDefault();
	},
});

return AbstractFileActions;

});