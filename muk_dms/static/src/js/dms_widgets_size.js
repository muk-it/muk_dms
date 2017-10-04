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

odoo.define('muk_dms_widgets.size', function(require) {
"use strict";

var core = require('web.core');
var form_widgets = require('web.form_widgets');
var list_widgets = require('web.ListView');

var _t = core._t;
var QWeb = core.qweb;

function format_size(bytes, si) {
    var thresh = si ? 1000 : 1024;
    if(Math.abs(bytes) < thresh) {
        return bytes + ' B';
    }
    var units = si
        ? ['kB','MB','GB','TB','PB','EB','ZB','YB']
        : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);
    return bytes.toFixed(1) + ' ' + units[u];
}

var SizeFormWidget = form_widgets.FieldFloat.extend({
	render_value: function() {
		var show_value = this.format_value(this.get('value'), '');
		if (this.$input) {
			this._super();
        } else {
            this.$el.text(format_size(show_value, this.options.si));
        }
	},
});

var SizeColumnWidget = list_widgets.Column.extend({
    _format: function (row_data, options) {
        var value = row_data[this.id].value;
        return format_size(value, false);
    }
});

core.form_widget_registry.add('dms_size', SizeFormWidget);
core.list_widget_registry.add('field.dms_size', SizeColumnWidget);


});
